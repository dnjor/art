from django.urls import path
from . import views

urlpatterns = [
    path("", views.gallery, name="gallery"),
    path("uplode/", views.uplode_painting, name="uplode_painting")
]
