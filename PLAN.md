# Plan: Fix Doctor/Patient Information Display Issue

## Problem
The user cannot see doctor names, patients, or any information on the frontend pages.

## Root Cause
The `core/home_views.py` makes HTTP requests to `http://127.0.0.1:8000/api/doctors/` to fetch data. This approach:
1. Requires the Django server to be running on port 8000
2. Can fail due to network issues
3. Is inefficient - making HTTP requests to itself

## Solution
Modify `home_views.py` to directly query the database using Django ORM instead of making HTTP requests to the API.

## Files to Edit
- `core/home_views.py` - Modify all view functions to directly query the database

## Changes to Make

### 1. doctors_list function
- Query Doctor.objects directly with select_related('user')
- Pass doctors to template

### 2. patients_list function
- Query Patient.objects directly with select_related('user')
- Pass patients to template

### 3. appointments_list function
- Query Appointment.objects directly with select_related('doctor__user', 'patient__user')
- Pass appointments to template

### 4. prescriptions_list function
- Query Prescription.objects directly with select_related
- Pass prescriptions to template

### 5. invoices_list function
- Query Invoice.objects directly with select_related
- Pass invoices to template

### 6. dashboard function
- Query database for statistics directly
- Pass stats to template

## Implementation Steps
1. Import necessary models in home_views.py
2. Replace HTTP requests with direct database queries
3. Test the changes
