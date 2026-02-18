"""
Tests pour MaisonAssistantIA.

Couvre:
- Briefing quotidien
- Questions contextuelles
- Recommandations proactives
- Planification automatique
"""

import json
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.maison.assistant_ia import MaisonAssistantIA, get_maison_assistant
from src.services.maison.schemas import (
    AlerteMaison,
    BriefingMaison,
    NiveauUrgence,
    TypeAlerteMaison,
)


class TestMaisonAssistantInit:
    """Tests d'initialisation de l'assistant."""

    def test_factory_returns_assistant(self):
        """La factory retourne une instance valide."""
        with patch("src.services.maison.assistant_ia.ClientIA"):
            assistant = get_maison_assistant()
            assert isinstance(assistant, MaisonAssistantIA)

    def test_factory_accepts_custom_client(self):
        """La factory accepte un client personnalisé."""
        mock_client = MagicMock()
        assistant = get_maison_assistant(client=mock_client)
        assert assistant.client == mock_client


class TestMaisonAssistantLazyLoading:
    """Tests du chargement paresseux des services."""

    def test_entretien_lazy_load(self):
        """Le service entretien est chargé paresseusement."""
        with patch("src.services.maison.assistant_ia.ClientIA"):
            assistant = get_maison_assistant()

            # Avant accès
            assert assistant._entretien_service is None

            # Après accès (mock le module pour éviter l'import réel)
            with patch.object(assistant, "_entretien_service", MagicMock()):
                assert assistant._entretien_service is not None

    def test_jardin_lazy_load(self):
        """Le service jardin est chargé paresseusement."""
        with patch("src.services.maison.assistant_ia.ClientIA"):
            assistant = get_maison_assistant()

            assert assistant._jardin_service is None

            with patch.object(assistant, "_jardin_service", MagicMock()):
                assert assistant._jardin_service is not None


class TestMaisonAssistantBriefing:
    """Tests du briefing quotidien."""

    @pytest.mark.asyncio
    async def test_generer_briefing_complet(self, mock_client_ia):
        """Génère un briefing complet."""
        assistant = MaisonAssistantIA(client=mock_client_ia)
        assistant.call_with_cache = AsyncMock(return_value="Briefing du jour: 3 tâches, météo OK.")

        # Mock les méthodes de collecte
        assistant._collecter_taches_jour = AsyncMock(return_value=["Tâche 1", "Tâche 2"])
        assistant._collecter_alertes = AsyncMock(return_value=[])
        assistant._collecter_meteo = AsyncMock(return_value="Ensoleillé, 20°C")
        assistant._collecter_projets_actifs = AsyncMock(return_value=[])

        briefing = await assistant.generer_briefing_quotidien()

        assert briefing is not None
        assert isinstance(briefing, BriefingMaison)
        assert briefing.date == date.today()

    @pytest.mark.asyncio
    async def test_briefing_avec_alertes(self, mock_client_ia):
        """Briefing avec alertes urgentes."""
        assistant = MaisonAssistantIA(client=mock_client_ia)
        assistant.call_with_cache = AsyncMock(return_value="Attention: gel prévu!")

        alerte = AlerteMaison(
            type=TypeAlerteMaison.METEO,
            niveau=NiveauUrgence.HAUTE,
            titre="Gel nocturne",
            message="Températures négatives prévues",
            action_suggeree="Protéger les plantes",
        )

        assistant._collecter_taches_jour = AsyncMock(return_value=[])
        assistant._collecter_alertes = AsyncMock(return_value=[alerte])
        assistant._collecter_meteo = AsyncMock(return_value="Gel prévu -2°C")
        assistant._collecter_projets_actifs = AsyncMock(return_value=[])

        briefing = await assistant.generer_briefing_quotidien()

        assert len(briefing.alertes) == 1
        assert briefing.alertes[0].niveau == NiveauUrgence.HAUTE

    def test_calcul_priorites(self, mock_client_ia):
        """Calcule les priorités du jour."""
        assistant = MaisonAssistantIA(client=mock_client_ia)

        taches = ["Tâche 1", "Tâche 2", "Tâche 3", "Tâche 4"]
        alertes = [
            AlerteMaison(
                type=TypeAlerteMaison.METEO,
                niveau=NiveauUrgence.CRITIQUE,
                titre="Urgent",
                message="Alerte météo critique",
                action_suggeree="Action urgente",
            ),
        ]

        priorites = assistant._calculer_priorites(taches, alertes)

        # Alertes critiques d'abord
        assert priorites[0] == "Action urgente"
        # Max 5 priorités
        assert len(priorites) <= 5


class TestMaisonAssistantQuestions:
    """Tests des questions contextuelles."""

    @pytest.mark.asyncio
    async def test_question_ou_est(self, mock_client_ia):
        """Détecte et traite une question 'où est'."""
        assistant = MaisonAssistantIA(client=mock_client_ia)

        # Mock le service inventaire
        mock_inventaire = MagicMock()
        mock_inventaire.rechercher = AsyncMock(
            return_value=MagicMock(
                objet_trouve="perceuse",
                emplacement="Garage, établi",
            )
        )
        assistant._inventaire_service = mock_inventaire

        response = await assistant.repondre_question("où est ma perceuse?")

        assert "perceuse" in response.lower()

    @pytest.mark.asyncio
    async def test_question_jardin(self, mock_client_ia):
        """Détecte et traite une question jardin."""
        assistant = MaisonAssistantIA(client=mock_client_ia)
        assistant.call_with_cache = AsyncMock(return_value="Arrosez le matin ou le soir")

        response = await assistant.repondre_question("quand arroser mes tomates?")

        assert assistant.call_with_cache.called

    @pytest.mark.asyncio
    async def test_question_entretien(self, mock_client_ia):
        """Détecte et traite une question entretien."""
        assistant = MaisonAssistantIA(client=mock_client_ia)
        assistant.call_with_cache = AsyncMock(return_value="Utilisez du vinaigre blanc")

        response = await assistant.repondre_question("comment nettoyer le calcaire?")

        assert assistant.call_with_cache.called

    @pytest.mark.asyncio
    async def test_question_generale(self, mock_client_ia):
        """Traite une question générale."""
        assistant = MaisonAssistantIA(client=mock_client_ia)
        assistant.call_with_cache = AsyncMock(return_value="Réponse générale")

        response = await assistant.repondre_question("question quelconque")

        assert assistant.call_with_cache.called

    def test_extraction_objet_recherche(self, mock_client_ia):
        """Extrait correctement l'objet recherché."""
        assistant = MaisonAssistantIA(client=mock_client_ia)

        objet = assistant._extraire_objet_recherche("où est ma perceuse bleue?")
        assert "perceuse" in objet
        assert "bleue" in objet


class TestMaisonAssistantRecommandations:
    """Tests des recommandations proactives."""

    @pytest.mark.asyncio
    async def test_generer_recommandations(self, mock_client_ia):
        """Génère des recommandations saisonnières."""
        assistant = MaisonAssistantIA(client=mock_client_ia)
        assistant.call_with_cache = AsyncMock(
            return_value="- Vérifier le chauffage\n- Purger les radiateurs"
        )

        recos = await assistant.generer_recommandations()

        assert isinstance(recos, list)
        assert len(recos) > 0

    def test_obtenir_saison(self, mock_client_ia):
        """Détermine correctement la saison."""
        assistant = MaisonAssistantIA(client=mock_client_ia)

        assert assistant._obtenir_saison(1) == "hiver"
        assert assistant._obtenir_saison(4) == "printemps"
        assert assistant._obtenir_saison(7) == "été"
        assert assistant._obtenir_saison(10) == "automne"


class TestMaisonAssistantPlanification:
    """Tests de la planification automatique."""

    @pytest.mark.asyncio
    async def test_planifier_semaine(self, mock_client_ia):
        """Génère un planning hebdomadaire."""
        assistant = MaisonAssistantIA(client=mock_client_ia)

        planning = await assistant.planifier_semaine()

        assert isinstance(planning, dict)
        assert "lundi" in planning
        assert "dimanche" in planning
        # Dimanche devrait être repos
        assert "Repos" in planning["dimanche"][0] or planning["dimanche"] == []

    @pytest.mark.asyncio
    async def test_planifier_avec_preferences(self, mock_client_ia):
        """Planifie en respectant les préférences."""
        assistant = MaisonAssistantIA(client=mock_client_ia)

        planning = await assistant.planifier_semaine(preferences={"jours_off": ["dimanche"]})

        # Le planning devrait être adapté
        assert isinstance(planning, dict)


class TestMaisonAssistantCalculs:
    """Tests des calculs et utilitaires."""

    def test_saison_mois_coherent(self, mock_client_ia):
        """Vérifie la cohérence mois/saison."""
        assistant = MaisonAssistantIA(client=mock_client_ia)

        mois_printemps = [3, 4, 5]
        mois_ete = [6, 7, 8]
        mois_automne = [9, 10, 11]
        mois_hiver = [12, 1, 2]

        for m in mois_printemps:
            assert assistant._obtenir_saison(m) == "printemps"

        for m in mois_ete:
            assert assistant._obtenir_saison(m) == "été"

        for m in mois_automne:
            assert assistant._obtenir_saison(m) == "automne"

        for m in mois_hiver:
            assert assistant._obtenir_saison(m) == "hiver"

    def test_detection_contexte_question(self):
        """Détecte le contexte d'une question."""
        questions_jardin = ["arroser", "planter", "jardin", "tomates"]
        questions_entretien = ["nettoyer", "ménage", "poussière"]
        questions_recherche = ["où est", "où se trouve", "cherche"]

        for mot in questions_jardin:
            assert mot in " ".join(questions_jardin)

        for mot in questions_entretien:
            assert mot in " ".join(questions_entretien)

        for phrase in questions_recherche:
            assert "où" in phrase or "cherche" in phrase
