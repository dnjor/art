from django import forms

from .models import Workshop


class WorkshopForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
        label="التاريخ",
    )
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
        label="آخر موعد للتسجيل",
    )

    class Meta:
        model = Workshop
        fields = [
            "title",
            "image",
            "description",
            "date",
            "deadline",
            "cost",
            "sessions",
            "seats",
            "zoom_link",
        ]
        labels = {
            "title": "العنوان",
            "image": "الصورة",
            "description": "الوصف",
            "cost": "السعر",
            "sessions": "عدد الجلسات",
            "seats": "عدد المقاعد",
            "zoom_link": "رابط زوم",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }
