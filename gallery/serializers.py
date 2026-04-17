from rest_framework import serializers
from .models import Painting


class PaintingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Painting
        fields = [
            "id",
            "title",
            "picture",
            "description",
            "date",
            "is_active",
        ]
