"""Export the contact database to a portable CSV file.

Usage: python export_messages.py messages.csv
Uses DATABASE_URL when present; otherwise reads instance/portfolio.sqlite3.
"""

from __future__ import annotations

import csv
import os
import sqlite3
import sys
from pathlib import Path


def main() -> int:
    destination = Path(sys.argv[1] if len(sys.argv) > 1 else "messages.csv")
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url:
        import psycopg

        connection = psycopg.connect(database_url)
        try:
            rows = connection.execute(
                "SELECT id, name, email, message, created_at FROM messages ORDER BY created_at DESC"
            ).fetchall()
        finally:
            connection.close()
    else:
        connection = sqlite3.connect(Path("instance") / "portfolio.sqlite3")
        try:
            rows = connection.execute(
                "SELECT id, name, email, message, created_at FROM messages ORDER BY created_at DESC"
            ).fetchall()
        finally:
            connection.close()

    with destination.open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(("id", "name", "email", "message", "created_at"))
        writer.writerows(rows)
    print(f"Exported {len(rows)} message(s) to {destination.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
