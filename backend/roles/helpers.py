"""Helper functions for implementing roles."""
from rest_framework.response import Response

def forbidden_no_privileges():
    """Forbidden due to insufficient privileges."""
    return Response({"error": "insufficient privileges"}, status=403)

def user_has_privilege(profile, bodyid, privilege):
    """Returns true if UserProfile has the privilege."""
    roles = profile.roles.all().filter(body__id=bodyid)
    if not roles:
        return False
    for role in roles:
        if not privilege in role.permissions:
            return False
    return True
