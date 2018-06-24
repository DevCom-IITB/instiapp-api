"""Helpers for locations."""
from django.db.models import Q
from locations.models import Location

def create_unreusable_locations(loc_list):
    """Takes a list of venues and creates venues which do not match
    any existing reusable venues. Returns a list of venue ids to be
    stored by the consumer."""

    # List of location ids to be returned
    loc_ids = []

    # Reuse reusable venues, add new otherwise
    for loc_name in loc_list:
        locs = Location.objects.filter(Q(name=loc_name) | Q(short_name=loc_name))
        if locs.count() == 0 or not locs[0].reusable:
            new_loc = Location.objects.create(name=loc_name, short_name=loc_name)
            new_loc.save()
            loc_ids.append(str(new_loc.id))
        else:
            loc_ids.append(str(locs[0].id))

    return loc_ids
