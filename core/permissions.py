from rest_framework.permissions import BasePermission
from rest_framework import permissions

from core.utils.constants import PHARMACIST, RIDER


class IsAdminOrReadOnly(BasePermission):
    """
    The request is authenticated as a admin, or is a read-only request.
    """

    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS and
            request.user and
            request.user.is_authenticated):
            return True
        elif ( not (request.method in permissions.SAFE_METHODS) and request.user and request.user.is_admin):
            return True
            
        return False

class IsPharmacist(BasePermission):
    """
    The request is authenticated as a pharmacist.
    """
    
    def has_permission(self, request, view):
        if (
            request.user and
            request.user.is_authenticated and 
            request.user.user_type==PHARMACIST):
            return True
            
        return False


class IsRider(BasePermission):
    """
    The request is authenticated as a rider.
    """
    
    def has_permission(self, request, view):
        if (
            request.user and
            request.user.is_authenticated and 
            request.user.user_type==RIDER):
            return True
            
        return False
  
  
class IsCurrentUser(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsRiderOwnerObject(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj.rider == request.user
