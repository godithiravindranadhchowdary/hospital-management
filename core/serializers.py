"""
Serializers for Hospital Management System.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Doctor, Patient, Appointment, Prescription, Invoice


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'address', 'date_of_birth', 'profile_picture',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'phone', 'address', 'date_of_birth'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model."""
    
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    user_details = UserSerializer(source='user', read_only=True)
    total_appointments = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user', 'user_id', 'user_details', 'specialty', 'qualification',
            'experience', 'license_number', 'bio', 'consultation_fee', 'is_available',
            'total_appointments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_appointments(self, obj):
        return obj.appointments.count()
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)
        if user_id:
            user = User.objects.get(id=user_id)
            user.role = 'doctor'
            user.save()
            validated_data['user'] = user
        return super().create(validated_data)


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model."""
    
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    user_details = UserSerializer(source='user', read_only=True)
    total_appointments = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'user', 'user_id', 'user_details', 'gender', 'blood_type',
            'emergency_contact', 'emergency_contact_name', 'medical_history', 'allergies',
            'total_appointments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_appointments(self, obj):
        return obj.appointments.count()
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None)
        if user_id:
            user = User.objects.get(id=user_id)
            user.role = 'patient'
            user.save()
            validated_data['user'] = user
        return super().create(validated_data)


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model."""
    
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)
    doctor_id = serializers.IntegerField(write_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'doctor', 'doctor_id', 'doctor_details',
            'patient', 'patient_id', 'patient_details',
            'appointment_date', 'status', 'notes', 'reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        doctor = data.get('doctor')
        patient = data.get('patient')
        appointment_date = data.get('appointment_date')
        
        # Check if doctor is available at the time
        if doctor and appointment_date:
            conflicting = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                status__in=['scheduled', 'confirmed']
            ).exists()
            if conflicting:
                raise serializers.ValidationError({
                    'appointment_date': 'Doctor is not available at this time.'
                })
        
        return data


class PrescriptionSerializer(serializers.ModelSerializer):
    """Serializer for Prescription model."""
    
    appointment_details = AppointmentSerializer(source='appointment', read_only=True)
    created_by_details = DoctorSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'appointment', 'appointment_details', 'medications',
            'dosage', 'instructions', 'notes', 'created_by', 'created_by_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    
    appointment_details = AppointmentSerializer(source='appointment', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'appointment', 'appointment_details', 'amount', 'description',
            'status', 'due_date', 'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'paid_at', 'created_at', 'updated_at']


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            data['user'] = user
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        return data


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    
    total_doctors = serializers.IntegerField()
    total_patients = serializers.IntegerField()
    total_appointments = serializers.IntegerField()
    today_appointments = serializers.IntegerField()
    pending_invoices = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    completed_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()
