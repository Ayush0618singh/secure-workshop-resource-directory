# System Architecture
## Secure Workshop Resource Directory

## 1. Architecture Overview

The Secure Workshop Resource Directory follows a simple layered web application architecture.

It separates:

- User interface
- Application logic
- Validation and authentication
- Data storage
- Configuration
- Audit logging

This separation improves maintainability, security and clarity.

---

## 2. High-Level Architecture

```text
                         ┌─────────────────────────────┐
                         │        NORMAL USER          │
                         │                             │
                         │ Browse / Search / Filter    │
                         │ View Details / Summary      │
                         │ Export Filtered CSV         │
                         └──────────────┬──────────────┘
                                        │
                                        │ HTTP Request
                                        ▼
┌───────────────────────────────────────────────────────────────────┐
│                      FLASK WEB APPLICATION                        │
│                                                                   │
│                           app.py                                  │
│                                                                   │
│  Public Routes                         Administrator Routes        │
│  ─────────────                         ────────────────────        │
│  /                                     /admin/login                │
│  /resource/<id>                        /admin                      │
│  /summary                              /admin/resource/new         │
│  /export.csv                           /edit                       │
│                                        /delete                     │
│                                        /forgot-password            │
└───────────────┬─────────────────┬──────────────────┬───────────────┘
                │                 │                  │
                │                 │                  │
                ▼                 ▼                  ▼
      ┌────────────────┐ ┌─────────────────┐ ┌──────────────────┐
      │ validators.py  │ │    auth.py      │ │   Templates      │
      │                │ │                 │ │                  │
      │ Required fields│ │ Admin password  │ │ HTML / Jinja     │
      │ Allowed values │ │ verification    │ │ Safe escaping    │
      │ URL validation │ │ Password reset  │ │ UI rendering     │
      │ Length checks  │ │ Password hash   │ │                  │
      └───────┬────────┘ └────────┬────────┘ └──────────────────┘
              │                   │
              │                   │
              ▼                   ▼
      ┌────────────────┐   ┌──────────────────────┐
      │   storage.py   │   │ data/admin_auth.json│
      │                │   │                      │
      │ Load resources │   │ Local password hash  │
      │ Create         │   │ Not committed to Git │
      │ Update         │   └──────────────────────┘
      │ Delete         │
      └───────┬────────┘
              │
              ▼
      ┌──────────────────────┐
      │ data/resources.json  │
      │                      │
      │ Workshop resources   │
      │ Session information  │
      │ URLs & prerequisites │
      │ Review status        │
      └──────────────────────┘


              FLASK APPLICATION
                     │
                     ├───────────────────────────┐
                     │                           │
                     ▼                           ▼
          ┌────────────────────┐      ┌──────────────────────┐
          │   logs/audit.log   │      │        .env          │
          │                    │      │                      │
          │ CREATE             │      │ Secret key           │
          │ UPDATE             │      │ Admin username       │
          │ DELETE             │      │ Initial password     │
          │ PASSWORD_RESET     │      │ Recovery code        │
          │ Timestamp          │      │ Environment mode     │
          └────────────────────┘      └──────────────────────┘
```

---

## 3. User Flow

```text
Normal User
    |
    v
Open Directory
    |
    +---- Search Resources
    |
    +---- Apply Filters
    |
    +---- View Resource Details
    |
    +---- View Session Summary
    |
    +---- Export Filtered CSV
```

Normal users do not require authentication.

They have read-only access to public workshop resources.

---

## 4. Administrator Flow

```text
Administrator
      |
      v
Admin Login
      |
      v
Credential Verification
      |
      v
Protected Admin Dashboard
      |
      +---- Create Resource
      |
      +---- Edit Resource
      |
      +---- Delete Resource
      |
      +---- Change Review Status
      |
      +---- Logout
```

Administrator resource-management operations are protected by a session-based role check.

---

## 5. Password Recovery Flow

```text
Forgot Password
      |
      v
Enter Admin Username
      |
      v
Enter Local Recovery Code
      |
      v
Validate Recovery Information
      |
      v
Validate New Password Strength
      |
      v
Generate Secure Password Hash
      |
      v
Store Hash Locally
      |
      v
Administrator Can Login
With New Password
```

Passwords are not intentionally written to audit logs.

---

## 6. Resource Creation Flow

```text
Administrator Form
      |
      v
CSRF Validation
      |
      v
Server-Side Validation
      |
      +---- Required Fields
      +---- Day Validation
      +---- Resource Type
      +---- Length Limits
      +---- HTTP/HTTPS URL
      +---- Review Status
      |
      v
Valid?
  /       \
No         Yes
|           |
v           v
Show       storage.py
Errors        |
              v
       resources.json
              |
              v
         Audit Log
              |
              v
      Admin Dashboard
```

---

## 7. Main Security Boundaries

### Public User to Flask Application

All user-controlled input is considered untrusted.

Search parameters and administrative form input are handled by application logic rather than trusted automatically.

### Administrator Area

Create, update and delete operations require an authenticated administrator session.

### Flask to Resource Storage

Only validated resource records are written to `resources.json`.

### Flask to External Resources

The application stores trusted HTTP/HTTPS resource URLs but does not automatically fetch arbitrary URLs.

### Source Code to Configuration

Sensitive local configuration is kept outside source code using `.env`.

---

## 8. Security Controls

The architecture implements:

1. Server-side input validation
2. HTTP/HTTPS URL validation
3. Administrator-only editing workflow
4. Session-based access control
5. CSRF protection
6. Audit logging
7. Configuration separation
8. Password hashing for locally reset passwords
9. Safe Jinja template escaping
10. Generic error handling
11. Field-length restrictions
12. No automatic arbitrary URL fetching

---

## 9. Data Storage

### Resource Data

Stored in:

```text
data/resources.json
```

Contains non-sensitive workshop resource information.

### Local Administrator Password Hash

Stored in:

```text
data/admin_auth.json
```

This file is generated locally after authentication initialization or password reset and is excluded from Git.

### Audit Log

Stored in:

```text
logs/audit.log
```

Records administrative actions without intentionally storing passwords.

---

## 10. Architecture Conclusion

The project uses a lightweight layered architecture appropriate for a workshop prototype.

The public resource directory is separated from protected administrator functions, while validation, configuration management, storage and audit logging are handled through dedicated components.