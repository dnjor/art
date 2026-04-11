from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegisterForm, CoustmLoginForm
from .models import Profile
from gallery.models import Painting
from workshop.models import Workshop, Registration


def index(request):
    if request.user.is_authenticated:
        response = check_google_login(request)
        if response:
            return response

        
    return render(request, "accounts/index.html",
    {
        "painting": Painting.objects.filter(is_active=True).count(),
        "workshop": Workshop.objects.filter(status="ended").count() + 30 ,
        "registers": Registration.objects.filter(payment_status="confirmed").count() + 250 ,
    })


def login(request):
    if request.method == "POST":
        form = CoustmLoginForm(request=request, data=request.POST)

        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("index")

        return render(
            request,
            "accounts/login.html",
            {
                "message": "خطأ في تسجيل الدخول. يرجى التحقق من البريد الإلكتروني وكلمة المرور.",
                "form": form,
            },
        )

    return render(
        request,
        "accounts/login.html",
        {
            "form": CoustmLoginForm(request=request),
        },
    )


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            authenticated_user = authenticate(
                request,
                username=user.username,
                password=form.cleaned_data["password"],
            )

            if authenticated_user is not None:
                auth_login(request, authenticated_user)
                messages.success(request, "تم إنشاء الحساب بنجاح.")
                return redirect("index")

            return render(
                request,
                "accounts/register.html",
                {
                    "message": "تم إنشاء الحساب ولكن لم يتم تسجيل الدخول تلقائياً.",
                    "form": RegisterForm(),
                },
            )

        return render(
            request,
            "accounts/register.html",
            {
                "message": "حدث خطأ في إنشاء الحساب",
                "form": form,
            },
        )

    return render(
        request,
        "accounts/register.html",
        {
            "form": RegisterForm(),
        },
    )


def login_by_google(user):
    """Return Google email and first name if the user logged in with Google."""
    social_account = user.socialaccount_set.first()

    if social_account and social_account.provider == "google":
        extra_data = social_account.extra_data
        email = extra_data.get("email")
        username = extra_data.get("given_name")
        return email, username

    return None, None


def check_google_login(request):
    user = request.user
    email, username = login_by_google(user)

    if not email and not username:
        return None

    if email:
        user.email = email

    if username and not user.username:
        user.username = username

    user.save()

    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "phone_number": "",
            "notifications": True,
        },
    )

    if not user.profile.phone_number:
        return redirect("accounts:login_incomplete")

    return None


@login_required
def login_incomplete(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        notifications = request.POST.get("notifications") == "on"

        if Profile.objects.filter(phone_number=phone_number).exists():
            return render(
                request,
                "accounts/login_incomplete.html",
                {
                    "message": "رقم الهاتف هذا مستخدم بالفعل. يرجى استخدام رقم هاتف آخر.",
                    "user": request.user,
                },
            )
        
        profile = Profile.objects.get(user=request.user)
        profile.phone_number = phone_number
        profile.notifications = notifications
        profile.save()

        return render(
            request,
            "accounts/index.html",
            {
                "message": "تم تحديث رقم الهاتف بنجاح.",
                "user": request.user,
            },
        )

    return render(
        request,
        "accounts/login_incomplete.html",
        {
            "message": "يرجى إكمال تسجيل الدخول بإضافة رقم هاتفك.",
            "user": request.user,
        },
    )
