from rest_framework import permissions

from django.contrib.auth.models import User
from users.models import SavedProgram

class IsAuthorOrPublicReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and not obj.private:
            return True
        return obj.author == request.user

class IsPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or not obj.private