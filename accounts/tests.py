from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .test_base import SocialAppTestCase

from .models import Profile

User = get_user_model()



class LoginViewPage(SocialAppTestCase):
    def test_login_page_returns_200(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)


    def test_active_user_can_login(self):
        user = User.objects.create_user(
            username= "ali",
            email= "ali@gmail.com",
            password="password123",
            is_active=True
        )

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "ali@gmail.com", #The form called username but it take's email, I use django auth that's why
                "password": "password123"
            },
            follow=True
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class registerViewPage(SocialAppTestCase):
    def test_register_page_returns_200(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)


    def test_user_can_register(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "king1900",
                "email": "king1900@gmail.com",
                "phone_number": "0511111111",
                "password": "password123",
                "notifications": False,
            },
        )

        user = User.objects.get(email="king1900@gmail.com")

        self.assertEqual(user.username, "king1900")
        self.assertFalse(user.is_active)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class IncompleteProfileViewPage(TestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(
            username= "ali",
            email= "ali@gmail.com",
            password="password123",
            is_active=True
            )

        self.profile = Profile.objects.create(
            user=self.user,
            phone_number="",
            notifications=False
        )

    def test_incomplete_profile_page_returns_200(self):
        response = self.client.get(reverse("accounts:login_incomplete"))
        self.assertEqual(response.status_code, 302)  #Because the user must been register before he come here


    def test_user_can_complete_profile(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:login_incomplete"),
            {
                "phone_number": "0511111111",
                "notifications": "on"
            },
            follow=True
        )

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.phone_number, "0511111111")
        self.assertTrue(self.profile.notifications)
        self.assertTrue(response.wsgi_request.user.is_authenticated)