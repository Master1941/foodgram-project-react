from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """Класс разрешений для админа или для всех пользователей на чтение."""

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_staff
        )


class IsAdminAuthorOrReadOnly(BasePermission):
    """Класс разрешений для админа и автора
    или для всех пользователей на чтение."""

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and (request.user.is_staff or obj.author == request.user)
            )
        )
