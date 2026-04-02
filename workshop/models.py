from django.conf import settings
from django.db import models


class Workshop(models.Model):
    STATUS_CHOICES = [
        ("open", "متاح للتسجيل"),
        ("closed", "مغلقة"),
        ("ended", "منتهية"),
        ("cancelled", "ملغية"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workshops"
    )
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="workshops/")
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField()
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    seats = models.PositiveIntegerField(blank=True, null=True)
    sessions = models.PositiveIntegerField()
    zoom_link = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Registration(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("under_review", "Under Review"),
        ("confirmed", "Confirmed"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations"
    )
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.CASCADE,
        related_name="registrations"
    )
    payment_proof = models.ImageField(upload_to="payment_proofs/", blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="under_review"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.workshop.title}"
