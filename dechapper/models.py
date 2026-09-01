from django.core.exceptions import ValidationError
from django.db import models


class SiteConfiguration(models.Model):
    next_available = models.DateField("eerstvolgende beschikbaarheid")
    email_reply = models.TextField(
        "bevestigingstekst",
        default="Bedankt voor uw aanvraag. We nemen zo snel mogelijk contact met u op.",
    )

    class Meta:
        verbose_name = "websiteconfiguratie"
        verbose_name_plural = "websiteconfiguratie"

    def clean(self):
        if not self.pk and SiteConfiguration.objects.exists():
            raise ValidationError("Er kan maar één websiteconfiguratie bestaan.")

    def __str__(self):
        return f"Beschikbaar vanaf {self.next_available:%d/%m/%Y}"

