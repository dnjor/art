from django.test import override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
from datetime import datetime
from django.core import mail
from .views import send_email

from accounts.test_base import SocialAppTestCase
from .models import Workshop, Registration
from accounts.models import Profile
User = get_user_model()


class WorkshopBaseTestCase(SocialAppTestCase):

    @staticmethod
    def generate_test_image_file():
        file_obj = BytesIO()
        image = Image.new("RGB", (100, 100), color="red")
        image.save(file_obj, "JPEG")
        file_obj.seek(0)

        return SimpleUploadedFile(
            name="test.jpg",
            content=file_obj.read(),
            content_type="image/jpeg"
        )

    @classmethod
    def setUpTestData(cls):
        cls.normal_user = User.objects.create_user(
            username="ali",
            email="ali@gmail.com",
            password="password123",
            is_active=True
        )
        
        cls.profile = Profile.objects.create(
            user=cls.normal_user,
            phone_number="0511111111",
            notifications=True
        )

        cls.staff_user = User.objects.create_user(
            username="admin",
            email="admin@gmail.com",
            password="admin123",
            is_active=True,
            is_staff=True
        )

        cls.workshop = Workshop.objects.create(
            user=cls.staff_user,
            title="ورشة فحم",
            image=cls.generate_test_image_file(),
            description="راح نتعلم كيف نقدر نتسخدم الفحم على اللوحات",
            start_date=datetime(2026, 4, 20, 10, 30),
            end_date=datetime(2026, 4, 29, 10, 30),
            deadline=datetime(2026, 4, 19, 10, 30),
            cost="100",
            sessions="10",
        )

        cls.register = Registration.objects.create(
            user=cls.normal_user,
            workshop=cls.workshop,
            payment_proof=cls.generate_test_image_file(),
            payment_status="under_review",
        )

    def get_valid_workshop_data(self, **overrides):
        data = {
            "title": "ورشة فحم",
            "image": self.generate_test_image_file(),
            "description": "راح نتعلم كيف نقدر نتسخدم الفحم على اللوحات",
            "start_date": "2026-04-20 10:30:00",
            "end_date": "2026-04-29 10:30:00",
            "deadline": "2026-04-19 10:30:00",
            "cost": "100",
            "sessions": "10",
        }
        data.update(overrides)
        return data

    def get_valid_register_date(self, **overrides):
        data = {
            "user": self.normal_user,
            "workshop": self.workshop,
            "payment_proof": self.generate_test_image_file(),
            "payment_status": "under_review",
        }
        data.update(overrides)
        return data


class WorkshopViewPageTest(WorkshopBaseTestCase):

    def test_view_page(self):
        response = self.client.get(reverse("workshop:workshop_list"))
        self.assertEqual(response.status_code, 200)


class WorkshopViewDetailPageTest(WorkshopBaseTestCase):

    def test_view_workshop_Detail(self):
        response = self.client.get(reverse("workshop:workshop_detail", kwargs={"workshop_id": self.workshop.id}))
        self.assertEqual(response.status_code, 200)


class WorkshopCreateWorkshopTest(WorkshopBaseTestCase):

    def test_normal_user_cannot_access_create_page(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse("workshop:create_workshop"))
        self.assertRedirects(response, reverse("workshop:workshop_list"))

    def test_staff_user_can_access_create_page(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("workshop:create_workshop"))
        self.assertEqual(response.status_code, 200)

    def test_staff_can_create_workshop_with_valid_dates(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("workshop:create_workshop"),
            self.get_valid_workshop_data(),
            follow=True
        )

        self.assertTrue(Workshop.objects.filter(title="ورشة فحم").exists())
        self.assertEqual(response.status_code, 200)

    def test_deadline_after_start_date_is_invalid(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("workshop:create_workshop"),
            self.get_valid_workshop_data(
                title="ورشة زيت",
                start_date="2026-04-18 10:30:00",
                deadline="2026-04-20 10:30:00",
            ),
            follow=True
        )

        self.assertFalse(Workshop.objects.filter(title="ورشة زيت").exists())
        self.assertContains(response, "آخر موعد للتسجيل يجب أن يكون قبل بداية الورشة")


class WorkshopUpdateWorkshopTest(WorkshopBaseTestCase):

    def test_normal_user_cannot_access_edit_page(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(
            reverse("workshop:update_workshop", kwargs={"workshop_id": self.workshop.id})
        )
        self.assertEqual(response.status_code, 302)

    def test_staff_user_can_access_edit_page(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(
            reverse("workshop:update_workshop", kwargs={"workshop_id": self.workshop.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_staff_can_edit_workshop(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("workshop:update_workshop", kwargs={"workshop_id": self.workshop.id}),
            self.get_valid_workshop_data(
                title="ورشة الاوان خشبية",
                description="راح نتعلم كيف نقدر نتسخدم الاوان الخشبيه على اللوحات",
                start_date="2026-05-01 10:30:00",
                end_date="2026-06-01 10:30:00",
                deadline="2026-04-27 10:30:00",
                cost="200",
                sessions="14",
            ),
            follow=True
        )

        self.workshop.refresh_from_db()

        self.assertEqual(self.workshop.title, "ورشة الاوان خشبية")
        self.assertNotEqual(
            self.workshop.description,
            "راح نتعلم كيف نقدر نتسخدم الفحم على اللوحات"
        )
        self.assertRedirects(response, reverse("workshop:workshop_list"))


class RegistrationViewPageTest(WorkshopBaseTestCase):

    def test_view_registr_page(self):
        response = self.client.get(reverse("workshop:register_workshop", kwargs={"workshop_id": self.workshop.id}))
        self.assertEqual(response.status_code, 302)


    def test_user_can_register_to_workshop(self):
        self.client.force_login(self.normal_user)

        response = self.client.post(
            reverse("workshop:register_workshop",
                    kwargs={"workshop_id": self.workshop.id}),
                self.get_valid_register_date(),
            follow=True
        )

        self.assertEqual(self.register.payment_status, "under_review")
        self.assertRedirects(response, reverse("workshop:workshop_detail", kwargs={"workshop_id": self.workshop.id}))


class RegistrationUpdatePageTest(WorkshopBaseTestCase):

    def test_normal_user_cannot_access_registration_page(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse("workshop:workshop_registrations", kwargs={"workshop_id": self.workshop.id}))
        self.assertEqual(response.status_code, 302)


    def test_staff_user_can_access_registration_page(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse ("workshop:workshop_registrations", kwargs={"workshop_id": self.workshop.id}))
        self.assertEqual(response.status_code, 200)


    def test_staff_update_status_register_to_confirmed(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("workshop:update_registration_status",
                    kwargs={"workshop_id": self.workshop.id, "registration_user": self.normal_user.id}),
                {
                    "payment_status": "confirmed"
                },
            follow=True
        )

        self.register.refresh_from_db()

        self.assertEqual(self.register.payment_status, "confirmed")
        self.assertRedirects(
            response, 
            reverse("workshop:workshop_registrations",
            kwargs={"workshop_id": self.workshop.id})
            )


    def test_staff_update_status_register_to_rejected(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("workshop:update_registration_status",
                    kwargs={"workshop_id": self.workshop.id, "registration_user": self.normal_user.id}),
                {
                    "payment_status": "rejected"
                },
            follow=True
        )

        self.register.refresh_from_db()

        self.assertEqual(self.register.payment_status, "rejected")
        self.assertRedirects(
            response, 
            reverse("workshop:workshop_registrations",
            kwargs={"workshop_id": self.workshop.id})
            )


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailFunctionTest(WorkshopBaseTestCase):

    def test_email_send(self):
        send_email(
            subject="الموت الاحمر",
            message="dexter",
            recipient_list=["mstrldyfy@gmail.com"],
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "الموت الاحمر")
        self.assertNotEqual(mail.outbox[0].message, "معصوب")
