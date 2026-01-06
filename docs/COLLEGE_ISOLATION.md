# Multi-College Data Isolation Implementation

This document outlines the comprehensive multi-college data isolation system implemented in SmartCampus.

## Overview

Every college's data is completely isolated. Users can only access data from their own college. Super Admins are the only exception and can access all colleges for system management.

## Security Layers

### 1. Decorators (`education/decorators.py`)

#### `@verify_college_access`
- Verifies user has access to the college specified in URL (`college_slug`)
- Non-super-admin users can only access their own college
- Raises `PermissionDenied` if access is denied

#### `@ensure_college_access(model_class, college_field='college')`
- Ensures user can only access objects from their college
- Automatically verifies object ownership before allowing access
- Used for detail/edit/delete views

#### `@filter_by_college(model_class, college_field='college')`
- Automatically filters querysets by user's college
- Used for list views

#### `@college_required`
- Ensures user belongs to a college (not super admin)

#### `@college_admin_required`
- Ensures user is college admin or super admin

#### `@lecturer_required`
- Ensures user is lecturer, college admin, or super admin

### 2. API Endpoints (`education/api_views.py`)

All API endpoints enforce college isolation:

- **`api_departments_list`** - Filters by college, verifies access
- **`api_department_detail`** - Verifies object belongs to college
- **`api_courses_list`** - Filters by college, verifies access
- **`api_course_detail`** - Verifies object belongs to college
- **`api_units_list`** - Filters by college, verifies access
- **`api_unit_detail`** - Verifies object belongs to college
- **`api_students_list`** - Filters by college, verifies access
- **`api_student_detail`** - Verifies object belongs to college

**Key Function: `verify_user_college_access(request, college)`**
- Verifies authenticated user has access to the specified college
- Super admins can access any college
- Regular users can only access their own college
- Raises `PermissionDenied` if access denied

### 3. View Functions (`education/views.py`)

All views that access college-specific data:

#### College-Specific Pages (using `college_slug`):
- **`college_dashboard_page`** - Uses `@verify_college_access`
- **`college_students_page`** - Uses `@verify_college_access`
- **`college_departments_page`** - Uses `@verify_college_access`
- **`college_courses_page`** - Uses `@verify_college_access`
- **`college_units_page`** - Uses `@verify_college_access`

#### CRUD Operations:
- **`student_list`** - Filters: `Student.objects.filter(college=request.user.college)`
- **`student_create`** - Auto-assigns: `student.college = request.user.college`
- **`student_detail`** - Uses `@ensure_college_access(Student)`
- **`course_list`** - Filters: `CollegeCourse.objects.filter(college=college)`
- **`course_create`** - Auto-assigns: `course.college = request.user.college`
- **`unit_list`** - Filters: `CollegeUnit.objects.filter(college=college)`
- **`unit_create`** - Auto-assigns: `unit.college = request.user.college`
- **`enrollment_list`** - Filters: `Enrollment.objects.filter(unit__college=college)`
- **`enrollment_create`** - Filters form querysets by college
- **`result_list`** - Filters: `Enrollment.objects.filter(unit__college=college)`
- **`result_edit`** - Verifies lecturer has access to unit

### 4. Middleware (`education/middleware.py`)

**`CollegeAccessMiddleware`**:
- Stores user's college in `request.user_college` for easy access
- Skips processing for Django admin URLs
- Available to all views via `request.user_college`

### 5. Model Relationships

All models that belong to a college have a `college` ForeignKey:

- **`Student`** - `college = ForeignKey(College)`
- **`CollegeCourse`** - `college = ForeignKey(College)`
- **`CollegeUnit`** - `college = ForeignKey(College)`
- **`Enrollment`** - `unit.college` (via unit relationship)
- **`Result`** - `enrollment.unit.college` (via enrollment → unit relationship)
- **`CustomUser`** - `college = ForeignKey(College)`

## Query Patterns

### List Views (Always Filter by College):
```python
college = request.user.college
items = Model.objects.filter(college=college)
```

### Create Operations (Auto-Assign College):
```python
item = form.save(commit=False)
item.college = request.user.college
item.save()
```

### Detail/Update/Delete (Verify Ownership):
```python
item = Model.objects.get(pk=pk, college=request.user.college)
# Or use decorator: @ensure_college_access(Model)
```

### API Endpoints (Verify Access):
```python
college = get_college_from_slug(college_slug)
verify_user_college_access(request, college)
items = Model.objects.filter(college=college)
```

## Super Admin Access

Super Admins can access all colleges but should use:
- `/superadmin/` routes for system-wide management
- `/django-admin/` for Django admin interface

Super Admin views explicitly check `user.is_super_admin()` before allowing access.

## Security Checklist

✅ All API endpoints verify college access
✅ All views filter by `request.user.college`
✅ All create operations auto-assign user's college
✅ All detail/edit/delete operations verify object ownership
✅ URL-based college access verified via decorators
✅ Middleware provides college context
✅ Super admin access properly isolated
✅ Form querysets filtered by college

## Testing Isolation

To verify isolation works:

1. **Login as College A admin**
2. **Try to access College B's URL**: `/college-b-slug/dashboard/`
   - Should get `PermissionDenied` error

3. **Try to access College B's API**: `/api/college-b-slug/students/`
   - Should get `PermissionDenied` error

4. **Try to access College B's student detail**: `/students/123/` (where 123 belongs to College B)
   - Should get `404` or `PermissionDenied` error

5. **Verify list views only show own college data**
   - Students list should only show College A students
   - Courses list should only show College A courses

## Notes

- All college-specific URLs use `college_slug` parameter
- College slug is generated from college name using `slugify()`
- Users are automatically associated with a college during registration
- Super admins are the only users without a college association

