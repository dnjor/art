from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
from unittest.mock import patch
import cloudinary

from accounts.test_base import SocialAppTestCase
from .models import Painting

User = get_user_model()

class GalleryBaseTestCase(SocialAppTestCase):

    @staticmethod
    def generate_test_image_file():
        file_obj = BytesIO()
        image = Image.new("RGB", (100,100), color="red")
        image.save(file_obj, "JPEG")
        file_obj.seek(0)

        return SimpleUploadedFile(
            name="test.jpg",
            content=file_obj.read(),
            content_type="image/jpeg"
        )

    @classmethod
    def get_mock_cloudinary_response():
        return {
            "public_id": "test_image",
            "version": "123",
            "signature": "abc123",
            "width": 100,
            "height": 100,
            "format": "jpg",
            "resource_type": "image",
            "type": "upload",
            "url": "https://example.com/test.jpg",
            "secure_url": "https://example.com/test.jpg"
        }


    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cloudinary.config(
            cloud_name="test",
            api_kay="123",
            api_secret="fake",
            secure=True
        ) 


    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        with patch("cloudinary.models.CloudinaryField.pre_save", return_value="test_image"):

            cls.normal_user = User.objects.create_user(
                username=f"user_{cls.__name__}",
                email=f"user_{cls.__name__.lower()}@gmail.com",
                password="password123",
                is_active=True
            )

            cls.staff_user = User.objects.create_user(
                username= f"staff_{cls.__name__}",
                email= f"staff_{cls.__name__.lower()}@gmail.com",
                password="admind123",
                is_active=True,
                is_staff=True
            )

            cls.painting = Painting.objects.create(
                title=f"title_{cls.__name__}",
                picture = cls.generate_test_image_file(),
                description="my home <3"
            )


class GalleryViewPageTest(GalleryBaseTestCase):
    def test_view_page(self):
        response = self.client.get(reverse("gallery:gallery"))
        self.assertEqual(response.status_code, 200)


class GalleryUploadePaintingTest(GalleryBaseTestCase):
    def test_normal_user_visiat_upload_page(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse("gallery:uplode_painting"))
        self.assertRedirects(response, reverse("gallery:gallery"))


    def test_staff_user_visiat_upload_page(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("gallery:uplode_painting"))
        self.assertEqual(response.status_code, 200)


    def test_upload_painting(self):
        self.client.force_login(self.staff_user)

        picture = self.generate_test_image_file()

        with patch("cloudinary.models.CloudinaryField.pre_save", return_value="test_image"):
            response = self.client.post(
                reverse("gallery:uplode_painting"),
                {
                    "title": "بحر العشاق",
                    "picture": picture,
                },
                follow=True
            )

        self.assertTrue(Painting.objects.filter(title="بحر العشاق").exists())
        painting = Painting.objects.get(title="بحر العشاق")

        self.assertTrue(bool(painting.picture))
        self.assertFalse(painting.description)
        self.assertRedirects(response, reverse("gallery:gallery"))


class GalleryEditPaintingTest(GalleryBaseTestCase):
    def test_normal_user_visiat_edit_page(self):
        self.client.force_login(self.normal_user)

        response = self.client.get(
            reverse("gallery:edit_painting",
            kwargs={"painting_id": self.painting.id}))

        self.assertEqual(response.status_code, 302)


    def test_staff_user_visiat_edit_page(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(
            reverse(
                "gallery:edit_painting",
            kwargs={"painting_id": self.painting.id}))

        self.assertEqual(response.status_code, 200)

    
    def test_edit_painting(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse(
                "gallery:edit_painting",
            kwargs={"painting_id": self.painting.id}),
            {
                "title": "Saudi Arabia",
                "description": "my contry"
            },
            follow=True
        )

        self.painting.refresh_from_db()

        self.assertTrue(Painting.objects.filter(title="Saudi Arabia").exists())
        painting = Painting.objects.get(title="Saudi Arabia")

        self.assertTrue(bool(painting.picture))
        self.assertNotEqual(painting.description, "my home <3")
        self.assertRedirects(response, reverse("gallery:gallery"))


class GalleryDeletePaintingTest(GalleryBaseTestCase):
    def test_normal_user_can_delete(self):
        self.client.force_login(self.normal_user)

        response = self.client.post(
            reverse("gallery:delete_painting",
            kwargs={"painting_id": self.painting.id}))

        self.assertEqual(response.status_code, 302)


    def test_staff_user_can_delete(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse(
                "gallery:delete_painting",
            kwargs={"painting_id": self.painting.id}),
            {
                "is_active": False
            }
        )

        self.assertRedirects(response, reverse("gallery:gallery"))


class GalleryDetailPaitningTest(GalleryBaseTestCase):
    def test_visite_painting_detail_page(self):
        response = self.client.get(
            reverse("gallery:painting_detail",
            kwargs={"painting_id": self.painting.id}))

        self.assertEqual(response.status_code, 200)


    def test_not_register_can_add_comment_to_painting(self):
        response = self.client.post(
            reverse("gallery:add_comment",
            kwargs={"painting_id": self.painting.id}),
            {
                "comment": "hello world"
            }
        )

        self.assertEqual(response.status_code, 302)


    def test_user_can_add_comment_to_painting(self):
        self.client.force_login(self.normal_user)

        response = self.client.post(
            reverse("gallery:add_comment",
            kwargs={"painting_id": self.painting.id}),
            {
                "comment": "hello world"
            },
        )

        self.assertRedirects(
            response, 
            reverse("gallery:painting_detail",
            kwargs={"painting_id": self.painting.id})
            )


    def test_not_register_can_add_like_to_painting(self):
        response = self.client.post(
            reverse("gallery:add_like",
            kwargs={"painting_id": self.painting.id})
        )

        self.assertEqual(response.status_code, 302)


    def test_user_can_add_like_to_painting(self):
        self.client.force_login(self.normal_user)

        response = self.client.post(
            reverse("gallery:add_like",
            kwargs={"painting_id": self.painting.id})
        )

        self.assertRedirects(
            response, 
            reverse("gallery:painting_detail",
            kwargs={"painting_id": self.painting.id})
            )