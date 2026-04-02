from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import WorkshopForm, RegistrationForm
from .models import Registration, Workshop


def close_expired_workshops():
    Workshop.objects.filter(
        status="open",
        deadline__lt=timezone.now(),
    ).update(status="closed")


def workshop_list(request):
    close_expired_workshops()
    workshops = Workshop.objects.order_by("start_date")

    return render(
        request,
        "workshop/workshop_list.html",
        {"workshops": workshops},
    )


@login_required
def create_workshop(request):
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
    close_expired_workshops()
    workshop = get_object_or_404(Workshop, id=workshop_id)
    return render(
        request,
        "workshop/workshop_detail.html", {
        "workshop": workshop
    })


@login_required
def register_workshop(request, workshop_id):
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
    if not request.user.is_staff:
        return redirect("workshop_list")

    workshop = get_object_or_404(Workshop, id=workshop_id)
    registrations = workshop.registrations.select_related("user").order_by("-created_at")

    return render(request, "workshop/workshop_registrations.html", {
        "workshop": workshop,
        "registrations": registrations,
    })


@login_required
def update_registration_status(request, registration_id, status):
    # Only staff can confirm or reject uploaded payment proofs.
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
