"""
Run this script to populate sample data for testing.
Usage: python populate_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pravaah.settings')
django.setup()

from django.contrib.auth.models import User
from students.models import Student, Attendance, Result, Notification
from datetime import date, timedelta
import random

print("Creating sample data...")

# Clear existing sample data to avoid conflicts
User.objects.filter(username__in=['student1', 'student2']).delete()
print("🧹 Cleared old sample students if any...")

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@pravaah.edu', 'admin@123')
    print("✅ Superuser created: admin / admin@123")
else:
    print("ℹ️  Admin already exists")

# Create sample students
students_data = [
    {
        'username': 'student1', 'first_name': 'Arjun', 'last_name': 'Sharma',
        'email': 'arjun@pravaah.edu', 'password': 'student@123',
        'dob': date(2002, 5, 15), 'gender': 'Male',
        'mobile': '9876543210', 'address': '12, MG Road, Mumbai',
        'course': 'B.Tech CSE', 'academic_year': '2nd Year',
    },
    {
        'username': 'student2', 'first_name': 'Priya', 'last_name': 'Patel',
        'email': 'priya@pravaah.edu', 'password': 'student@123',
        'dob': date(2001, 8, 22), 'gender': 'Female',
        'mobile': '9988776655', 'address': '45, Link Road, Pune',
        'course': 'BCA', 'academic_year': '3rd Year',
    },
]

created_students = []
for s in students_data:
    # Create User
    user = User.objects.create_user(
        username=s['username'],
        password=s['password'],
        first_name=s['first_name'],
        last_name=s['last_name'],
        email=s['email']
    )
    # Create Student profile linked to user
    student = Student.objects.create(
        user=user,
        dob=s['dob'],
        gender=s['gender'],
        mobile=s['mobile'],
        address=s['address'],
        course=s['course'],
        academic_year=s['academic_year'],
        is_approved=True
    )
    created_students.append(student)
    print(f"✅ Student created: {s['username']} / {s['password']}")

# Create attendance records
subjects = ['Mathematics', 'Physics', 'Programming', 'Database', 'Networking']
statuses = ['Present', 'Present', 'Present', 'Absent', 'Late']

for student in created_students:
    for i in range(30):
        rec_date = date.today() - timedelta(days=i)
        for subject in subjects[:3]:
            try:
                Attendance.objects.create(
                    student=student,
                    date=rec_date,
                    subject=subject,
                    status=random.choice(statuses)
                )
            except Exception:
                pass
    print(f"✅ Attendance records created for {student}")

# Create results
semesters = ['Semester 1', 'Semester 2']
for student in created_students:
    for sem in semesters:
        for subj in subjects:
            marks = random.randint(55, 98)
            if marks >= 90:   grade = 'A+'
            elif marks >= 80: grade = 'A'
            elif marks >= 70: grade = 'B+'
            elif marks >= 60: grade = 'B'
            elif marks >= 50: grade = 'C'
            else:             grade = 'D'
            Result.objects.create(
                student=student,
                subject=subj,
                semester=sem,
                max_marks=100,
                obtained_marks=marks,
                grade=grade
            )
    print(f"✅ Results created for {student}")

# Global notifications
Notification.objects.get_or_create(
    title='Welcome to PRAVAAH!',
    defaults={
        'message': 'Welcome to the PRAVAAH Student Management Portal. Your one-stop platform for all academic needs.',
        'is_global': True
    }
)
Notification.objects.get_or_create(
    title='End Semester Exams Schedule',
    defaults={
        'message': 'End semester examinations will begin from next month. Please check the timetable on the notice board.',
        'is_global': True
    }
)
print("✅ Notifications created")

print("\n🎉 Sample data populated successfully!")
print("\n" + "="*45)
print("  LOGIN CREDENTIALS")
print("="*45)
print("  Admin Panel  : admin / admin@123")
print("  Student 1    : student1 / student@123")
print("  Student 2    : student2 / student@123")
print("="*45)
print("\n  Admin URL : http://127.0.0.1:8000/admin/")
print("  Site URL  : http://127.0.0.1:8000/")
print("="*45)