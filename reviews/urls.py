from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.reviews_list, name="reviews_list"),
    
    path("sync/", views.sync_review_from_sheet, name="sync_review_from_sheet"),
]
