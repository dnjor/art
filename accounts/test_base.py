from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.conf import settings
from allauth.socialaccount.models import SocialApp


User = get_user_model()


class SocialAppTestCase(TestCase):
    """"Create a fake google socialapp for tests"""
    @classmethod
    def setUpTestData(cls):
        site, _ = Site.objects.get_or_create(
            id=settings.SITE_ID,
            defaults={
                "domain": "testserver",
                "name": "testserver"
            }
        )

        google_app, _ = SocialApp.objects.get_or_create(
            provider="google",
            name="Google Test App",
            defaults={
                "client_id": "fake-client-id",
                "secret": "fake-secret"
            },
        )
        google_app.sites.add(site)