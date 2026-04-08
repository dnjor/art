from django.contrib import messages # For showing success or error messages to the user
from django.contrib.auth.decorators import login_required # To restrict access to certain views to only logged-in users
from django.shortcuts import get_object_or_404, redirect, render 
from django.utils import timezone # To handle date and time, especially for checking workshop deadlines
from django.core.mail import send_mail

from accounts.models import Profile # For sending emails to users when their payment proof is confirmed or rejected
from .forms import WorkshopForm, RegistrationForm 
from .models import Registration, Workshop 


def close_expired_workshops():
    """This function checks for workshops that have passed their deadline and updates their status to closed."""
    Workshop.objects.filter(
        status="open",
        deadline__lt=timezone.now(),
    ).update(status="closed")


def workshop_list(request):
    """Display a list of all workshops"""
    close_expired_workshops()
    workshops = Workshop.objects.order_by("start_date")

    return render(
        request,
        "workshop/workshop_list.html",
        {"workshops": workshops},
    )


@login_required
def create_workshop(request):
    """"Create a new workshop, only staff users can access this view"""
    if not request.user.is_staff:
        return redirect("workshop_list")

    if request.method == "POST":
        form = WorkshopForm(request.POST, request.FILES)
        if form.is_valid():
            workshop = form.save(commit=False)
            workshop.user = request.user
            workshop.save()
            messages.success(request, "تم إنشاء الورشة بنجاح")
            return redirect("workshop_list")
    else:
        form = WorkshopForm(initial={"status": "open"})

    return render(
        request,
        "workshop/create_workshop.html",
        {"form": form},
    )


@login_required
def update_workshop(request, workshop_id):
    """"This view allows staff users to update their workshops details"""
    if not request.user.is_staff:
        return redirect("workshop_list")

    close_expired_workshops()
    workshop = get_object_or_404(Workshop, id=workshop_id)

    if request.method == "POST":
        form = WorkshopForm(request.POST, request.FILES, instance=workshop)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث الورشة بنجاح")
            return redirect("workshop_list")
    else:
        form = WorkshopForm(instance=workshop)

    return render(
        request,
        "workshop/update_workshop.html",
        {"form": form, "workshop": workshop},
    )


def workshop_detail(request, workshop_id):
    """Display details of the workshop"""
    close_expired_workshops()
    workshop = get_object_or_404(Workshop, id=workshop_id)
    return render(
        request,
        "workshop/workshop_detail.html", {
        "workshop": workshop
    })


@login_required
def register_workshop(request, workshop_id):
    """ This view allows users to register for a workshop by uploading a payment proof. """
    workshop = get_object_or_404(Workshop, id=workshop_id)

    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.workshop = workshop
            registration.save()
            messages.success(request, 
            "تم رفع إثبات الدفع بنجاح، سيتم مراجعة طلبك قريبًا")
            return redirect("workshop_detail", workshop_id=workshop.id)
        else:
            messages.error(request,
            "حدث خطأ في رفع إثبات الدفع، يرجى المحاولة مرة أخرى")

    return render(request, "workshop/register_workshop.html", {
        "workshop": workshop,
        "form": RegistrationForm()
        })


@login_required
def workshop_registrations(request, workshop_id):
    # This page is only for staff so the artist can review one workshop at a time.
    # update and let sending email to the user when the payment proof is confirmed or rejected.
    if not request.user.is_staff:
        return redirect("workshop_list")

    workshop = get_object_or_404(Workshop, id=workshop_id)
    registrations = workshop.registrations.select_related("user", "user__profile").order_by("-created_at")

    return render(request, "workshop/workshop_registrations.html", {
        "workshop": workshop,
        "registrations": registrations,
        #we want the phone number apper
        #there a bug with the workshop it do not update after the workshop close
    })

# Check both functions up and below

@login_required
def update_registration_status(request, registration_id, status):
    # Only staff can confirm or reject uploaded payment proofs.
    # update and let sending email to the user when the payment proof is confirmed or rejected.
    if not request.user.is_staff:
        return redirect("workshop_list")

    registration = get_object_or_404(Registration, id=registration_id)

    if status not in ["confirmed", "rejected"]:
        messages.error(request, "حالة الدفع غير صحيحة.")
        return redirect("workshop_registrations", workshop_id=registration.workshop.id)

    registration.payment_status = status
    registration.save()

    messages.success(request, "تم تحديث حالة التسجيل بنجاح.")
    return redirect("workshop_registrations", workshop_id=registration.workshop.id)


def send_email(subject, message, recipient_list):
    """
    Reusable function for sending emails in the project.

    subject: email title
    message: email body
    recipient_list: list of receiver emails
    """

    send_mail(
        subject=subject,          # Email title
        message=message,          # Email content
        from_email=None,          # Use DEFAULT_FROM_EMAIL from settings.py
        recipient_list=recipient_list,   # Who will receive the email
        fail_silently=False       # Show error if sending fails
    )
