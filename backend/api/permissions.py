from rest_framework import permissions, status


class AnonymAdminAuthor(permissions.BasePermission):
    message = status.HTTP_403_FORBIDDEN
    edit_methods = ("PUT", "PATCH", "DELETE",)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method == "POST":
            return user == user.is_authenticated
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method in self.edit_methods:
            return (
                user.is_admin()
                or user == obj.author
            )
        return False
