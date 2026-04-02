from django.contrib.auth import logout
from django.shortcuts import render

from .forms import RegisterForm


def index(request):
    return render(request, "account/index.html")


def login(request):
    return render(request, "account/login.html")


def logout(request):
    logout(request)


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            # The form now creates both the User and the Profile for us.
            user = form.save()
            return render(request, "account/index.html", {
                "message": "تم انشاء الحساب بالنجاح",
                "user": user
            })
        else:
            return render(request, "account/register.html", {
                "message": "حدث خطأ في انشاء الحساب",
                "form": form
            })

    return render(request, "account/register.html", {
        "form": RegisterForm()})
