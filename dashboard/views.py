from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from students.models import Student, Attendance, Result, Notification

@login_required
def home(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('landing')
    
    attendance_pct = student.attendance_percentage()
    recent_attendance = Attendance.objects.filter(student=student)[:5]
    recent_results = Result.objects.filter(student=student)[:5]
    notifications = Notification.objects.filter(student=student, is_global=False) | \
                    Notification.objects.filter(is_global=True)
    notifications = notifications.order_by('-created_at')[:5]
    
    total_subjects = Result.objects.filter(student=student).values('subject').distinct().count()
    total_attendance_days = Attendance.objects.filter(student=student).count()
    
    context = {
        'student': student,
        'attendance_pct': attendance_pct,
        'recent_attendance': recent_attendance,
        'recent_results': recent_results,
        'notifications': notifications,
        'total_subjects': total_subjects,
        'total_attendance_days': total_attendance_days,
    }
    return render(request, 'dashboard/home.html', context)
