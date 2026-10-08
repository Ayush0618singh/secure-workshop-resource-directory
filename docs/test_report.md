# Test Report
## Secure Workshop Resource Directory

## 1. Testing Objective

The application was tested to verify:

- Resource listing
- Search and filtering
- Resource details
- Administrator access control
- Input validation
- URL validation
- Resource creation
- Resource modification
- Resource deletion
- Audit logging
- CSV export
- Session-wise summary
- Safe handling of malicious-looking input

---

## 2. Functional and Security Test Cases

| Test ID | Feature | Input / Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-01 | Home Page | Open `/` | Directory should load | Directory loaded successfully | PASS |
| TC-02 | Search | Search `Flask` | Matching resource should appear | Matching Flask resource displayed | PASS |
| TC-03 | Day Filter | Select Day 4 | Only Day 4 records should appear | Day 4 records displayed | PASS |
| TC-04 | Resource Detail | Click View Details | Full resource details should open | Details page opened | PASS |
| TC-05 | Admin Protection | Open `/admin` without login | Redirect to login | Redirected to admin login | PASS |
| TC-06 | Admin Login | Valid local credentials | Dashboard should open | Admin dashboard opened | PASS |
| TC-07 | Required Fields | Submit empty form | Validation errors should appear | Required-field errors displayed | PASS |
| TC-08 | Unsafe URL | `javascript:alert(1)` | URL should be rejected | URL rejected | PASS |
| TC-09 | HTML-like Input | `<script>alert('test')</script>` | Text must not execute | Displayed safely as text | PASS |
| TC-10 | Create Resource | Valid resource data | Resource should be created | Resource created successfully | PASS |
| TC-11 | Edit Resource | Modify existing record | Changes should save | Changes saved successfully | PASS |
| TC-12 | Delete Resource | Delete confirmed record | Resource should be removed | Resource removed | PASS |
| TC-13 | Audit Logging | Create/Edit/Delete | Actions should be logged | Actions recorded in audit log | PASS |
| TC-14 | CSV Export | Export filtered directory | CSV should download | CSV downloaded successfully | PASS |
| TC-15 | Summary | Open Summary page | Session-wise summary should display | Summary displayed | PASS |
| TC-16 | Invalid Resource | Open unknown resource ID | 404 page should appear | Custom 404 page displayed | PASS |

---

## 3. Malicious-Looking Input Test

### Test Input

`<script>alert('test')</script>`

### Expected Result

The value should be treated as text and must not execute JavaScript.

### Actual Result

The application displayed the submitted string as normal text.

No JavaScript alert was executed.

### Result

PASS

---

## 4. Unsafe URL Test

### Test Input

`javascript:alert(1)`

### Expected Result

The application should reject the URL because it is not an HTTP or HTTPS URL.

### Actual Result

The application displayed:

`Only http:// and https:// URLs are allowed.`

The resource was not saved.

### Result

PASS

---

## 5. Automated Testing

Automated tests are stored in:

`tests/test_core.py`

Command:

```bash
python -m unittest discover -s tests -v