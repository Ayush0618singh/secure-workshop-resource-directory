from urllib.parse import urlparse


VALID_RESOURCE_TYPES = (
    "Documentation",
    "Video",
    "Article",
    "Repository",
    "PDF",
    "Tool",
    "Other",
)

VALID_REVIEW_STATUSES = (
    "Pending",
    "Reviewed",
    "Needs Review",
)


MAX_LENGTHS = {
    "session_title": 120,
    "resource_type": 40,
    "description": 1000,
    "url": 500,
    "prerequisite": 250,
    "review_status": 40,
}


def _clean(value):
    """Convert a value to a trimmed string safely."""
    return str(value or "").strip()


def validate_url(url):
    """
    Allow only normal HTTP/HTTPS URLs.

    The application stores trusted URLs but never automatically
    fetches or opens arbitrary URLs on the server.
    """
    url = _clean(url)

    if not url:
        return False, "URL is required."

    if len(url) > MAX_LENGTHS["url"]:
        return False, f"URL must be at most {MAX_LENGTHS['url']} characters."

    if any(character.isspace() for character in url):
        return False, "URL must not contain spaces."

    try:
        parsed = urlparse(url)
    except ValueError:
        return False, "Enter a valid URL."

    if parsed.scheme.lower() not in {"http", "https"}:
        return False, "Only http:// and https:// URLs are allowed."

    if not parsed.netloc:
        return False, "URL must include a valid host name."

    return True, ""


def validate_resource(form_data):
    """
    Validate and normalize a submitted workshop resource.
    """

    cleaned = {
        "session_title": _clean(form_data.get("session_title")),
        "day": _clean(form_data.get("day")),
        "resource_type": _clean(form_data.get("resource_type")),
        "description": _clean(form_data.get("description")),
        "url": _clean(form_data.get("url")),
        "prerequisite": _clean(form_data.get("prerequisite")),
        "review_status": _clean(form_data.get("review_status")) or "Pending",
    }

    errors = {}

    required_fields = {
        "session_title": "Session title",
        "day": "Day",
        "resource_type": "Resource type",
        "description": "Description",
        "url": "URL",
        "prerequisite": "Prerequisite",
    }

    # Required-field validation
    for field, label in required_fields.items():
        if not cleaned[field]:
            errors[field] = f"{label} is required."

    # Session title validation
    if (
        cleaned["session_title"]
        and len(cleaned["session_title"]) > MAX_LENGTHS["session_title"]
    ):
        errors["session_title"] = (
            f"Session title must be at most "
            f"{MAX_LENGTHS['session_title']} characters."
        )

    # Workshop runs from Day 1 to Day 5
    try:
        day_number = int(cleaned["day"])

        if day_number < 1 or day_number > 5:
            raise ValueError

        cleaned["day"] = day_number

    except (TypeError, ValueError):
        errors["day"] = "Day must be a number from 1 to 5."

    # Resource-type validation
    if (
        cleaned["resource_type"]
        and cleaned["resource_type"] not in VALID_RESOURCE_TYPES
    ):
        errors["resource_type"] = "Select a valid resource type."

    # Description length validation
    if (
        cleaned["description"]
        and len(cleaned["description"]) > MAX_LENGTHS["description"]
    ):
        errors["description"] = (
            f"Description must be at most "
            f"{MAX_LENGTHS['description']} characters."
        )

    # Prerequisite length validation
    if (
        cleaned["prerequisite"]
        and len(cleaned["prerequisite"]) > MAX_LENGTHS["prerequisite"]
    ):
        errors["prerequisite"] = (
            f"Prerequisite must be at most "
            f"{MAX_LENGTHS['prerequisite']} characters."
        )

    # Review-status validation
    if cleaned["review_status"] not in VALID_REVIEW_STATUSES:
        errors["review_status"] = "Select a valid review status."

    # URL validation
    if cleaned["url"]:
        is_valid, url_error = validate_url(cleaned["url"])

        if not is_valid:
            errors["url"] = url_error

    return cleaned, errors