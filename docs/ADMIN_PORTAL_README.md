# Admin Portal Front-End Documentation

## Overview

This document describes the Admin Portal front-end implementation for the SmartCampus College Management System. The portal includes a modern, responsive Admin Login Page and Admin Dashboard Page.

## Files Created

### Templates
- `templates/admin/login.html` - Admin login page
- `templates/admin/dashboard.html` - Admin dashboard page

### Static Files
- `static/css/admin/admin.css` - Complete styling for admin portal
- `static/js/admin/admin.js` - JavaScript functionality and API integration

### Backend Integration
- Added views in `education/views.py`:
  - `admin_login_page()` - Handles login page rendering and authentication
  - `admin_dashboard_page()` - Renders dashboard page
- Added URL routes in `education/urls.py`:
  - `/admin/login/` - Admin login page
  - `/admin/dashboard/` - Admin dashboard page

## Features

### Admin Login Page

1. **Modern Design**
   - Clean, professional interface
   - Gradient background
   - Card-based layout with smooth animations
   - Responsive design for all devices

2. **Form Features**
   - Username/Email input field
   - Password input with show/hide toggle
   - "Remember me" checkbox
   - Forgot password link (fully implemented)
   - Loading state during authentication
   - Error message display

3. **Functionality**
   - Form validation
   - Password visibility toggle
   - Token storage in localStorage
   - Automatic redirect to dashboard on success
   - Error handling and display

### Admin Dashboard Page

1. **Top Navbar**
   - College logo/name display
   - Mobile-responsive hamburger menu
   - Notifications dropdown with badge counter
   - Profile dropdown with:
     - Profile link
     - Settings link
     - Logout button

2. **Sidebar Navigation**
   - Collapsible on mobile devices
   - Active page highlighting
   - Icon-based navigation
   - Menu items:
     - Dashboard
     - Students
     - Departments
     - Courses
     - Units
     - Lecturers
     - Exams & Results
     - Fees & Finance
     - Announcements
     - Timetable
     - Settings
     - Logout

3. **Main Content Area**
   - **Overview Cards** (5 cards):
     - Total Students
     - Total Departments
     - Total Courses
     - Total Lecturers
     - Active Units
     - Each card shows:
       - Icon with gradient background
       - Current value
       - Change indicator (positive/negative/neutral)

   - **Recent Announcements Section**
     - List of recent announcements
     - Icon indicators
     - Timestamps
     - "View All" link

   - **System Activity Section**
     - Recent system activities
     - Color-coded activity types
     - Timestamps
     - "View Report" link

4. **Responsive Design**
   - Mobile-first approach
   - Sidebar collapses on mobile
   - Touch-friendly interface
   - Adaptive grid layouts

## JavaScript Functionality

### Authentication
- Token management (localStorage)
- User data storage
- Authentication check on dashboard load
- Automatic redirect to login if not authenticated

### API Integration
- `apiCall()` function for making authenticated API requests
- Placeholder API endpoints ready for backend integration
- Error handling and user feedback

### UI Interactions
- Mobile menu toggle
- Dropdown menus (notifications, profile)
- Navigation highlighting
- Loading states
- Error/success message display

### Dashboard Data Loading
- Overview statistics (placeholder API calls)
- Announcements loading
- System activity loading
- Number formatting utilities

## API Endpoints (Placeholders)

The following API endpoints are referenced in the code and should be implemented in the backend:

```
GET  /api/admin/dashboard/stats      - Get overview statistics
GET  /api/admin/announcements/recent - Get recent announcements
GET  /api/admin/activity/recent      - Get recent system activity
GET  /api/admin/user/profile          - Get current user profile
POST /api/admin/logout                - Logout user
```

## Usage

### Accessing the Admin Portal

1. **Login Page**: Navigate to `/admin/login/`
2. **Dashboard**: Navigate to `/admin/dashboard/` (requires authentication)

### Authentication Flow

1. User enters credentials on login page
2. Form submits to Django backend (`/admin/login/`)
3. Django authenticates user and creates session
4. JavaScript stores token in localStorage (for API calls)
5. User is redirected to dashboard
6. Dashboard checks for token and loads user data

### Logout Flow

1. User clicks logout button (navbar or sidebar)
2. JavaScript clears localStorage (token and user data)
3. User is redirected to login page
4. Django session is cleared on next request

## Customization

### Styling
All styles are in `static/css/admin/admin.css`. Key CSS variables can be modified:

```css
:root {
    --primary-color: #2563eb;
    --primary-dark: #1e40af;
    --success-color: #10b981;
    --danger-color: #ef4444;
    /* ... more variables */
}
```

### API Configuration
Update the API base URL in `static/js/admin/admin.js`:

```javascript
const API_BASE_URL = '/api/admin'; // Change to your API base URL
```

### Adding New Pages
1. Add navigation link in sidebar (`dashboard.html`)
2. Create corresponding view in `education/views.py`
3. Add URL route in `education/urls.py`
4. Update JavaScript navigation handler if needed

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Notes

- The portal uses Django's session-based authentication
- Token storage in localStorage is for future API integration
- All API calls are placeholders and need backend implementation
- The design is fully responsive and mobile-friendly
- All icons use Font Awesome 6.0

## Password Reset Feature

### User Password Reset (Self-Service)

Users can reset their own passwords through the "Forgot Password?" link on the login page:

1. **Request Reset**: User enters their email or phone number used during registration
   - For directors: Uses email/phone from college registration
   - For other users: Uses email/phone from their user account
2. **Verify Code**: A 6-digit code is sent to the email or phone
   - Code expires in 15 minutes
   - Code can be verified once
3. **Set New Password**: After verification, user sets a new password
   - Password must be at least 8 characters
   - Password confirmation required

### Admin Password Reset (Director/Principal)

Directors and Principals can reset passwords for other users in their college:

- **Access**: Available through admin interface
- **Permissions**:
  - Directors can reset passwords for all users in their college
  - Principals can reset passwords for users in their college (except directors)
  - Directors can reset their own passwords via email/phone only

### Implementation Details

- **Models**: `PasswordResetCode` model stores reset codes with expiration
- **Views**: 
  - `password_reset_request` - Request reset code
  - `password_reset_verify` - Verify code
  - `password_reset_confirm` - Set new password
  - `admin_password_reset` - Admin-initiated password reset
- **Forms**: 
  - `PasswordResetRequestForm` - Request form
  - `PasswordResetVerifyForm` - Code verification
  - `PasswordResetForm` - Password reset
- **Templates**: Located in `templates/admin/`
  - `password_reset_request.html`
  - `password_reset_verify.html`
  - `password_reset_confirm.html`
  - `admin_password_reset.html`

### Email/SMS Integration

- **Email**: Uses Django's `send_mail` function (configure SMTP in settings)
- **SMS**: Placeholder implementation - integrate with SMS service (Twilio, AWS SNS, etc.)

## Future Enhancements

- Implement actual API endpoints
- Add JWT token-based authentication
- Real-time notifications
- Data visualization charts
- Export functionality
- Advanced filtering and search
- Dark mode support
- Complete SMS integration for password reset codes

