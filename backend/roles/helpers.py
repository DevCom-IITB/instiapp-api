"""Helper functions for implementing roles."""
from rest_framework.response import Response

def forbidden_no_privileges():
    """Forbidden due to insufficient privileges."""
    return Response({
        "message": "insufficient privileges",
        "detail": "You have insufficient priveleges to perform this action."
    }, status=403)

def user_has_privilege(profile, bodyid, privilege):
    """Returns true if UserProfile has the privilege."""
    return check_roles(profile.roles.all().filter(body__id=bodyid), privilege)

def user_has_insti_privilege(profile, privilege):
    """Returns true if UserProfile has the institute privilege."""
    return check_roles(profile.institute_roles.all(), privilege)

def check_roles(roles, privilege):
    """Private helper function."""
    return any([(privilege in role.permissions) for role in roles])

def diff_set(first, second):
    """Difference between two lists."""
    second = set(second)
    return [item for item in first if item not in second]

def login_required_ajax(func):
    """
    Just make sure the user is authenticated to access a certain ajax view

    Otherwise return a HttpResponse 401 - authentication required
    instead of the 302 redirect of the original Django decorator
    """
    def wrapper(*args, **kw):
        """Wrapper after checking if authenticated."""
        if args[1].user.is_authenticated:
            return func(*args, **kw)
        return Response({
            'message': 'unauthenticated',
            'detail': 'Log in to continue!'
        }, status=401)

    return wrapper

def insti_permission_required(permission):
    """Check for institute permission."""
    def real_decorator(func):
        @login_required_ajax
        def wrapper(*args, **kw):
            if user_has_insti_privilege(args[1].user.profile, permission):
                return func(*args, **kw)
            return forbidden_no_privileges()
        return wrapper
    return real_decorator
