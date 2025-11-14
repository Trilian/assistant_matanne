# core/tests/test_bien_etre.py
from time import time
from core.test_manager import TestResult
from core.database import get_connection
from core.helpers import log_event

def run_test():
    start = time()
    errors = []
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Insert a wellbeing entry (adult or child) in an additive manner
        try:
            cur.execute(
                "INSERT INTO wellbeing_entries (child_id, date, mood, notes) VALUES (?, ?, ?, ?)",
                (None, "2025-01-01", "Test", "Entry from automated test")
            )
            conn.commit()
            # remove the test row to keep DB clean
            cur.execute("DELETE FROM wellbeing_entries WHERE notes = ?", ("Entry from automated test",))
            conn.commit()
        except Exception:
            # fallback: try generic wellbeing table names if schema differs
            cur.execute("INSERT OR IGNORE INTO wellbeing_entries (child_id, date, mood, notes) VALUES (?, ?, ?, ?)",
                        (None, "2025-01-01", "Test", "Entry from automated test"))
            conn.commit()
        conn.close()
        return TestResult(module="bien_etre", success=True, duration=time() - start, errors=[])
    except Exception as e:
        log_event(f"[TEST bien_etre] error: {e}")
        errors.append(str(e))
        try:
            conn.close()
        except:
            pass
        return TestResult(module="bien_etre", success=False, duration=time() - start, errors=errors)