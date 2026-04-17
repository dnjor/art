from django.urls import path
from . import views


urlpatterns = [
    path("", views.reviews_list, name="reviews_list"),
    path("sync/", views.sync_review_from_sheet, name="sync_review_from_sheet"),
]
