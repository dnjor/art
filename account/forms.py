from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        error_messages={
            "min_length": "password must be at least 8 charachers long."
        })

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        help_texts = {
            "username": None,
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("username already exists.")
        return username
