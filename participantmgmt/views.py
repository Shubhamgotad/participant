import json
import re
from uuid import uuid4
from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import get_valid_filename

from participantmgmt.forms import (
	AcademicDetailsForm,
	CourseSelectionForm,
	LoginForm,
	PAYMENT_METHOD_CHOICES,
	PaymentForm,
	PersonalDetailsForm,
	StudentProfileForm,
)
from participantmgmt.models import Attendance, Notification, Result, Student


ADMISSION_SESSION_KEY = 'admission_draft'
TEMP_ADMISSION_FOLDER = 'admission_drafts'
DOCUMENT_TYPE_CHOICES = [
	('aadhaar_card', 'Aadhaar Card'),
	('pan_card', 'PAN Card'),
	('tenth_marksheet', '10th Marksheet'),
	('twelfth_marksheet', '12th Marksheet'),
	('graduation_certificate', 'Graduation Certificate'),
	('transfer_certificate', 'Transfer Certificate'),
	('passport_photo', 'Passport Size Photo'),
	('other_document', 'Other Document'),
]

COURSE_CATALOG = {
	'B.Tech CSE': {
		'duration': '4 Years',
		'fees': 'Rs. 1,20,000 per year',
		'description': 'A hands-on software engineering track with programming, web development, databases, cloud, and placement-focused labs.',
		'highlights': ['Full stack labs', 'Coding practice', 'Placement support'],
	},
	'B.Tech ECE': {
		'duration': '4 Years',
		'fees': 'Rs. 1,10,000 per year',
		'description': 'Electronics and communication fundamentals with embedded systems, signals, and industry-relevant projects.',
		'highlights': ['Embedded systems', 'Circuit design', 'Project work'],
	},
	'B.Tech ME': {
		'duration': '4 Years',
		'fees': 'Rs. 1,05,000 per year',
		'description': 'Mechanical engineering covering design, manufacturing, thermal systems, and practical workshops.',
		'highlights': ['CAD/CAM', 'Workshop practice', 'Industry projects'],
	},
	'B.Tech Civil': {
		'duration': '4 Years',
		'fees': 'Rs. 1,00,000 per year',
		'description': 'Civil engineering basics, structural design, surveying, and site-based learning for future engineers.',
		'highlights': ['Survey labs', 'Structure design', 'Site exposure'],
	},
	'BCA': {
		'duration': '3 Years',
		'fees': 'Rs. 75,000 per year',
		'description': 'A computer applications program focused on programming, databases, networking, and application development.',
		'highlights': ['Programming basics', 'Database skills', 'Application building'],
	},
	'MCA': {
		'duration': '2 Years',
		'fees': 'Rs. 90,000 per year',
		'description': 'Advanced software development program for graduates who want deep application engineering skills.',
		'highlights': ['Advanced software labs', 'System design', 'Project mentoring'],
	},
	'MBA': {
		'duration': '2 Years',
		'fees': 'Rs. 1,50,000 per year',
		'description': 'A management-focused track with strategy, communication, operations, analytics, and leadership modules.',
		'highlights': ['Business case studies', 'Analytics', 'Leadership training'],
	},
	'B.Sc': {
		'duration': '3 Years',
		'fees': 'Rs. 55,000 per year',
		'description': 'Science foundation program with lab work, quantitative reasoning, and specialization options.',
		'highlights': ['Lab sessions', 'Foundation subjects', 'Research exposure'],
	},
	'M.Sc': {
		'duration': '2 Years',
		'fees': 'Rs. 65,000 per year',
		'description': 'Postgraduate science track with advanced theory, projects, and applied research exposure.',
		'highlights': ['Advanced concepts', 'Research projects', 'Mentored learning'],
	},
}


def _ensure_session_key(request):
	if not request.session.session_key:
		request.session.create()
	return request.session.session_key


def _get_admission_draft(request):
	return request.session.get(ADMISSION_SESSION_KEY, {
		'personal': {},
		'academic': {},
		'course': {},
		'payment': {},
		'documents': [],
	})


def _save_admission_draft(request, draft):
	request.session[ADMISSION_SESSION_KEY] = draft
	request.session.modified = True


def _clear_admission_draft(request):
	request.session.pop(ADMISSION_SESSION_KEY, None)
	request.session.modified = True


def _admission_doc_rows(draft):
	documents = draft.get('documents') or []
	if not documents:
		return [{'index': 1, 'document_type': '', 'file_name': ''}]
	rows = []
	for index, document in enumerate(documents, start=1):
		rows.append({
			'index': index,
			'document_type': document.get('document_type', ''),
			'file_name': document.get('original_name', ''),
		})
	return rows


def _save_temp_upload(uploaded_file, subfolder):
	file_name = get_valid_filename(uploaded_file.name)
	temp_key = uuid4().hex
	temp_path = f'{TEMP_ADMISSION_FOLDER}/{subfolder}/{temp_key}_{file_name}'
	return default_storage.save(temp_path, uploaded_file)


def _read_temp_file(temp_path, final_name):
	with default_storage.open(temp_path, 'rb') as temp_file:
		return ContentFile(temp_file.read(), name=final_name)


def _extract_document_rows(post_data, files_data):
	indices = set()
	pattern = re.compile(r'^(document_type|document_file)_(\d+)$')
	for key in list(post_data.keys()) + list(files_data.keys()):
		match = pattern.match(key)
		if match:
			indices.add(int(match.group(2)))

	documents = []
	incomplete = []
	for index in sorted(indices):
		document_type = post_data.get(f'document_type_{index}', '').strip()
		uploaded_file = files_data.get(f'document_file_{index}')
		if document_type and uploaded_file:
			documents.append({
				'document_type': document_type,
				'original_name': uploaded_file.name,
				'temp_file': uploaded_file,
			})
		elif document_type or uploaded_file:
			incomplete.append(index)
	return documents, incomplete


def _posted_document_rows(post_data, files_data):
	indices = set()
	pattern = re.compile(r'^(document_type|document_file)_(\d+)$')
	for key in list(post_data.keys()) + list(files_data.keys()):
		match = pattern.match(key)
		if match:
			indices.add(int(match.group(2)))

	rows = []
	for index in sorted(indices):
		file_object = files_data.get(f'document_file_{index}')
		rows.append({
			'index': index,
			'document_type': post_data.get(f'document_type_{index}', ''),
			'file_name': getattr(file_object, 'name', ''),
		})
	return rows or [{'index': 1, 'document_type': '', 'file_name': ''}]


def _course_snapshot(course_name):
	return COURSE_CATALOG.get(course_name, {})


def _personal_initial_data(personal_data):
	initial = dict(personal_data or {})
	if initial.get('dob') and isinstance(initial['dob'], str):
		try:
			initial['dob'] = date.fromisoformat(initial['dob'])
		except ValueError:
			initial['dob'] = None
	return initial


def _manifest_for_draft(request, draft):
	return {
		'student_name': f"{draft.get('personal', {}).get('first_name', '')} {draft.get('personal', {}).get('last_name', '')}".strip(),
		'username': draft.get('course', {}).get('username', ''),
		'email': draft.get('personal', {}).get('email', ''),
		'course': draft.get('course', {}).get('course', ''),
		'academic_year': draft.get('academic', {}).get('academic_year', ''),
		'payment': draft.get('payment', {}),
		'documents': draft.get('documents', []),
		'submitted_at': timezone.now().isoformat(),
		'course_snapshot': _course_snapshot(draft.get('course', {}).get('course', '')),
		'session_key': request.session.session_key,
	}


def _finalize_admission(request, draft):
	personal = draft.get('personal', {})
	academic = draft.get('academic', {})
	course = draft.get('course', {})
	payment = draft.get('payment', {})
	documents = draft.get('documents', [])

	if User.objects.filter(username=course.get('username')).exists():
		raise ValueError('That username is already taken.')

	user = User.objects.create_user(
		username=course['username'],
		password=course['password1'],
		email=personal.get('email', ''),
		first_name=personal.get('first_name', ''),
		last_name=personal.get('last_name', ''),
	)

	student = Student.objects.create(
		user=user,
		dob=date.fromisoformat(personal['dob']),
		gender=personal['gender'],
		mobile=personal['mobile'],
		address=personal['address'],
		course=course['course'],
		academic_year=academic['academic_year'],
		is_approved=False,
	)

	photo_path = personal.get('photo_path')
	if photo_path:
		student.photo.save(get_valid_filename(photo_path.split('/')[-1]), _read_temp_file(photo_path, photo_path.split('/')[-1]), save=True)

	final_documents = []
	for document in documents:
		stored_name = get_valid_filename(document['original_name'])
		final_path = f'student_documents/{user.username}/{document["document_type"]}_{stored_name}'
		default_storage.save(final_path, _read_temp_file(document['temp_path'], stored_name))
		final_documents.append({
			'document_type': document['document_type'],
			'file_path': final_path,
		})

	receipt_path = payment.get('receipt_path', '')
	if receipt_path:
		stored_receipt_name = get_valid_filename(receipt_path.split('/')[-1])
		final_receipt_path = f'student_documents/{user.username}/payment_{stored_receipt_name}'
		default_storage.save(final_receipt_path, _read_temp_file(receipt_path, stored_receipt_name))
		payment['receipt_final_path'] = final_receipt_path

	manifest = _manifest_for_draft(request, draft)
	manifest['documents'] = final_documents
	manifest_path = f'student_documents/{user.username}/application_summary.json'
	default_storage.save(manifest_path, ContentFile(json.dumps(manifest, indent=2), name='application_summary.json'))

	return student


def landing(request):
	return render(request, 'landing.html')


def register_view(request):
	if request.user.is_authenticated:
		return redirect('participantmgmt:home')
	draft = _get_admission_draft(request)
	if request.method == 'POST':
		form = PersonalDetailsForm(request.POST, request.FILES)
		if form.is_valid():
			draft['personal'] = {
				'first_name': form.cleaned_data['first_name'],
				'last_name': form.cleaned_data['last_name'],
				'dob': form.cleaned_data['dob'].isoformat(),
				'gender': form.cleaned_data['gender'],
				'mobile': form.cleaned_data['mobile'],
				'email': form.cleaned_data['email'],
				'address': form.cleaned_data['address'],
			}
			if form.cleaned_data.get('photo'):
				draft['personal']['photo_path'] = _save_temp_upload(form.cleaned_data['photo'], _ensure_session_key(request))
			_save_admission_draft(request, draft)
			return redirect('participantmgmt:register_documents')
	else:
		form = PersonalDetailsForm(initial=_personal_initial_data(draft.get('personal', {})))
	return render(request, 'accounts/register_step1.html', {'form': form})


def register_documents_view(request):
	if request.user.is_authenticated:
		return redirect('participantmgmt:home')
	draft = _get_admission_draft(request)
	if not draft.get('personal'):
		return redirect('participantmgmt:register')

	academic_form = AcademicDetailsForm(initial=draft.get('academic', {}))
	document_rows = _admission_doc_rows(draft)
	if request.method == 'POST':
		academic_form = AcademicDetailsForm(request.POST)
		documents, incomplete_rows = _extract_document_rows(request.POST, request.FILES)
		if academic_form.is_valid() and not incomplete_rows and documents:
			draft['academic'] = academic_form.cleaned_data
			draft_documents = []
			for document in documents:
				draft_documents.append({
					'document_type': document['document_type'],
					'original_name': document['original_name'],
					'temp_path': _save_temp_upload(document['temp_file'], _ensure_session_key(request)),
				})
			draft['documents'] = draft_documents
			_save_admission_draft(request, draft)
			return redirect('participantmgmt:register_course')
		if not documents:
			academic_form.add_error(None, 'Please upload at least one document.')
		elif incomplete_rows:
			academic_form.add_error(None, 'Each document row must include both a document type and a file.')
		document_rows = _posted_document_rows(request.POST, request.FILES)
	return render(request, 'accounts/register_step2.html', {
		'form': academic_form,
		'document_rows': document_rows,
		'document_choices': DOCUMENT_TYPE_CHOICES,
	})


def register_course_view(request):
	if request.user.is_authenticated:
		return redirect('participantmgmt:home')
	draft = _get_admission_draft(request)
	if not draft.get('personal') or not draft.get('academic') or not draft.get('documents'):
		return redirect('participantmgmt:register')

	form = CourseSelectionForm(initial=draft.get('course', {}))
	if request.method == 'POST':
		form = CourseSelectionForm(request.POST)
		if form.is_valid():
			if User.objects.filter(username=form.cleaned_data['username']).exists():
				form.add_error('username', 'This username is already taken.')
			else:
				draft['course'] = form.cleaned_data
				_save_admission_draft(request, draft)
				return redirect('participantmgmt:register_payment')
	return render(request, 'accounts/register_step3.html', {
		'form': form,
		'course_catalog': COURSE_CATALOG,
	})


def register_payment_view(request):
	if request.user.is_authenticated:
		return redirect('participantmgmt:home')
	draft = _get_admission_draft(request)
	if not draft.get('personal') or not draft.get('academic') or not draft.get('documents') or not draft.get('course'):
		return redirect('participantmgmt:register')

	form = PaymentForm(initial=draft.get('payment', {}))
	if request.method == 'POST':
		form = PaymentForm(request.POST, request.FILES)
		if form.is_valid():
			draft['payment'] = {
				'payment_method': form.cleaned_data['payment_method'],
				'transaction_id': form.cleaned_data['transaction_id'],
			}
			if form.cleaned_data.get('receipt'):
				draft['payment']['receipt_path'] = _save_temp_upload(form.cleaned_data['receipt'], _ensure_session_key(request))

			try:
				student = _finalize_admission(request, draft)
			except ValueError as error:
				form.add_error('payment_method', str(error))
			else:
				_clear_admission_draft(request)
				messages.success(request, f'Application submitted successfully for {student.get_full_name()}. Please wait for admin approval.')
				return redirect('participantmgmt:login')

	return render(request, 'accounts/register_payment.html', {
		'form': form,
		'draft': draft,
		'course_summary': _course_snapshot(draft.get('course', {}).get('course', '')),
		'payment_methods': PAYMENT_METHOD_CHOICES,
	})


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