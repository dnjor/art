from django import forms
from .models import Painting, Comments

class PaintingForm(forms.ModelForm):
    class Meta:
        model = Painting
        fields = [
            "title",
            "picture",
            "description"
        ]
        labels = {
            "title": "العنوان",
            "picture": "الصورة",
            "description": "الوصف"
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = [
            "comment"
        ]
        labels = {
            "comment": "تعليق"
        }

