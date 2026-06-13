from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@example.com", password="OldPass123!")

    def test_request_sends_email_and_does_not_leak_unknown_accounts(self):
        r1 = self.client.post(reverse("password-reset"), {"email": "user@example.com"})
        r2 = self.client.post(reverse("password-reset"), {"email": "nobody@example.com"})
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)  # identical response for unknown email
        self.assertEqual(len(mail.outbox), 1)  # email only sent for the real user

    def test_confirm_sets_new_password(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        resp = self.client.post(
            reverse("password-reset-confirm"),
            {"uid": uid, "token": token, "password": "BrandNew456!"},
        )
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("BrandNew456!"))

    def test_confirm_rejects_bad_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        resp = self.client.post(
            reverse("password-reset-confirm"),
            {"uid": uid, "token": "bogus-token", "password": "BrandNew456!"},
        )
        self.assertEqual(resp.status_code, 400)
