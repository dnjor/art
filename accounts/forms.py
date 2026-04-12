from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=10, label="رقم الهاتف")
    notifications = forms.BooleanField(
        required=False,
        label="أريد تلقي الإشعارات عبر البريد الإلكتروني عن ورش العمل الجديدة والتحديثات.",
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        label="كلمة المرور",
        error_messages={
            "min_length": "كلمة المرور يجب أن تكون على الأقل 8 أحرف."
        },
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone_number",
            "password",
            "notifications",
        ]
        help_texts = {
            "username": None,
        }
        labels = {
            "username": "اسم المستخدم",
            "email": "البريد الإلكتروني",
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("اسم المستخدم مستخدم بالفعل.")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("البريد الإلكتروني مستخدم بالفعل.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("رقم الهاتف مستخدم بالفعل.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = (self.cleaned_data.get("email") or "").strip()
        user.set_password(self.cleaned_data["password"])

        user.is_active = False  # Deactivate account until email confirmation

        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                phone_number=self.cleaned_data["phone_number"],
                notifications=self.cleaned_data["notifications"],
            )

        return user


class CoustmLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={"placeholder": "name@example.com"}),
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={"placeholder": "********"}),
    )

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            try:
                user = User.objects.get(email__iexact=email)
                
            except User.DoesNotExist:
                raise forms.ValidationError("لا يوجد مستخدم بهذا البريد الإلكتروني.")
            
            self.cleaned_data["username"] = user.username
        return super().clean()
