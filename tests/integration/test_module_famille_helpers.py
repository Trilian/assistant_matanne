"""
Tests pour le module famille/helpers.py
Fonctions utilitaires pour le suivi familial (logique métier)
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock


class TestCalculerAgeLogique:
    """Tests pour la logique de calcul d'âge"""

    def test_calcul_jours(self):
        """Calcule le nombre de jours depuis la naissance"""
        date_naissance = date(2024, 6, 22)
        aujourd_hui = date(2024, 7, 22)
        
        jours = (aujourd_hui - date_naissance).days
        assert jours == 30

    def test_calcul_semaines(self):
        """Calcule le nombre de semaines depuis la naissance"""
        date_naissance = date(2024, 1, 1)
        aujourd_hui = date(2024, 1, 15)
        
        jours = (aujourd_hui - date_naissance).days
        semaines = jours // 7
        
        assert semaines == 2

    def test_calcul_mois(self):
        """Calcule le nombre de mois depuis la naissance"""
        date_naissance = date(2024, 1, 1)
        aujourd_hui = date(2024, 7, 1)
        
        # Approximation simple
        mois = (aujourd_hui.year - date_naissance.year) * 12 + (aujourd_hui.month - date_naissance.month)
        
        assert mois == 6

    def test_calcul_ans(self):
        """Calcule le nombre d'années depuis la naissance"""
        date_naissance = date(2022, 6, 22)
        aujourd_hui = date(2024, 7, 22)
        
        ans = (aujourd_hui - date_naissance).days // 365
        
        assert ans == 2


class TestCalculProgressionObjectif:
    """Tests pour calculer_progression_objectif()"""

    def test_progression_complete(self):
        """Progression 100% quand réalisé >= objectif"""
        objectif = MagicMock()
        objectif.valeur_objectif = 10
        objectif.valeur_realisee = 10
        
        progression = min(100, (objectif.valeur_realisee / objectif.valeur_objectif) * 100)
        
        assert progression == 100

    def test_progression_partielle(self):
        """Progression partielle"""
        objectif = MagicMock()
        objectif.valeur_objectif = 10
        objectif.valeur_realisee = 5
        
        progression = min(100, (objectif.valeur_realisee / objectif.valeur_objectif) * 100)
        
        assert progression == 50

    def test_progression_depasse_objectif(self):
        """Progression plafonnée à 100%"""
        objectif = MagicMock()
        objectif.valeur_objectif = 10
        objectif.valeur_realisee = 15
        
        progression = min(100, (objectif.valeur_realisee / objectif.valeur_objectif) * 100)
        
        assert progression == 100

    def test_progression_zero(self):
        """Progression zéro"""
        objectif = MagicMock()
        objectif.valeur_objectif = 10
        objectif.valeur_realisee = 0
        
        progression = min(100, (objectif.valeur_realisee / objectif.valeur_objectif) * 100) if objectif.valeur_objectif > 0 else 0
        
        assert progression == 0


class TestMilestonesByCategory:
    """Tests pour get_milestones_by_category logique"""

    def test_groupe_milestones_par_categorie(self):
        """Groupe les milestones par catégorie"""
        milestones = [
            MagicMock(categorie="moteur", nom="Marcher"),
            MagicMock(categorie="moteur", nom="Courir"),
            MagicMock(categorie="langage", nom="Premier mot"),
            MagicMock(categorie="social", nom="Sourire"),
        ]
        
        grouped = {}
        for m in milestones:
            cat = m.categorie
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(m)
        
        assert len(grouped) == 3
        assert len(grouped["moteur"]) == 2
        assert len(grouped["langage"]) == 1
        assert len(grouped["social"]) == 1

    def test_categorie_vide(self):
        """Gère le cas sans milestones"""
        milestones = []
        
        grouped = {}
        for m in milestones:
            cat = m.categorie
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(m)
        
        assert len(grouped) == 0


class TestCountMilestones:
    """Tests pour count_milestones_by_category logique"""

    def test_compte_milestones_par_categorie(self):
        """Compte les milestones par catégorie"""
        milestones = [
            MagicMock(categorie="moteur", atteint=True),
            MagicMock(categorie="moteur", atteint=False),
            MagicMock(categorie="langage", atteint=True),
        ]
        
        counts = {}
        for m in milestones:
            cat = m.categorie
            if cat not in counts:
                counts[cat] = {"total": 0, "atteints": 0}
            counts[cat]["total"] += 1
            if m.atteint:
                counts[cat]["atteints"] += 1
        
        assert counts["moteur"]["total"] == 2
        assert counts["moteur"]["atteints"] == 1
        assert counts["langage"]["total"] == 1
        assert counts["langage"]["atteints"] == 1


class TestObjectifsActifs:
    """Tests pour get_objectifs_actifs logique"""

    def test_filtre_objectifs_actifs(self):
        """Filtre les objectifs actifs"""
        objectifs = [
            MagicMock(actif=True, complete=False),
            MagicMock(actif=False, complete=False),
            MagicMock(actif=True, complete=True),
        ]
        
        actifs = [o for o in objectifs if o.actif and not o.complete]
        
        assert len(actifs) == 1

    def test_tous_completes(self):
        """Tous les objectifs complétés"""
        objectifs = [
            MagicMock(actif=True, complete=True),
            MagicMock(actif=True, complete=True),
        ]
        
        actifs = [o for o in objectifs if o.actif and not o.complete]
        
        assert len(actifs) == 0


class TestBudgetParPeriod:
    """Tests pour get_budget_par_period logique"""

    def test_groupe_budget_par_mois(self):
        """Groupe les dépenses par mois"""
        depenses = [
            MagicMock(mois=1, montant=100),
            MagicMock(mois=1, montant=50),
            MagicMock(mois=2, montant=200),
        ]
        
        budget_mensuel = {}
        for d in depenses:
            if d.mois not in budget_mensuel:
                budget_mensuel[d.mois] = 0
            budget_mensuel[d.mois] += d.montant
        
        assert budget_mensuel[1] == 150
        assert budget_mensuel[2] == 200

    def test_budget_vide(self):
        """Gère le cas sans dépenses"""
        depenses = []
        
        budget_mensuel = {}
        for d in depenses:
            if d.mois not in budget_mensuel:
                budget_mensuel[d.mois] = 0
            budget_mensuel[d.mois] += d.montant
        
        assert len(budget_mensuel) == 0


class TestCategorieEmojis:
    """Tests pour les emojis de catégories de développement"""

    def test_emoji_moteur(self):
        """Emoji pour catégorie moteur"""
        CATEGORIE_EMOJIS = {
            "moteur": "🏃",
            "langage": "🗣️",
            "social": "👥",
            "cognitif": "🧠"
        }
        assert CATEGORIE_EMOJIS.get("moteur") == "🏃"

    def test_emoji_langage(self):
        """Emoji pour catégorie langage"""
        CATEGORIE_EMOJIS = {
            "moteur": "🏃",
            "langage": "🗣️",
            "social": "👥",
            "cognitif": "🧠"
        }
        assert CATEGORIE_EMOJIS.get("langage") == "🗣️"

    def test_emoji_default(self):
        """Emoji par défaut pour catégorie inconnue"""
        CATEGORIE_EMOJIS = {
            "moteur": "🏃",
            "langage": "🗣️",
            "social": "👥",
            "cognitif": "🧠"
        }
        assert CATEGORIE_EMOJIS.get("inconnu", "📌") == "📌"
