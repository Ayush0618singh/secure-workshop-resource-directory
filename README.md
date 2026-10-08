# Secure Workshop Resource Directory

A secure and searchable workshop learning-resource management application developed using Python and Flask.

The project allows workshop participants to browse trusted learning resources, search and filter content, review prerequisites and explore session-wise information.

A protected administrator workspace is provided for creating, updating, reviewing and deleting workshop resource records.

---

## Project Context

This project was developed as:

**Mini-Project B — Secure Workshop Resource Directory**

for the **Secure Application Development** workshop.

The project demonstrates secure application-development concepts including:

- Web application architecture
- Search and filtering
- Server-side input validation
- Safe URL handling
- Administrator access control
- Audit logging
- Configuration hygiene
- Security testing
- Threat modelling
- SSDLC practices

---

## Problem Statement

Workshop participants require a centralized and searchable directory where they can easily find:

- Workshop sessions
- Learning resources
- Resource types
- Descriptions
- Trusted URLs
- Prerequisites
- Review status

The application should allow participants to access resources easily while restricting modification operations to an administrator.

---

## Project Objectives

The project aims to:

- Build a searchable application with clear navigation
- Validate submitted resource records
- Keep configuration separate from application source code
- Provide protected administrator resource management
- Record administrative create/update/delete activity
- Generate session-wise resource summaries
- Export filtered resource data
- Test malicious-looking but harmless input
- Document threats, security controls and setup instructions

---

# Core Features

## Public Resource Directory

Participants can:

- Browse all workshop resources
- Search resources
- Filter resources by workshop day
- Filter by resource type
- Filter by review status
- View full resource details
- View prerequisites
- View session-wise summaries
- Export filtered resources as CSV

Normal users do not require an account or login.

---

## Administrator Workspace

The protected administrator area supports:

- Administrator login
- Add resource
- Edit resource
- Delete resource
- Change resource review status
- View resource statistics
- Audit administrative operations
- Logout

---

## Password Recovery

A local password-recovery workflow is also included as an additional project feature.

The administrator can:

- Verify the configured username
- Verify a local recovery code
- Create a new password
- Confirm the password
- Store the new password as a secure password hash

The recovery feature is intended only for the local workshop prototype.

---

## Search and Filtering

Resources can be filtered using:

- Search text
- Workshop day
- Resource type
- Review status

The currently filtered directory can also be exported to CSV.

---

## Session-wise Resource Summary

The application generates a summary showing:

- Session title
- Workshop day
- Resource types
- Total number of resources
- Number of reviewed resources

---

## Resource Review Extension

The optional resource review-status feature has been implemented.

Supported statuses:

- Pending
- Reviewed
- Needs Review

---

# Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Flask | Web application framework |
| HTML | Page structure |
| CSS | Responsive and professional UI |
| JavaScript | Client-side UI interactions |
| Jinja | Server-side HTML templates |
| JSON | Resource data storage |
| Python Logging | Administrative audit logging |
| python-dotenv | Environment configuration |
| Werkzeug Security | Password hashing and verification |

---

# System Architecture

The project follows a lightweight layered architecture:

```text
Users
  |
  v
Flask Web Application
  |
  +---- Templates / UI
  |
  +---- Input Validation
  |
  +---- Admin Authentication
  |
  +---- Resource Storage
  |
  +---- Audit Logging
  |
  +---- Environment Configuration
```

Detailed architecture documentation:

```text
docs/architecture.md
```

---

# Project Structure

```text
Secure Workshop Resource Directory/
│
├── app.py
├── auth.py
├── storage.py
├── validators.py
│
├── requirements.txt
├── README.md
├── .env
├── .env.example
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── resource_detail.html
│   ├── admin_login.html
│   ├── forgot_password.html
│   ├── admin_dashboard.html
│   ├── resource_form.html
│   ├── summary.html
│   ├── 400.html
│   ├── 404.html
│   └── 500.html
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── premium.css
│   │   └── login.css
│   │
│   └── js/
│       └── app.js
│
├── data/
│   ├── resources.json
│   └── admin_auth.json
│
├── logs/
│   └── audit.log
│
├── tests/
│   └── test_core.py
│
├── docs/
│   ├── architecture.md
│   ├── threat_model.md
│   └── test_report.md
│
└── screenshots/
```

`admin_auth.json`, `.env` and local log files are not intended for source-control publication.

---

# Resource Data Model

Each workshop resource contains:

```text
Resource ID
Session Title
Workshop Day
Resource Type
Description
URL
Prerequisite
Review Status
```

Example:

```json
{
  "id": "RES-006",
  "session_title": "Flask Application Development",
  "day": 4,
  "resource_type": "Documentation",
  "description": "Official Flask learning resource.",
  "url": "https://flask.palletsprojects.com/",
  "prerequisite": "Python and basic web concepts",
  "review_status": "Reviewed"
}
```

---

# Security Controls

The application implements multiple security controls.

### Server-Side Input Validation

Resource data is validated before storage.

Validation includes:

- Required fields
- Allowed workshop day
- Allowed resource type
- Allowed review status
- Maximum field lengths
- URL validation

### Safe URL Validation

Only:

```text
http://
https://
```

schemes are accepted.

Example rejected input:

```text
javascript:alert(1)
```

### Administrator Access Control

Create, edit and delete routes require an authenticated administrator session.

### CSRF Protection

State-changing forms use a session-generated CSRF token.

### Safe Template Output

Jinja template escaping prevents malicious-looking HTML strings from being intentionally rendered as executable markup.

Example test input:

```text
<script>alert('test')</script>
```

is displayed as text rather than executed.

### Audit Logging

Administrative actions are recorded in:

```text
logs/audit.log
```

Logged actions include:

```text
CREATE
UPDATE
DELETE
PASSWORD_RESET
```

Passwords are not intentionally written to audit logs.

### Configuration Separation

Local configuration is stored in:

```text
.env
```

Example configuration is provided in:

```text
.env.example
```

`.env` is excluded from Git.

### Password Hashing

When the local password-recovery workflow is used, the new administrator password is stored as a password hash rather than plain text.

---

# Installation and Setup

## Requirements

Recommended:

```text
Python 3.10+
VS Code
Modern web browser
```

---

## 1. Open Project Folder

Extract the project ZIP or clone the repository.

Open:

```text
Secure Workshop Resource Directory
```

in VS Code.

---

## 2. Create Virtual Environment

Windows PowerShell:

```powershell
py -m venv .venv
```

---

## 3. Activate Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 4. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## 5. Create Local Configuration

Copy:

```text
.env.example
```

and create:

```text
.env
```

Example:

```env
FLASK_SECRET_KEY=replace-with-a-local-secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-a-local-password
ADMIN_RECOVERY_CODE=replace-with-a-local-recovery-code
APP_ENV=production
```

Use only local demonstration credentials.

Do not use real passwords or sensitive institutional credentials.

---

## 6. Run the Application

```powershell
python app.py
```

Expected local server:

```text
http://127.0.0.1:5000
```

Open the URL in a browser.

---

# Application Routes

| Route | Purpose |
|---|---|
| `/` | Resource directory |
| `/resource/<id>` | Resource details |
| `/summary` | Session summary |
| `/export.csv` | CSV export |
| `/admin/login` | Administrator login |
| `/admin/forgot-password` | Local password recovery |
| `/admin` | Admin dashboard |
| `/admin/resource/new` | Create resource |

Editing and deletion routes are also available only to the authenticated administrator.

---

# Testing

Automated tests are located in:

```text
tests/test_core.py
```

Run:

```powershell
python -m unittest discover -s tests -v
```

A successful run should end with:

```text
OK
```

---

# Security Testing

The project was tested using normal, invalid and malicious-looking but harmless input.

Examples include:

```text
javascript:alert(1)
```

and:

```text
<script>alert('test')</script>
```

The first is rejected as an unsafe URL scheme.

The second is safely displayed as text rather than executed as JavaScript.

Detailed testing documentation:

```text
docs/test_report.md
```

---

# Threat Model

The project threat model documents:

- Assets
- Trust boundaries
- Threat scenarios
- Security controls
- Mitigations
- Known limitations

File:

```text
docs/threat_model.md
```

---

# Audit Log

Administrative activity is stored locally in:

```text
logs/audit.log
```

Example:

```text
CREATE
UPDATE
DELETE
PASSWORD_RESET
```

The application does not intentionally log administrator passwords.

---

# Screenshots

Project screenshots are stored in:

```text
screenshots/
```

Recommended demonstration screenshots include:

```text
01-home-page.png
02-search-and-filter.png
03-resource-details.png
04-session-summary.png
05-admin-login.png
06-admin-dashboard.png
07-add-resource-form.png
08-validation-error.png
09-malicious-input-test.png
10-url-validation-test.png
11-audit-log.png
12-automated-tests.png
```

---

# SSDLC Applied

The project follows basic Secure Software Development Life Cycle principles.

## Requirements

Identify participants, administrator actions and expected resource-management functionality.

## Design

Separate:

- Public interface
- Administrator interface
- Validation
- Authentication
- Storage
- Logging
- Configuration

## Threat Modelling

Identify threats such as:

- Unauthorized modification
- Unsafe URLs
- Malicious-looking input
- CSRF
- Configuration exposure
- Sensitive logging

## Secure Implementation

Apply:

- Validation
- Access control
- CSRF protection
- Safe templates
- Audit logging
- Configuration separation

## Verification

Test:

- Normal input
- Invalid input
- Boundary conditions
- Unauthorized access
- Malicious-looking input

## Operation

Document clean setup and safe local execution.

---

# Security and Ethics

The project uses synthetic workshop-resource information and trusted public learning URLs.

It does not require:

- Real student records
- Institutional credentials
- Sensitive personal information

The application does not automatically fetch arbitrary submitted URLs.

---

# Known Limitations

This project is an educational workshop prototype.

Current limitations include:

- JSON file-based persistence
- Simple local administrator authentication
- Local recovery-code mechanism
- No account lockout
- No rate limiting
- No email-based password recovery
- No production HTTPS configuration
- External URLs are not automatically checked for availability
- Not designed for storing sensitive institutional information

---

# Future Improvements

Possible future improvements include:

- Relational database storage
- Multiple administrator accounts
- Role-based authorization
- Rate limiting
- Password-reset email workflow
- Resource link-health checking
- Advanced audit-log viewer
- Deployment with HTTPS
- Additional automated security tests

---

# Demonstration Flow

For a project demonstration:

1. Open the public resource directory.
2. Search for a resource.
3. Apply day/type/status filters.
4. Open a resource-detail page.
5. Show the session summary.
6. Export filtered resources.
7. Open administrator login.
8. Login as administrator.
9. Create a resource.
10. Edit the resource.
11. Show validation using an unsafe URL.
12. Delete the test resource.
13. Show the audit log.
14. Show automated test results.
15. Explain the architecture and threat model.

---

# Conclusion

The Secure Workshop Resource Directory demonstrates how a small web application can combine usability with secure application-development practices.

The project implements searchable workshop-resource management, validation, administrator access control, configuration separation, audit logging, security testing, threat modelling and clear documentation in a lightweight Flask application.