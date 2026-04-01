from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from .forms import WorkshopForm
from .models import Workshop


def workshop_list(request):
    workshops = Workshop.objects.filter(deadline__gte=timezone.now()).order_by("date")
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
            return redirect("workshop_list")
    else:
        form = WorkshopForm()

    return render(
        request,
        "workshop/create_workshop.html",
        {"form": form},
    )
