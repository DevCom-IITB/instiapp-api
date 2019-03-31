"""Dangerous: Convert all roles to former roles."""
import random
from django.core.management.base import BaseCommand
from roles.models import BodyRole
from users.models import UserFormerRole

class Command(BaseCommand):
    help = 'Dangerous: Convert all roles to former roles.'

    def handle(self, *args, **options):

        # Verify a challenge
        a = random.randint(100, 999)
        b = random.randint(100, 999)

        challenge = input('%i + %i = ? ' % (a, b))
        if int(challenge) != a + b:
            self.stdout.write(self.style.ERROR('Challenge Failed'))
            return

        # Get input year
        tenure_year = input('Enter the tenure year in the format 2018-19: ')

        # Iterate over all body roles
        for role in BodyRole.objects.filter(permanent=False):
            if role.official_post:
                # Create a former role for each user
                for user in role.users.all():
                    UserFormerRole.objects.create(user=user, role=role, year=tenure_year)
                    print(role, user)

            # Clear all users from the role
            role.users.clear()

        self.stdout.write(self.style.SUCCESS('Role reset chore completed successfully'))
