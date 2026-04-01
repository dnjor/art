from django.db import models

class User(models.Model):
    username = models.CharField(max_length=64, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=128, null=False)
    notifications = models.BooleanField(default=True)