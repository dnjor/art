from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

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
        })

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
            "email": "البريد الإلكتروني"
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("اسم المستخدم بالفعل مستخدم.")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("رقم الهاتف بالفعل مستخدم.")
        return phone_number

    def save(self, commit=True):
        # Save the Django auth user first, then create the related profile.
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                phone_number=self.cleaned_data["phone_number"],
                notifications=self.cleaned_data["notifications"],
            )

        return user

class CoustmLoginForm(AuthenticationForm):
    username = forms.CharField(label="اسم المستخدم")
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput)
