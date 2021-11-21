from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from notifications.signals import notify
from querybot.models import UnresolvedQuery

def handle_entry(entry):
    """Handle a single entry from a feed."""

    # Try to get an entry existing
    id = entry.id
    db_entry = UnresolvedQuery.objects.filter(id = id).first()

    # Send notification to mentioned people
    if db_entry.resolved:
        # Send notifications to user
        users = User.objects.filter(id=db_entry.user.user.id)
        # notify.send(db_entry, recipient=users, verb="Your query has been resolved")

        db_entry.delete()

def clear_queries():
    """"Query all entires from database."""

    entries = UnresolvedQuery.objects.all()

    # Add each entry if doesn't exist
    for entry in entries:
        handle_entry(entry)


class Command(BaseCommand):
    help = 'Delete resolved queries and notify user'

    def handle(self, *args, **options):
        """Run the chore."""

        clear_queries()

        self.stdout.write(self.style.SUCCESS('Query Bot Chore completed successfully'))
