"""
Tests pour JardinGamificationMixin.

Couvre les méthodes pure logique de gamification:
- calculer_autonomie
- calculer_streak
- calculer_stats
- obtenir_badges
- obtenir_ids_badges
- generer_planning
- generer_previsions_recoltes
- _trouver_prochain_mois
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_catalogue():
    """Catalogue de plantes mock."""
    return {
        "plantes": {
            "tomate": {
                "nom": "Tomate",
                "emoji": "🍅",
                "categorie": "légume-fruit",
                "rendement_kg_m2": 5,
                "plantation_exterieur": [4, 5, 6],
                "recolte": [7, 8, 9],
            },
            "salade": {
                "nom": "Salade",
                "emoji": "🥬",
                "categorie": "légume-feuille",
                "rendement_kg_m2": 3,
                "plantation_exterieur": [3, 4, 5, 6, 7],
                "recolte": [5, 6, 7, 8, 9],
            },
            "carotte": {
                "nom": "Carotte",
                "emoji": "🥕",
                "categorie": "légume-racine",
                "rendement_kg_m2": 4,
                "plantation_exterieur": [3, 4, 5],
                "recolte": [6, 7, 8, 9],
            },
        },
        "objectifs_autonomie": {
            "legumes_fruits_kg": 100,
            "legumes_feuilles_kg": 50,
            "legumes_racines_kg": 60,
            "aromatiques_kg": 5,
        },
    }


@pytest.fixture
def gamification_mixin(mock_catalogue):
    """Instance du mixin avec catalogue mocké."""
    from src.services.maison.jardin_gamification_mixin import JardinGamificationMixin

    # Créer une sous-classe test qui mocke charger_catalogue_plantes
    class TestMixin(JardinGamificationMixin):
        def charger_catalogue_plantes(self):
            return mock_catalogue

    return TestMixin()


@pytest.fixture
def plantes_test():
    """Liste de plantes de test."""
    return [
        {"plante_id": "tomate", "surface_m2": 4, "semis_fait": True, "plante_en_terre": True},
        {"plante_id": "salade", "surface_m2": 2, "semis_fait": True, "plante_en_terre": True},
        {"plante_id": "carotte", "surface_m2": 3, "semis_fait": False, "plante_en_terre": False},
    ]


@pytest.fixture
def recoltes_test():
    """Liste de récoltes de test."""
    return [
        {"plante_id": "tomate", "quantite_kg": 8, "date": str(date.today())},
        {"plante_id": "salade", "quantite_kg": 2, "date": str(date.today() - timedelta(days=1))},
    ]


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER AUTONOMIE
# ═══════════════════════════════════════════════════════════


class TestCalculerAutonomie:
    """Tests pour calculer_autonomie."""

    def test_autonomie_avec_plantes(self, gamification_mixin, plantes_test, recoltes_test):
        """Calcule l'autonomie avec des plantes et récoltes."""
        result = gamification_mixin.calculer_autonomie(plantes_test, recoltes_test)

        assert "production_prevue_kg" in result
        assert "production_reelle_kg" in result
        assert "besoins_kg" in result
        assert "pourcentage_prevu" in result
        assert "pourcentage_reel" in result
        assert "par_categorie" in result

        # Production prévue: tomate 4*5 + salade 2*3 + carotte 3*4 = 20+6+12 = 38 kg
        assert result["production_prevue_kg"] == 38.0

        # Production réelle: 8 + 2 = 10 kg
        assert result["production_reelle_kg"] == 10.0

    def test_autonomie_sans_plantes(self, gamification_mixin):
        """Calcule l'autonomie avec listes vides."""
        result = gamification_mixin.calculer_autonomie([], [])

        assert result["production_prevue_kg"] == 0
        assert result["production_reelle_kg"] == 0
        assert result["pourcentage_prevu"] == 0
        assert result["pourcentage_reel"] == 0

    def test_autonomie_categorie_mapping(self, gamification_mixin, plantes_test, recoltes_test):
        """Vérifie le mapping des catégories."""
        result = gamification_mixin.calculer_autonomie(plantes_test, recoltes_test)

        par_cat = result["par_categorie"]

        # légume-fruit devrait avoir la production des tomates
        assert "légume-fruit" in par_cat
        assert par_cat["légume-fruit"]["prevu"] == 20.0  # 4m² * 5kg/m²


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER STREAK
# ═══════════════════════════════════════════════════════════


class TestCalculerStreak:
    """Tests pour calculer_streak."""

    def test_streak_consecutif(self, gamification_mixin):
        """Calcule un streak de jours consécutifs."""
        today = date.today()
        activites = [
            {"date": str(today)},
            {"date": str(today - timedelta(days=1))},
            {"date": str(today - timedelta(days=2))},
        ]

        streak = gamification_mixin.calculer_streak(activites)
        assert streak == 3

    def test_streak_avec_gap(self, gamification_mixin):
        """Streak interrompu par un gap."""
        today = date.today()
        activites = [
            {"date": str(today)},
            {"date": str(today - timedelta(days=2))},  # Gap day 1
        ]

        streak = gamification_mixin.calculer_streak(activites)
        assert streak == 1  # Seulement aujourd'hui compte

    def test_streak_vide(self, gamification_mixin):
        """Streak zéro si pas d'activités."""
        streak = gamification_mixin.calculer_streak([])
        assert streak == 0

    def test_streak_pas_aujourdhui(self, gamification_mixin):
        """Streak zéro si pas d'activité aujourd'hui."""
        yesterday = str(date.today() - timedelta(days=1))
        activites = [{"date": yesterday}]

        streak = gamification_mixin.calculer_streak(activites)
        assert streak == 0

    def test_streak_date_invalide(self, gamification_mixin):
        """Ignore les dates invalides."""
        today = str(date.today())
        activites = [
            {"date": today},
            {"date": "invalid-date"},
            {"date": None},
        ]

        streak = gamification_mixin.calculer_streak(activites)
        assert streak == 1  # Seulement la date valide compte


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER STATS
# ═══════════════════════════════════════════════════════════


class TestCalculerStats:
    """Tests pour calculer_stats."""

    def test_stats_completes(self, gamification_mixin, plantes_test, recoltes_test):
        """Calcule les statistiques complètes."""
        today = str(date.today())
        activites = [{"date": today}]

        stats = gamification_mixin.calculer_stats(plantes_test, recoltes_test, activites)

        assert stats["semis_total"] == 2  # tomate et salade
        assert stats["nb_plantes"] == 3
        assert stats["recoltes_total"] == 2
        assert stats["varietes_uniques"] == 3
        assert stats["streak"] >= 1
        assert "autonomie_pourcent" in stats
        assert "production_kg" in stats

    def test_stats_sans_activites(self, gamification_mixin, plantes_test, recoltes_test):
        """Calcule stats sans activités explicites."""
        stats = gamification_mixin.calculer_stats(plantes_test, recoltes_test)

        assert stats["semis_total"] == 2
        assert stats["nb_plantes"] == 3

    def test_stats_pratiques_eco(self, gamification_mixin):
        """Compte les pratiques écologiques."""
        plantes_eco = [
            {"plante_id": "tomate", "compost": True, "recup_eau": False},
            {"plante_id": "salade", "compost": False, "recup_eau": True},
        ]

        stats = gamification_mixin.calculer_stats(plantes_eco, [])

        assert stats["pratiques_eco"] == 2  # compost + recup_eau


# ═══════════════════════════════════════════════════════════
# TESTS BADGES
# ═══════════════════════════════════════════════════════════


class TestObtenir_badges:
    """Tests pour obtenir_badges et obtenir_ids_badges."""

    def test_badge_premier_semis(self, gamification_mixin):
        """Badge premier semis débloqué."""
        stats = {"semis_total": 1, "nb_plantes": 0, "recoltes_total": 0, "streak": 0}

        badges = gamification_mixin.obtenir_badges(stats)
        ids = gamification_mixin.obtenir_ids_badges(stats)

        assert "premier_semis" in ids
        # Vérifier structure du badge
        badge = next(b for b in badges if b["id"] == "premier_semis")
        assert badge["nom"] == "Premier Semis"
        assert badge["emoji"] == "🌱"

    def test_badge_pouce_vert(self, gamification_mixin):
        """Badge pouce vert débloqué à 10 plantes."""
        stats = {"semis_total": 0, "nb_plantes": 10, "recoltes_total": 0, "streak": 0}

        ids = gamification_mixin.obtenir_ids_badges(stats)

        assert "pouce_vert" in ids

    def test_badge_jardinier_assidu(self, gamification_mixin):
        """Badge jardinier assidu débloqué à 7 jours de streak."""
        stats = {"semis_total": 0, "nb_plantes": 0, "recoltes_total": 0, "streak": 7}

        ids = gamification_mixin.obtenir_ids_badges(stats)

        assert "jardinier_assidu" in ids

    def test_badge_autosuffisant_50(self, gamification_mixin):
        """Badge 50% autonomie."""
        stats = {
            "semis_total": 0,
            "nb_plantes": 0,
            "recoltes_total": 0,
            "streak": 0,
            "autonomie_pourcent": 55,
        }

        ids = gamification_mixin.obtenir_ids_badges(stats)

        assert "autosuffisant_50" in ids
        assert "autosuffisant_25" in ids  # Les deux doivent être débloqués

    def test_aucun_badge(self, gamification_mixin):
        """Aucun badge avec stats vides."""
        stats = {
            "semis_total": 0,
            "nb_plantes": 0,
            "recoltes_total": 0,
            "streak": 0,
            "varietes_uniques": 0,
            "autonomie_pourcent": 0,
            "pratiques_eco": 0,
        }

        badges = gamification_mixin.obtenir_badges(stats)

        assert len(badges) == 0


# ═══════════════════════════════════════════════════════════
# TESTS PLANNING
# ═══════════════════════════════════════════════════════════


class TestGenererPlanning:
    """Tests pour generer_planning."""

    def test_planning_plantation(self, gamification_mixin):
        """Génère planning de plantation pour plante non en terre."""
        plantes = [{"plante_id": "tomate", "plante_en_terre": False}]

        planning = gamification_mixin.generer_planning(plantes, horizon_mois=12)

        plantations = [p for p in planning if p["type"] == "plantation"]
        assert len(plantations) >= 1
        assert plantations[0]["titre"] == "Planter Tomate"
        assert plantations[0]["emoji"] == "🍅"

    def test_planning_recolte(self, gamification_mixin):
        """Génère planning de récolte pour plante en terre."""
        plantes = [{"plante_id": "tomate", "plante_en_terre": True}]

        planning = gamification_mixin.generer_planning(plantes, horizon_mois=12)

        recoltes = [p for p in planning if p["type"] == "recolte"]
        assert len(recoltes) >= 1
        assert recoltes[0]["titre"] == "Récolter Tomate"

    def test_planning_trie_par_mois(self, gamification_mixin, plantes_test):
        """Planning trié par mois croissant."""
        planning = gamification_mixin.generer_planning(plantes_test, horizon_mois=12)

        if len(planning) >= 2:
            for i in range(1, len(planning)):
                assert planning[i]["mois"] >= planning[i - 1]["mois"]

    def test_planning_plante_inconnue(self, gamification_mixin):
        """Ignore les plantes non présentes dans le catalogue."""
        plantes = [{"plante_id": "plante_inexistante", "plante_en_terre": False}]

        planning = gamification_mixin.generer_planning(plantes)

        assert len(planning) == 0


# ═══════════════════════════════════════════════════════════
# TESTS PRÉVISIONS RÉCOLTES
# ═══════════════════════════════════════════════════════════


class TestGenererPrevisionsRecoltes:
    """Tests pour generer_previsions_recoltes."""

    def test_previsions_plantes_en_terre(self, gamification_mixin):
        """Génère prévisions pour plantes en terre en période de récolte."""
        # Simuler que c'est juillet (mois 7 = période récolte tomates)
        with patch("src.services.maison.jardin_gamification_mixin.date") as mock_date:
            mock_date.today.return_value = date(2025, 7, 15)

            plantes = [{"plante_id": "tomate", "surface_m2": 4, "plante_en_terre": True}]

            previsions = gamification_mixin.generer_previsions_recoltes(plantes)

            # Tomate récolte en [7,8,9], donc devrait apparaître
            assert len(previsions) >= 1
            prev = previsions[0]
            assert prev["nom"] == "Tomate"
            assert prev["quantite_prevue_kg"] == 20.0  # 4m² * 5kg/m²

    def test_previsions_ignore_non_en_terre(self, gamification_mixin):
        """N'inclut pas les plantes pas encore en terre."""
        plantes = [{"plante_id": "tomate", "surface_m2": 4, "plante_en_terre": False}]

        previsions = gamification_mixin.generer_previsions_recoltes(plantes)

        # Tomate pas en terre = pas de prévision
        assert len(previsions) == 0


# ═══════════════════════════════════════════════════════════
# TESTS TROUVER PROCHAIN MOIS
# ═══════════════════════════════════════════════════════════


class TestTrouverProchainMois:
    """Tests pour _trouver_prochain_mois."""

    def test_prochain_mois_dans_horizon(self, gamification_mixin):
        """Trouve le prochain mois dans l'horizon donné."""
        # En janvier, chercher un mois de plantation [4,5,6] sur 6 mois
        result = gamification_mixin._trouver_prochain_mois(1, [4, 5, 6], 6)
        assert result == 4  # Avril

    def test_prochain_mois_cyclique(self, gamification_mixin):
        """Trouve le prochain mois en cyclant sur l'année."""
        # En novembre, chercher [1,2,3] sur 6 mois
        result = gamification_mixin._trouver_prochain_mois(11, [1, 2, 3], 6)
        assert result == 1  # Janvier prochain

    def test_prochain_mois_hors_horizon(self, gamification_mixin):
        """Retourne None si pas de mois dans l'horizon."""
        # En janvier, chercher [11,12] sur 3 mois
        result = gamification_mixin._trouver_prochain_mois(1, [11, 12], 3)
        assert result is None

    def test_prochain_mois_liste_vide(self, gamification_mixin):
        """Retourne None si liste de mois vide."""
        result = gamification_mixin._trouver_prochain_mois(1, [], 12)
        assert result is None

    def test_prochain_mois_actuel_inclus(self, gamification_mixin):
        """Trouve le mois actuel s'il est dans la liste."""
        result = gamification_mixin._trouver_prochain_mois(5, [5, 6, 7], 6)
        assert result == 5  # Mai (mois actuel)
