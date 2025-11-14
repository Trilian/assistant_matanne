# core/tests/test_notifications.py
from time import time
from core.test_manager import TestResult
from core.database import get_connection
from datetime import datetime

def run_test():
    start = time()
    errors = []
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        # insert a notification row
        cur.execute("INSERT INTO user_notifications (user_id, module, message, created_at, read) VALUES (?, ?, ?, ?, ?)",
                    (1, "TestModule", "Notification test", datetime.now().isoformat(), 0))
        nid = cur.lastrowid
        conn.commit()
        # read it back
        cur.execute("SELECT message FROM user_notifications WHERE id = ?", (nid,))
        row = cur.fetchone()
        if not row:
            errors.append("notification not inserted")
        # mark read and cleanup
        cur.execute("UPDATE user_notifications SET read = 1 WHERE id = ?", (nid,))
        cur.execute("DELETE FROM user_notifications WHERE id = ?", (nid,))
        conn.commit()
        conn.close()
        return TestResult(module="notifications", success=len(errors) == 0, duration=time() - start, errors=errors)
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        return TestResult(module="notifications", success=False, duration=time() - start, errors=[str(e)])