from rest_framework import serializers
from .models import Workshop


class WorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = [
            "id",
            "title",
            "image",
            "description",
            "start_date",
            "end_date",
            "deadline",
            "cost",
            "seats",
            "sessions",
            "zoom_link",
            "status",
            "created_at",
        ]

