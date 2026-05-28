from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student, Attendance, Result
from .forms import StudentProfileForm

@login_required
def profile_view(request):
    student = get_object_or_404(Student, user=request.user)
    return render(request, 'students/profile.html', {'student': student})

@login_required
def profile_edit(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('students:profile')
        else:
            messages.error(request, 'Please correct the errors.')
    else:
        form = StudentProfileForm(instance=student)
    return render(request, 'students/profile_edit.html', {'form': form, 'student': student})

@login_required
def attendance_view(request):
    student = get_object_or_404(Student, user=request.user)
    attendance_records = Attendance.objects.filter(student=student)
    percentage = student.attendance_percentage()
    month_filter = request.GET.get('month', '')
    if month_filter:
        attendance_records = attendance_records.filter(date__month=month_filter)
    return render(request, 'students/attendance.html', {
        'student': student,
        'attendance_records': attendance_records,
        'percentage': percentage,
        'month_filter': month_filter,
    })

@login_required
def results_view(request):
    student = get_object_or_404(Student, user=request.user)
    results = Result.objects.filter(student=student)
    semester_filter = request.GET.get('semester', '')
    if semester_filter:
        results = results.filter(semester=semester_filter)
    semesters = Result.objects.filter(student=student).values_list('semester', flat=True).distinct()
    total_marks = sum(r.obtained_marks for r in results)
    max_total = sum(r.max_marks for r in results)
    overall_pct = round((total_marks / max_total) * 100, 1) if max_total else 0
    return render(request, 'students/results.html', {
        'student': student,
        'results': results,
        'semesters': semesters,
        'semester_filter': semester_filter,
        'overall_pct': overall_pct,
    })
