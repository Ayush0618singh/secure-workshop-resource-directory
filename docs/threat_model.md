# Threat Model
## Secure Workshop Resource Directory

## 1. Project Overview

The Secure Workshop Resource Directory is a Flask-based web application developed for workshop participants.

It provides a searchable directory of workshop sessions, trusted learning resources and prerequisites.

Participants can browse, search, filter and view resources, while an administrator can create, update and delete resource records through a restricted administrative workflow.

---

## 2. Assets to Protect

The main assets are:

- Workshop resource records
- Administrator access
- Local configuration values
- Audit logs
- Resource URLs
- Application integrity

The project uses synthetic workshop data and does not require real student or institutional information.

---

## 3. Main Components

User Browser
        |
        v
Flask Web Application
        |
        +---- Input Validation
        |
        +---- Administrator Access Control
        |
        +---- Audit Logging
        |
        v
JSON Resource Dataset

Configuration values are stored separately in the local `.env` file.

---

## 4. Trust Boundaries

### Browser to Application

All submitted form data is considered untrusted and is validated by the Flask application before storage.

### Public Area to Administrator Area

Normal users can browse resources but cannot directly perform create, update or delete operations.

### Application to Data File

Only validated application data is written to the local resource dataset.

### External URLs

External resource URLs are stored as references only.

The application does not automatically fetch arbitrary URLs.

---

## 5. Threats and Mitigations

### Threat 1: Unauthorized Resource Modification

Risk:

A normal user may attempt to access administrator functionality.

Mitigation:

- Administrator login
- Session-based role check
- Protected administrator routes
- Create, update and delete operations restricted to administrators

---

### Threat 2: Unsafe URL Scheme

Risk:

A malicious-looking URL such as:

`javascript:alert(1)`

could be submitted.

Mitigation:

- Server-side URL validation
- Only HTTP and HTTPS schemes are accepted
- A valid host name is required
- Arbitrary URLs are not automatically fetched

---

### Threat 3: Malicious-Looking HTML Input

Risk:

A user may submit:

`<script>alert('test')</script>`

or similar HTML-like input.

Mitigation:

- Input validation
- Field-length restrictions
- Flask/Jinja automatic output escaping
- User input is displayed as text rather than intentionally executed as HTML or JavaScript

---

### Threat 4: Cross-Site Request Forgery

Risk:

An attacker may attempt to trigger administrator actions without authorization.

Mitigation:

- CSRF token generated for forms
- Token validation before state-changing actions
- POST requests are used for delete and logout operations

---

### Threat 5: Sensitive Information in Logs

Risk:

Passwords or sensitive information may accidentally be recorded.

Mitigation:

Audit logs contain only:

- Timestamp
- Action
- Administrator identifier
- Resource ID
- Resource title

Passwords are not written to the audit log.

---

### Threat 6: Configuration Exposure

Risk:

Administrator credentials or configuration values may be hard-coded in source code.

Mitigation:

- Local configuration is stored in `.env`
- `.env` is excluded using `.gitignore`
- `.env.example` contains only example configuration
- Real secrets are not committed to source control

---

## 6. Implemented Security Controls

1. Server-side input validation
2. URL scheme validation
3. Administrator-only editing workflow
4. Session-based access control
5. CSRF protection
6. Audit logging
7. Configuration separation
8. Safe template escaping
9. Field-length validation
10. Generic application error pages

---

## 7. Security Tests

The application was tested with normal and malicious-looking but harmless input.

Examples:

- Empty required fields
- Invalid workshop day
- Unsupported URL scheme
- `javascript:alert(1)`
- `<script>alert('test')</script>`
- Unauthorized administrator access
- Invalid administrator credentials

The malicious-looking HTML input was displayed as text and was not executed.

The unsafe JavaScript URL scheme was rejected.

---

## 8. Known Limitations

This project is an educational workshop prototype.

Current limitations include:

- Simple local administrator authentication
- JSON file-based storage
- No password recovery
- No rate limiting
- No account lockout
- Resource URLs are not automatically checked for availability
- HTTPS is not configured for localhost development
- The application is not intended to store sensitive institutional data

---

## 9. Security and Ethics

Only trusted and non-sensitive learning-resource URLs are used.

The application does not automatically fetch arbitrary URLs.

Synthetic data and local demonstration credentials are used during development and testing.