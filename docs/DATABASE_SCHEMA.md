# Database Schema Documentation

This document describes the complete database schema for the SmartCampus Multi-College Education Management System.

## Entity Relationship Overview

```
Colleges (1) ──< (N) Users
Colleges (1) ──< (N) Students
Colleges (1) ──< (N) CollegeCourses
Colleges (1) ──< (N) CollegeUnits

GlobalCourses (1) ──< (N) GlobalCourseUnits >── (N) GlobalUnits
GlobalCourses (1) ──< (N) CollegeCourses (optional link)

CollegeCourses (1) ──< (N) Students
CollegeCourses (1) ──< (N) CollegeCourseUnits >── (N) CollegeUnits

CollegeUnits (1) ──< (N) Enrollments
CollegeUnits (N) >── (1) Users (assigned_lecturer)

Students (1) ──< (N) Enrollments
Enrollments (1) ──< (1) Results
Results (N) >── (1) Users (entered_by)
```

## Tables

### 1. colleges
Stores college/institution information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(200) | NOT NULL | College name |
| address | TEXT | NOT NULL | Physical address |
| county | VARCHAR(100) | NOT NULL | County location |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Contact email |
| phone | VARCHAR(20) | NOT NULL | Contact phone |
| principal_name | VARCHAR(100) | NOT NULL | Principal's name |
| registration_status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Status: pending/active/inactive |
| created_at | DATETIME | NOT NULL | Registration timestamp |
| updated_at | DATETIME | NOT NULL | Last update timestamp |

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (email)
- INDEX (registration_status)

---

### 2. users
Custom user model extending Django's AbstractUser.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | User ID |
| username | VARCHAR(150) | UNIQUE, NOT NULL | Username |
| email | VARCHAR(255) | UNIQUE | Email address |
| password | VARCHAR(128) | NOT NULL | Hashed password |
| first_name | VARCHAR(150) | | First name |
| last_name | VARCHAR(150) | | Last name |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'lecturer' | Role: super_admin/college_admin/lecturer |
| college_id | INT | FOREIGN KEY, NULL | Associated college |
| phone | VARCHAR(20) | | Phone number |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| is_staff | BOOLEAN | DEFAULT FALSE | Staff status |
| is_superuser | BOOLEAN | DEFAULT FALSE | Superuser status |
| date_joined | DATETIME | NOT NULL | Registration date |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Update timestamp |

**Foreign Keys:**
- college_id → colleges(id) ON DELETE CASCADE

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (username)
- UNIQUE (email)
- INDEX (college_id)
- INDEX (role)

---

### 3. global_courses
Global course templates that colleges can use.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(200) | NOT NULL | Course name |
| level | VARCHAR(20) | NOT NULL | Level: certificate/diploma/higher_diploma |
| category | VARCHAR(100) | NOT NULL | Course category |
| created_at | DATETIME | NOT NULL | Creation timestamp |

**Indexes:**
- PRIMARY KEY (id)
- INDEX (level)

---

### 4. global_units
Global unit templates.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(200) | NOT NULL | Unit name |
| code | VARCHAR(50) | UNIQUE, NOT NULL | Unit code |
| created_at | DATETIME | NOT NULL | Creation timestamp |

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (code)

---

### 5. global_course_units
Mapping of global courses to global units.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| course_id | INT | FOREIGN KEY, NOT NULL | Global course ID |
| unit_id | INT | FOREIGN KEY, NOT NULL | Global unit ID |
| semester | INT | NOT NULL | Semester (1-4) |

**Foreign Keys:**
- course_id → global_courses(id) ON DELETE CASCADE
- unit_id → global_units(id) ON DELETE CASCADE

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (course_id, unit_id)
- INDEX (semester)

---

### 6. college_courses
College-specific courses.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| college_id | INT | FOREIGN KEY, NOT NULL | College ID |
| global_course_id | INT | FOREIGN KEY, NULL | Optional link to global course |
| name | VARCHAR(200) | NOT NULL | Course name |
| duration_years | INT | NOT NULL | Duration in years (1-5) |
| admission_requirements | TEXT | | Admission requirements |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Update timestamp |

**Foreign Keys:**
- college_id → colleges(id) ON DELETE CASCADE
- global_course_id → global_courses(id) ON DELETE SET NULL

**Indexes:**
- PRIMARY KEY (id)
- INDEX (college_id)
- INDEX (global_course_id)

---

### 7. college_units
College-specific units.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| college_id | INT | FOREIGN KEY, NOT NULL | College ID |
| global_unit_id | INT | FOREIGN KEY, NULL | Optional link to global unit |
| name | VARCHAR(200) | NOT NULL | Unit name |
| code | VARCHAR(50) | NOT NULL | Unit code |
| semester | INT | NOT NULL | Semester (1-4) |
| assigned_lecturer_id | INT | FOREIGN KEY, NULL | Assigned lecturer |
| created_at | DATETIME | NOT NULL | Creation timestamp |
| updated_at | DATETIME | NOT NULL | Update timestamp |

**Foreign Keys:**
- college_id → colleges(id) ON DELETE CASCADE
- global_unit_id → global_units(id) ON DELETE SET NULL
- assigned_lecturer_id → users(id) ON DELETE SET NULL

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (college_id, code)
- INDEX (college_id)
- INDEX (assigned_lecturer_id)
- INDEX (semester)

---

### 8. college_course_units
Mapping of college courses to college units.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| course_id | INT | FOREIGN KEY, NOT NULL | College course ID |
| unit_id | INT | FOREIGN KEY, NOT NULL | College unit ID |
| semester | INT | NOT NULL | Semester |
| college_id | INT | FOREIGN KEY, NOT NULL | College ID |

**Foreign Keys:**
- course_id → college_courses(id) ON DELETE CASCADE
- unit_id → college_units(id) ON DELETE CASCADE
- college_id → colleges(id) ON DELETE CASCADE

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (course_id, unit_id)
- INDEX (college_id)

---

### 9. students
Student records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| college_id | INT | FOREIGN KEY, NOT NULL | College ID |
| admission_number | VARCHAR(50) | NOT NULL | Admission number |
| full_name | VARCHAR(200) | NOT NULL | Full name |
| course_id | INT | FOREIGN KEY, NULL | Enrolled course |
| year_of_study | INT | NOT NULL | Year (1-5) |
| gender | VARCHAR(1) | NOT NULL | Gender: M/F/O |
| date_of_birth | DATE | NOT NULL | Date of birth |
| email | VARCHAR(255) | | Email address |
| phone | VARCHAR(20) | | Phone number |
| created_at | DATETIME | NOT NULL | Registration timestamp |
| updated_at | DATETIME | NOT NULL | Update timestamp |

**Foreign Keys:**
- college_id → colleges(id) ON DELETE CASCADE
- course_id → college_courses(id) ON DELETE SET NULL

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (college_id, admission_number)
- INDEX (college_id)
- INDEX (course_id)

---

### 10. enrollments
Student enrollments in units.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| student_id | INT | FOREIGN KEY, NOT NULL | Student ID |
| unit_id | INT | FOREIGN KEY, NOT NULL | Unit ID |
| academic_year | VARCHAR(20) | NOT NULL | Academic year (e.g., 2024/2025) |
| semester | INT | NOT NULL | Semester (1-4) |
| enrolled_at | DATETIME | NOT NULL | Enrollment timestamp |

**Foreign Keys:**
- student_id → students(id) ON DELETE CASCADE
- unit_id → college_units(id) ON DELETE CASCADE

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (student_id, unit_id, academic_year, semester)
- INDEX (student_id)
- INDEX (unit_id)
- INDEX (academic_year)

---

### 11. results
Student results/marks.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| enrollment_id | INT | FOREIGN KEY, UNIQUE, NOT NULL | Enrollment ID |
| cat_marks | DECIMAL(5,2) | NULL | CAT marks (0-100) |
| exam_marks | DECIMAL(5,2) | NULL | Exam marks (0-100) |
| total | DECIMAL(5,2) | NULL | Total marks (auto-calculated) |
| entered_by_id | INT | FOREIGN KEY, NULL | User who entered results |
| entered_at | DATETIME | NOT NULL | Entry timestamp |
| updated_at | DATETIME | NOT NULL | Update timestamp |

**Foreign Keys:**
- enrollment_id → enrollments(id) ON DELETE CASCADE
- entered_by_id → users(id) ON DELETE SET NULL

**Indexes:**
- PRIMARY KEY (id)
- UNIQUE (enrollment_id)
- INDEX (entered_by_id)

---

## Data Isolation Strategy

The system implements multi-tenant data isolation through:

1. **College Foreign Key**: All college-specific tables include a `college_id` foreign key
2. **Middleware Filtering**: The `CollegeAccessMiddleware` automatically filters queries by college
3. **View-Level Decorators**: Access control decorators ensure users can only access their college's data
4. **Model-Level Constraints**: Unique constraints include `college_id` to prevent cross-college conflicts

## Relationships Summary

- **One-to-Many:**
  - College → Users
  - College → Students
  - College → Courses
  - College → Units
  - Course → Students
  - Unit → Enrollments
  - Student → Enrollments

- **Many-to-Many:**
  - Global Courses ↔ Global Units (via global_course_units)
  - College Courses ↔ College Units (via college_course_units)

- **One-to-One:**
  - Enrollment → Result

## Notes

- All timestamps use DATETIME type
- Decimal fields use DECIMAL(5,2) for marks (supports up to 999.99)
- Foreign keys use CASCADE delete for parent-child relationships
- Foreign keys use SET NULL for optional template links
- Unique constraints prevent duplicate entries
- Indexes are created on foreign keys and frequently queried fields

