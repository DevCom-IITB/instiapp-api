"""Mess menu chore."""
import gspread
from django.core.management.base import BaseCommand
from oauth2client.service_account import ServiceAccountCredentials
from messmenu.models import MenuEntry
from messmenu.models import Hostel

def update_day(sheet, day, hostel):
    """Update one day's menu."""
    # Check if object exists or create one
    menu = MenuEntry.objects.filter(hostel=hostel, day=day).first()
    if not menu:
        menu = MenuEntry.objects.create(hostel=hostel, day=day)

    # Fill in the mess!
    menu.breakfast = sheet[1][day]
    menu.lunch = sheet[2][day]
    menu.snacks = sheet[3][day]
    menu.dinner = sheet[4][day]

    # Commit
    menu.save()

def fetch_hostel(client, hostel):
    """Update menu of one hostel."""
    # Open Google sheet
    sheet = client.open_by_url(hostel.mess_gsheet).sheet1

    # Read
    vals = sheet.get_all_values()

    # Update all days
    for i in range(1, 8):
        update_day(vals, i, hostel)

class Command(BaseCommand):
    help = 'Fetches mess menus from Google'

    def handle(self, *args, **options):
        """Fetch Mess Menus."""

        # Use credentials to create a client to interact with the Google Drive API
        print("Authorizing - ", end="", flush=True)
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        creds = ServiceAccountCredentials.from_json_keyfile_name('google_client_secret.json', scope)
        client = gspread.authorize(creds)
        print("OK")

        # Iterate over all hostels
        for hostel in Hostel.objects.all():
            print("Updating " + hostel.name + " - ", end="", flush=True)
            if hostel.mess_gsheet:
                try:
                    fetch_hostel(client, hostel)
                    print("OK")
                except Exception:  # pylint: disable=W0703
                    print("FAIL")
            else:
                print("SKIP")
