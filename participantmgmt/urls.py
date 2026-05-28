from django.urls import path

from participantmgmt import views

app_name = 'participantmgmt'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('dashboard/', views.home, name='home'),
    path('students/profile/', views.profile_view, name='profile'),
    path('students/profile/edit/', views.profile_edit, name='profile_edit'),
    path('students/attendance/', views.attendance_view, name='attendance'),
    path('students/results/', views.results_view, name='results'),
]