from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

# libary for checking email
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from workshop.views import send_email

from .forms import RegisterForm, CoustmLoginForm
from .models import Profile
from gallery.models import Painting
from workshop.models import Workshop, Registration


def index(request):
    if request.user.is_authenticated:
        response = check_google_login(request)
        if response:
            return response

    return render(
        request,
        "accounts/index.html",
        {
            "painting": Painting.objects.filter(is_active=True).count(),
            "workshop": Workshop.objects.filter(status="ended").count() + 30,
            "registers": Registration.objects.filter(payment_status="confirmed").count()
            + 250,
        },
    )


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

            try:
                send_verification_email(request, user) # check if the user use his email
            except Exception as e:
                print("Email Error:", e)

            messages.success(
                request,
                "تم إنشاء الحساب بنجاح. يرجى التحقق من بريدك الإلكتروني لتفعيل الحساب.",
            )
            return redirect("accounts:login")

        else:
            return render(
                request,
                "accounts/register.html",
                {
                    "message": "خطأ في التسجيل. يرجى التحقق من البيانات المدخلة.",
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
    """check if the user login with google or not"""
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
    """Handle the case when a user logged in with google"""
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


def send_verification_email(request, user):
    """Send verification to his email"""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    # Create secure one-time token
    token = default_token_generator.make_token(user)

    # Build activation URL
    activation_url = request.build_absolute_uri(
        reverse("accounts:activate_account", kwargs={"uidb64": uidb64, "token": token})
    )

    # Email subject
    subject = "Verify your email address"

    # Plain text email body
    message = f"""
اهلااً {user.username},

شكرا لك على التسجيل.

من فضلك اضغط على الرابط التالي لتأكيد بريدك الإلكتروني:

{activation_url}

اذا لم تقم بإنشاء هذا الحساب، يمكنك تجاهل هذا البريد الإلكتروني.
"""

    # Send email
    send_email(
        subject,
        message,
        [user.email],
    )


def activate_account(request, uidb64, token):
    """"Check if user click the link"""
    User = get_user_model()

    try:
        # Decode the user id from the URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Validate token
    if user is not None and default_token_generator.check_token(user, token):
        # Activate account
        user.is_active = True
        user.save(update_fields=["is_active"])

        messages.success(request, "تم تفعيل حسابك بنجاح. يمكنك الآن تسجيل الدخول.")
        return redirect("accounts:login")

    messages.error(request, " الرابط غير صحيح أو انتهت صلاحيته.")
    return redirect("accounts:register")
