"""
Super Admin URL Configuration
All Super Admin routes are prefixed with /superadmin/
"""
from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    # Super Admin Login (uses same template as college admin)
    path('login/', views.superadmin_login, name='login'),
    
    # Super Admin Dashboard
    path('dashboard/', views.superadmin_dashboard, name='dashboard'),
    
    # Super Admin Pages
    path('colleges/', views.superadmin_colleges, name='colleges'),
    path('academic/', views.superadmin_academic, name='academic'),
    path('analytics/', views.superadmin_analytics, name='analytics'),
    path('settings/', views.superadmin_settings, name='settings'),
    path('profile/', views.superadmin_profile, name='profile'),
    
    # Super Admin Logout
    path('logout/', views.superadmin_logout, name='logout'),
]

