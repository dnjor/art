from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import CoustmLoginForm

app_name = "accounts"

urlpatterns = [
    path("index/", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/",views.login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("login_incomplete/", views.login_incomplete, name="login_incomplete"),
]
