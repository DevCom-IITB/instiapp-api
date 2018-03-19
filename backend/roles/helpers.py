"""Helper functions for implementing roles."""
from rest_framework.response import Response

def forbidden_no_privileges():
    """Forbidden due to insufficient privileges."""
    return Response({"error": "insufficient privileges"}, status=403)

def user_has_privilege(profile, bodyid, privilege):
    """Returns true if UserProfile has the privilege."""
    return check_roles(profile.roles.all().filter(body__id=bodyid), privilege)

def user_has_insti_privilege(profile, privilege):
    """Returns true if UserProfile has the institute privilege."""
    return check_roles(profile.institute_roles.all(), privilege)

def check_roles(roles, privilege):
    """Private helper function."""
    if not roles:
        return False
    for role in roles:
        if privilege in role.permissions:
            return True
    return False

def diff_set(first, second):
    """Difference between two lists."""
    second = set(second)
    return [item for item in first if item not in second]

def login_required_ajax(f):
    """
    Just make sure the user is authenticated to access a certain ajax view

    Otherwise return a HttpResponse 401 - authentication required
    instead of the 302 redirect of the original Django decorator
    """
    def wrapper(*args, **kw):
        """Wrapper after checking if authenticated."""
        if args[1].user.is_authenticated:
            return f(*args, **kw)
        else:
            return Response({'error': 'unauthenticated'}, status=401)

    return wrapper
