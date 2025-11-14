# core/tests/test_routines.py
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
        # ensure a child exists
        cur.execute("SELECT id FROM child_profiles LIMIT 1")
        r = cur.fetchone()
        if not r:
            cur.execute("INSERT INTO child_profiles (name, birth_date) VALUES (?, ?)", ("test_child_routine", "2024-01-01"))
            child_id = cur.lastrowid
        else:
            child_id = r[0]
        # create routine
        cur.execute("INSERT INTO routines (name, child_id) VALUES (?, ?)", ("Routine test", child_id))
        rid = cur.lastrowid
        # add a task
        cur.execute("INSERT INTO routine_tasks (routine_id, task_name, scheduled_time, status) VALUES (?, ?, ?, ?)",
                    (rid, "Test tâche", datetime.now().strftime("%H:%M"), "en cours"))
        tid = cur.lastrowid
        conn.commit()
        # mark task as completed
        cur.execute("UPDATE routine_tasks SET status = ? WHERE id = ?", ("terminé", tid))
        conn.commit()
        # cleanup
        cur.execute("DELETE FROM routine_tasks WHERE id = ?", (tid,))
        cur.execute("DELETE FROM routines WHERE id = ?", (rid,))
        conn.commit()
        conn.close()
        return TestResult(module="routines", success=True, duration=time() - start, errors=[])
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        return TestResult(module="routines", success=False, duration=time() - start, errors=[str(e)])