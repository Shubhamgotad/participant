from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from participantmgmt.forms import LoginForm, StudentProfileForm, StudentRegistrationForm
from participantmgmt.models import Attendance, Notification, Result, Student


def landing(request):
	return render(request, 'landing.html')


def register_view(request):
	if request.user.is_authenticated:
		return redirect('participantmgmt:home')
	if request.method == 'POST':
		form = StudentRegistrationForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			messages.success(request, 'Registration successful! Please wait for admin approval before logging in.')
			return redirect('participantmgmt:login')
		messages.error(request, 'Please correct the errors below.')
	else:
		form = StudentRegistrationForm()
	return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
	if request.user.is_authenticated:
		return redirect('participantmgmt:home')
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(request, username=username, password=password)
			if user:
				if user.is_superuser:
					login(request, user)
					return redirect('/admin/')
				try:
					student = user.student
					if not student.is_approved:
						messages.warning(request, 'Your account is pending admin approval.')
						return render(request, 'accounts/login.html', {'form': form})
				except Exception:
					pass
				login(request, user)
				return redirect('participantmgmt:home')
			messages.error(request, 'Invalid username or password.')
	else:
		form = LoginForm()
	return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
	logout(request)
	messages.success(request, 'You have been logged out successfully.')
	return redirect('participantmgmt:landing')


@login_required
def home(request):
	try:
		student = Student.objects.get(user=request.user)
	except Student.DoesNotExist:
		return redirect('participantmgmt:landing')

	attendance_pct = student.attendance_percentage()
	recent_attendance = Attendance.objects.filter(student=student)[:5]
	recent_results = Result.objects.filter(student=student)[:5]
	notifications = Notification.objects.filter(student=student, is_global=False) | Notification.objects.filter(is_global=True)
	notifications = notifications.order_by('-created_at')[:5]

	total_subjects = Result.objects.filter(student=student).values('subject').distinct().count()
	total_attendance_days = Attendance.objects.filter(student=student).count()

	return render(request, 'dashboard/home.html', {
		'student': student,
		'attendance_pct': attendance_pct,
		'recent_attendance': recent_attendance,
		'recent_results': recent_results,
		'notifications': notifications,
		'total_subjects': total_subjects,
		'total_attendance_days': total_attendance_days,
	})


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
			return redirect('participantmgmt:profile')
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