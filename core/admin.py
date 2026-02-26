"""
Django admin configuration for Hospital Management System.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Doctor, Patient, Appointment, Prescription, Invoice


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'address', 'date_of_birth', 'profile_picture')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'address')}),
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Admin configuration for Doctor model."""
    
    list_display = ['user', 'specialty', 'qualification', 'experience', 'license_number', 'is_available', 'created_at']
    list_filter = ['specialty', 'is_available', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'license_number']
    ordering = ['-created_at']
    raw_id_fields = ['user']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin configuration for Patient model."""
    
    list_display = ['user', 'gender', 'blood_type', 'emergency_contact', 'created_at']
    list_filter = ['gender', 'blood_type', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['-created_at']
    raw_id_fields = ['user']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin configuration for Appointment model."""
    
    list_display = ['id', 'doctor', 'patient', 'appointment_date', 'status', 'created_at']
    list_filter = ['status', 'appointment_date', 'created_at']
    search_fields = ['doctor__user__username', 'patient__user__username', 'notes']
    ordering = ['-appointment_date']
    raw_id_fields = ['doctor', 'patient']
    date_hierarchy = 'appointment_date'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    """Admin configuration for Prescription model."""
    
    list_display = ['id', 'appointment', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['appointment__id', 'medications', 'instructions']
    ordering = ['-created_at']
    raw_id_fields = ['appointment', 'created_by']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin configuration for Invoice model."""
    
    list_display = ['id', 'appointment', 'amount', 'status', 'due_date', 'paid_at', 'created_at']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['appointment__id', 'description']
    ordering = ['-created_at']
    raw_id_fields = ['appointment']
    date_hierarchy = 'created_at'
