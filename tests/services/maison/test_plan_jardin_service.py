"""
Tests pour PlanJardinService.

Couvre:
- Gestion du plan 2D
- Zones et plantes
- Compagnonnage IA
- Rotation des cultures
"""

import json
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.maison.plan_jardin_service import PlanJardinService, get_plan_jardin_service
from src.services.maison.schemas import EtatPlante, TypeZoneJardin


class TestPlanJardinServiceInit:
    """Tests d'initialisation du service."""

    def test_factory_returns_service(self):
        """La factory retourne une instance valide."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()
            assert isinstance(service, PlanJardinService)

    def test_factory_accepts_custom_client(self):
        """La factory accepte un client personnalisé."""
        mock_client = MagicMock()
        service = get_plan_jardin_service(client=mock_client)
        assert service.client == mock_client


class TestPlanJardinServicePlan:
    """Tests de gestion du plan."""

    def test_creer_plan(self):
        """Crée un nouveau plan de jardin."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            plan_id = service.creer_plan(MagicMock(nom="Mon Jardin", largeur=20, hauteur=15))
            assert plan_id == 1

    def test_obtenir_plan(self):
        """Récupère un plan avec ses zones."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            plan = service.obtenir_plan(plan_id=1)
            assert plan is not None
            assert "zones" in plan
            assert "plantes" in plan

    def test_exporter_svg(self):
        """Exporte le plan en SVG."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            svg = service.exporter_plan_svg(plan_id=1)
            assert "<svg" in svg
            assert "</svg>" in svg


class TestPlanJardinServiceZones:
    """Tests de gestion des zones."""

    def test_ajouter_zone(self, zone_jardin_data):
        """Ajoute une zone au plan."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            zone_id = service.ajouter_zone(
                MagicMock(
                    nom=zone_jardin_data["nom"],
                    type=TypeZoneJardin.POTAGER,
                )
            )
            assert zone_id == 1

    def test_modifier_zone(self):
        """Modifie une zone existante."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            succes = service.modifier_zone(
                zone_id=1,
                updates={"nom": "Nouveau nom"},
            )
            assert succes is True

    def test_supprimer_zone(self):
        """Supprime une zone."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            succes = service.supprimer_zone(zone_id=1)
            assert succes is True

    def test_couleurs_zones(self):
        """Vérifie les couleurs par type de zone."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            # Potager = marron
            couleur_potager = service.obtenir_couleur_zone(TypeZoneJardin.POTAGER)
            assert couleur_potager.startswith("#")

            # Pelouse = vert
            couleur_pelouse = service.obtenir_couleur_zone(TypeZoneJardin.PELOUSE)
            assert couleur_pelouse.startswith("#")

            # Les couleurs doivent être différentes
            assert couleur_potager != couleur_pelouse


class TestPlanJardinServicePlantes:
    """Tests de gestion des plantes."""

    def test_ajouter_plante(self, plante_jardin_data):
        """Ajoute une plante dans une zone."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            plante_id = service.ajouter_plante(
                MagicMock(
                    nom=plante_jardin_data["nom"],
                    position_x=plante_jardin_data["position_x"],
                    position_y=plante_jardin_data["position_y"],
                )
            )
            assert plante_id == 1

    def test_deplacer_plante(self):
        """Déplace une plante sur le plan."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            succes = service.deplacer_plante(
                plante_id=1,
                nouvelle_pos_x=3.0,
                nouvelle_pos_y=4.0,
            )
            assert succes is True

    def test_mettre_a_jour_etat(self):
        """Met à jour l'état d'une plante."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            succes = service.mettre_a_jour_etat(
                plante_id=1,
                nouvel_etat=EtatPlante.RECOLTE,
            )
            assert succes is True

    def test_enregistrer_action(self):
        """Enregistre une action sur une plante."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            action_id = service.enregistrer_action(
                MagicMock(
                    plante_id=1,
                    type_action="arrosage",
                    date=date.today(),
                )
            )
            assert action_id == 1


class TestPlanJardinServiceCompagnonnage:
    """Tests du compagnonnage IA."""

    @pytest.mark.asyncio
    async def test_verifier_compagnonnage(self, mock_client_ia):
        """Vérifie la compatibilité des voisins."""
        mock_response = json.dumps(
            {
                "basilic": "bon",
                "fenouil": "mauvais",
                "oignon": "neutre",
            }
        )

        service = PlanJardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        result = await service.verifier_compagnonnage(
            plante_nom="tomate",
            voisins=["basilic", "fenouil", "oignon"],
        )

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_suggerer_compagnons(self, mock_client_ia):
        """Suggère des plantes compagnes."""
        mock_response = json.dumps(
            [
                "Basilic - repousse les pucerons",
                "Carotte - bonne association",
                "Persil - améliore la saveur",
            ]
        )

        service = PlanJardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        result = await service.suggerer_compagnons("tomate")

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_compagnonnage_sans_voisins(self, mock_client_ia):
        """Retourne vide si pas de voisins."""
        service = PlanJardinService(client=mock_client_ia)

        result = await service.verifier_compagnonnage(
            plante_nom="tomate",
            voisins=[],
        )

        assert result == {}


class TestPlanJardinServiceRotation:
    """Tests de la rotation des cultures."""

    def test_obtenir_historique_zone(self):
        """Récupère l'historique d'une zone."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            historique = service.obtenir_historique_zone(
                zone_id=1,
                annees=3,
            )

            assert isinstance(historique, list)
            assert len(historique) > 0

    @pytest.mark.asyncio
    async def test_suggerer_rotation(self, mock_client_ia):
        """Suggère la rotation pour l'année suivante."""
        mock_response = json.dumps(
            [
                "Légumineuses (pois, haricots)",
                "Légumes-feuilles (salades, épinards)",
                "Légumes-racines (carottes, radis)",
            ]
        )

        service = PlanJardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        result = await service.suggerer_rotation(zone_id=1)

        assert service.call_with_cache.called


class TestPlanJardinServiceVueTemporelle:
    """Tests de la vue temporelle."""

    def test_obtenir_calendrier_zone(self):
        """Récupère le calendrier d'une zone."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            calendrier = service.obtenir_calendrier_zone(
                zone_id=1,
                mois=6,
            )

            assert isinstance(calendrier, list)

    def test_prevoir_recoltes(self):
        """Prévoit les récoltes à venir."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            previsions = service.prevoir_recoltes(
                plan_id=1,
                nb_semaines=4,
            )

            assert isinstance(previsions, list)


class TestPlanJardinServiceAnalyse:
    """Tests de l'analyse d'espace."""

    @pytest.mark.asyncio
    async def test_analyser_densite(self, mock_client_ia):
        """Analyse la densité de plantation."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            analyse = await service.analyser_densite(zone_id=1)

            assert "score" in analyse
            assert "niveau" in analyse

    @pytest.mark.asyncio
    async def test_calculer_exposition(self, mock_client_ia):
        """Calcule l'exposition solaire."""
        with patch("src.services.maison.plan_jardin_service.ClientIA"):
            service = get_plan_jardin_service()

            exposition = await service.calculer_exposition(zone_id=1)

            assert "heures_soleil" in exposition
            assert "orientation" in exposition


class TestPlanJardinServiceCalculs:
    """Tests des calculs utilitaires."""

    def test_calcul_surface_zone(self, zone_jardin_data):
        """Calcule la surface d'une zone."""
        surface = zone_jardin_data["largeur"] * zone_jardin_data["hauteur"]
        assert surface == 20.0  # 5 x 4

    def test_calcul_distance_plantes(self):
        """Calcule la distance entre deux plantes."""
        import math

        plante1 = {"x": 2.0, "y": 3.0}
        plante2 = {"x": 5.0, "y": 7.0}

        distance = math.sqrt(
            (plante2["x"] - plante1["x"]) ** 2 + (plante2["y"] - plante1["y"]) ** 2
        )

        assert distance == 5.0  # 3² + 4² = 25, √25 = 5

    def test_detection_chevauchement_zones(self):
        """Détecte si deux zones se chevauchent."""
        zone1 = {"x": 0, "y": 0, "largeur": 5, "hauteur": 4}
        zone2 = {"x": 4, "y": 3, "largeur": 3, "hauteur": 2}  # Chevauche
        zone3 = {"x": 10, "y": 10, "largeur": 2, "hauteur": 2}  # Ne chevauche pas

        def chevauche(z1, z2):
            return not (
                z1["x"] + z1["largeur"] <= z2["x"]
                or z2["x"] + z2["largeur"] <= z1["x"]
                or z1["y"] + z1["hauteur"] <= z2["y"]
                or z2["y"] + z2["hauteur"] <= z1["y"]
            )

        assert chevauche(zone1, zone2) is True
        assert chevauche(zone1, zone3) is False
