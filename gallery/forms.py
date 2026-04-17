from django import forms
from .models import Painting, Comments


class PaintingForm(forms.ModelForm):

    class Meta:
        model = Painting
        fields = ["title", "picture", "description"]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 8, "class": "custom-textarea"})
        }

        labels = {"title": "العنوان", "picture": "الصورة", "description": "الوصف"}

    def clean_title(self):
        title = self.cleaned_data.get("title")

        if not title:
            raise forms.ValidationError("العنوان مطلوب")

        # Checking if there another painitng in the same name, and exclude the one he edit it
        if Painting.objects.filter(title=title).exclude(id=self.instance.id):
            raise forms.ValidationError("عنوان اللوحة مستخدم بالفعل")

        return title


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["comment"]
        labels = {"comment": "تعليق"}
