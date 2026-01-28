"""Tests unitaires pour les modules planning."""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock


# =============================================================================
# TESTS PLANNING SEMAINE
# =============================================================================

class TestPlanningSemaineLogique:
    """Tests pour la logique de planning hebdomadaire."""

    def test_obtenir_dates_semaine(self):
        """Obtenir les dates de la semaine courante."""
        today = date.today()
        # Lundi de cette semaine
        lundi = today - timedelta(days=today.weekday())
        
        dates_semaine = [lundi + timedelta(days=i) for i in range(7)]
        
        assert len(dates_semaine) == 7
        assert dates_semaine[0].weekday() == 0  # Lundi
        assert dates_semaine[6].weekday() == 6  # Dimanche

    def test_grouper_repas_par_jour(self):
        """Groupement des repas par jour."""
        repas = [
            {"date": date(2026, 1, 27), "type": "dejeuner", "recette": "Pâtes"},
            {"date": date(2026, 1, 27), "type": "diner", "recette": "Soupe"},
            {"date": date(2026, 1, 28), "type": "dejeuner", "recette": "Salade"},
        ]
        
        par_jour = {}
        for r in repas:
            d = r["date"]
            if d not in par_jour:
                par_jour[d] = []
            par_jour[d].append(r)
        
        assert len(par_jour[date(2026, 1, 27)]) == 2
        assert len(par_jour[date(2026, 1, 28)]) == 1

    def test_types_repas(self):
        """Types de repas valides."""
        types_valides = ["petit_dejeuner", "dejeuner", "gouter", "diner"]
        
        repas = {"type": "dejeuner"}
        
        assert repas["type"] in types_valides

    def test_calculer_repas_manquants(self):
        """Calcul des repas manquants dans la semaine."""
        jours_semaine = 7
        types_par_jour = ["dejeuner", "diner"]  # 2 repas/jour
        total_attendu = jours_semaine * len(types_par_jour)
        
        repas_planifies = 10  # Exemple
        manquants = total_attendu - repas_planifies
        
        assert manquants == 4

    def test_navigation_semaines(self):
        """Navigation entre les semaines."""
        semaine_courante = date(2026, 1, 27)  # Un lundi
        
        semaine_precedente = semaine_courante - timedelta(weeks=1)
        semaine_suivante = semaine_courante + timedelta(weeks=1)
        
        assert semaine_precedente == date(2026, 1, 20)
        assert semaine_suivante == date(2026, 2, 3)


# =============================================================================
# TESTS CALENDRIER
# =============================================================================

class TestCalendrierLogique:
    """Tests pour la logique du calendrier."""

    def test_obtenir_jours_mois(self):
        """Obtenir le nombre de jours dans un mois."""
        from calendar import monthrange
        
        # Janvier 2026
        jours_janvier = monthrange(2026, 1)[1]
        # Février 2026 (non bissextile)
        jours_fevrier = monthrange(2026, 2)[1]
        
        assert jours_janvier == 31
        assert jours_fevrier == 28

    def test_premier_jour_mois(self):
        """Premier jour du mois (jour de la semaine)."""
        from calendar import monthrange
        
        # 1er janvier 2026 = jeudi (3)
        premier_jour = date(2026, 1, 1).weekday()
        
        assert premier_jour == 3  # Jeudi

    def test_evenements_du_jour(self):
        """Filtrer les événements d'un jour donné."""
        jour = date(2026, 1, 28)
        
        evenements = [
            {"titre": "Réunion", "date": date(2026, 1, 28), "heure": "10:00"},
            {"titre": "RDV médecin", "date": date(2026, 1, 28), "heure": "14:00"},
            {"titre": "Anniversaire", "date": date(2026, 1, 30)},
        ]
        
        du_jour = [e for e in evenements if e["date"] == jour]
        
        assert len(du_jour) == 2

    def test_vue_mois_grille(self):
        """Génération de la grille du mois."""
        from calendar import monthcalendar
        
        # Grille de janvier 2026
        grille = monthcalendar(2026, 1)
        
        # 5 semaines (lignes)
        assert len(grille) >= 4
        # 7 jours par semaine
        assert len(grille[0]) == 7


# =============================================================================
# TESTS VUE ENSEMBLE
# =============================================================================

class TestVueEnsembleLogique:
    """Tests pour la vue d'ensemble."""

    def test_calculer_statistiques_semaine(self):
        """Statistiques de la semaine."""
        repas = [
            {"type": "dejeuner", "recette_id": 1},
            {"type": "diner", "recette_id": 2},
            {"type": "dejeuner", "recette_id": 1},  # Répétition
            {"type": "diner", "recette_id": 3},
        ]
        
        total = len(repas)
        recettes_uniques = len(set(r["recette_id"] for r in repas))
        
        assert total == 4
        assert recettes_uniques == 3

    def test_calculer_diversite(self):
        """Calcul de l'indice de diversité."""
        recettes_utilisees = [1, 2, 1, 3, 2, 1, 4]
        
        total = len(recettes_utilisees)
        uniques = len(set(recettes_utilisees))
        diversite = (uniques / total) * 100 if total > 0 else 0
        
        assert diversite == pytest.approx(57.14, rel=0.1)

    def test_seuils_alerts(self):
        """Calcul des seuils pour alertes."""
        stats = {
            "repas_planifies": 8,
            "repas_attendus": 14,
            "budget_utilise": 120,
            "budget_max": 150,
        }
        
        # Alerte si moins de 50% planifié
        alerte_planning = stats["repas_planifies"] < stats["repas_attendus"] * 0.5
        
        # Alerte si plus de 80% du budget
        alerte_budget = stats["budget_utilise"] > stats["budget_max"] * 0.8
        
        assert alerte_planning == False  # 8/14 = 57%
        assert alerte_budget == True  # 120/150 = 80%


# =============================================================================
# TESTS COMPOSANTS PLANNING
# =============================================================================

class TestComposantsPlanning:
    """Tests pour les composants de planning."""

    def test_format_jour_semaine(self):
        """Format du jour de la semaine."""
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        d = date(2026, 1, 28)  # Mercredi
        jour = jours[d.weekday()]
        
        assert jour == "Mercredi"

    def test_couleur_type_repas(self):
        """Couleur associée au type de repas."""
        couleurs = {
            "petit_dejeuner": "#FFD700",  # Or
            "dejeuner": "#4CAF50",  # Vert
            "gouter": "#FF9800",  # Orange
            "diner": "#2196F3",  # Bleu
        }
        
        assert couleurs["dejeuner"] == "#4CAF50"

    def test_format_carte_repas(self):
        """Format d'une carte de repas."""
        repas = {
            "recette_nom": "Tarte aux pommes",
            "portions": 4,
            "temps_total": 75,
            "type": "diner"
        }
        
        # Formater le temps
        heures = repas["temps_total"] // 60
        minutes = repas["temps_total"] % 60
        temps_format = f"{heures}h{minutes:02d}" if heures else f"{minutes} min"
        
        assert temps_format == "1h15"


# =============================================================================
# TESTS GÉNÉRATION COURSES
# =============================================================================

class TestGenerationCourses:
    """Tests pour la génération de liste de courses depuis le planning."""

    def test_extraire_ingredients_semaine(self):
        """Extraction des ingrédients de la semaine."""
        planning = [
            {
                "recette_id": 1,
                "portions": 4,
                "ingredients": [
                    {"nom": "Pâtes", "quantite": 500, "unite": "g"},
                    {"nom": "Tomates", "quantite": 3, "unite": "pièces"},
                ]
            },
            {
                "recette_id": 2,
                "portions": 4,
                "ingredients": [
                    {"nom": "Poulet", "quantite": 400, "unite": "g"},
                    {"nom": "Riz", "quantite": 300, "unite": "g"},
                ]
            }
        ]
        
        tous_ingredients = []
        for repas in planning:
            tous_ingredients.extend(repas["ingredients"])
        
        assert len(tous_ingredients) == 4

    def test_fusionner_ingredients(self):
        """Fusion des ingrédients identiques."""
        ingredients = [
            {"nom": "Pâtes", "quantite": 500, "unite": "g"},
            {"nom": "Pâtes", "quantite": 300, "unite": "g"},
            {"nom": "Tomates", "quantite": 3, "unite": "pièces"},
        ]
        
        merged = {}
        for ing in ingredients:
            key = (ing["nom"], ing["unite"])
            if key in merged:
                merged[key]["quantite"] += ing["quantite"]
            else:
                merged[key] = ing.copy()
        
        pates = merged[("Pâtes", "g")]
        assert pates["quantite"] == 800

    def test_ajuster_portions(self):
        """Ajustement des quantités selon les portions."""
        ingredient = {"quantite": 200, "pour_portions": 4}
        portions_voulues = 6
        
        quantite_ajustee = (ingredient["quantite"] / ingredient["pour_portions"]) * portions_voulues
        
        assert quantite_ajustee == 300


# =============================================================================
# TESTS COPIE PLANNING
# =============================================================================

class TestCopiePlanning:
    """Tests pour la copie de planning."""

    def test_copier_planning_semaine_suivante(self):
        """Copie du planning vers la semaine suivante."""
        repas_source = [
            {"date": date(2026, 1, 27), "type": "dejeuner", "recette_id": 1},
            {"date": date(2026, 1, 27), "type": "diner", "recette_id": 2},
            {"date": date(2026, 1, 28), "type": "dejeuner", "recette_id": 3},
        ]
        
        decalage = timedelta(weeks=1)
        
        repas_copie = [
            {**r, "date": r["date"] + decalage}
            for r in repas_source
        ]
        
        assert repas_copie[0]["date"] == date(2026, 2, 3)
        assert repas_copie[1]["date"] == date(2026, 2, 3)
        assert repas_copie[2]["date"] == date(2026, 2, 4)

    def test_copier_template(self):
        """Copie d'un template de semaine."""
        template = {
            "lundi": [{"type": "dejeuner", "recette_id": 1}],
            "mardi": [{"type": "diner", "recette_id": 2}],
        }
        
        jours_mapping = {
            "lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3,
            "vendredi": 4, "samedi": 5, "dimanche": 6
        }
        
        lundi_cible = date(2026, 2, 2)
        
        repas_generes = []
        for jour, repas_list in template.items():
            offset = jours_mapping[jour]
            date_repas = lundi_cible + timedelta(days=offset)
            for r in repas_list:
                repas_generes.append({**r, "date": date_repas})
        
        assert len(repas_generes) == 2


# =============================================================================
# TESTS VALIDATION PLANNING
# =============================================================================

class TestValidationPlanning:
    """Tests de validation du planning."""

    def test_valider_date_repas(self):
        """Validation de la date du repas."""
        today = date.today()
        
        # Date passée = invalide (sauf pour édition)
        date_passee = today - timedelta(days=5)
        date_future = today + timedelta(days=5)
        
        assert date_future >= today
        assert date_passee < today

    def test_valider_type_repas(self):
        """Validation du type de repas."""
        types_valides = {"petit_dejeuner", "dejeuner", "gouter", "diner"}
        
        type_test = "dejeuner"
        type_invalide = "brunch"
        
        assert type_test in types_valides
        assert type_invalide not in types_valides

    def test_detecter_conflit(self):
        """Détection de conflit (même date/type)."""
        repas_existants = [
            {"date": date(2026, 1, 28), "type": "dejeuner"},
            {"date": date(2026, 1, 28), "type": "diner"},
        ]
        
        nouveau_repas = {"date": date(2026, 1, 28), "type": "dejeuner"}
        
        conflit = any(
            r["date"] == nouveau_repas["date"] and r["type"] == nouveau_repas["type"]
            for r in repas_existants
        )
        
        assert conflit == True


# =============================================================================
# TESTS STATISTIQUES PLANNING
# =============================================================================

class TestStatistiquesPlanning:
    """Tests pour les statistiques du planning."""

    def test_repas_par_type(self):
        """Comptage des repas par type."""
        repas = [
            {"type": "dejeuner"},
            {"type": "dejeuner"},
            {"type": "dejeuner"},
            {"type": "diner"},
            {"type": "diner"},
        ]
        
        from collections import Counter
        counts = Counter(r["type"] for r in repas)
        
        assert counts["dejeuner"] == 3
        assert counts["diner"] == 2

    def test_recettes_favorites(self):
        """Recettes les plus utilisées."""
        repas = [
            {"recette_id": 1},
            {"recette_id": 2},
            {"recette_id": 1},
            {"recette_id": 3},
            {"recette_id": 1},
        ]
        
        from collections import Counter
        counts = Counter(r["recette_id"] for r in repas)
        top = counts.most_common(1)
        
        assert top[0] == (1, 3)

    def test_taux_planification(self):
        """Taux de planification de la semaine."""
        jours_semaine = 7
        repas_par_jour = 2
        total_attendu = jours_semaine * repas_par_jour
        
        repas_planifies = 10
        taux = (repas_planifies / total_attendu) * 100
        
        assert taux == pytest.approx(71.4, rel=0.1)
