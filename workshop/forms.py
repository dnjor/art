from django import forms

from .models import Workshop, Registration


class WorkshopForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
        label="تاريخ البداية",
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
        label="تاريخ النهاية",
        required=False,
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
            "start_date",
            "end_date",
            "deadline",
            "cost",
            "sessions",
            "seats",
            "zoom_link",
            "status",
        ]
        labels = {
            "title": "العنوان",
            "image": "الصورة",
            "description": "الوصف",
            "cost": "السعر",
            "sessions": "عدد الجلسات",
            "seats": "عدد المقاعد",
            "zoom_link": "رابط زوم",
            "status": "الحالة",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        deadline = cleaned_data.get("deadline")

        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "تاريخ النهاية يجب أن يكون بعد تاريخ البداية")

        if start_date and deadline and deadline > start_date:
            self.add_error("deadline", "آخر موعد للتسجيل يجب أن يكون قبل بداية الورشة")

        return cleaned_data


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ["payment_proof"]
        labels = {"payment_proof": "إثبات الدفع"}
