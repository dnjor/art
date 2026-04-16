from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    workshop = models.ForeignKey(
        "workshop.Workshop",
        on_delete=models.CASCADE,
        related_name="reviews",
        blank=True,
        null=True,
    )
    review_name = models.CharField(max_length=100, blank=True)
    rating_1 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_2 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_3 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_4 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_5 = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    average = models.DecimalField(max_digits=3, decimal_places=2, editable=False)
    comment = models.TextField(blank=True)
    status = models.CharField(choices=STATUS_CHOICES, default="pending")
    source_timestamp = models.CharField(max_length=100,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.average = (
            self.rating_1 +
            self.rating_2 +
            self.rating_3 +
            self.rating_4 +
            self.rating_5
        ) / 5
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.workshop} - {self.review_name or 'Anonymous'} - {self.average}"

