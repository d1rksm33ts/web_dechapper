import json
import logging
from urllib import parse, request

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def verify_turnstile(token, remote_ip=None):
    if not settings.TURNSTILE_REQUIRED:
        return True
    if not token or not settings.TURNSTILE_SECRET_KEY:
        return False
    payload = {"secret": settings.TURNSTILE_SECRET_KEY, "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip
    try:
        data = parse.urlencode(payload).encode()
        with request.urlopen("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data, timeout=5) as response:
            result = json.load(response)
    except (OSError, ValueError):
        logger.warning("Turnstile verification failed", exc_info=True)
        return False
    if not result.get("success") or result.get("action") != "contact":
        return False
    expected_hostnames = settings.TURNSTILE_EXPECTED_HOSTNAMES
    return not expected_hostnames or result.get("hostname") in expected_hostnames


def send_contact_email(data, confirmation_text):
    details = [
        f"Beste {data['name']},",
        "",
        confirmation_text,
        "",
        "Overzicht van uw aanvraag:",
        "",
        f"Naam: {data['name']}",
        f"E-mail: {data['email']}",
        f"Werfadres: {data['address']}",
        f"Dikte: {data.get('thickness') or '-'} cm",
        f"Oppervlakte: {data.get('area') or '-'} m²",
        f"Vloerverwarming: {data.get('floor_heating') or '-'}",
        f"BTW-tarief: {data['vat_rate']}%",
        f"Bericht: {data['message']}",
        "",
        "Met vriendelijke groeten,",
        "De Chapper",
    ]
    confirmation_parts = confirmation_text.split(". ", 1)
    confirmation_intro = confirmation_parts[0]
    if len(confirmation_parts) > 1:
        confirmation_intro = confirmation_intro.rstrip(".") + " ..."
    html_context = {
        **data,
        "confirmation_intro": confirmation_intro,
        "confirmation_remainder": confirmation_parts[1] if len(confirmation_parts) > 1 else "",
        "thickness": data.get("thickness") or "",
        "area": data.get("area") or "",
        "floor_heating": data.get("floor_heating") or "",
    }
    email = EmailMultiAlternatives(
        subject=f"Vraag/Prijsofferte - {data['name']}",
        body="\n".join(details),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[data["email"]],
        reply_to=settings.CONTACT_REPLY_TO,
        bcc=settings.CONTACT_BCC,
    )
    email.attach_alternative(render_to_string("dechapper/email/contact.html", html_context), "text/html")
    email.send(fail_silently=False)
