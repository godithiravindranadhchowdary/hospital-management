"""
URL Configuration for Hospital Management System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.home_views import (
    home, doctors_list, patients_list, appointments_list,
    prescriptions_list, invoices_list, dashboard, login_view, logout_view,
    # Patient views
    patient_dashboard, patient_appointments, patient_prescriptions, patient_invoices,
    patient_payments, patient_medical_records, patient_profile,
    # Doctor views
    doctor_dashboard, doctor_appointments, doctor_patients, doctor_leaves,
    doctor_operations, doctor_profile,
    # Admin views
    admin_doctors, admin_patients, admin_operations, admin_leaves,
    admin_payments, admin_medical_records
)

# Custom admin site login - override the admin login view
from django.contrib.auth.views import LoginView

admin.site.login = LoginView.as_view(
    template_name='admin_login.html',
    success_url='/admin/'
)

urlpatterns = [
    path('', home, name='home'),
    path('admin/login/', admin.site.login, name='admin_login'),
    
    # =======================
    # ADMIN PORTAL ROUTES (must come BEFORE admin.site.urls)
    # =======================
    path('admin/doctors/', admin_doctors, name='admin_doctors'),
    path('admin/patients/', admin_patients, name='admin_patients'),
    path('admin/operations/', admin_operations, name='admin_operations'),
    path('admin/leaves/', admin_leaves, name='admin_leaves'),
    path('admin/payments/', admin_payments, name='admin_payments'),
    path('admin/medical-records/', admin_medical_records, name='admin_medical_records'),
    
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    
    # Public pages
    path('doctors/', doctors_list, name='doctors'),
    path('patients/', patients_list, name='patients'),
    path('appointments/', appointments_list, name='appointments'),
    path('prescriptions/', prescriptions_list, name='prescriptions'),
    path('invoices/', invoices_list, name='invoices'),
    path('dashboard/', dashboard, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # =======================
    # PATIENT PORTAL ROUTES
    # =======================
    path('patient/', patient_dashboard, name='patient_dashboard'),
    path('patient/appointments/', patient_appointments, name='patient_appointments'),
    path('patient/prescriptions/', patient_prescriptions, name='patient_prescriptions'),
    path('patient/invoices/', patient_invoices, name='patient_invoices'),
    path('patient/payments/', patient_payments, name='patient_payments'),
    path('patient/medical-records/', patient_medical_records, name='patient_medical_records'),
    path('patient/profile/', patient_profile, name='patient_profile'),
    
    # =======================
    # DOCTOR PORTAL ROUTES
    # =======================
    path('doctor/', doctor_dashboard, name='doctor_dashboard'),
    path('doctor/appointments/', doctor_appointments, name='doctor_appointments'),
    path('doctor/patients/', doctor_patients, name='doctor_patients'),
    path('doctor/leaves/', doctor_leaves, name='doctor_leaves'),
    path('doctor/operations/', doctor_operations, name='doctor_operations'),
    path('doctor/profile/', doctor_profile, name='doctor_profile'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
