from rest_framework.permissions import BasePermission

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

class IsAdminOrReadOnly(BasePermission):
    """
    The request is authenticated as a admin, or is a read-only request.
    """

    def has_permission(self, request, view):
        if (request.method in SAFE_METHODS and
            request.user and
            request.user.is_authenticated):
            return True
        elif ( not (request.method in SAFE_METHODS) and request.user and request.user.is_admin):
            return True
            
        return False
