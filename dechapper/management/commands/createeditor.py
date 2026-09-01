from getpass import getpass

from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update a non-admin account for the availability editor."

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, *args, **options):
        username = options["username"]
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(username=username)

        password = getpass("Wachtwoord: ")
        if password != getpass("Wachtwoord bevestigen: "):
            if created:
                user.delete()
            raise CommandError("De wachtwoorden komen niet overeen.")
        try:
            password_validation.validate_password(password, user)
        except ValidationError as exc:
            if created:
                user.delete()
            raise CommandError(" ".join(exc.messages)) from exc

        user.set_password(password)
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        user.save()
        action = "aangemaakt" if created else "bijgewerkt"
        self.stdout.write(self.style.SUCCESS(f"Editor '{username}' is {action}."))
