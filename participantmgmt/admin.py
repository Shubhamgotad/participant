from django.contrib import admin

from participantmgmt.models import Attendance, Notification, Result, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'course', 'academic_year', 'mobile', 'is_approved', 'created_at']
    list_filter = ['course', 'academic_year', 'is_approved', 'gender']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'mobile']
    list_editable = ['is_approved']
    readonly_fields = ['created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.short_description = 'Full Name'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'subject', 'status']
    list_filter = ['status', 'subject', 'date']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    date_hierarchy = 'date'


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'semester', 'obtained_marks', 'max_marks', 'grade']
    list_filter = ['semester', 'grade', 'subject']
    search_fields = ['student__user__first_name', 'student__user__last_name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'is_global', 'created_at']
    list_filter = ['is_global', 'is_read']


admin.site.site_header = 'PRAVAAH Administration'
admin.site.site_title = 'PRAVAAH Admin'
admin.site.index_title = 'Student Management System'