from __future__ import annotations

import json
import secrets
from datetime import datetime
from typing import Any

from vercel.blob.sync import put_blob


def save_contact_message_to_blob(
    *,
    name: str,
    email: str,
    message: str,
    created_at: datetime,
) -> None:
    """Persist one contact submission as a private, immutable JSON blob."""
    timestamp = created_at.strftime("%Y%m%dT%H%M%S%fZ")
    pathname = (
        f"messages/{created_at:%Y/%m/%d}/"
        f"{timestamp}-{secrets.token_hex(6)}.json"
    )
    payload: dict[str, Any] = {
        "name": name,
        "email": email,
        "message": message,
        "created_at": created_at.isoformat(),
    }
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )

    put_blob(
        pathname,
        body,
        access="private",
        content_type="application/json; charset=utf-8",
        add_random_suffix=False,
    )
