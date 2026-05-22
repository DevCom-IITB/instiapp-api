from calendarhub.models import CalendarSourcePreference


def get_month_buckets(start, end):
    """Return list of 'YYYY-MM' strings covering [start, end]."""
    months = []
    current = start.replace(day=1)
    while current <= end:
        months.append(current.strftime('%Y-%m'))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return months


def get_preferences(user):
    """Get or create CalendarSourcePreference for user."""
    prefs, _ = CalendarSourcePreference.objects.get_or_create(user=user)
    return prefs
