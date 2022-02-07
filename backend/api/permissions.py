from rest_framework import permissions, status


class AnonymAdminAuthor(permissions.BasePermission):
    message = status.HTTP_403_FORBIDDEN
    edit_methods = ("PATCH", "DELETE",)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method in self.edit_methods:
            return (
                request.user.is_admin()
                or request.user == obj.author
            )
        return False
