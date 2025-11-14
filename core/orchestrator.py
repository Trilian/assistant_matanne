# assistant_matanne_v2/core/orchestrator.py

from datetime import datetime
from core.database import get_connection
import random

class Orchestrator:
    """
    Gère la logique centrale de l’assistant :
    - Génération de suggestions repas
    - Génération de routines quotidiennes
    - Calcul de faisabilité (ingrédients disponibles)
    """

    def __init__(self):
        self.conn = get_connection()

    # ============================================================
    # 🥗 SUGGESTIONS DE REPAS
    # ============================================================
    def generate_meal_suggestions(self, nb_meals: int = 3):
        """
        Génère automatiquement des suggestions de repas à partir
        des recettes et de l’inventaire disponible.
        Retourne :
            [
              {
                "id": 1,
                "nom": "Gratin dauphinois",
                "ingredients": ["pommes de terre", "lait", "crème"],
                "score": 80,
                "realisable": True,
                "manquants": ["crème"]
              },
              ...
            ]
        """
        cursor = self.conn.cursor()

        # Charger les recettes
        cursor.execute("SELECT id, nom, ingredients FROM recettes")
        recettes = cursor.fetchall()
        if not recettes:
            return []

        # Charger l’inventaire
        cursor.execute("SELECT nom FROM inventaire WHERE quantite > 0")
        inventaire = [row[0].strip().lower() for row in cursor.fetchall()]

        suggestions = []
        for rec in random.sample(recettes, min(nb_meals, len(recettes))):
            rec_id, rec_nom, rec_ingredients = rec
            ingredients = [i.strip().lower() for i in rec_ingredients.split(",") if i.strip()]
            dispo = [i for i in ingredients if i in inventaire]
            manquants = [i for i in ingredients if i not in inventaire]

            score = int(100 * len(dispo) / len(ingredients)) if ingredients else 0
            realisable = score >= 70

            suggestions.append({
                "id": rec_id,
                "nom": rec_nom,
                "ingredients": ingredients,
                "score": score,
                "realisable": realisable,
                "manquants": manquants
            })

        return suggestions

    # ============================================================
    # 🧭 SUGGESTIONS DE ROUTINES
    # ============================================================
    def generate_routines(self):
        """
        Génère automatiquement les routines à faire aujourd’hui
        selon leur fréquence et dernière exécution.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
                       SELECT id, nom, categorie, frequence_jours, derniere_execution
                       FROM routines
                       WHERE active = 1
                       """)
        rows = cursor.fetchall()

        today = datetime.now().date()
        routines = []
        for rid, nom, cat, freq, last in rows:
            last_date = None
            if last:
                try:
                    last_date = datetime.strptime(last, "%Y-%m-%d").date()
                except ValueError:
                    pass

            doit_faire = not last_date or (today - last_date).days >= freq
            routines.append({
                "id": rid,
                "nom": nom,
                "categorie": cat,
                "frequence": freq,
                "dernier": last_date.strftime("%Y-%m-%d") if last_date else None,
                "a_faire": doit_faire
            })

        # Routines à faire d’abord
        routines.sort(key=lambda r: (not r["a_faire"], r["nom"]))
        return routines

    def mark_routine_done(self, routine_id: int) -> bool:
        """Met à jour la date d’exécution d’une routine après validation."""
        try:
            cursor = self.conn.cursor()
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "UPDATE routines SET derniere_execution = ? WHERE id = ?",
                (today, routine_id)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False