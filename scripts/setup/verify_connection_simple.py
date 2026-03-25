import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env.local
env_file = PROJECT_ROOT / ".env.local"
if env_file.exists():
    print(f"Loading {env_file}")
    load_dotenv(env_file, override=True)
else:
    print("Loading .env from root")
    load_dotenv(PROJECT_ROOT / ".env", override=True)

try:
    from src.core.db.engine import obtenir_moteur

    print("Obtaining engine...")
    engine = obtenir_moteur()
    print(f"Engine created: {engine.url}")

    print("Connecting...")
    with engine.connect() as conn:
        print("Connected successfully!")
        result = conn.execute(text("SELECT version();")).fetchone()
        print(f"DB Version: {result[0]}")

        # Check if column likely exists
        check_sql = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='listes_courses' AND column_name='archivee';
        """)
        col = conn.execute(check_sql).fetchone()
        if col:
            print("Column 'archivee' ALREADY EXISTS.")
        else:
            print("Column 'archivee' MISSING. Attempting to add it...")
            add_sql = text(
                "ALTER TABLE listes_courses ADD COLUMN IF NOT EXISTS archivee BOOLEAN DEFAULT FALSE;"
            )
            conn.execute(add_sql)
            conn.commit()
            print("Column added successfully!")

except Exception as e:
    print(f"CONNECTION FAILED: {e}")
    # Print env var without password for debugging
    url = os.environ.get("DATABASE_URL", "NOT_SET")
    # Mask password
    if "@" in url:
        part1 = url.split("@")[0]
        # find last colon before @
        if ":" in part1:
            user_part, _ = part1.rsplit(":", 1)
            print(f"URL User part: {user_part}:***@{url.split('@')[1]}")
        else:
            print(f"URL: {url}")
    else:
        print(f"URL: {url}")
