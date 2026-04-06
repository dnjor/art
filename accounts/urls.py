from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import CoustmLoginForm


urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=CoustmLoginForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("login_incomplete/", views.login_incomplete, name="login_incomplete"),
]
