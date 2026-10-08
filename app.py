import csv
import io
import logging
import os
import secrets

from collections import defaultdict
from functools import wraps
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

from flask import (
    Flask,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from auth import (
    set_admin_password,
    validate_new_password,
    verify_admin_password,
)

from storage import (
    create_resource,
    delete_resource,
    get_resource,
    load_resources,
    update_resource,
)

from validators import (
    VALID_RESOURCE_TYPES,
    VALID_REVIEW_STATUSES,
    validate_resource,
)


# ---------------------------------------------------------
# Application configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY",
    secrets.token_hex(32),
)

app.config["ADMIN_USERNAME"] = os.getenv(
    "ADMIN_USERNAME",
    "admin",
)

app.config["ADMIN_PASSWORD"] = os.getenv(
    "ADMIN_PASSWORD",
    "",
)

app.config["ADMIN_RECOVERY_CODE"] = os.getenv(
    "ADMIN_RECOVERY_CODE",
    "",
)

app.config["APP_ENV"] = os.getenv(
    "APP_ENV",
    "production",
)


# ---------------------------------------------------------
# Audit logging
# ---------------------------------------------------------

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

audit_handler = RotatingFileHandler(
    LOG_DIR / "audit.log",
    maxBytes=500_000,
    backupCount=3,
    encoding="utf-8",
)

audit_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
)

audit_logger = logging.getLogger(
    "resource_audit"
)

audit_logger.setLevel(logging.INFO)
audit_logger.propagate = False

if not audit_logger.handlers:
    audit_logger.addHandler(
        audit_handler
    )


# ---------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------

def admin_required(view_function):

    @wraps(view_function)
    def wrapped(*args, **kwargs):

        if not session.get("is_admin"):

            flash(
                "Administrator access is required.",
                "warning",
            )

            return redirect(
                url_for(
                    "admin_login",
                    next=request.path,
                )
            )

        return view_function(
            *args,
            **kwargs,
        )

    return wrapped


# ---------------------------------------------------------
# CSRF
# ---------------------------------------------------------

def get_csrf_token():

    token = session.get(
        "_csrf_token"
    )

    if not token:
        token = secrets.token_urlsafe(32)

        session["_csrf_token"] = token

    return token


def validate_csrf():

    submitted = request.form.get(
        "_csrf_token",
        "",
    )

    expected = session.get(
        "_csrf_token",
        "",
    )

    if (
        not submitted
        or not expected
        or not secrets.compare_digest(
            submitted,
            expected,
        )
    ):
        abort(
            400,
            description=(
                "Invalid or missing form token."
            ),
        )


@app.context_processor
def inject_template_globals():

    return {
        "csrf_token": get_csrf_token,
        "resource_types": VALID_RESOURCE_TYPES,
        "review_statuses": VALID_REVIEW_STATUSES,
        "is_admin": bool(
            session.get("is_admin")
        ),
    }


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def _safe_day(resource):

    try:
        return int(
            resource.get("day", 99)
        )

    except (
        TypeError,
        ValueError,
    ):
        return 99


def _filter_resources(resources):

    query = request.args.get(
        "q",
        "",
    ).strip().lower()

    day = request.args.get(
        "day",
        "",
    ).strip()

    resource_type = request.args.get(
        "resource_type",
        "",
    ).strip()

    review_status = request.args.get(
        "review_status",
        "",
    ).strip()

    filtered_resources = []

    for resource in resources:

        searchable_text = " ".join(
            [
                str(
                    resource.get(
                        "session_title",
                        "",
                    )
                ),
                str(
                    resource.get(
                        "resource_type",
                        "",
                    )
                ),
                str(
                    resource.get(
                        "description",
                        "",
                    )
                ),
                str(
                    resource.get(
                        "prerequisite",
                        "",
                    )
                ),
            ]
        ).lower()

        if query and query not in searchable_text:
            continue

        if (
            day
            and str(
                resource.get("day", "")
            ) != day
        ):
            continue

        if (
            resource_type
            and resource.get(
                "resource_type"
            ) != resource_type
        ):
            continue

        if (
            review_status
            and resource.get(
                "review_status"
            ) != review_status
        ):
            continue

        filtered_resources.append(
            resource
        )

    return filtered_resources


def _current_filters():

    return {
        "q": request.args.get(
            "q",
            "",
        ).strip(),

        "day": request.args.get(
            "day",
            "",
        ).strip(),

        "resource_type":
            request.args.get(
                "resource_type",
                "",
            ).strip(),

        "review_status":
            request.args.get(
                "review_status",
                "",
            ).strip(),
    }


# ---------------------------------------------------------
# Public routes
# ---------------------------------------------------------

@app.route("/")
def index():

    resources = _filter_resources(
        load_resources()
    )

    resources.sort(
        key=lambda item: (
            _safe_day(item),

            item.get(
                "session_title",
                "",
            ).lower(),
        )
    )

    return render_template(
        "index.html",
        resources=resources,
        filters=_current_filters(),
    )


@app.route(
    "/resource/<resource_id>"
)
def resource_detail(resource_id):

    resource = get_resource(
        resource_id
    )

    if not resource:
        abort(404)

    return render_template(
        "resource_detail.html",
        resource=resource,
    )


@app.route("/summary")
def summary():

    resources = load_resources()

    summary_map = defaultdict(
        lambda: {
            "count": 0,
            "days": set(),
            "types": set(),
            "reviewed": 0,
        }
    )

    for resource in resources:

        session_title = resource.get(
            "session_title",
            "Untitled Session",
        )

        entry = summary_map[
            session_title
        ]

        entry["count"] += 1

        entry["days"].add(
            resource.get("day")
        )

        entry["types"].add(
            resource.get(
                "resource_type"
            )
        )

        if (
            resource.get(
                "review_status"
            )
            == "Reviewed"
        ):
            entry["reviewed"] += 1

    summary_rows = []

    for (
        session_title,
        entry,
    ) in summary_map.items():

        summary_rows.append(
            {
                "session_title":
                    session_title,

                "count":
                    entry["count"],

                "days":
                    sorted(
                        day
                        for day
                        in entry["days"]
                        if day is not None
                    ),

                "types":
                    sorted(
                        item
                        for item
                        in entry["types"]
                        if item
                    ),

                "reviewed":
                    entry["reviewed"],
            }
        )

    summary_rows.sort(
        key=lambda item:
            item[
                "session_title"
            ].lower()
    )

    return render_template(
        "summary.html",
        summary_rows=summary_rows,
        total_resources=len(resources),
    )


@app.route("/export.csv")
def export_csv():

    resources = _filter_resources(
        load_resources()
    )

    output = io.StringIO(
        newline=""
    )

    writer = csv.writer(
        output
    )

    writer.writerow(
        [
            "ID",
            "Session Title",
            "Day",
            "Resource Type",
            "Description",
            "URL",
            "Prerequisite",
            "Review Status",
        ]
    )

    for resource in resources:

        writer.writerow(
            [
                resource.get(
                    "id",
                    "",
                ),
                resource.get(
                    "session_title",
                    "",
                ),
                resource.get(
                    "day",
                    "",
                ),
                resource.get(
                    "resource_type",
                    "",
                ),
                resource.get(
                    "description",
                    "",
                ),
                resource.get(
                    "url",
                    "",
                ),
                resource.get(
                    "prerequisite",
                    "",
                ),
                resource.get(
                    "review_status",
                    "",
                ),
            ]
        )

    response = Response(
        output.getvalue(),
        mimetype="text/csv",
    )

    response.headers[
        "Content-Disposition"
    ] = (
        "attachment; "
        "filename="
        "filtered_workshop_resources.csv"
    )

    return response


# ---------------------------------------------------------
# Administrator login
# ---------------------------------------------------------

@app.route(
    "/admin/login",
    methods=["GET", "POST"],
)
def admin_login():

    if session.get("is_admin"):

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )

    if request.method == "POST":

        validate_csrf()

        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        configured_username = (
            app.config[
                "ADMIN_USERNAME"
            ]
        )

        username_ok = (
            secrets.compare_digest(
                username,
                configured_username,
            )
        )

        password_ok = (
            verify_admin_password(
                password,
                app.config[
                    "ADMIN_PASSWORD"
                ],
            )
        )

        if (
            username_ok
            and password_ok
        ):

            session.clear()

            session[
                "is_admin"
            ] = True

            session[
                "admin_username"
            ] = configured_username

            flash(
                (
                    "Administrator login "
                    "successful."
                ),
                "success",
            )

            next_url = request.args.get(
                "next",
                "",
            )

            if (
                next_url.startswith("/")
                and not
                next_url.startswith("//")
            ):
                return redirect(
                    next_url
                )

            return redirect(
                url_for(
                    "admin_dashboard"
                )
            )

        flash(
            (
                "Invalid administrator "
                "credentials."
            ),
            "danger",
        )

    return render_template(
        "admin_login.html"
    )


# ---------------------------------------------------------
# Forgot / Reset password
# ---------------------------------------------------------

@app.route(
    "/admin/forgot-password",
    methods=["GET", "POST"],
)
def forgot_password():

    if request.method == "POST":

        validate_csrf()

        username = request.form.get(
            "username",
            "",
        ).strip()

        recovery_code = (
            request.form.get(
                "recovery_code",
                "",
            )
        )

        new_password = (
            request.form.get(
                "new_password",
                "",
            )
        )

        confirm_password = (
            request.form.get(
                "confirm_password",
                "",
            )
        )

        configured_username = (
            app.config[
                "ADMIN_USERNAME"
            ]
        )

        configured_recovery = (
            app.config[
                "ADMIN_RECOVERY_CODE"
            ]
        )

        if not configured_recovery:

            flash(
                (
                    "Password recovery is "
                    "not configured."
                ),
                "danger",
            )

            return render_template(
                "forgot_password.html"
            ), 500

        username_ok = (
            secrets.compare_digest(
                username,
                configured_username,
            )
        )

        recovery_ok = (
            secrets.compare_digest(
                recovery_code,
                configured_recovery,
            )
        )

        if (
            not username_ok
            or not recovery_ok
        ):

            flash(
                (
                    "Invalid username or "
                    "recovery code."
                ),
                "danger",
            )

            return render_template(
                "forgot_password.html"
            ), 400

        if (
            new_password
            != confirm_password
        ):

            flash(
                (
                    "New password and "
                    "confirmation do not match."
                ),
                "danger",
            )

            return render_template(
                "forgot_password.html"
            ), 400

        password_errors = (
            validate_new_password(
                new_password
            )
        )

        if password_errors:

            for error in password_errors:
                flash(
                    error,
                    "danger",
                )

            return render_template(
                "forgot_password.html"
            ), 400

        set_admin_password(
            new_password
        )

        session.clear()

        audit_logger.info(
            (
                "PASSWORD_RESET | "
                "actor=%s"
            ),
            configured_username,
        )

        flash(
            (
                "Password reset successful. "
                "Sign in using your new password."
            ),
            "success",
        )

        return redirect(
            url_for(
                "admin_login"
            )
        )

    return render_template(
        "forgot_password.html"
    )


@app.route(
    "/admin/logout",
    methods=["POST"],
)
@admin_required
def admin_logout():

    validate_csrf()

    session.clear()

    flash(
        "You have been logged out.",
        "success",
    )

    return redirect(
        url_for("index")
    )


# ---------------------------------------------------------
# Administrator dashboard
# ---------------------------------------------------------

@app.route("/admin")
@admin_required
def admin_dashboard():

    resources = load_resources()

    resources.sort(
        key=lambda item: (
            _safe_day(item),

            item.get(
                "session_title",
                "",
            ).lower(),
        )
    )

    counts = {
        "total":
            len(resources),

        "reviewed":
            sum(
                1
                for item in resources
                if item.get(
                    "review_status"
                ) == "Reviewed"
            ),

        "pending":
            sum(
                1
                for item in resources
                if item.get(
                    "review_status"
                ) == "Pending"
            ),

        "needs_review":
            sum(
                1
                for item in resources
                if item.get(
                    "review_status"
                ) == "Needs Review"
            ),
    }

    return render_template(
        "admin_dashboard.html",
        resources=resources,
        counts=counts,
    )


# ---------------------------------------------------------
# Create resource
# ---------------------------------------------------------

@app.route(
    "/admin/resource/new",
    methods=["GET", "POST"],
)
@admin_required
def admin_resource_new():

    form_data = {}

    if request.method == "POST":

        validate_csrf()

        cleaned, errors = (
            validate_resource(
                request.form
            )
        )

        form_data = cleaned

        if not errors:

            resource = (
                create_resource(
                    cleaned
                )
            )

            audit_logger.info(
                (
                    "CREATE | actor=%s | "
                    "resource_id=%s | "
                    "title=%r"
                ),
                session.get(
                    "admin_username",
                    "admin",
                ),
                resource["id"],
                resource[
                    "session_title"
                ],
            )

            flash(
                (
                    "Resource created "
                    "successfully."
                ),
                "success",
            )

            return redirect(
                url_for(
                    "admin_dashboard"
                )
            )

        flash(
            (
                "Please correct the "
                "highlighted validation "
                "errors."
            ),
            "danger",
        )

        return render_template(
            "resource_form.html",
            mode="create",
            form_data=form_data,
            errors=errors,
        ), 400

    return render_template(
        "resource_form.html",
        mode="create",
        form_data=form_data,
        errors={},
    )


# ---------------------------------------------------------
# Edit resource
# ---------------------------------------------------------

@app.route(
    "/admin/resource/<resource_id>/edit",
    methods=["GET", "POST"],
)
@admin_required
def admin_resource_edit(
    resource_id
):

    resource = get_resource(
        resource_id
    )

    if not resource:
        abort(404)

    if request.method == "POST":

        validate_csrf()

        cleaned, errors = (
            validate_resource(
                request.form
            )
        )

        if not errors:

            updated = update_resource(
                resource_id,
                cleaned,
            )

            audit_logger.info(
                (
                    "UPDATE | actor=%s | "
                    "resource_id=%s | "
                    "title=%r"
                ),
                session.get(
                    "admin_username",
                    "admin",
                ),
                updated["id"],
                updated[
                    "session_title"
                ],
            )

            flash(
                (
                    "Resource updated "
                    "successfully."
                ),
                "success",
            )

            return redirect(
                url_for(
                    "admin_dashboard"
                )
            )

        flash(
            (
                "Please correct the "
                "highlighted validation "
                "errors."
            ),
            "danger",
        )

        return render_template(
            "resource_form.html",
            mode="edit",
            form_data=cleaned,
            errors=errors,
            resource_id=resource_id,
        ), 400

    return render_template(
        "resource_form.html",
        mode="edit",
        form_data=resource,
        errors={},
        resource_id=resource_id,
    )


# ---------------------------------------------------------
# Delete resource
# ---------------------------------------------------------

@app.route(
    "/admin/resource/<resource_id>/delete",
    methods=["POST"],
)
@admin_required
def admin_resource_delete(
    resource_id
):

    validate_csrf()

    deleted = delete_resource(
        resource_id
    )

    if not deleted:
        abort(404)

    audit_logger.info(
        (
            "DELETE | actor=%s | "
            "resource_id=%s | "
            "title=%r"
        ),
        session.get(
            "admin_username",
            "admin",
        ),
        deleted["id"],
        deleted[
            "session_title"
        ],
    )

    flash(
        (
            "Resource deleted "
            "successfully."
        ),
        "success",
    )

    return redirect(
        url_for(
            "admin_dashboard"
        )
    )


# ---------------------------------------------------------
# Error handlers
# ---------------------------------------------------------

@app.errorhandler(400)
def bad_request(error):

    return render_template(
        "400.html",
        error=error,
    ), 400


@app.errorhandler(404)
def not_found(error):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def server_error(error):

    app.logger.error(
        (
            "Unexpected application "
            "error: %s"
        ),
        error,
    )

    return render_template(
        "500.html"
    ), 500


# ---------------------------------------------------------
# Run locally
# ---------------------------------------------------------

if __name__ == "__main__":

    debug_enabled = (
        app.config[
            "APP_ENV"
        ].lower()
        == "development"
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=debug_enabled,
    )