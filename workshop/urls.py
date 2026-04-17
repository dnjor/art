from django.urls import path
from . import views

urlpatterns = [
    path("", views.workshop_list, name="workshop_list"),
    path("<int:workshop_id>/", views.workshop_detail, name="workshop_detail"),
    path("create/", views.create_workshop, name="create_workshop"),
    path("update/<int:workshop_id>/", views.update_workshop, name="update_workshop"),
    path(
        "register/<int:workshop_id>/", views.register_workshop, name="register_workshop"
    ),
    path(
        "<int:workshop_id>/registrations/",
        views.workshop_registrations,
        name="workshop_registrations",
    ),
    path(
        "<int:workshop_id>/registrations/send_review/",
        views.send_link_review,
        name="send_link_review",
    ),
    path(
        "registrations/<int:registration_id>/<str:status>/",
        views.update_registration_status,
        name="update_registration_status",
    ),
]
