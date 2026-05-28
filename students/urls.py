from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('results/', views.results_view, name='results'),
]
