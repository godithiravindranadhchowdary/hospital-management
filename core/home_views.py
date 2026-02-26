"""
Home page views for Hospital Management System.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta, datetime

from .models import User, Doctor, Patient, Appointment, Prescription, Invoice, DoctorLeave, Operation, Payment, MedicalRecord, DoctorSchedule


def home(request):
    """Render the home page."""
    return render(request, 'index.html')


# ============================================
# PUBLIC VIEWS
# ============================================

def doctors_list(request):
    """Display list of doctors."""
    doctors = Doctor.objects.select_related('user').all()
    return render(request, 'doctors.html', {'doctors': doctors})


def patients_list(request):
    """Display list of patients."""
    patients = Patient.objects.select_related('user').all()
    return render(request, 'patients.html', {'patients': patients})


def appointments_list(request):
    """Display list of appointments."""
    appointments = Appointment.objects.select_related(
        'doctor__user', 'patient__user'
    ).all()
    return render(request, 'appointments.html', {'appointments': appointments})


def prescriptions_list(request):
    """Display list of prescriptions."""
    prescriptions = Prescription.objects.select_related(
        'appointment__doctor__user', 'appointment__patient__user', 'created_by__user'
    ).all()
    return render(request, 'prescriptions.html', {'prescriptions': prescriptions})


def invoices_list(request):
    """Display list of invoices."""
    invoices = Invoice.objects.select_related(
        'appointment__doctor__user', 'appointment__patient__user'
    ).all()
    return render(request, 'invoices.html', {'invoices': invoices})


def dashboard(request):
    """Display admin dashboard with statistics."""
    today = timezone.now().date()
    today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    today_end = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))
    
    # Check if user is admin
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Admin access required!')
        return redirect('login')
    
    # Basic stats
    stats = {
        'total_doctors': Doctor.objects.count(),
        'total_patients': Patient.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'today_appointments': Appointment.objects.filter(
            appointment_date__gte=today_start,
            appointment_date__lte=today_end
        ).count(),
        'pending_invoices': Invoice.objects.filter(status='pending').count(),
        'total_revenue': Invoice.objects.filter(status='paid').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'completed_appointments': Appointment.objects.filter(status='completed').count(),
        'cancelled_appointments': Appointment.objects.filter(status='cancelled').count(),
    }
    
    # Extended stats
    stats['total_operations'] = Operation.objects.count()
    stats['pending_leaves'] = DoctorLeave.objects.filter(status='pending').count()
    stats['pending_payments'] = Payment.objects.filter(status='pending').count()
    
    return render(request, 'dashboard.html', {'stats': stats})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def login_view(request):
    """Handle login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['user'] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
            }
            request.session['role'] = user.role
            messages.success(request, f'Welcome {user.first_name}!')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect('dashboard')
            elif user.role == 'doctor':
                return redirect('doctor_dashboard')
            elif user.role == 'patient':
                return redirect('patient_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials!')
    
    return render(request, 'login.html')


def logout_view(request):
    """Handle logout."""
    logout(request)
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('home')


# ============================================
# DOCTOR DASHBOARD VIEWS
# ============================================

def doctor_dashboard(request):
    """Doctor dashboard - shows doctor's personal statistics."""
    # Check if user is logged in and is a doctor
    if not request.user.is_authenticated:
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied! This portal is for doctors only.')
        return redirect('home')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found!')
        return redirect('home')
    
    today = timezone.now().date()
    today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    today_end = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))
    
    # Get today's appointments
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=today_start,
        appointment_date__lte=today_end
    ).select_related('patient__user').order_by('appointment_date')
    
    # Get all appointments for this doctor
    all_appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related('patient__user').order_by('-appointment_date')[:10]
    
    # Get completed appointments count
    completed_count = Appointment.objects.filter(doctor=doctor, status='completed').count()
    pending_count = Appointment.objects.filter(doctor=doctor, status='scheduled').count()
    
    # Get recent patients
    recent_patients = Appointment.objects.filter(
        doctor=doctor
    ).select_related('patient__user').order_by('-appointment_date')[:5]
    
    # Get unique patients count
    unique_patients = Appointment.objects.filter(doctor=doctor).values('patient').distinct().count()
    
    # Stats
    stats = {
        'total_appointments': Appointment.objects.filter(doctor=doctor).count(),
        'today_appointments': today_appointments.count(),
        'completed_appointments': completed_count,
        'pending_appointments': pending_count,
        'total_patients_treated': unique_patients,
        'total_earnings': doctor.total_earnings,
    }
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'all_appointments': all_appointments,
        'stats': stats,
        'recent_patients': recent_patients,
    }
    
    return render(request, 'doctor_dashboard.html', context)


def doctor_appointments(request):
    """Doctor's appointment list."""
    if not request.user.is_authenticated or request.user.role != 'doctor':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('doctor_dashboard')
    
    appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related('patient__user').order_by('-appointment_date')
    
    return render(request, 'doctor_appointments.html', {'appointments': appointments})


def doctor_patients(request):
    """View patients assigned to doctor."""
    if not request.user.is_authenticated or request.user.role != 'doctor':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('doctor_dashboard')
    
    # Get unique patients
    patient_ids = Appointment.objects.filter(doctor=doctor).values_list('patient_id', flat=True).distinct()
    patients = Patient.objects.filter(id__in=patient_ids).select_related('user')
    
    return render(request, 'doctor_patients.html', {'patients': patients})


def doctor_leaves(request):
    """Doctor leave management."""
    if not request.user.is_authenticated or request.user.role != 'doctor':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('doctor_dashboard')
    
    leaves = DoctorLeave.objects.filter(doctor=doctor).order_by('-created_at')
    
    return render(request, 'doctor_leaves.html', {'leaves': leaves})


def doctor_operations(request):
    """Doctor's operations/surgeries."""
    if not request.user.is_authenticated or request.user.role != 'doctor':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('doctor_dashboard')
    
    operations = Operation.objects.filter(doctor=doctor).select_related('patient__user').order_by('-operation_date')
    
    return render(request, 'doctor_operations.html', {'operations': operations})


def doctor_profile(request):
    """Doctor's profile view."""
    if not request.user.is_authenticated or request.user.role != 'doctor':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('doctor_dashboard')
    
    return render(request, 'doctor_profile.html', {'doctor': doctor})


# ============================================
# PATIENT PORTAL VIEWS
# ============================================

def patient_dashboard(request):
    """Patient dashboard - shows patient's own data."""
    # Check if user is logged in
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to view your dashboard!')
        return redirect('login')
    
    # Check if user is a patient
    if request.user.role != 'patient':
        messages.error(request, 'Access denied! This portal is for patients only.')
        return redirect('home')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found!')
        return redirect('home')
    
    # Get patient's appointments
    appointments = Appointment.objects.filter(
        patient=patient
    ).select_related('doctor__user').order_by('-appointment_date')[:5]
    
    # Get patient's prescriptions
    prescriptions = Prescription.objects.filter(
        appointment__patient=patient
    ).select_related('appointment__doctor__user', 'created_by__user').order_by('-created_at')[:5]
    
    # Get patient's invoices
    invoices = Invoice.objects.filter(
        appointment__patient=patient
    ).select_related('appointment__doctor__user').order_by('-created_at')[:5]
    
    # Get patient's payments
    payments = Payment.objects.filter(
        patient=patient
    ).order_by('-created_at')[:5]
    
    # Get patient's medical records
    medical_records = MedicalRecord.objects.filter(
        patient=patient
    ).select_related('doctor__user').order_by('-created_at')[:5]
    
    # Calculate stats
    stats = {
        'total_appointments': Appointment.objects.filter(patient=patient).count(),
        'completed_appointments': Appointment.objects.filter(patient=patient, status='completed').count(),
        'pending_invoices': Invoice.objects.filter(appointment__patient=patient, status='pending').count(),
        'total_spent': patient.total_spent,
        'total_prescriptions': Prescription.objects.filter(appointment__patient=patient).count(),
    }
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'invoices': invoices,
        'payments': payments,
        'medical_records': medical_records,
        'stats': stats,
    }
    
    return render(request, 'patient_dashboard.html', context)


def patient_appointments(request):
    """Patient's appointment history."""
    if not request.user.is_authenticated or request.user.role != 'patient':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_dashboard')
    
    appointments = Appointment.objects.filter(
        patient=patient
    ).select_related('doctor__user').order_by('-appointment_date')
    
    return render(request, 'patient_appointments.html', {'appointments': appointments})


def patient_prescriptions(request):
    """Patient's prescriptions."""
    if not request.user.is_authenticated or request.user.role != 'patient':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_dashboard')
    
    prescriptions = Prescription.objects.filter(
        appointment__patient=patient
    ).select_related('appointment__doctor__user', 'created_by__user').order_by('-created_at')
    
    return render(request, 'patient_prescriptions.html', {'prescriptions': prescriptions})


def patient_invoices(request):
    """Patient's invoices."""
    if not request.user.is_authenticated or request.user.role != 'patient':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_dashboard')
    
    invoices = Invoice.objects.filter(
        appointment__patient=patient
    ).select_related('appointment__doctor__user').order_by('-created_at')
    
    return render(request, 'patient_invoices.html', {'invoices': invoices})


def patient_payments(request):
    """Patient's payment history."""
    if not request.user.is_authenticated or request.user.role != 'patient':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_dashboard')
    
    payments = Payment.objects.filter(patient=patient).order_by('-created_at')
    
    return render(request, 'patient_payments.html', {'payments': payments})


def patient_medical_records(request):
    """Patient's medical records."""
    if not request.user.is_authenticated or request.user.role != 'patient':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_dashboard')
    
    medical_records = MedicalRecord.objects.filter(
        patient=patient
    ).select_related('doctor__user').order_by('-created_at')
    
    return render(request, 'patient_medical_records.html', {'medical_records': medical_records})


def patient_profile(request):
    """Patient's profile view."""
    if not request.user.is_authenticated or request.user.role != 'patient':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_dashboard')
    
    return render(request, 'patient_profile.html', {'patient': patient})


# ============================================
# ADMIN VIEWS
# ============================================

def admin_doctors(request):
    """Admin view all doctors with details."""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Admin access required!')
        return redirect('login')
    
    search_query = request.GET.get('search', '')
    if search_query:
        doctors = Doctor.objects.select_related('user').filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialty__icontains=search_query) |
            Q(qualification__icontains=search_query)
        ).order_by('-created_at')
    else:
        doctors = Doctor.objects.select_related('user').order_by('-created_at')
    
    return render(request, 'admin_doctors.html', {'doctors': doctors, 'search_query': search_query})


def admin_patients(request):
    """Admin view all patients with details."""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Admin access required!')
        return redirect('login')
    
    search_query = request.GET.get('search', '')
    if search_query:
        patients = Patient.objects.select_related('user').filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(blood_type__icontains=search_query)
        ).order_by('-created_at')
    else:
        patients = Patient.objects.select_related('user').order_by('-created_at')
    
    return render(request, 'admin_patients.html', {'patients': patients, 'search_query': search_query})


def admin_operations(request):
    """Admin view all operations."""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Admin access required!')
        return redirect('login')
    
    # Get all operations grouped by doctor
    operations = Operation.objects.select_related('doctor__user', 'patient__user').order_by('-operation_date')
    
    # Group operations by doctor
    doctor_operations = {}
    for op in operations:
        doctor = op.doctor
        if doctor not in doctor_operations:
            doctor_operations[doctor] = {
                'surgeries': [],
                'count': 0,
                'completed_count': 0
            }
        doctor_operations[doctor]['surgeries'].append(op)
        doctor_operations[doctor]['count'] += 1
        if op.status == 'completed':
            doctor_operations[doctor]['completed_count'] += 1
    
    return render(request, 'admin_operations.html', {'doctor_operations': doctor_operations})


def admin_leaves(request):
    """Admin view all doctor leaves."""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Admin access required!')
        return redirect('login')
    
    # Get all leaves grouped by doctor
    leaves = DoctorLeave.objects.select_related('doctor__user').order_by('-created_at')
    
    # Group leaves by doctor
    doctor_leaves = {}
    for leave in leaves:
        doctor = leave.doctor
        if doctor not in doctor_leaves:
            doctor_leaves[doctor] = {
                'leaves': [],
                'count': 0,
                'approved_count': 0
            }
        doctor_leaves[doctor]['leaves'].append(leave)
        doctor_leaves[doctor]['count'] += 1
        if leave.status == 'approved':
            doctor_leaves[doctor]['approved_count'] += 1
    
    return render(request, 'admin_leaves.html', {'doctor_leaves': doctor_leaves})


def admin_payments(request):
    """Admin view all payments."""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Admin access required!')
        return redirect('login')
    
    payments = Payment.objects.select_related('patient__user', 'invoice').order_by('-created_at')
    return render(request, 'admin_payments.html', {'payments': payments})


def admin_medical_records(request):
    """Admin view all medical records."""
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'Admin access required!')
        return redirect('login')
    
    records = MedicalRecord.objects.select_related('patient__user', 'doctor__user').order_by('-created_at')
    return render(request, 'admin_medical_records.html', {'records': records})
