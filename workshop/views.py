from django.contrib import messages  # For showing success or error messages to the user
from django.contrib.auth.decorators import (
    login_required,
)  # To restrict access to certain views to only logged-in users
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import (
    timezone,
)  # To handle date and time, especially for checking workshop deadlines
from django.core.mail import send_mail

from accounts.models import (
    Profile,
)  # For sending emails to users when their payment proof is confirmed or rejected
from .forms import WorkshopForm, RegistrationForm
from .models import Registration, Workshop
from reviews.models import Review


def close_expired_workshops():
    """This function checks for workshops that have passed their deadline and updates their status to closed."""
    Workshop.objects.filter(
        status="open",
        deadline__lt=timezone.now(),
    ).update(status="closed")


def workshop_list(request):
    """Display workshop page, and reviews"""
    reviews = list(Review.objects.filter(status="approved").order_by("-created_at"))

    for review in reviews:
        review.star_range = range(max(int(review.average or 0), 0))

    return render(request, "workshop/workshop_list.html", {"reviews": reviews})


@login_required
def create_workshop(request):
    """ "Create a new workshop, only staff users can access this view"""
    if not request.user.is_staff:
        return redirect("workshop:workshop_list")

    if request.method == "POST":
        form = WorkshopForm(request.POST, request.FILES)

        if form.is_valid():
            workshop_detail = form.save(commit=False)
            workshop_detail.user = request.user
            workshop_detail = form.save()

            users = Profile.objects.filter(notifications=True).select_related("user")

            for user in users:

                subject = f"ورشة عمل جديدة: {workshop_detail.title}"

                message = f""" مرحباً {user.user.username}!

                تم إضافة ورشة عمل جديدة

                {workshop_detail.title} عنوان الورشة:

                يمكنك زيارة الموقع للاطلاع على تفاصيل كاملة والتسجيل:
                http://arwa-art.onrender.com/workshop/{workshop_detail.id}/

                مع خالص التحية,
                منصة اروى الفنية
                """

                send_email(subject, message, [user.user.email])

            messages.success(request, "تم إنشاء الورشة بنجاح")
            return redirect("workshop:workshop_list")
    else:
        form = WorkshopForm(initial={"status": "open"})

    return render(
        request,
        "workshop/create_workshop.html",
        {"form": form},
    )


@login_required
def update_workshop(request, workshop_id):
    if not request.user.is_staff:
        return redirect("workshop:workshop_list")

    close_expired_workshops()
    workshop = get_object_or_404(Workshop, id=workshop_id)

    if request.method == "POST":
        form = WorkshopForm(request.POST, request.FILES, instance=workshop)
        new_picture = request.FILES.get("picture")

        if form.is_valid():
            workshop = form.save(commit=False)

            if new_picture:
                workshop.image = new_picture

        workshop.save()
        messages.success(request, "تم تحديث الورشة بنجاح")
        return redirect("workshop:workshop_list")
    else:
        form = WorkshopForm(instance=workshop)

    return render(
        request,
        "workshop/update_workshop.html",
        {
            "form": form,
            "workshop": workshop,
        },
    )


def workshop_detail(request, workshop_id):
    close_expired_workshops()
    workshop = get_object_or_404(Workshop, id=workshop_id)

    return render(
        request,
        "workshop/workshop_detail.html",
        {
            "workshop": workshop,
        },
    )


@login_required
def register_workshop(request, workshop_id):
    """This view allows users to register for a workshop by uploading a payment proof."""
    workshop = get_object_or_404(Workshop, id=workshop_id)

    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.workshop = workshop
            registration.save()

            request.user.profile.notifications = True  # Enable notifications for the user when they register for a workshop, so they can receive updates about their registration status.
            request.user.profile.save()

            messages.success(
                request,
                "تم رفع إثبات الدفع بنجاح، سيتم مراجعة طلبك قريبًا, واعلامك عبر البريد الإلكتروني",
            )
            return redirect("workshop:workshop_detail", workshop_id=workshop.id)
        else:
            messages.error(
                request, "حدث خطأ في رفع إثبات الدفع، يرجى المحاولة مرة أخرى"
            )

    return render(
        request,
        "workshop/register_workshop.html",
        {"workshop": workshop, "form": RegistrationForm()},
    )


@login_required
def workshop_registrations(request, workshop_id):
    """Display all the registrations how regisrt in the workshop"""
    if not request.user.is_staff:
        return redirect("workshop:workshop_list")

    workshop = get_object_or_404(Workshop, id=workshop_id)
    registrations = workshop.registrations.select_related(
        "user", "user__profile"
    ).order_by("-created_at")

    return render(
        request,
        "workshop/workshop_registrations.html",
        {
            "workshop": workshop,
            "registrations": registrations,
        },
    )


@login_required
def update_registration_status(request, workshop_id, registration_user):
    """Updating by confirmed or rejected for evrey registrations"""
    if not request.user.is_staff:
        return redirect("workshop:workshop_list")

    workshop = get_object_or_404(Workshop, id=workshop_id)
    registration = Registration.objects.get(workshop=workshop, user=registration_user)

    if request.method == "POST":
        status = request.POST.get("payment_status")

        if status == "confirmed":
            subject = f" تحديث بخصوص طلبك في ورشة العمل: {workshop.title}"

            message = f""" مرحباً {registration.user.username}!

            يسرنا أبلاغك بانه تمت الموافقة على طلب تسجيلك في ورشة عمل

            يمكنك زيارة الموقع للاطلاع على تفاصيل الورشة ومتابعة اي تحديثات متعلقة بها:
            http://arwa-art.onrender.com/workshop/{workshop.id}/

            مع خالص التحية,
            منصة اروى الفنية
            """

            send_email(subject, message, [registration.user.email])

        elif status == "rejected":
            subject = f" تحديث بخصوص طلبك في ورشة العمل: {workshop.title}"

            message = f""" مرحباً {registration.user.username}!

            نأسف لإبلاغك بانه تم رفض طلب تسجيلك في ورشة عمل

            للاعتراض زور الموقع وتواصل معنا عبر تطبيق الواتساب مع ذكر اسم الورشة التي قدمت لها، وسنقوم بمراجعة طلبك مرة أخرى.

            رابط الموقع:
            http://arwa-art.onrender.com

            مع خالص التحية,
            منصة اروى الفنية
            """

            send_email(subject, message, [registration.user.email])
        
        else:
            messages.error(request, "الرجاء تحديد حالة التسجيل بقول او الرفض.")
            return redirect("workshop:workshop_registrations", workshop_id=workshop.id)

        registration.payment_status = status
        registration.save()

        messages.success(request, "تم تحديث حالة التسجيل بنجاح.")
        return redirect("workshop:workshop_registrations", workshop_id=workshop.id)


@login_required
def send_link_review(request, workshop_id):
    if not request.user.is_staff:
        return redirect("workshop:workshop_list")

    registrations = Registration.objects.filter(workshop=workshop_id)
    workshop = get_object_or_404(Workshop, id=workshop_id)

    if workshop.registration_email_sent_at:
        messages.error(request, "تم ارسال للمشاركين رابط التقييم من قبل.")
        return redirect("workshop:workshop_list")

    if not registrations.exists():
        messages.error(request, "لا يوجد مسجلين في الورشة")
        return redirect("workshop:workshop_list")

    for registration in registrations:
        subject = f" شاركنا رأيك في الورشة - تقييمك يهمنا {registration.workshop.title}"

        message = f""" اهلااَ {registration.user.username}!

        نود معرفة رأيك في الورشة التي حضرتها.
        تقييمك يساعدنا على تطوير وتحسين ورشاتنا القادمة

        اضغط على الرابط لتقييم الورشة:
        {{ https://forms.gle/MLntK1YXrMZs3owUA }}

        شكراَ لك
        """

        send_email(subject, message, [registration.user.email])

    workshop.registration_email_sent_at = timezone.now()
    workshop.save()
    messages.success(request, "تم ارسال رابط التقييم لجميع المسجلين")
    return redirect("workshop:workshop_list")


def send_email(subject, message, recipient_list):
    send_mail(
        subject=subject,  # Email title
        message=message,  # Email content
        from_email=None,  # Use DEFAULT_FROM_EMAIL from settings.py
        recipient_list=recipient_list,  # Who will receive the email
        fail_silently=False,  # Show error if sending fails
    )
