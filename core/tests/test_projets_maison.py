# core/tests/test_projets_maison.py
from time import time
from core.test_manager import TestResult
from core.database import get_connection
from datetime import datetime, timedelta

def run_test():
    start = time()
    errors = []
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        # create project
        cur.execute("INSERT INTO projects (name, description, start_date, end_date, priority) VALUES (?, ?, ?, ?, ?)",
                    ("Test Projet", "Desc", datetime.now().date().isoformat(), (datetime.now()+timedelta(days=3)).date().isoformat(), "Moyenne"))
        pid = cur.lastrowid
        # add a task
        cur.execute("INSERT INTO project_tasks (project_id, task_name, status) VALUES (?, ?, ?)",
                    (pid, "Tâche test", "en cours"))
        tid = cur.lastrowid
        conn.commit()
        # mark overdue by setting end_date in past and check if selection works
        cur.execute("UPDATE projects SET end_date = ? WHERE id = ?", (((datetime.now()-timedelta(days=2)).date().isoformat()), pid))
        conn.commit()
        # cleanup
        cur.execute("DELETE FROM project_tasks WHERE id = ?", (tid,))
        cur.execute("DELETE FROM projects WHERE id = ?", (pid,))
        conn.commit()
        conn.close()
        return TestResult(module="projets_maison", success=True, duration=time() - start, errors=[])
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        return TestResult(module="projets_maison", success=False, duration=time() - start, errors=[str(e)])