# core/tests/test_jardin.py
from time import time
from core.test_manager import TestResult
from core.database import get_connection

def run_test():
    start = time()
    errors = []
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        # insert garden item
        cur.execute("INSERT INTO garden_items (name, category, quantity, unit) VALUES (?, ?, ?, ?)",
                    ("Test Tomate", "Légume", 3, "plants"))
        gid = cur.lastrowid
        conn.commit()
        # simulate depleting stock to trigger alerts
        cur.execute("UPDATE garden_items SET quantity = ? WHERE id = ?", (0, gid))
        conn.commit()
        # cleanup
        cur.execute("DELETE FROM garden_items WHERE id = ?", (gid,))
        conn.commit()
        conn.close()
        return TestResult(module="jardin", success=True, duration=time() - start, errors=[])
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        return TestResult(module="jardin", success=False, duration=time() - start, errors=[str(e)])