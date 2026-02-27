"""Simple DB check helper that prints a traceback on failure.

Usage:
  set DATABASE_URL=postgresql://user:pass@host/db
  python scripts/check_db.py

The script attempts to connect using SQLAlchemy and prints detailed errors.
"""

import os
import traceback

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


def main():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set. Export it before running.")
        return

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("DB connected, SELECT 1 ->", result.scalar())
    except SQLAlchemyError as e:
        print("SQLAlchemyError caught:")
        traceback.print_exc()
    except Exception as e:
        print("Unexpected exception:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
