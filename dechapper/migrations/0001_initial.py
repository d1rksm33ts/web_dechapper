import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="SiteConfiguration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("next_available", models.DateField(verbose_name="eerstvolgende beschikbaarheid")),
                ("email_reply", models.TextField(default="Bedankt voor uw aanvraag. We nemen zo snel mogelijk contact met u op.", verbose_name="bevestigingstekst")),
            ],
            options={"verbose_name": "websiteconfiguratie", "verbose_name_plural": "websiteconfiguratie"},
        )
    ]

