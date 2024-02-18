"""Helper functions for implementing roles."""
import datetime
from rest_framework.response import Response
from dateutil.relativedelta import relativedelta
from bodies.models import Body
from community.models import Community
from bans.models import SSOBan
from users.models import UserProfile
from roles.models import BodyRole
from bodies.serializer_min import BodySerializerMin


def user_is_banned(profile):
    try:
        ban = SSOBan.objects.get(banned_user=profile.id)
        current_time = datetime.datetime.now()
        ban_created = ban.time_of_creation
        ban_duration = ban.duration_of_ban

        if ban_duration == "Permanent":
            return True

        duration_month = int(ban_duration.split(" ")[0])
        banned_till = ban_created + relativedelta(months=duration_month)

        if banned_till > current_time:
            return True
        return False
    except SSOBan.DoesNotExist:
        return False


def forbidden_no_privileges():
    """Forbidden due to insufficient privileges."""
    return Response(
        {
            "message": "insufficient privileges",
            "detail": "You have insufficient priveleges to perform this action.",
        },
        status=403,
    )


def user_has_privilege(profile, bodyid, privilege):
    """Returns true if UserProfile has or has inherited the privilege."""
    body = Body.objects.get(pk=bodyid)
    parents = get_parents_recursive(body, [])
    for role in profile.roles.all().filter(body__in=parents):
        if (role.body == body or role.inheritable) and privilege in role.permissions:
            return True
    return False


def user_has_community_privilege(profile, communityid, privilege):
    """Returns true if UserProfile has or has inherited the privilege."""
    community = Community.objects.get(pk=communityid)
    parents = get_parents_recursive(community, [])
    for role in profile.roles.all().filter(community__in=parents):
        if (
            role.body == community or role.inheritable
        ) and privilege in role.permissions:
            return True
    return False


def user_has_insti_privilege(profile, privilege):
    """Returns true if UserProfile has the institute privilege."""
    return check_roles(profile.institute_roles.all(), privilege)


def check_roles(roles, privilege):
    """Private helper function."""
    return any([(privilege in role.permissions) for role in roles])


def get_parents_recursive(body, parents):
    """Get array of parents. Includes the body itself."""
    for child_body_relation in body.parents.all():
        get_parents_recursive(child_body_relation.parent, parents)
    parents.append(body)
    return parents


def diff_set(first, second):
    """Difference between two lists."""
    second = set(second)
    return [item for item in first if item not in second]


def add_doc(value):
    def _doc(func):
        func.__doc__ = value
        return func

    return _doc


def login_required_ajax(func):
    """
    Just make sure the user is authenticated to access a certain ajax view

    Otherwise return a HttpResponse 401 - authentication required
    instead of the 302 redirect of the original Django decorator
    """

    @add_doc(func.__doc__)
    def wrapper(*args, **kw):
        if args[1].user.is_authenticated:
            user = args[1].user
            profile = UserProfile.objects.get(user=user)
            if not user_is_banned(profile):
                return func(*args, **kw)
            else:
                return Response(
                    {"message": "banned", "detail": "your SSO has been banned/disabled"}
                )
        return Response(
            {"message": "unauthenticated", "detail": "Log in to continue!"}, status=401
        )

    return wrapper


def insti_permission_required(permission):
    """Check for institute permission."""

    def real_decorator(func):
        @login_required_ajax
        @add_doc(func.__doc__)
        def wrapper(*args, **kw):
            if user_has_insti_privilege(args[1].user.profile, permission):
                return func(*args, **kw)
            return forbidden_no_privileges()

        return wrapper

    return real_decorator

def bodies_with_users_having_privilege(privilege):
    bodies_with_privilege = set()
    body_roles = BodyRole.objects.all()
    for role in body_roles:
        if (role.permissions and privilege in role.permissions):
            bodies_with_privilege.add(role.body)

    serialized_bodies = BodySerializerMin(list(bodies_with_privilege), many=True).data

    return serialized_bodies
