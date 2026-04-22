from rest_framework import serializers
from .models import Painting


class PaintingSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()

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

    def get_picture(self, obj):
        if obj.picture:
            return obj.picture.url
        return None
