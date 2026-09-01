import logging
from datetime import timedelta

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_safe

from .forms import ContactForm
from .models import SiteConfiguration
from .services import send_contact_email, verify_recaptcha

logger = logging.getLogger(__name__)

MONTHS_SHORT = ("", "JAN", "FEB", "MRT", "APR", "MEI", "JUN", "JUL", "AUG", "SEP", "OKT", "NOV", "DEC")


def availability():
    config = SiteConfiguration.objects.first()
    if config:
        next_date = config.next_available
    else:
        today = timezone.localdate()
        next_date = today + timedelta(days=(7 - today.weekday()) % 7 or 7)
    return {
        "date": next_date,
        "week": next_date.isocalendar().week,
        "day": next_date.day,
        "month": MONTHS_SHORT[next_date.month],
        "reply": config.email_reply if config else SiteConfiguration._meta.get_field("email_reply").default,
    }


@require_safe
def home(request):
    return render(request, "dechapper/index.html", {
        "availability": availability(),
        "contact_form": ContactForm(),
        "contact_form_enabled": settings.CONTACT_FORM_ENABLED,
        "recaptcha_required": settings.RECAPTCHA_REQUIRED,
        "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY,
    })


@require_safe
def privacy(request):
    return render(request, "dechapper/privacy.html")


@require_POST
def contact(request):
    if not settings.CONTACT_FORM_ENABLED:
        return JsonResponse({"ok": False, "message": "Het contactformulier is tijdelijk niet beschikbaar."}, status=503)
    form = ContactForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "message": "Controleer de ingevulde gegevens.", "errors": form.errors.get_json_data()}, status=400)
    if not verify_recaptcha(form.cleaned_data["recaptcha_token"], request.META.get("REMOTE_ADDR")):
        return JsonResponse({"ok": False, "message": "De beveiligingscontrole is niet gelukt. Probeer opnieuw."}, status=400)
    try:
        send_contact_email(form.cleaned_data, availability()["reply"])
    except Exception:
        logger.exception("Unable to send contact request")
        return JsonResponse({"ok": False, "message": "Uw bericht kon niet worden verstuurd. Probeer later opnieuw of mail ons rechtstreeks."}, status=502)
    return JsonResponse({"ok": True, "message": "Bedankt voor uw aanvraag. U ontvangt zo meteen een bevestiging per e-mail."})


@require_safe
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        logger.exception("Database health check failed")
        return JsonResponse({"status": "unhealthy"}, status=503)
    return JsonResponse({"status": "ok"})
