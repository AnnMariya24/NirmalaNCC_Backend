from rest_framework.permissions import BasePermission


class IsProfileCompleted(BasePermission):
    """
    Allows access only if user's profile is completed.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile_completed