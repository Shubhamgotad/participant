from django.contrib.auth.models import User
from django.db import models


GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
COURSE_CHOICES = [
    ('B.Tech CSE', 'B.Tech CSE'), ('B.Tech ECE', 'B.Tech ECE'),
    ('B.Tech ME', 'B.Tech ME'), ('B.Tech Civil', 'B.Tech Civil'),
    ('BCA', 'BCA'), ('MCA', 'MCA'), ('MBA', 'MBA'),
    ('B.Sc', 'B.Sc'), ('M.Sc', 'M.Sc'),
]
YEAR_CHOICES = [('1st Year', '1st Year'), ('2nd Year', '2nd Year'), ('3rd Year', '3rd Year'), ('4th Year', '4th Year')]
STATUS_CHOICES = [('Present', 'Present'), ('Absent', 'Absent'), ('Late', 'Late')]
GRADE_CHOICES = [('A+', 'A+'), ('A', 'A'), ('B+', 'B+'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')]


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    course = models.CharField(max_length=50, choices=COURSE_CHOICES)
    academic_year = models.CharField(max_length=20, choices=YEAR_CHOICES)
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

    def get_full_name(self):
        return self.user.get_full_name()

    def attendance_percentage(self):
        total = self.attendance_set.count()
        if total == 0:
            return 0
        present = self.attendance_set.filter(status='Present').count()
        return round((present / total) * 100, 1)

    class Meta:
        ordering = ['-created_at']
        db_table = 'students_student'


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    subject = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Present')
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

    class Meta:
        ordering = ['-date']
        unique_together = ['student', 'date', 'subject']
        db_table = 'students_attendance'


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    semester = models.CharField(max_length=20)
    max_marks = models.IntegerField(default=100)
    obtained_marks = models.IntegerField()
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES)
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.grade}"

    def percentage(self):
        return round((self.obtained_marks / self.max_marks) * 100, 1)

    class Meta:
        ordering = ['semester', 'subject']
        db_table = 'students_result'


class Notification(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_global = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        db_table = 'students_notification'