from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


from accounts.test_base import SocialAppTestCase

from .models import Review
User = get_user_model()


class ReviewBaseTest(SocialAppTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.review = Review.objects.create(
            source_timestamp="2026-4-11 10:30:00",
            review_name="شاهي",
            rating_1=5,
            rating_2=5,
            rating_3=3,
            rating_4=5,
            rating_5=5,
            comment="الله يسعدك يا استاذا اروى",
            status="pending",
        )

        cls.staff_user = User.objects.create_user(
            username="admin",
            email="admin@gmail.com",
            password="admin123",
            is_active=True,
            is_staff=True
        )

        cls.normal_user = User.objects.create_user(
            username="ali",
            email="ali@gmail.com",
            password="password123",
            is_active=True
        )
        


class ReviewsViewPage(ReviewBaseTest):
    def test_normal_user_cannot_access_reviews_page(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse("reviews:reviews_list"))
        self.assertEqual(response.status_code, 302)


    def test_staff_user_can_access_reviews_page(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse ("reviews:reviews_list"))
        self.assertEqual(response.status_code, 200)


    def test_staff_update_status_review_to_rejected(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("reviews:reviews_list"),
                {
                    "review_id": self.review.id,
                    "status": "rejected",
                },
            follow=True
        )

        self.review.refresh_from_db()

        self.assertEqual(self.review.status, "rejected")
        self.assertRedirects(response, reverse("reviews:reviews_list"))



    def test_staff_update_status_review_to_approved(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("reviews:reviews_list"),
                {
                    "review_id": self.review.id,
                    "status": "approved",
                },
            follow=True
        )

        self.review.refresh_from_db()

        self.assertEqual(self.review.status, "approved")
        self.assertRedirects(response, reverse("reviews:reviews_list"))