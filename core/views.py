"""
API views for Hospital Management System.
"""
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, Doctor, Patient, Appointment, Prescription, Invoice
from .serializers import (
    UserSerializer, UserCreateSerializer, DoctorSerializer, PatientSerializer,
    AppointmentSerializer, PrescriptionSerializer, InvoiceSerializer,
    LoginSerializer, ChangePasswordSerializer, DashboardStatsSerializer
)
from .permissions import (
    IsAdminUser, IsDoctorUser, IsPatientUser, IsAdminOrReadOnly,
    IsDoctorOrAdmin, IsPatientOrDoctor, CanManageAppointment
)


class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints."""
    
    permission_classes = [AllowAny]
    
    def login(self, request):
        """User login endpoint."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def logout(self, request):
        """User logout endpoint."""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout successful'})
        except Exception:
            return Response({'message': 'Logout successful'})
    
    def register(self, request):
        """User registration endpoint."""
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    """Change password endpoint."""
    
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'Current password is incorrect.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User management."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['role', 'is_active']
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class DoctorViewSet(viewsets.ModelViewSet):
    """ViewSet for Doctor management."""
    
    queryset = Doctor.objects.select_related('user').all()
    serializer_class = DoctorSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['specialty', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'specialty']
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        return Doctor.objects.select_related('user').all()
    
    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        """Get all appointments for a specific doctor."""
        doctor = self.get_object()
        appointments = doctor.appointments.all()
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet for Patient management."""
    
    queryset = Patient.objects.select_related('user').all()
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['blood_type', 'gender']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        return Patient.objects.select_related('user').all()
    
    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        """Get all appointments for a specific patient."""
        patient = self.get_object()
        appointments = patient.appointments.all()
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Appointment management."""
    
    queryset = Appointment.objects.select_related(
        'doctor__user', 'patient__user'
    ).all()
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['status', 'doctor', 'patient']
    
    def get_permissions(self):
        if self.action in ['list', 'create']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        return Appointment.objects.select_related(
            'doctor__user', 'patient__user'
        ).all()
    
    def perform_create(self, serializer):
        doctor_id = self.request.data.get('doctor')
        patient_id = self.request.data.get('patient')
        
        # Create appointment
        appointment = serializer.save()
        
        # Create invoice for the appointment
        doctor = Doctor.objects.get(id=doctor_id)
        Invoice.objects.create(
            appointment=appointment,
            amount=doctor.consultation_fee,
            description=f"Consultation fee for appointment on {appointment.appointment_date}"
        )


class PrescriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for Prescription management."""
    
    queryset = Prescription.objects.select_related(
        'appointment__doctor__user', 'appointment__patient__user', 'created_by__user'
    ).all()
    serializer_class = PrescriptionSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['appointment']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsDoctorOrAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Prescription.objects.select_related(
                'appointment__doctor__user', 'appointment__patient__user', 'created_by__user'
            ).all()
        elif user.role == 'doctor':
            return Prescription.objects.select_related(
                'appointment__doctor__user', 'appointment__patient__user', 'created_by__user'
            ).filter(created_by__user=user)
        elif user.role == 'patient':
            return Prescription.objects.select_related(
                'appointment__doctor__user', 'appointment__patient__user', 'created_by__user'
            ).filter(appointment__patient__user=user)
        return Prescription.objects.none()
    
    def perform_create(self, serializer):
        doctor = Doctor.objects.get(user=self.request.user)
        serializer.save(created_by=doctor)


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice management."""
    
    queryset = Invoice.objects.select_related(
        'appointment__doctor__user', 'appointment__patient__user'
    ).all()
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['status', 'appointment']
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Invoice.objects.select_related(
                'appointment__doctor__user', 'appointment__patient__user'
            ).all()
        elif user.role == 'doctor':
            return Invoice.objects.select_related(
                'appointment__doctor__user', 'appointment__patient__user'
            ).filter(appointment__doctor__user=user)
        elif user.role == 'patient':
            return Invoice.objects.select_related(
                'appointment__doctor__user', 'appointment__patient__user'
            ).filter(appointment__patient__user=user)
        return Invoice.objects.none()
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark invoice as paid."""
        invoice = self.get_object()
        invoice.status = 'paid'
        invoice.paid_at = timezone.now()
        invoice.save()
        return Response(InvoiceSerializer(invoice).data)


class DashboardViewSet(viewsets.ViewSet):
    """Dashboard analytics with Redis caching."""
    
    permission_classes = [IsAdminUser]
    
    def list(self, request):
        """Get dashboard statistics."""
        from django.core.cache import cache
        
        # Try to get from cache
        cache_key = 'dashboard_stats'
        stats = cache.get(cache_key)
        
        if stats is None:
            # Calculate statistics
            today = timezone.now().date()
            today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
            today_end = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))
            
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
            
            # Cache for 5 minutes
            cache.set(cache_key, stats, 300)
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def revenue(self, request):
        """Get revenue statistics."""
        from django.db.models.functions import TruncMonth
        
        # Monthly revenue
        monthly_revenue = Invoice.objects.filter(
            status='paid'
        ).annotate(
            month=TruncMonth('paid_at')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        return Response(list(monthly_revenue))
    
    @action(detail=False, methods=['get'])
    def appointments_by_status(self, request):
        """Get appointments grouped by status."""
        appointments = Appointment.objects.values('status').annotate(
            count=Count('id')
        )
        return Response(list(appointments))
    
    @action(detail=False, methods=['get'])
    def clear_cache(self, request):
        """Clear dashboard cache."""
        from django.core.cache import cache
        cache.delete('dashboard_stats')
        return Response({'message': 'Cache cleared successfully'})
