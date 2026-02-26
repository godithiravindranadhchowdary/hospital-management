# Hospital Management System

A comprehensive Django-based Hospital Management System with role-based access for Admin, Doctors, and Patients.

## Features

### 🏥 Admin Features
- **Dashboard**: View all hospital statistics
- **Manage Doctors**: View all doctors with their earnings, patients treated
- **Manage Patients**: View all patients with their total spending
- **Manage Operations**: Track all surgeries and procedures
- **Manage Leaves**: Approve/reject doctor leave requests
- **Manage Payments**: View all payment transactions
- **Medical Records**: View all patient medical records
- **Django Admin**: Full admin panel access

### 👨‍⚕️ Doctor Features
- **Personal Dashboard**: View today's appointments, completed visits, earnings
- **My Appointments**: View all scheduled appointments with patients
- **My Patients**: View all patients you've treated
- **Operations**: Track surgeries performed
- **Leaves**: Request time off
- **Profile**: View and manage your profile with experience and qualifications

### 🏥 Patient Features
- **Personal Dashboard**: View your health dashboard
- **My Appointments**: View all your appointments with doctors
- **My Prescriptions**: View all prescriptions from doctors
- **My Invoices**: View and pay bills
- **My Payments**: View payment history
- **Medical Records**: View your complete medical history
- **Profile**: View and manage your profile

### ✨ Design Features
- **Glassmorphism UI**: Beautiful transparent mirror effect
- **Animated gradient orbs**: Smooth floating animations
- **Responsive design**: Works on all devices
- **Dark theme**: Easy on the eyes

## Technology Stack
- **Backend**: Django 5.x
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: Docker, Docker Compose, Render

## Installation

1. Clone the repository:
```
bash
cd hospital-management
```

2. Create virtual environment:
```
bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```
bash
pip install -r requirements.txt
```

4. Run migrations:
```
bash
python manage.py migrate
```

5. Create sample data:
```
bash
python populate_data.py
```

6. Run the server:
```
bash
python manage.py runserver
```

7. Visit: http://127.0.0.1:8000/

## Login Credentials

### Admin
- **URL**: http://127.0.0.1:8000/admin/login/
- **Username**: `admin`
- **Password**: `admin123`

### Doctors (30 doctors available)
- **URL**: http://127.0.0.1:8000/login/
- **Username**: `doctor1` to `doctor30`
- **Password**: `doctor123`

### Patients (63 patients available)
- **URL**: http://127.0.0.1:8000/login/
- **Username**: `patient1` to `patient63`
- **Password**: `patient123`

## Project Structure

```
hospital-management/
├── config/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                # Main application
│   ├── models.py       # Database models
│   ├── views.py        # API views
│   ├── home_views.py   # Frontend views
│   ├── serializers.py
│   ├── permissions.py
│   └── urls.py
├── templates/           # HTML templates
│   ├── index.html
│   ├── dashboard.html
│   ├── doctor_*.html
│   ├── patient_*.html
│   └── admin_*.html
├── static/             # Static files
├── populate_data.py    # Sample data generator
├── manage.py
├── requirements.txt
└── README.md
```

## Screenshots

The application features a beautiful glassmorphism design with:
- Dark gradient background (#1a1a2e → #16213e → #0f3460)
- Animated floating gradient orbs
- Frosted glass cards with backdrop blur
- Smooth hover animations

## License

MIT License
