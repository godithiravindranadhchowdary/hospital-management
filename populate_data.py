"""
Script to populate sample data for Hospital Management System.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
import random
from core.models import User, Doctor, Patient, Appointment, Prescription, Invoice

# Clear existing data
User.objects.filter(role='doctor').delete()
User.objects.filter(role='patient').delete()
User.objects.filter(role='admin').delete()

# ============================================
# CREATE ADMIN USER
# ============================================
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@hospital.com',
    password='admin123',
    first_name='System',
    last_name='Administrator',
    role='admin',
    phone='+919999999999'
)
print("✅ Admin user created!")
print(f"   Username: admin")
print(f"   Password: admin123")
print(f"   Login URL: http://127.0.0.1:8000/admin/login/")

# ============================================
# CREATE DOCTOR USERS
# ============================================

# Doctor specialties and their qualifications
doctors_data = [
    {'specialty': 'Cardiology', 'qualification': 'MD, DM Cardiology', 'experience': 15},
    {'specialty': 'Neurology', 'qualification': 'MD, DM Neurology', 'experience': 12},
    {'specialty': 'Orthopedics', 'qualification': 'MS Orthopedics', 'experience': 10},
    {'specialty': 'Pediatrics', 'qualification': 'MD Pediatrics', 'experience': 8},
    {'specialty': 'Dermatology', 'qualification': 'MD Dermatology', 'experience': 7},
    {'specialty': 'Ophthalmology', 'qualification': 'MS Ophthalmology', 'experience': 9},
    {'specialty': 'ENT', 'qualification': 'MS ENT', 'experience': 11},
    {'specialty': 'Gynecology', 'qualification': 'MD Gynecology', 'experience': 14},
    {'specialty': 'General Medicine', 'qualification': 'MD General Medicine', 'experience': 10},
    {'specialty': 'Psychiatry', 'qualification': 'MD Psychiatry', 'experience': 8},
    {'specialty': 'Cardiology', 'qualification': 'MD, DM Cardiology', 'experience': 18},
    {'specialty': 'Neurology', 'qualification': 'MD, DM Neurology', 'experience': 16},
    {'specialty': 'Orthopedics', 'qualification': 'MS Orthopedics', 'experience': 12},
    {'specialty': 'Pediatrics', 'qualification': 'MD Pediatrics', 'experience': 9},
    {'specialty': 'Dermatology', 'qualification': 'MD Dermatology', 'experience': 11},
    {'specialty': 'Ophthalmology', 'qualification': 'MS Ophthalmology', 'experience': 13},
    {'specialty': 'ENT', 'qualification': 'MS ENT', 'experience': 10},
    {'specialty': 'Gynecology', 'qualification': 'MD Gynecology', 'experience': 15},
    {'specialty': 'General Medicine', 'qualification': 'MD General Medicine', 'experience': 12},
    {'specialty': 'Psychiatry', 'qualification': 'MD Psychiatry', 'experience': 9},
    {'specialty': 'Cardiology', 'qualification': 'MD, DM Cardiology', 'experience': 20},
    {'specialty': 'Neurology', 'qualification': 'MD, DM Neurology', 'experience': 14},
    {'specialty': 'Orthopedics', 'qualification': 'MS Orthopedics', 'experience': 11},
    {'specialty': 'Pediatrics', 'qualification': 'MD Pediatrics', 'experience': 7},
    {'specialty': 'Dermatology', 'qualification': 'MD Dermatology', 'experience': 6},
    {'specialty': 'Ophthalmology', 'qualification': 'MS Ophthalmology', 'experience': 8},
    {'specialty': 'ENT', 'qualification': 'MS ENT', 'experience': 12},
    {'specialty': 'Gynecology', 'qualification': 'MD Gynecology', 'experience': 16},
    {'specialty': 'General Medicine', 'qualification': 'MD General Medicine', 'experience': 14},
    {'specialty': 'Psychiatry', 'qualification': 'MD Psychiatry', 'experience': 10},
    {'specialty': 'Cardiology', 'qualification': 'MD, DM Cardiology', 'experience': 17},
]

doctor_first_names = [
    'Rajesh', 'Amit', 'Sanjay', 'Vikram', 'Anil', 'Raj', 'Vijay', 'Deepak', 'Suresh', 'Ramesh',
    'Mahesh', 'Prashant', 'Nitin', 'Praveen', 'Arun', 'Krishna', 'Harish', 'Vishal', 'Ajay', 'Manish',
    'Ashish', 'Gaurav', 'Rahul', 'Shankar', 'Gopal', 'Madhav', 'Yash', 'Harsh', 'Kunal', 'Rohan'
]

doctor_last_names = [
    'Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Verma', 'Reddy', 'Joshi', 'Mehta', 'Shah',
    'Chowdhury', 'Mukherjee', 'Iyer', 'Menon', 'Nair', 'Pillai', 'Bhatia', 'Kapoor', 'Malhotra', 'Khanna',
    'Bose', 'Das', 'Sen', 'Roy', 'Banerjee', 'Chatterjee', 'Agarwal', 'Jain', 'Sinha', 'Pandey'
]

# Create 30 doctors
doctors = []
for i in range(30):
    first_name = doctor_first_names[i]
    last_name = doctor_last_names[i]
    username = f"doctor{i+1}"
    
    user = User.objects.create_user(
        username=username,
        email=f"{username}@hospital.com",
        password='doctor123',
        first_name=first_name,
        last_name=last_name,
        role='doctor',
        phone=f"+91{random.randint(9000000000, 9999999999)}"
    )
    
    doctor_data = doctors_data[i]
    doctor = Doctor.objects.create(
        user=user,
        specialty=doctor_data['specialty'],
        qualification=doctor_data['qualification'],
        experience=doctor_data['experience'],
        license_number=f"MD{random.randint(10000, 99999)}",
        consultation_fee=random.randint(500, 2000),
        is_available=True
    )
    doctors.append(doctor)
    print(f"Created doctor: Dr. {first_name} {last_name} - {doctor_data['specialty']}")

# Patient problems and corresponding medications
patient_conditions = [
    ('Hypertension', 'High blood pressure, headache', 'Amlodipine 5mg once daily, Aspirin 75mg once daily', 'Low salt diet, regular exercise'),
    ('Diabetes Type 2', 'High blood sugar, fatigue', 'Metformin 500mg twice daily, Glibenclamide 5mg once daily', 'Low sugar diet, regular monitoring'),
    ('Asthma', 'Breathing difficulty, wheezing', 'Salbutamol inhaler SOS, Budesonide 200mcg twice daily', 'Avoid dust, smoke'),
    ('Arthritis', 'Joint pain, stiffness', 'Ibuprofen 400mg thrice daily, Glucosamine supplements', 'Hot compress, gentle exercise'),
    ('Migraine', 'Severe headache, nausea', 'Sumatriptan 50mg SOS, Propranolol 40mg once daily', 'Avoid bright lights, stress'),
    ('Back Pain', 'Lower back pain, stiffness', 'Diclofenac gel local application, Vitamin D supplements', 'Proper posture, physiotherapy'),
    ('Anxiety', 'Restlessness, panic attacks', 'Escitalopram 10mg once daily, Alprazolam 0.25mg SOS', 'Meditation, breathing exercises'),
    ('Depression', 'Sadness, loss of interest', 'Sertraline 50mg once daily, counseling', 'Regular routine, social interaction'),
    ('Heart Disease', 'Chest pain, shortness of breath', 'Atorvastatin 20mg once daily, Clopidogrel 75mg once daily', 'Low fat diet, walking'),
    ('Thyroid', 'Weight changes, fatigue', 'Thyroxine 50mcg once daily empty stomach', 'Regular sleep, balanced diet'),
    ('Pneumonia', 'Cough, fever, breathing difficulty', 'Azithromycin 500mg once daily, expectorants', 'Rest, plenty of fluids'),
    ('Gastroenteritis', 'Vomiting, diarrhea, stomach pain', 'ORS solution, Ondansetron 4mg SOS', 'Light diet, hydration'),
    ('Allergy', 'Sneezing, itching, rash', 'Cetirizine 10mg once daily, Fexofenadine SOS', 'Avoid allergens'),
    ('Insomnia', 'Difficulty sleeping', 'Melatonin 3mg at night, sleep hygiene', 'Regular sleep schedule'),
    ('Anemia', 'Weakness, pale skin', 'Ferrous sulfate tablets, Folic acid', 'Iron-rich diet'),
]

# Create 63 patients
patients = []
patient_first_names = [
    'Priya', 'Rahul', 'Anjali', 'Vijay', 'Sneha', 'Amit', 'Pooja', 'Rohit', 'Neha', 'Kunal',
    'Divya', 'Sanjay', 'Meera', 'Ashok', 'Kavita', 'Mahesh', 'Sunita', 'Ramesh', 'Lakshmi', 'Ganesh',
    'Radha', 'Krishnan', 'Uma', 'Siva', 'Parvati', 'Brahma', 'Saraswati', 'Vishnu', 'Lakshmi', 'Shiva',
    'Durga', 'Kartik', 'Murugan', 'Janaki', 'Rama', 'Sita', 'Hanuman', 'Garuda', 'Narasimha', 'Vishnu',
    'Matsya', 'Kurma', 'Varaha', 'Narasimha', 'Vamana', 'Parasurama', 'Balarama', 'Buddha', 'Kalki', 'Aditya',
    'Surya', 'Chandra', 'Mangala', 'Budha', 'Brihaspati', 'Shukra', 'Shani', 'Rahu', 'Ketu', 'Pushya', 'Uttara',
    'Aarav', 'Aanya', 'Vihaan', 'Saanvi', 'Arjun', 'Ananya', 'Reyansh', 'Pari', 'Ayaan', 'Myra'
]

patient_last_names = [
    'Patel', 'Sharma', 'Singh', 'Kumar', 'Gupta', 'Verma', 'Reddy', 'Joshi', 'Mehta', 'Shah',
    'Desai', 'Chopra', 'Kapoor', 'Malhotra', 'Khanna', 'Bhatia', 'Saxena', 'Mishra', 'Pandey', 'Trivedi'
]

blood_types = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
genders = ['male', 'female', 'other']

for i in range(63):
    first_name = patient_first_names[i]
    last_name = patient_last_names[i % 20]
    username = f"patient{i+1}"
    
    user = User.objects.create_user(
        username=username,
        email=f"{username}@email.com",
        password='patient123',
        first_name=first_name,
        last_name=last_name,
        role='patient',
        phone=f"+91{random.randint(7000000000, 9999999999)}"
    )
    
    # Assign random medical condition
    condition, symptoms, medicines, instructions = random.choice(patient_conditions)
    
    patient = Patient.objects.create(
        user=user,
        gender=random.choice(genders),
        blood_type=random.choice(blood_types),
        emergency_contact=f"+91{random.randint(7000000000, 9999999999)}",
        emergency_contact_name=random.choice(patient_first_names[:30]),
        medical_history=condition,
        allergies='None' if random.random() > 0.3 else random.choice(['Penicillin', 'Aspirin', 'Pollen', 'Dust'])
    )
    patients.append(patient)
    print(f"Created patient: {first_name} {last_name} - {condition}")

# Create appointments for all patients with random doctors
print("\nCreating appointments...")
for i, patient in enumerate(patients):
    doctor = random.choice(doctors)
    days_offset = random.randint(-5, 10)
    appointment_date = timezone.now() + timedelta(days=days_offset)
    appointment_date = appointment_date.replace(hour=random.randint(9, 17), minute=random.choice([0, 30]))
    
    if days_offset < 0:
        status = 'completed' if random.random() > 0.2 else 'cancelled'
    elif days_offset == 0:
        status = random.choice(['scheduled', 'confirmed'])
    else:
        status = random.choice(['scheduled', 'confirmed', 'completed'])
    
    appointment = Appointment.objects.create(
        doctor=doctor,
        patient=patient,
        appointment_date=appointment_date,
        status=status,
        reason=patient.medical_history,
        notes=f"Follow-up for {patient.medical_history}"
    )
    
    # Create invoice automatically
    Invoice.objects.create(
        appointment=appointment,
        amount=doctor.consultation_fee,
        description=f"Consultation fee for {patient.medical_history}",
        status='paid' if status == 'completed' else 'pending'
    )
    
    # Create prescription for completed appointments
    if status == 'completed':
        Prescription.objects.create(
            appointment=appointment,
            medications=medicines,
            dosage='As prescribed',
            instructions=instructions,
            notes=f"Patient presented with {condition}.",
            created_by=doctor
        )
    
    print(f"Created appointment: {patient.user.first_name} with Dr. {doctor.user.first_name} - {status}")

print("\n✅ Data population complete!")
print(f"- 30 Doctors created")
print(f"- 63 Patients created")
print(f"- 63 Appointments created (with invoices)")
print(f"- Prescriptions created for completed appointments")
