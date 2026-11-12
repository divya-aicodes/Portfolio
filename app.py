from __future__ import annotations

import hmac
import os
import re
import secrets
import sqlite3
import threading
import time
from collections import defaultdict, deque
from datetime import UTC, datetime
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from flask import Flask, g, jsonify, render_template, request, session

import contact_storage
from portfolio_data import PROFILE, PROJECTS, SKILL_GROUPS


BASE_DIR = Path(__file__).resolve().parent
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
RATE_LIMIT_WINDOW_SECONDS = 10 * 60
RATE_LIMIT_REQUESTS = 5


class ContactRateLimiter:
    """Small in-memory guard for a single-process student portfolio."""

    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - RATE_LIMIT_WINDOW_SECONDS
        with self._lock:
            attempts = self._requests[key]
            while attempts and attempts[0] < cutoff:
                attempts.popleft()
            if len(attempts) >= RATE_LIMIT_REQUESTS:
                return False
            attempts.append(now)
            return True


rate_limiter = ContactRateLimiter()


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    configured_database = os.environ.get("DATABASE_PATH", "").strip()
    if configured_database:
        default_database = configured_database
    elif os.environ.get("VERCEL"):
        default_database = str(Path(gettempdir()) / "portfolio.sqlite3")
    else:
        default_database = str(Path(app.instance_path) / "portfolio.sqlite3")

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=default_database,
        LINKEDIN_URL=os.environ.get("LINKEDIN_URL", "").strip(),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("APP_ENV") == "production",
        MAX_CONTENT_LENGTH=32 * 1024,
        RATE_LIMIT_ENABLED=True,
        CONTACT_STORAGE="blob" if os.environ.get("VERCEL") else "sqlite",
    )

    if test_config:
        app.config.update(test_config)

    if app.config["CONTACT_STORAGE"] == "sqlite":
        Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    app.teardown_appcontext(close_database)

    if app.config["CONTACT_STORAGE"] == "sqlite":
        with app.app_context():
            init_database()

    @app.get("/")
    def index():
        profile = {
            **PROFILE,
            "linkedin_url": app.config["LINKEDIN_URL"],
        }
        return render_template(
            "index.html",
            profile=profile,
            projects=PROJECTS,
            skill_groups=SKILL_GROUPS,
            csrf_token=get_csrf_token(),
            current_year=datetime.now(UTC).year,
        )

    @app.get("/health")
    def health():
        return jsonify(status="ok", service="divya-portfolio")

    @app.get("/api/profile")
    def profile_api():
        return jsonify(
            name=PROFILE["name"],
            role=PROFILE["role"],
            project_count=len(PROJECTS),
            python_project_count=sum(
                "Python" in project["technologies"] for project in PROJECTS
            ),
            served_by="Flask",
            generated_at=datetime.now(UTC).isoformat(),
        )

    @app.post("/api/contact")
    def contact_api():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Please submit the contact form as JSON."), 400

        token = str(payload.get("csrf_token", ""))
        expected_token = str(session.get("csrf_token", ""))
        if not expected_token or not hmac.compare_digest(token, expected_token):
            return jsonify(error="Your session expired. Refresh the page and try again."), 403

        if str(payload.get("website", "")).strip():
            return jsonify(message="Thanks — your message was received."), 200

        client_key = request.remote_addr or "unknown"
        if app.config["RATE_LIMIT_ENABLED"] and not rate_limiter.allow(client_key):
            return jsonify(error="Too many messages. Please try again in a few minutes."), 429

        name = normalize_text(payload.get("name"), 80)
        email = normalize_text(payload.get("email"), 254).lower()
        message = normalize_text(payload.get("message"), 1500)

        errors: dict[str, str] = {}
        if len(name) < 2:
            errors["name"] = "Please enter at least 2 characters."
        if not EMAIL_PATTERN.fullmatch(email):
            errors["email"] = "Please enter a valid email address."
        if len(message) < 20:
            errors["message"] = "Please enter at least 20 characters."

        if errors:
            return jsonify(error="Please correct the highlighted fields.", fields=errors), 422

        created_at = datetime.now(UTC)
        if app.config["CONTACT_STORAGE"] == "blob":
            try:
                contact_storage.save_contact_message_to_blob(
                    name=name,
                    email=email,
                    message=message,
                    created_at=created_at,
                )
            except Exception:
                app.logger.exception("Private contact-message storage failed.")
                return (
                    jsonify(
                        error=(
                            "The message could not be saved right now. "
                            "Please email Divya directly."
                        )
                    ),
                    503,
                )
        else:
            database = get_database()
            database.execute(
                "INSERT INTO messages (name, email, message, created_at) VALUES (?, ?, ?, ?)",
                (name, email, message, created_at.isoformat()),
            )
            database.commit()

        session["csrf_token"] = secrets.token_urlsafe(32)
        return (
            jsonify(
                message="Message sent successfully. Divya will get back to you soon.",
                csrf_token=session["csrf_token"],
            ),
            201,
        )

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return jsonify(error="Not found."), 404
        return render_template("404.html"), 404

    @app.errorhandler(413)
    def too_large(_error):
        return jsonify(error="That request is too large."), 413

    @app.after_request
    def add_security_headers(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' https://avatars.githubusercontent.com data:; "
            "script-src 'self'; style-src 'self'; connect-src 'self'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

    return app


def normalize_text(value: Any, maximum_length: int) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())[:maximum_length]


def get_csrf_token() -> str:
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return str(token)


def get_database() -> sqlite3.Connection:
    if "database" not in g:
        g.database = sqlite3.connect(
            current_app_database_path(),
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.database.row_factory = sqlite3.Row
    return g.database


def current_app_database_path() -> str:
    from flask import current_app

    return str(current_app.config["DATABASE"])


def close_database(_error: BaseException | None = None) -> None:
    database = g.pop("database", None)
    if database is not None:
        database.close()


def init_database() -> None:
    database = get_database()
    database.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK(length(name) BETWEEN 2 AND 80),
            email TEXT NOT NULL CHECK(length(email) <= 254),
            message TEXT NOT NULL CHECK(length(message) BETWEEN 20 AND 1500),
            created_at TEXT NOT NULL
        )
        """
    )
    database.commit()


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
