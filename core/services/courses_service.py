# core/services/courses_service.py
from core.database import get_connection

def add_item_to_courses(name: str, quantity: float = 1.0):
    """Ajoute un item à la liste de courses (avec auto-match inventaire)."""

    name_norm = name.strip().lower()
    conn = get_connection()
    cur = conn.cursor()

    # Vérifier si item existe dans inventaire
    inv = cur.execute(
        "SELECT id, unit FROM inventory_items WHERE LOWER(name) = ?", (name_norm,)
    ).fetchone()

    if inv:
        item_id = inv["id"]
    else:
        item_id = None

    # Voir si déjà présent dans courses
    existing = cur.execute(
        "SELECT id, needed_quantity FROM courses WHERE item_id = ?",
        (item_id,)
    ).fetchone() if item_id else None

    if existing:
        new_qty = float(existing["needed_quantity"]) + quantity
        cur.execute(
            "UPDATE courses SET needed_quantity = ? WHERE id = ?",
            (new_qty, existing["id"])
        )
    else:
        cur.execute(
            "INSERT INTO courses (item_id, needed_quantity) VALUES (?, ?)",
            (item_id, quantity)
        )

    conn.commit()
    conn.close()