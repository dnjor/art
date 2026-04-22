from rest_framework import serializers
from .models import Workshop


class WorkshopSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

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

    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
