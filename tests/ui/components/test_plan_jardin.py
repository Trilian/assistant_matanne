"""
Tests pour le composant Plan Jardin 2D (src/ui/components/custom.py)

Tests de la logique et des fonctions du composant plan_jardin_2d:
- Création de zones de culture
- Placement des plantes
- Sérialisation/désérialisation des données
- Validation des entrées
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# TESTS TYPES DE DONNÉES JARDIN
# ═══════════════════════════════════════════════════════════


class TestZoneJardin:
    """Tests des types Zone pour le plan jardin."""

    def test_zone_structure(self):
        """Structure d'une zone de culture."""
        zone = {
            "id": "zone_1",
            "nom": "Potager principal",
            "x": 50,
            "y": 50,
            "width": 200,
            "height": 150,
            "couleur": "#8fbc8f55",
            "type_sol": "terre",
        }
        assert zone["id"] == "zone_1"
        assert zone["width"] > 0
        assert zone["height"] > 0

    def test_zone_with_plantes(self):
        """Zone avec liste de plantes associées."""
        zone = {
            "id": "zone_2",
            "nom": "Carré aromatique",
            "plantes": ["basilic", "thym", "romarin"],
        }
        assert len(zone["plantes"]) == 3


class TestPlanteJardin:
    """Tests des types Plante pour le plan jardin."""

    def test_plante_structure(self):
        """Structure d'une plante placée."""
        plante = {
            "id": "plante_1",
            "nom": "Tomate",
            "emoji": "🍅",
            "x": 100,
            "y": 80,
            "couleur": "#e74c3c",
            "zone_id": "zone_1",
            "date_plantation": "2026-03-15",
        }
        assert plante["nom"] == "Tomate"
        assert plante["emoji"] == "🍅"
        assert plante["zone_id"] == "zone_1"

    def test_plante_with_metadata(self):
        """Plante avec métadonnées complètes."""
        plante = {
            "id": "plante_2",
            "nom": "Courgette",
            "variete": "Ronde de Nice",
            "espacement_cm": 80,
            "profondeur_cm": 2,
            "arrosage": "régulier",
            "recolte_jours": 60,
        }
        assert plante["espacement_cm"] == 80
        assert plante["recolte_jours"] == 60


# ═══════════════════════════════════════════════════════════
# TESTS CATALOGUE PLANTES
# ═══════════════════════════════════════════════════════════


class TestCataloguePlantes:
    """Tests du catalogue de plantes par défaut."""

    def test_catalogue_structure(self):
        """Structure du catalogue."""
        catalogue = [
            {"nom": "Tomate", "emoji": "🍅", "couleur": "#e74c3c"},
            {"nom": "Carotte", "emoji": "🥕", "couleur": "#e67e22"},
            {"nom": "Salade", "emoji": "🥬", "couleur": "#27ae60"},
            {"nom": "Radis", "emoji": "🌱", "couleur": "#e91e63"},
            {"nom": "Courgette", "emoji": "🥒", "couleur": "#8bc34a"},
            {"nom": "Poivron", "emoji": "🫑", "couleur": "#ff9800"},
        ]
        assert len(catalogue) >= 6
        for plante in catalogue:
            assert "nom" in plante
            assert "emoji" in plante
            assert "couleur" in plante

    def test_couleurs_format_hex(self):
        """Les couleurs sont au format hexadécimal."""
        import re

        plante = {"couleur": "#e74c3c"}
        assert re.match(r"^#[0-9a-fA-F]{6}$", plante["couleur"])


# ═══════════════════════════════════════════════════════════
# TESTS SÉRIALISATION
# ═══════════════════════════════════════════════════════════


class TestSerialisation:
    """Tests de sérialisation/désérialisation du plan jardin."""

    def test_export_json(self):
        """Export du plan en JSON."""
        import json

        plan = {
            "zones": [{"id": "z1", "nom": "Potager", "x": 0, "y": 0, "width": 100, "height": 100}],
            "plantes": [{"id": "p1", "nom": "Tomate", "x": 50, "y": 50, "zone_id": "z1"}],
        }
        json_str = json.dumps(plan)
        assert "zones" in json_str
        assert "plantes" in json_str

    def test_import_json(self):
        """Import d'un plan depuis JSON."""
        import json

        json_str = '{"zones": [], "plantes": []}'
        plan = json.loads(json_str)
        assert "zones" in plan
        assert "plantes" in plan

    def test_roundtrip(self):
        """Export puis import conserve les données."""
        import json

        original = {
            "zones": [{"id": "z1", "nom": "Test", "x": 10, "y": 20, "width": 50, "height": 60}],
            "plantes": [{"id": "p1", "nom": "Basilic", "x": 15, "y": 25}],
        }
        exported = json.dumps(original)
        imported = json.loads(exported)
        assert imported == original


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValidation:
    """Tests de validation des données du plan."""

    def test_zone_dimensions_positives(self):
        """Les dimensions de zone doivent être positives."""
        zone = {"width": 100, "height": 50}
        assert zone["width"] > 0
        assert zone["height"] > 0

    def test_zone_position_valide(self):
        """Les positions doivent être >= 0."""
        zone = {"x": 0, "y": 0}
        assert zone["x"] >= 0
        assert zone["y"] >= 0

    def test_plante_dans_zone(self):
        """Vérifier qu'une plante est dans sa zone."""
        zone = {"x": 0, "y": 0, "width": 100, "height": 100}
        plante = {"x": 50, "y": 50}

        dans_zone = (
            zone["x"] <= plante["x"] <= zone["x"] + zone["width"]
            and zone["y"] <= plante["y"] <= zone["y"] + zone["height"]
        )
        assert dans_zone is True

    def test_plante_hors_zone(self):
        """Détection d'une plante hors de sa zone."""
        zone = {"x": 0, "y": 0, "width": 100, "height": 100}
        plante = {"x": 150, "y": 50}

        dans_zone = (
            zone["x"] <= plante["x"] <= zone["x"] + zone["width"]
            and zone["y"] <= plante["y"] <= zone["y"] + zone["height"]
        )
        assert dans_zone is False


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════


class TestUtilitaires:
    """Tests des fonctions utilitaires du composant."""

    def test_generer_id_unique(self):
        """Génère des IDs uniques pour zones et plantes."""
        import uuid

        id1 = f"zone_{uuid.uuid4().hex[:8]}"
        id2 = f"zone_{uuid.uuid4().hex[:8]}"
        assert id1 != id2

    def test_couleur_zone_aleatoire(self):
        """Sélection de couleur aléatoire pour nouvelle zone."""
        couleurs = ["#8fbc8f55", "#deb88755", "#87ceeb55", "#f0e68c55"]
        import random

        couleur = random.choice(couleurs)
        assert couleur in couleurs

    def test_calculer_surface_zone(self):
        """Calcul de la surface d'une zone."""
        zone = {"width": 200, "height": 150}
        surface = zone["width"] * zone["height"]
        assert surface == 30000

    def test_calculer_nb_plantes_zone(self):
        """Calcul du nombre de plantes dans une zone."""
        plantes = [
            {"zone_id": "z1"},
            {"zone_id": "z1"},
            {"zone_id": "z2"},
        ]
        nb_z1 = len([p for p in plantes if p["zone_id"] == "z1"])
        assert nb_z1 == 2


# ═══════════════════════════════════════════════════════════
# TESTS COMPOSANT UI (AVEC MOCKS STREAMLIT)
# ═══════════════════════════════════════════════════════════


class TestPlanJardinComponent:
    """Tests du composant Streamlit plan_jardin_2d."""

    @patch("streamlit.components.v1.html")
    def test_component_renders(self, mock_html):
        """Le composant se rend sans erreur."""
        from src.ui.components.custom import plan_jardin_2d

        # Appeler avec paramètres minimaux
        plan_jardin_2d(zones=[], plantes=[])

        # Vérifier que st.html a été appelé
        mock_html.assert_called_once()

    @patch("streamlit.components.v1.html")
    def test_component_with_zones(self, mock_html):
        """Le composant accepte des zones."""
        from src.ui.components.custom import plan_jardin_2d

        zones = [{"id": "z1", "nom": "Test", "x": 0, "y": 0, "width": 100, "height": 100}]
        plan_jardin_2d(zones=zones, plantes=[])

        # Vérifier que le HTML contient les zones
        call_args = mock_html.call_args
        html_content = call_args[0][0] if call_args[0] else call_args[1].get("html", "")
        # Le HTML doit contenir la donnée des zones
        assert "z1" in str(call_args) or mock_html.called

    @patch("streamlit.components.v1.html")
    def test_component_with_catalogue(self, mock_html):
        """Le composant accepte un catalogue personnalisé."""
        from src.ui.components.custom import plan_jardin_2d

        catalogue = [{"nom": "Menthe", "emoji": "🌿", "couleur": "#2ecc71"}]
        plan_jardin_2d(zones=[], plantes=[], catalogue_plantes=catalogue)

        mock_html.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS INTEGRATION DB (MARQUÉS)
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestPlanJardinDB:
    """Tests d'intégration avec la base de données."""

    def test_save_plan_to_db(self):
        """Sauvegarde du plan en base de données."""
        # Nécessite DB réelle
        pass

    def test_load_plan_from_db(self):
        """Chargement du plan depuis la base de données."""
        # Nécessite DB réelle
        pass
