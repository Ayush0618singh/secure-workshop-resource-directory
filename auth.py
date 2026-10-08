import json
import os
import tempfile
from pathlib import Path

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)


BASE_DIR = Path(__file__).resolve().parent
AUTH_FILE = BASE_DIR / "data" / "admin_auth.json"


def _write_password_hash(password):
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "password_hash": generate_password_hash(password)
    }

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=AUTH_FILE.parent,
            prefix="admin_auth_",
            suffix=".tmp",
        ) as temp_file:

            json.dump(
                payload,
                temp_file,
                indent=2,
            )

            temp_path = Path(temp_file.name)

        os.replace(temp_path, AUTH_FILE)

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)


def ensure_admin_auth(default_password):
    if AUTH_FILE.exists():
        return

    if not default_password:
        raise RuntimeError(
            "ADMIN_PASSWORD is not configured."
        )

    _write_password_hash(default_password)


def verify_admin_password(password, default_password):
    ensure_admin_auth(default_password)

    try:
        with AUTH_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        password_hash = data.get(
            "password_hash",
            "",
        )

        if not password_hash:
            return False

        return check_password_hash(
            password_hash,
            password,
        )

    except (
        OSError,
        json.JSONDecodeError,
        ValueError,
    ):
        return False


def set_admin_password(new_password):
    _write_password_hash(new_password)


def validate_new_password(password):
    errors = []

    if len(password) < 8:
        errors.append(
            "Password must contain at least 8 characters."
        )

    if not any(char.isupper() for char in password):
        errors.append(
            "Password must contain an uppercase letter."
        )

    if not any(char.islower() for char in password):
        errors.append(
            "Password must contain a lowercase letter."
        )

    if not any(char.isdigit() for char in password):
        errors.append(
            "Password must contain a number."
        )

    if not any(
        not char.isalnum()
        for char in password
    ):
        errors.append(
            "Password must contain a special character."
        )

    return errors