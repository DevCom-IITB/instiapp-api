"""Helpers for locations."""
from django.db.models import Q
from locations.models import Location

def create_unreusable_locations(loc_list):
    """Takes a list of venues and creates venues which do not match
    any existing venues. Returns a list of venue ids to be
    stored by the consumer."""

    # List of location ids to be returned
    loc_ids = []

    # Reuse venues, add new otherwise
    for loc_name in loc_list:
        loc = Location.objects.filter(Q(name=loc_name) | Q(short_name=loc_name)).first()
        if not loc:
            loc = Location.objects.create(name=loc_name, short_name=loc_name)
        loc_ids.append(str(loc.id))

    return loc_ids
