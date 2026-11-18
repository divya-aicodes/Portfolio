from __future__ import annotations

from datetime import datetime


def save_contact_message(
    database,
    *,
    is_postgres: bool,
    name: str,
    email: str,
    message: str,
    created_at: datetime,
) -> None:
    """Persist a contact submission in the configured SQL database."""
    placeholder = "%s" if is_postgres else "?"
    database.execute(
        f"INSERT INTO messages (name, email, message, created_at) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})",
        (name, email, message, created_at if is_postgres else created_at.isoformat()),
    )
    database.commit()
