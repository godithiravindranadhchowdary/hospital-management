"""
Custom permissions for role-based access control.
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Allow only admin users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsDoctorUser(permissions.BasePermission):
    """Allow only doctor users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'doctor'


class IsPatientUser(permissions.BasePermission):
    """Allow only patient users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'patient'


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read access to all, write access only to admin."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsDoctorOrAdmin(permissions.BasePermission):
    """Allow access to doctors and admins."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['doctor', 'admin']


class IsPatientOrDoctor(permissions.BasePermission):
    """Allow access to patients and doctors."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['patient', 'doctor', 'admin']


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access to owner or admin."""
    
    def has_object_permission(self, request, view, obj):
        # Admin always has access
        if request.user.role == 'admin':
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'patient'):
            return obj.patient.user == request.user
        
        if hasattr(obj, 'doctor'):
            return obj.doctor.user == request.user
        
        return False


class CanManageAppointment(permissions.BasePermission):
    """Permission for appointment management."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin can manage all
        if request.user.role == 'admin':
            return True
        
        # Doctor can manage their appointments
        if request.user.role == 'doctor':
            return obj.doctor.user == request.user
        
        # Patient can only view their appointments
        if request.method in permissions.SAFE_METHODS:
            return obj.patient.user == request.user
        
        return False
