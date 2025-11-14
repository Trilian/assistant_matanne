# core/tests/test_inventaire.py
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
        # Insert a test inventory item
        cur.execute("INSERT INTO inventory_items (name, category, quantity, unit) VALUES (?, ?, ?, ?)",
                    ("test_pates", "Aliments", 0.5, "kg"))
        iid = cur.lastrowid
        conn.commit()
        # Read it back
        cur.execute("SELECT name, quantity FROM inventory_items WHERE id = ?", (iid,))
        row = cur.fetchone()
        if not row:
            errors.append("inventory read failed")
        # Update quantity
        cur.execute("UPDATE inventory_items SET quantity = ? WHERE id = ?", (1.0, iid))
        conn.commit()
        # Cleanup
        cur.execute("DELETE FROM inventory_items WHERE id = ?", (iid,))
        conn.commit()
        conn.close()
        success = len(errors) == 0
        return TestResult(module="inventaire", success=success, duration=time() - start, errors=errors)
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        errors.append(str(e))
        return TestResult(module="inventaire", success=False, duration=time() - start, errors=errors)