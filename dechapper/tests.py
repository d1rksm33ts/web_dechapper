from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings

from .models import SiteConfiguration
from .services import verify_turnstile


class PublicPagesTests(TestCase):
    def test_home_contains_core_legacy_identity(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kristof Vanderheyden")
        self.assertContains(response, "Chapewerken")
        self.assertContains(response, "Vloerisolatie")
        self.assertContains(response, "Bekerveldweg 80")
        self.assertContains(response, "info@dechapper.be")
        self.assertContains(response, "dechapper/css/legacy.")
        self.assertContains(response, '<time class="icon">', count=2)

    def test_navigation_preserves_original_sections(self):
        response = self.client.get("/")
        for target in ("#hero", "#about", "#services", "#portfolio", "#available", "#contact"):
            self.assertContains(response, f'href="{target}"')
        self.assertContains(response, 'href="/beheer/"')

    def test_home_supports_head_requests(self):
        response = self.client.head("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")

    def test_configured_availability_is_rendered(self):
        SiteConfiguration.objects.create(next_available=date(2026, 8, 31), email_reply="We bellen u snel.")
        response = self.client.get("/")
        self.assertContains(response, "WK 36")
        self.assertContains(response, ">31<")
        self.assertContains(response, "AUG")

    def test_privacy_page(self):
        response = self.client.get("/privacy/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contactformulier")
        self.assertContains(response, "niet in de databank")
        self.assertContains(response, "Cloudflare Turnstile")
        self.assertNotContains(response, "Google reCAPTCHA")

    @override_settings(
        CONTACT_FORM_ENABLED=True,
        TURNSTILE_REQUIRED=True,
        TURNSTILE_SITE_KEY="test-site-key",
    )
    def test_enabled_contact_form_renders_turnstile(self):
        response = self.client.get("/")
        self.assertContains(response, "https://challenges.cloudflare.com/turnstile/v0/api.js")
        self.assertContains(response, 'class="cf-turnstile"')
        self.assertContains(response, 'data-sitekey="test-site-key"')
        self.assertContains(response, 'data-action="contact"')

    def test_health_checks_database(self):
        self.assertJSONEqual(self.client.get("/health/").content, {"status": "ok"})


class AvailabilityManagementTests(TestCase):
    password = "a-long-test-password"

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="editor", password=self.password)
        self.configuration = SiteConfiguration.objects.create(
            next_available=date(2026, 8, 31),
            email_reply="We bellen u snel.",
        )

    def test_management_requires_login(self):
        response = self.client.get("/beheer/")
        self.assertRedirects(response, "/beheer/login/?next=/beheer/")

    def test_login_uses_dedicated_page_and_redirects_to_editor(self):
        response = self.client.get("/beheer/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log in om de beschikbaarheid")

        response = self.client.post(
            "/beheer/login/",
            {"username": "editor", "password": self.password},
        )
        self.assertRedirects(response, "/beheer/")

    def test_editor_contains_date_picker_and_public_site_link(self):
        self.client.force_login(self.user)
        response = self.client.get("/beheer/")
        self.assertContains(response, 'type="date"')
        self.assertContains(response, 'value="2026-08-31"')
        self.assertContains(response, 'href="/#available"')
        self.assertContains(response, "Datum opslaan")

    def test_saving_updates_database_and_public_calendar(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/beheer/",
            {"next_available": "2026-10-05"},
            follow=True,
        )
        self.assertContains(response, "De beschikbaarheidsdatum is opgeslagen.")
        self.configuration.refresh_from_db()
        self.assertEqual(self.configuration.next_available, date(2026, 10, 5))

        response = self.client.get("/")
        self.assertContains(response, "WK 41")
        self.assertContains(response, ">5<")
        self.assertContains(response, "OKT")

    def test_invalid_date_is_not_saved(self):
        self.client.force_login(self.user)
        response = self.client.post("/beheer/", {"next_available": "geen-datum"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Voer een geldige datum in")
        self.configuration.refresh_from_db()
        self.assertEqual(self.configuration.next_available, date(2026, 8, 31))

    def test_logout_is_post_only_and_closes_session(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get("/beheer/logout/").status_code, 405)
        response = self.client.post("/beheer/logout/")
        self.assertRedirects(response, "/")
        self.assertRedirects(self.client.get("/beheer/"), "/beheer/login/?next=/beheer/")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_REPLY_TO=["info@dechapper.be"],
    CONTACT_BCC=["info@dechapper.be", "info@yanoa.be"],
    CONTACT_FORM_ENABLED=True,
    TURNSTILE_REQUIRED=False,
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
        "turnstile_token": "",
    }

    def test_valid_request_sends_notification_and_confirmation(self):
        SiteConfiguration.objects.create(next_available=date(2026, 9, 14), email_reply="We nemen snel contact op.")
        response = self.client.post("/contact/", self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["klant@example.test"])
        self.assertEqual(mail.outbox[0].bcc, ["info@dechapper.be", "info@yanoa.be"])
        self.assertEqual(mail.outbox[0].reply_to, ["info@dechapper.be"])
        self.assertIn("We nemen snel contact op.", mail.outbox[0].body)
        self.assertIn("Graag ontvang ik een offerte.", mail.outbox[0].body)

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

    @override_settings(TURNSTILE_REQUIRED=True, TURNSTILE_SECRET_KEY="secret")
    @patch("dechapper.views.verify_turnstile", return_value=False)
    def test_failed_turnstile_is_rejected(self, verifier):
        response = self.client.post("/contact/", self.payload | {"turnstile_token": "bad"})
        self.assertEqual(response.status_code, 400)
        verifier.assert_called_once()
        self.assertEqual(mail.outbox, [])

    @override_settings(CONTACT_FORM_ENABLED=False)
    def test_disabled_form_does_not_send(self):
        response = self.client.post("/contact/", self.payload)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(mail.outbox, [])


@override_settings(
    TURNSTILE_REQUIRED=True,
    TURNSTILE_SECRET_KEY="protected-secret",
    TURNSTILE_EXPECTED_HOSTNAMES=["dechapper.be"],
)
class TurnstileTests(TestCase):
    def test_missing_token_is_rejected_without_network_call(self):
        with patch("dechapper.services.request.urlopen") as opener:
            self.assertFalse(verify_turnstile(""))
        opener.assert_not_called()

    @patch("dechapper.services.json.load")
    @patch("dechapper.services.request.urlopen")
    def test_valid_contact_token_for_expected_hostname_is_accepted(self, opener, load):
        load.return_value = {"success": True, "action": "contact", "hostname": "dechapper.be"}
        self.assertTrue(verify_turnstile("valid-token"))
        request_url = opener.call_args.args[0]
        self.assertEqual(request_url, "https://challenges.cloudflare.com/turnstile/v0/siteverify")

    @patch("dechapper.services.json.load")
    @patch("dechapper.services.request.urlopen")
    def test_token_for_wrong_hostname_is_rejected(self, opener, load):
        load.return_value = {"success": True, "action": "contact", "hostname": "attacker.example"}
        self.assertFalse(verify_turnstile("valid-token"))

    @patch("dechapper.services.json.load")
    @patch("dechapper.services.request.urlopen")
    def test_token_for_wrong_action_is_rejected(self, opener, load):
        load.return_value = {"success": True, "action": "login", "hostname": "dechapper.be"}
        self.assertFalse(verify_turnstile("valid-token"))
