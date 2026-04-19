from django.urls import path
from . import views

app_name = "gallery"

urlpatterns = [
    path("", views.gallery, name="gallery"),
    path("uplode/", views.uplode_painting, name="uplode_painting"),
    path("update/<int:painting_id>/", views.edit_painting, name="edit_painting"),
    path("delete/<int:painting_id>/", views.delete_painting, name="delete_painting"),
    path("painting/<int:painting_id>/", views.painting_detail, name="painting_detail"),
    path("painting/<int:painting_id>/comment", views.add_comment, name="add_comment"),
    path("painting/<int:painting_id>/like", views.add_like, name="add_like"),
]
