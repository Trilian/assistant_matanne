import os
from pathlib import Path

import psycopg2


def get_connection_string():
    # Try to find .env.local first
    env_local = Path(".env.local")
    env = Path(".env")

    conn_str = None

    if env_local.exists():
        with open(env_local) as f:
            for line in f:
                if line.strip().startswith("DATABASE_URL="):
                    conn_str = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                    print("Found DATABASE_URL in .env.local")
                    break

    if not conn_str and env.exists():
        with open(env) as f:
            for line in f:
                if line.strip().startswith("DATABASE_URL="):
                    conn_str = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                    print("Found DATABASE_URL in .env")
                    break

    return conn_str


def apply_migration():
    conn_str = get_connection_string()
    if not conn_str:
        print("Error: Could not find DATABASE_URL in .env or .env.local")
        return

    print("Connecting to DB...")
    # Hide password in logs
    safe_url = conn_str.split("@")[-1] if "@" in conn_str else "..."
    print(f"Target: ...@{safe_url}")

    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()

        sql = """
        ALTER TABLE IF EXISTS listes_courses
        ADD COLUMN IF NOT EXISTS archivee BOOLEAN DEFAULT FALSE;

        CREATE INDEX IF NOT EXISTS ix_listes_courses_archivee ON listes_courses (archivee);
        """

        print("Executing migration...")
        cur.execute(sql)
        conn.commit()
        print("Migration applied successfully!")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error applying migration: {e}")


if __name__ == "__main__":
    apply_migration()
