from datetime import date
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings

from .models import SiteConfiguration


class PublicPagesTests(TestCase):
    def test_home_contains_core_legacy_identity(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kristof Vanderheyden")
        self.assertContains(response, "Chapewerken")
        self.assertContains(response, "Vloerisolatie")
        self.assertContains(response, "Bekerveldweg 80")

    def test_configured_availability_is_rendered(self):
        SiteConfiguration.objects.create(next_available=date(2026, 9, 14), email_reply="We bellen u snel.")
        response = self.client.get("/")
        self.assertContains(response, "WK 38")
        self.assertContains(response, ">14<")
        self.assertContains(response, "september")

    def test_privacy_page(self):
        response = self.client.get("/privacy/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contactformulier")
        self.assertContains(response, "niet in de databank")

    def test_health_checks_database(self):
        self.assertJSONEqual(self.client.get("/health/").content, {"status": "ok"})


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_RECIPIENTS=["info@dechapper.be"],
    CONTACT_BCC=["office@example.test"],
    CONTACT_FORM_ENABLED=True,
    RECAPTCHA_REQUIRED=False,
)
class ContactTests(TestCase):
    payload = {
        "name": "Test Klant",
        "email": "klant@example.test",
        "thickness": "7.5",
        "area": "120",
        "floor_heating": "Ja",
        "address": "Teststraat 1, Zonhoven",
        "message": "Graag ontvang ik een offerte.",
        "website": "",
        "recaptcha_token": "",
    }

    def test_valid_request_sends_notification_and_confirmation(self):
        SiteConfiguration.objects.create(next_available=date(2026, 9, 14), email_reply="We nemen snel contact op.")
        response = self.client.post("/contact/", self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["info@dechapper.be"])
        self.assertEqual(mail.outbox[0].reply_to, ["klant@example.test"])
        self.assertEqual(mail.outbox[1].to, ["klant@example.test"])
        self.assertIn("We nemen snel contact op.", mail.outbox[1].body)

    def test_invalid_input_returns_safe_validation_response(self):
        payload = self.payload | {"email": "invalid", "area": "-5"}
        response = self.client.post("/contact/", payload)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        self.assertEqual(mail.outbox, [])

    def test_honeypot_rejects_bot(self):
        response = self.client.post("/contact/", self.payload | {"website": "spam.example"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(mail.outbox, [])

    @override_settings(RECAPTCHA_REQUIRED=True, RECAPTCHA_SECRET_KEY="secret")
    @patch("dechapper.views.verify_recaptcha", return_value=False)
    def test_failed_recaptcha_is_rejected(self, verifier):
        response = self.client.post("/contact/", self.payload | {"recaptcha_token": "bad"})
        self.assertEqual(response.status_code, 400)
        verifier.assert_called_once()
        self.assertEqual(mail.outbox, [])

    @override_settings(CONTACT_FORM_ENABLED=False)
    def test_disabled_form_does_not_send(self):
        response = self.client.post("/contact/", self.payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(mail.outbox, [])

