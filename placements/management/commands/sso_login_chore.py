import pickle
from requests import Session
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import pyotp


class Command(BaseCommand):
    help = "Updates the placement blog database"

    def handle(self, *args, **options):
        # """Run the chore."""

        s = Session()

        init_response = s.get("https://sso.iitb.ac.in/login")

        if not settings.LDAP_USERNAME or not settings.LDAP_PASSWORD:
            raise CommandError("SSO LOGIN CHORE FAILED: NO CREDENTIALS PROVIDED")

        s.post(
            "https://sso.iitb.ac.in/login",
            cookies=init_response.cookies,
            data={
                "username": settings.LDAP_USERNAME,
                "password": settings.LDAP_PASSWORD,
                "remember": "on",
                "redir": "/",
                "totp": int(pyotp.TOTP(settings.SSO_TOTP_TOKEN).now()),
            },
            allow_redirects=True,
        )

        f = open("session.obj", "wb")
        pickle.dump(obj=s, file=f)
        f.close()

        self.stdout.write(self.style.SUCCESS("SSO Login Chore completed successfully"))
