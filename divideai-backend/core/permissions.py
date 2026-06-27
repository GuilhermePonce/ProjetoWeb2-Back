from rest_framework import permissions


class IsGroupMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "members"):
            return obj.members.filter(id=request.user.id).exists()
        if hasattr(obj, "group"):
            return obj.group.members.filter(id=request.user.id).exists()
        return False
