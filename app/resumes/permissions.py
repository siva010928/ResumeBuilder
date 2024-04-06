from rest_framework.permissions import BasePermission
from django.conf import settings


class HasSpecialToken(BasePermission):
    """
    Allows access only to requests that have a valid special token.
    """

    def has_permission(self, request, view):
        special_token = request.headers.get('X-Special-Token')
        return special_token == settings.SPECIAL_TOKEN
