import unittest

from app import app
from validators import validate_resource, validate_url


class SecureWorkshopDirectoryTests(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_summary_page_loads(self):
        response = self.client.get("/summary")
        self.assertEqual(response.status_code, 200)

    def test_admin_page_is_protected(self):
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.location)

    def test_valid_https_url(self):
        valid, error = validate_url(
            "https://docs.python.org/3/"
        )

        self.assertTrue(valid)
        self.assertEqual(error, "")

    def test_javascript_url_is_rejected(self):
        valid, error = validate_url(
            "javascript:alert(1)"
        )

        self.assertFalse(valid)
        self.assertIn(
            "http:// and https://",
            error
        )

    def test_invalid_day_is_rejected(self):
        data = {
            "session_title": "Security Testing",
            "day": "10",
            "resource_type": "Documentation",
            "description": "Test resource",
            "url": "https://example.com/",
            "prerequisite": "Basic Python",
            "review_status": "Pending",
        }

        cleaned, errors = validate_resource(data)

        self.assertIn("day", errors)

    def test_missing_required_fields_are_rejected(self):
        data = {
            "session_title": "",
            "day": "",
            "resource_type": "",
            "description": "",
            "url": "",
            "prerequisite": "",
            "review_status": "Pending",
        }

        cleaned, errors = validate_resource(data)

        self.assertIn("session_title", errors)
        self.assertIn("day", errors)
        self.assertIn("resource_type", errors)
        self.assertIn("description", errors)
        self.assertIn("url", errors)
        self.assertIn("prerequisite", errors)


if __name__ == "__main__":
    unittest.main()