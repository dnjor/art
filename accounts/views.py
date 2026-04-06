from django.contrib.auth import logout
from django.shortcuts import redirect, render
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from .models import Profile


def index(request):
    if request.user.is_authenticated:
        response = check_google_login(request)
        if response:
            return response
    
    return render(request, "accounts/index.html")

def login(request):
    return render(request, "accounts/login.html")


def logout(request):
    logout(request)


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            # The form now creates both the User and the Profile for us.
            user = form.save()
            return render(request, "accounts/index.html", {
                "message": "تم انشاء الحساب بالنجاح",
                "user": user
            })
        else:
            return render(request, "accounts/register.html", {
                "message": "حدث خطأ في انشاء الحساب",
                "form": form
            })

    return render(request, "accounts/register.html", {
        "form": RegisterForm()})


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
        user=user,
        defaults={
            "phone_number": "",
            "notifications": True,
        }
    )

    if not profile.phone_number:
        return redirect("login_incomplete")

    return None


@login_required
def login_incomplete(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "phone_number": "",
            "notifications": True,
        }
    )

    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        notifications = request.POST.get("notifications") == "on"

        if Profile.objects.filter(phone_number=phone_number).exists():
            return render(request, "accounts/login_incomplete.html", {
                "message": "رقم الهاتف هذا مستخدم بالفعل. يرجى استخدام رقم هاتف آخر.",
                "user": request.user
            })

        profile.phone_number = phone_number
        profile.notifications = notifications
        profile.save()

        return render(request, "accounts/index.html", {
            "message": "تم تحديث رقم الهاتف بنجاح.",
            "user": request.user
        })

    return render(request, "accounts/login_incomplete.html", {
        "message": "يرجى إكمال تسجيل الدخول بإضافة رقم هاتفك.",
        "user": request.user
    })

