from django.conf import settings
from django.db import models


class Profile(models.Model):
    # Keep Django's built-in user and store extra account fields here.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, unique=True)
    notifications = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
