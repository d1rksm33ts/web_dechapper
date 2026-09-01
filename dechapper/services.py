import json
import logging
from urllib import parse, request

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def verify_recaptcha(token, remote_ip=None):
    if not settings.RECAPTCHA_REQUIRED:
        return True
    if not token or not settings.RECAPTCHA_SECRET_KEY:
        return False
    payload = {"secret": settings.RECAPTCHA_SECRET_KEY, "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip
    try:
        data = parse.urlencode(payload).encode()
        with request.urlopen("https://www.google.com/recaptcha/api/siteverify", data=data, timeout=5) as response:
            return bool(json.load(response).get("success"))
    except (OSError, ValueError):
        logger.warning("reCAPTCHA verification failed", exc_info=True)
        return False


def send_contact_email(data, confirmation_text):
    details = [
        f"Naam: {data['name']}",
        f"E-mail: {data['email']}",
        f"Werfadres: {data['address']}",
        f"Dikte: {data.get('thickness') or '-'} cm",
        f"Oppervlakte: {data.get('area') or '-'} m²",
        f"Vloerverwarming: {data.get('floor_heating') or '-'}",
        "",
        data["message"],
    ]
    EmailMessage(
        subject=f"Nieuwe aanvraag via dechapper.be — {data['name']}",
        body="\n".join(details),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=settings.CONTACT_RECIPIENTS,
        reply_to=[data["email"]],
        bcc=settings.CONTACT_BCC,
    ).send(fail_silently=False)
    EmailMessage(
        subject="We hebben uw aanvraag ontvangen — De Chapper",
        body=f"Beste {data['name']},\n\n{confirmation_text}\n\nMet vriendelijke groeten,\nDe Chapper",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[data["email"]],
        reply_to=settings.CONTACT_RECIPIENTS,
    ).send(fail_silently=False)

