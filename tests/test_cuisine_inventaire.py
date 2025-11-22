# tests/test_cuisine_inventaire.py

import os
import pytest
import sqlite3

# On utilise ta vraie fonction
from core.schema_manager import reset_tables, create_all_tables
from core.database import get_connection


# ------------------------
#  FIXTURE : DB propre
# ------------------------
@pytest.fixture(scope="function")
def fresh_db():
    """
    Réinitialise TOUTES les tables avant chaque test.
    """
    reset_tables()
    conn = get_connection()
    yield conn
    conn.close()


# ------------------------
#      TESTS SCHEMA
# ------------------------
def test_tables_exist(fresh_db):
    """
    Vérifie l'existence de TOUTES les tables importantes.
    """
    cursor = fresh_db.cursor()

    required = [
        "recipes", "ingredients", "recipe_ingredients",
        "inventory_items", "courses"
    ]

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    for r in required:
        assert r in tables, f"❌ Table manquante : {r}"


# ------------------------
#      TEST RECETTE
# ------------------------
def test_add_recipe_and_ingredients(fresh_db):
    cursor = fresh_db.cursor()

    # Ajouter recette
    cursor.execute("INSERT INTO recipes (name) VALUES ('Pâtes Carbo')")
    rid = cursor.lastrowid

    # Ajouter un ingrédient
    cursor.execute("INSERT INTO ingredients (name, unit) VALUES ('Pâtes', 'g')")
    iid = cursor.lastrowid

    # Lier les deux
    cursor.execute("""
                   INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity)
                   VALUES (?, ?, ?)
                   """, (rid, iid, 200))

    fresh_db.commit()

    # Vérifications
    cursor.execute("SELECT * FROM recipes")
    assert cursor.fetchone() is not None

    cursor.execute("SELECT * FROM ingredients")
    assert cursor.fetchone() is not None

    cursor.execute("SELECT * FROM recipe_ingredients")
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == rid
    assert row[2] == iid


# ------------------------
#  TEST INVENTAIRE
# ------------------------
def test_add_inventory_item(fresh_db):
    cursor = fresh_db.cursor()

    cursor.execute("""
                   INSERT INTO inventory_items (name, category, quantity, unit)
                   VALUES ('Carottes', 'Légume', 5, 'pcs')
                   """)

    fresh_db.commit()

    cursor.execute("SELECT name, quantity FROM inventory_items WHERE name='Carottes'")
    row = cursor.fetchone()

    assert row is not None
    assert row[0] == "Carottes"
    assert row[1] == 5


# ------------------------
#   TEST COURSES
# ------------------------
def test_add_to_courses(fresh_db):
    cursor = fresh_db.cursor()

    # On ajoute un item dans l'inventaire
    cursor.execute("""
                   INSERT INTO inventory_items (name, category, quantity, unit)
                   VALUES ('Tomates', 'Légume', 1, 'pcs')
                   """)
    item_id = cursor.lastrowid

    # On crée un besoin dans "courses"
    cursor.execute("""
                   INSERT INTO courses (item_id, needed_quantity)
                   VALUES (?, ?)
                   """, (item_id, 4))

    fresh_db.commit()

    cursor.execute("SELECT needed_quantity FROM courses WHERE item_id=?", (item_id,))
    row = cursor.fetchone()

    assert row is not None
    assert row[0] == 4