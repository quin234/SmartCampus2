"""
Super Admin Views
Handles all Super Admin functionality - completely separate from College Admin
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.utils.text import slugify
from functools import wraps
import json

from education.models import College, CustomUser, Student, CollegeCourse, CollegeUnit, SchoolRegistration, GlobalCourse, GlobalUnit
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


def superadmin_login_required(view_func):
    """Custom login_required decorator that redirects to superadmin login instead of admin login"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Redirect to superadmin login with next parameter
            from django.urls import reverse
            login_url = reverse('superadmin:login')
            path = request.get_full_path()
            # Avoid redirect loop - don't add next if already going to login
            if '/superadmin/login' not in path:
                return redirect(f'{login_url}?next={path}')
            else:
                return redirect(login_url)
        # If authenticated but not super admin, redirect to appropriate page
        if not request.user.is_super_admin():
            if hasattr(request.user, 'college') and request.user.college:
                return redirect('college_landing', college_slug=request.user.college.get_slug())
            else:
                return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def superadmin_login(request):
    """Super Admin login page - uses same template as college admin"""
    # Redirect if already authenticated
    if request.user.is_authenticated:
        if request.user.is_super_admin():
            # Check for next parameter to redirect to intended page
            next_url = request.GET.get('next', None)
            # Avoid redirect loop - don't redirect to login page itself
            if next_url and next_url.startswith('/superadmin/') and '/superadmin/login' not in next_url:
                return redirect(next_url)
            return redirect('superadmin:dashboard')
        elif request.user.role == 'college_admin' and hasattr(request.user, 'college') and request.user.college:
            return redirect('director_dashboard')
        elif hasattr(request.user, 'college') and request.user.college:
            return redirect('college_landing', college_slug=request.user.college.get_slug())
        else:
            return redirect('admin_login')

    # Handle POST request
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_super_admin():
                login(request, user)
                messages.success(request, f'Welcome, {user.username}!')
                # Check for next parameter to redirect to intended page
                next_url = request.POST.get('next') or request.GET.get('next', None)
                # Avoid redirect loop - don't redirect to login page itself
                if next_url and next_url.startswith('/superadmin/') and '/superadmin/login' not in next_url:
                    return redirect(next_url)
                return redirect('superadmin:dashboard')
            else:
                messages.error(request, 'Access denied. Super Admin access required.')
                return render(request, 'admin/login.html', {'error': 'Access denied. Super Admin access required.'})
        else:
            return render(request, 'admin/login.html', {'error': 'Invalid username or password.'})

    return render(request, 'admin/login.html')


@superadmin_login_required
def superadmin_dashboard(request):
    """Super Admin Dashboard - system-wide overview"""
    user = request.user
    
    # Calculate total departments (unique course names across all colleges)
    total_departments = CollegeCourse.objects.values('name').distinct().count()
    
    # Get colleges statistics
    total_colleges = College.objects.count()
    active_colleges = College.objects.filter(registration_status='active').count()
    pending_colleges = College.objects.filter(registration_status='pending').count()
    suspended_colleges = College.objects.filter(registration_status='inactive').count()
    
    # Calculate colleges added this month
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    colleges_this_month = College.objects.filter(created_at__gte=start_of_month).count()
    
    # Get recent colleges (last 10)
    recent_colleges = College.objects.select_related().order_by('-created_at')[:10]
    
    # Get recent school registrations (pending approvals)
    recent_registrations = SchoolRegistration.objects.filter(status='pending').order_by('-created_at')[:10]
    
    # Calculate student distribution by college
    student_distribution = Student.objects.values('college__name').annotate(
        student_count=Count('id')
    ).order_by('-student_count')[:10]
    
    # Calculate colleges growth by month (last 12 months)
    colleges_growth_data = []
    for i in range(11, -1, -1):
        month_start = (now - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            month_end = now
        else:
            month_end = (now - timedelta(days=30*(i-1))).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        count = College.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        colleges_growth_data.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    # Convert to JSON for JavaScript
    colleges_growth_json = json.dumps(colleges_growth_data)
    student_distribution_json = json.dumps(list(student_distribution))
    
    context = {
        'user': user,
        'total_colleges': total_colleges,
        'active_colleges': active_colleges,
        'pending_colleges': pending_colleges,
        'suspended_colleges': suspended_colleges,
        'total_students': Student.objects.count(),
        'total_lecturers': CustomUser.objects.filter(role='lecturer').count(),
        'total_departments': total_departments,
        'colleges_this_month': colleges_this_month,
        'recent_colleges': recent_colleges,
        'recent_registrations': recent_registrations,
        'colleges_growth': colleges_growth_json,
        'student_distribution': student_distribution_json,
    }
    
    return render(request, 'superadmin/dashboard.html', context)


@superadmin_login_required
def superadmin_colleges(request):
    """Super Admin - Colleges Management Page"""
    user = request.user
    
    context = {
        'user': user,
    }
    
    return render(request, 'superadmin/colleges.html', context)


@superadmin_login_required
def superadmin_academic(request):
    """Super Admin - Academic Management Page (Global Units and Courses)"""
    user = request.user
    
    # Handle POST requests for creating global units and courses
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_global_unit':
            code = request.POST.get('code', '').strip().upper()
            name = request.POST.get('name', '').strip()
            
            if not code or not name:
                messages.error(request, 'Unit code and name are required.')
            else:
                # Check if unit code already exists
                if GlobalUnit.objects.filter(code=code).exists():
                    messages.error(request, f'A unit with code {code} already exists.')
                else:
                    GlobalUnit.objects.create(code=code, name=name)
                    messages.success(request, f'Global unit {code} - {name} created successfully.')
        
        elif action == 'create_global_course':
            name = request.POST.get('name', '').strip()
            level = request.POST.get('level', '').strip()
            category = request.POST.get('category', '').strip()
            
            if not name or not level or not category:
                messages.error(request, 'Course name, level, and category are required.')
            else:
                GlobalCourse.objects.create(name=name, level=level, category=category)
                messages.success(request, f'Global course {name} created successfully.')
        
        return redirect('superadmin:academic')
    
    # Get all global units and courses for display
    global_units = GlobalUnit.objects.all().order_by('code')
    global_courses = GlobalCourse.objects.all().order_by('name')
    
    context = {
        'user': user,
        'global_units': global_units,
        'global_courses': global_courses,
        'level_choices': GlobalCourse.LEVEL_CHOICES,
    }
    
    return render(request, 'superadmin/academic.html', context)


@superadmin_login_required
def superadmin_analytics(request):
    """Super Admin - Analytics Page"""
    user = request.user
    
    context = {
        'user': user,
    }
    
    return render(request, 'superadmin/analytics.html', context)


@superadmin_login_required
def superadmin_settings(request):
    """Super Admin - System Settings Page"""
    user = request.user
    
    context = {
        'user': user,
    }
    
    return render(request, 'superadmin/settings.html', context)


@superadmin_login_required
def superadmin_profile(request):
    """Super Admin - Profile Page"""
    user = request.user
    
    context = {
        'user': user,
    }
    
    return render(request, 'superadmin/profile.html', context)


@superadmin_login_required
def superadmin_logout(request):
    """Super Admin logout - redirects to admin login"""
    from django.contrib.auth import logout
    
    # Handle both GET and POST requests
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        
        # If it's an AJAX request, return JSON
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': 'Logged out successfully'})
        
        # Always redirect to admin login
        return redirect('admin_login')
    
    return redirect('admin_login')
