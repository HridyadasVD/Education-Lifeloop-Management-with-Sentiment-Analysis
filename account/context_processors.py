from django.core.exceptions import ObjectDoesNotExist


def user_role(request):
    role = None
    if request.user.is_authenticated:
        try:
            role = request.user.user_profile.user_type
        except (ObjectDoesNotExist, AttributeError):
            role = None
    return {'user_role': role}
