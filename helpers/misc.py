"""Misc helpers."""

def get_url_friendly(name):
    """Converts the name to a url friendly string for use in `str_id`"""
    temp = "-".join(name.lower().split())
    return "".join(c for c in temp if c.isalnum() or c == "-")
