from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

from django.core.management.base import BaseCommand
from querybot.models import Query


def handle_entry_fromsheet(row):
    """Handle a single entry from a feed."""

    # Try to get an entry existing
    if row[0] == "":
        return
    db_entry = Query(question=row[1], answer=row[2], category=row[3].strip())
    # Fill the db entry
    if row[4] in row:
        db_entry.sub_category = row[4]
    if row[5] in row:
        db_entry.sub_sub_category = row[5]

    db_entry.save()


def fill_faq():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "querybot/cred.json", scope
    )
    service = discovery.build("sheets", "v4", credentials=creds)
    spreadsheet_id = "1JYdfLpaExhR2pMXWouj9b-nxa6ztt1FRL8cBEqwdAic"
    range_ = "sheet1!A:F"

    request = (
        service.spreadsheets()
        .values()
        .batchGet(
            spreadsheetId=spreadsheet_id, ranges=range_, valueRenderOption="FORMULA"
        )
    )
    response = request.execute()
    # Get the feed
    valueRanges = response["valueRanges"]
    values = valueRanges[0]["values"]
    for row in values[0:20]:
        handle_entry_fromsheet(row)


class Command(BaseCommand):
    help = "Sync all questions from the sheet"

    def handle(self, *args, **options):
        """Run the chore."""

        fill_faq()

        self.stdout.write(self.style.SUCCESS("Query Bot Chore completed successfully"))
