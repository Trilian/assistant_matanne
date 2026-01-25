"""
Tests Composants Planning UI

Tests pour composants réutilisables du module planning
✅ Badges (charge, priorité)
✅ Cartes (repas, activité, projet, event)
✅ Sélecteurs (semaine)
✅ Affichages (alertes, stats)

À lancer: pytest tests/test_planning_components.py -v
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

# Import des composants
from src.modules.planning.components import (
    afficher_badge_charge,
    afficher_badge_priorite,
    afficher_badge_jules_adapte,
    carte_repas,
    carte_activite,
    carte_projet,
    carte_event,
    selecteur_semaine,
    afficher_liste_alertes,
    afficher_stats_semaine,
)


# ═══════════════════════════════════════════════════════════
# TESTS: BADGES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBadges:
    """Tests badges"""

    def test_badge_charge_faible(self):
        """Badge charge faible"""
        result = afficher_badge_charge(25)

        assert result is not None
        assert "faible" in result.lower() or "🟢" in result

    def test_badge_charge_normal(self):
        """Badge charge normal"""
        result = afficher_badge_charge(50)

        assert result is not None
        assert "normal" in result.lower() or "🟡" in result

    def test_badge_charge_intense(self):
        """Badge charge intense"""
        result = afficher_badge_charge(85)

        assert result is not None
        assert "intense" in result.lower() or "🔴" in result

    def test_badge_charge_limites(self):
        """Badge charge aux limites"""
        # Minimum
        result_min = afficher_badge_charge(0)
        assert result_min is not None

        # Maximum
        result_max = afficher_badge_charge(100)
        assert result_max is not None

    def test_badge_priorite_basse(self):
        """Badge priorité basse"""
        result = afficher_badge_priorite("basse")

        assert result is not None
        assert "basse" in result.lower() or "⬜" in result

    def test_badge_priorite_normale(self):
        """Badge priorité normale"""
        result = afficher_badge_priorite("normale")

        assert result is not None
        assert "normale" in result.lower() or "🟨" in result

    def test_badge_priorite_haute(self):
        """Badge priorité haute"""
        result = afficher_badge_priorite("haute")

        assert result is not None
        assert "haute" in result.lower() or "🔴" in result

    def test_badge_jules_adapte_oui(self):
        """Badge Jules adapté - oui"""
        result = afficher_badge_jules_adapte(True)

        assert result is not None
        assert "Jules" in result or "✅" in result

    def test_badge_jules_adapte_non(self):
        """Badge Jules adapté - non"""
        result = afficher_badge_jules_adapte(False)

        assert result is not None
        assert "adultes" in result.lower() or "❌" in result


# ═══════════════════════════════════════════════════════════
# TESTS: CARTES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCartes:
    """Tests cartes"""

    def test_carte_repas_minimal(self):
        """Carte repas minimale"""
        repas_data = {
            "type": "dîner",
            "recette": "Pâtes",
        }

        result = carte_repas(repas_data)

        assert result is not None
        assert "Pâtes" in result or "dîner" in result.lower()

    def test_carte_repas_complet(self):
        """Carte repas complète"""
        repas_data = {
            "type": "dîner",
            "recette": "Pizza maison",
            "portions": 4,
            "temps_total": 45,
        }

        result = carte_repas(repas_data)

        assert result is not None
        assert "Pizza maison" in result
        assert ("4" in result or "portions" in result.lower())

    def test_carte_activite_minimal(self):
        """Carte activité minimale"""
        activite_data = {
            "titre": "Parc",
            "type": "loisirs",
        }

        result = carte_activite(activite_data)

        assert result is not None
        assert "Parc" in result

    def test_carte_activite_avec_jules(self):
        """Carte activité adaptée Jules"""
        activite_data = {
            "titre": "Parc",
            "type": "loisirs",
            "pour_jules": True,
        }

        result = carte_activite(activite_data)

        assert result is not None
        assert "Parc" in result
        assert ("Jules" in result or "✅" in result)

    def test_carte_activite_avec_budget(self):
        """Carte activité avec budget"""
        activite_data = {
            "titre": "Musée",
            "type": "culturel",
            "pour_jules": True,
            "budget": 40.0,
        }

        result = carte_activite(activite_data)

        assert result is not None
        assert "Musée" in result
        assert ("40" in result or "€" in result)

    def test_carte_projet_minimal(self):
        """Carte projet minimale"""
        projet_data = {
            "nom": "Rénovation",
            "priorite": "haute",
        }

        result = carte_projet(projet_data)

        assert result is not None
        assert "Rénovation" in result

    def test_carte_projet_avec_priorite(self):
        """Carte projet avec priorité"""
        projet_data = {
            "nom": "Rénovation cuisine",
            "priorite": "haute",
            "statut": "en_cours",
        }

        result = carte_projet(projet_data)

        assert result is not None
        assert "Rénovation cuisine" in result
        assert ("haute" in result.lower() or "🔴" in result)

    def test_carte_event_minimal(self):
        """Carte événement minimale"""
        event_data = {
            "titre": "RDV",
            "type": "santé",
        }

        result = carte_event(event_data)

        assert result is not None
        assert "RDV" in result

    def test_carte_event_avec_details(self):
        """Carte événement avec détails"""
        event_data = {
            "titre": "RDV pédiatre",
            "type": "santé",
            "heure": "10:00",
            "lieu": "Clinique",
        }

        result = carte_event(event_data)

        assert result is not None
        assert "RDV pédiatre" in result
        assert ("10:00" in result or "Clinique" in result)


# ═══════════════════════════════════════════════════════════
# TESTS: SÉLECTEURS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSelecteurs:
    """Tests sélecteurs"""

    @patch("streamlit.columns")
    @patch("streamlit.button")
    def test_selecteur_semaine_structure(self, mock_button, mock_columns):
        """Sélecteur semaine structure"""
        # Mock Streamlit
        mock_columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_button.return_value = False

        today = date.today()

        # Appel fonction
        # Note: Cette fonction a des side-effects Streamlit, donc le test est limité
        # On teste juste qu'il ne crash pas
        try:
            selecteur_semaine(key_prefix="test")
            assert True
        except Exception as e:
            pytest.fail(f"selecteur_semaine raised {e}")


# ═══════════════════════════════════════════════════════════
# TESTS: AFFICHAGES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAffichages:
    """Tests affichages"""

    def test_afficher_liste_alertes_vide(self):
        """Affichage alertes vide"""
        result = afficher_liste_alertes([])

        # Doit retourner quelque chose (peut être vide ou message)
        assert result is not None

    def test_afficher_liste_alertes_simple(self):
        """Affichage alertes simples"""
        alertes = ["Jour chargé", "Pas d'activité Jules"]

        result = afficher_liste_alertes(alertes)

        assert result is not None
        assert "Jour chargé" in result or "Jules" in result

    def test_afficher_liste_alertes_nombreuses(self):
        """Affichage alertes nombreuses"""
        alertes = [f"Alerte {i}" for i in range(10)]

        result = afficher_liste_alertes(alertes)

        assert result is not None

    def test_afficher_stats_semaine_minimal(self):
        """Affichage stats semaine minimal"""
        stats = {
            "total_repas": 10,
            "total_activites": 5,
        }

        result = afficher_stats_semaine(stats)

        assert result is not None
        assert "10" in result or "repas" in result.lower()

    def test_afficher_stats_semaine_complet(self):
        """Affichage stats semaine complet"""
        stats = {
            "total_repas": 12,
            "total_activites": 8,
            "total_events": 5,
            "total_projets": 3,
            "charge_moyenne": 55,
            "budget_total": 350.50,
        }

        result = afficher_stats_semaine(stats)

        assert result is not None
        assert ("12" in result or "repas" in result.lower())
        assert ("55" in result or "charge" in result.lower())


# ═══════════════════════════════════════════════════════════
# TESTS: FORMATAGE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFormatage:
    """Tests formatage données"""

    def test_formatage_badge_consiste(self):
        """Formatage badge cohérent"""
        # Même input → même output
        result1 = afficher_badge_charge(50)
        result2 = afficher_badge_charge(50)

        assert result1 == result2

    def test_formatage_carte_consiste(self):
        """Formatage carte cohérent"""
        repas = {"type": "dîner", "recette": "Pâtes"}

        result1 = carte_repas(repas)
        result2 = carte_repas(repas)

        assert result1 == result2

    def test_badge_avec_donnees_speciales(self):
        """Badge avec caractères spéciaux"""
        result = afficher_badge_charge(50)

        # Doit gérer emojis
        assert isinstance(result, str)

    def test_carte_avec_donnees_speciales(self):
        """Carte avec données spéciales"""
        repas = {
            "type": "dîner",
            "recette": "Pâtes à l'ail & huile d'olive",
        }

        result = carte_repas(repas)

        assert result is not None
        assert "ail" in result.lower() or "olive" in result.lower()


# ═══════════════════════════════════════════════════════════
# TESTS: INTÉGRATION COMPOSANTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIntegrationComposants:
    """Tests intégration composants"""

    def test_sequence_badges(self):
        """Sequence badges"""
        # Afficher badges pour charges variables
        for score in [10, 35, 50, 70, 90]:
            result = afficher_badge_charge(score)
            assert result is not None

    def test_sequence_cartes(self):
        """Sequence cartes"""
        cartes = [
            carte_repas({"type": "petit-déj", "recette": "Porridge"}),
            carte_activite({"titre": "Parc", "pour_julius": True}),
            carte_projet({"nom": "Projet", "priorite": "haute"}),
            carte_event({"titre": "RDV", "heure": "10:00"}),
        ]

        for carte in cartes:
            assert carte is not None

    def test_priorites_differentes(self):
        """Priorités différentes"""
        for priorite in ["basse", "normale", "haute"]:
            result = afficher_badge_priorite(priorite)
            assert result is not None

    def test_charges_differentes(self):
        """Charges différentes"""
        scores = [0, 25, 50, 75, 100]
        labels = ["faible", "faible", "normal", "intense", "intense"]

        for score, label in zip(scores, labels):
            result = afficher_badge_charge(score)
            assert result is not None
            assert label.lower() in result.lower() or "🟢" in result or "🟡" in result or "🔴" in result


# ═══════════════════════════════════════════════════════════
# MARQUEURS
# ═══════════════════════════════════════════════════════════

pytest.mark.unit
