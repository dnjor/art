from django.urls import path
from . import views

urlpatterns = [
    path("", views.workshop_list, name="workshop_list"),
    path("create/", views.create_workshop, name="create_workshop"),
]
