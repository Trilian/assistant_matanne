"""
Tests pour src/core/ai_agent.py (AgentIA)

Tests couvrant:
- Initialisation et gestion du client IA
- Méthodes analyser et generer_analyse
- Gestion du contexte
- Gestion des erreurs
- Intégrations avec ClientIA
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from src.core.ai_agent import AgentIA
from src.core.errors import ErreurServiceIA


# ═══════════════════════════════════════════════════════════
# SECTION 1: TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAgentIAInit:
    """Tests d'initialisation de l'agent."""

    @patch('src.core.ai_agent.ClientIA')
    def test_agent_creation_success(self, mock_client_class):
        """Test création réussie d'un agent."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        
        assert agent is not None
        assert agent.client is not None
        assert agent.contexte == {}

    @patch('src.core.ai_agent.ClientIA')
    def test_agent_creation_error(self, mock_client_class):
        """Test gestion d'erreur lors de la création."""
        mock_client_class.side_effect = Exception("Erreur ClientIA")
        
        agent = AgentIA()
        
        assert agent.client is None
        assert agent.contexte == {}

    @patch('src.core.ai_agent.ClientIA')
    def test_agent_contexte_initial(self, mock_client_class):
        """Test que le contexte est vide au démarrage."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        
        assert agent.contexte == {}


# ═══════════════════════════════════════════════════════════
# SECTION 2: TESTS ANALYSER
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAgentIAAnalyser:
    """Tests de la méthode analyser."""

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_analyser_simple(self, mock_client_class):
        """Test analyse simple."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="Analyse résultat")
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        reponse = await agent.analyser("Quel est ton avis?")
        
        assert reponse == "Analyse résultat"
        mock_client.appeler.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_analyser_avec_contexte(self, mock_client_class):
        """Test analyse avec contexte."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="Analyse enrichie")
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        contexte = {"famille": "4 personnes", "budget": 500}
        reponse = await agent.analyser(
            "Suggère un repas",
            contexte=contexte
        )
        
        assert reponse == "Analyse enrichie"
        # Vérifier que le contexte est inclus dans le prompt
        call_args = mock_client.appeler.call_args
        prompt = call_args.kwargs.get('prompt') or call_args.args[0]
        assert "Contexte" in prompt or str(contexte) in prompt

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_analyser_temperature_custom(self, mock_client_class):
        """Test avec température personnalisée."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="Réponse créative")
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        await agent.analyser(
            "Sois créatif",
            temperature=1.5
        )
        
        # Vérifier que la température est passée
        call_args = mock_client.appeler.call_args
        assert call_args.kwargs.get('temperature') == 1.5

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_analyser_client_none(self, mock_client_class):
        """Test quand le client n'est pas disponible."""
        mock_client_class.side_effect = Exception("Erreur")
        
        agent = AgentIA()
        reponse = await agent.analyser("Test")
        
        assert "n'est pas disponible" in reponse or "non disponible" in reponse

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_analyser_erreur_client(self, mock_client_class):
        """Test gestion d'erreur du client."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(side_effect=Exception("Erreur réseau"))
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        reponse = await agent.analyser("Test")
        
        assert "Erreur" in reponse


# ═══════════════════════════════════════════════════════════
# SECTION 3: TESTS GENERER_ANALYSE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAgentIAGenererAnalyse:
    """Tests de génération d'analyses spécifiques."""

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_generer_analyse_bien_etre(self, mock_client_class):
        """Test génération d'analyse bien-être."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="Analyse bien-être")
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        donnees = {"stress": 7, "sommeil": 6}
        reponse = await agent.generer_analyse(donnees, "bien_etre")
        
        assert reponse == "Analyse bien-être"

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_generer_analyse_cuisine(self, mock_client_class):
        """Test génération d'analyse cuisine."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="Suggestions culinaires")
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        donnees = {"recettes_cette_semaine": 5, "budget": 80}
        reponse = await agent.generer_analyse(donnees, "cuisine")
        
        assert reponse == "Suggestions culinaires"

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_generer_analyse_budget(self, mock_client_class):
        """Test génération d'analyse budget."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="Tendances budgétaires")
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        donnees = {"total_janvier": 1200, "total_février": 1350}
        reponse = await agent.generer_analyse(donnees, "budget")
        
        assert reponse == "Tendances budgétaires"

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_generer_analyse_jardin(self, mock_client_class):
        """Test génération d'analyse jardin."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="Conseils jardinage")
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        donnees = {"plantes": 15, "surface": "50m²"}
        reponse = await agent.generer_analyse(donnees, "jardin")
        
        assert reponse == "Conseils jardinage"

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_generer_analyse_routines(self, mock_client_class):
        """Test génération d'analyse routines."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="Optimisations routines")
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        donnees = {"reveille": "7:00", "coucher": "23:00"}
        reponse = await agent.generer_analyse(donnees, "routines")
        
        assert reponse == "Optimisations routines"

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_generer_analyse_type_inconnu(self, mock_client_class):
        """Test avec type d'analyse inconnu."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="Analyse générale")
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        reponse = await agent.generer_analyse({"data": "test"}, "type_inconnu")
        
        assert reponse == "Analyse générale"


# ═══════════════════════════════════════════════════════════
# SECTION 4: TESTS GESTION CONTEXTE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAgentIAContexte:
    """Tests de gestion du contexte."""

    @patch('src.core.ai_agent.ClientIA')
    def test_ajouter_contexte(self, mock_client_class):
        """Test ajout d'élément au contexte."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        agent.ajouter_contexte("famille_size", 4)
        
        assert agent.contexte["famille_size"] == 4

    @patch('src.core.ai_agent.ClientIA')
    def test_obtenir_contexte(self, mock_client_class):
        """Test récupération d'élément du contexte."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        agent.ajouter_contexte("budget_mensuel", 2000)
        
        valeur = agent.obtenir_contexte("budget_mensuel")
        assert valeur == 2000

    @patch('src.core.ai_agent.ClientIA')
    def test_obtenir_contexte_inexistant(self, mock_client_class):
        """Test récupération d'une clé inexistante."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        valeur = agent.obtenir_contexte("inexistant")
        
        assert valeur is None

    @patch('src.core.ai_agent.ClientIA')
    def test_effacer_contexte(self, mock_client_class):
        """Test effacement du contexte."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        agent.ajouter_contexte("key1", "value1")
        agent.ajouter_contexte("key2", "value2")
        
        assert len(agent.contexte) == 2
        
        agent.effacer_contexte()
        
        assert agent.contexte == {}

    @patch('src.core.ai_agent.ClientIA')
    def test_contexte_multiple_values(self, mock_client_class):
        """Test stockage de multiples valeurs."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        
        contexte_data = {
            "utilisateur": "Alice",
            "budget": 1500,
            "preferences": ["pasta", "pizza"],
        }
        
        for cle, valeur in contexte_data.items():
            agent.ajouter_contexte(cle, valeur)
        
        for cle, valeur in contexte_data.items():
            assert agent.obtenir_contexte(cle) == valeur


# ═══════════════════════════════════════════════════════════
# SECTION 5: TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestAgentIAIntegration:
    """Tests d'intégration complets."""

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_workflow_complet_analyse_avec_contexte(self, mock_client_class):
        """Test workflow complet: contexte + analyse."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="Recommandation personnalisée")
        mock_client_class.return_value = mock_client
        
        # Créer l'agent
        agent = AgentIA()
        
        # Ajouter contexte
        agent.ajouter_contexte("allergies", ["arachides", "fruits de mer"])
        agent.ajouter_contexte("nombre_personnes", 4)
        
        # Effectuer analyse
        reponse = await agent.analyser(
            "Suggère un repas",
            contexte=agent.contexte
        )
        
        assert reponse == "Recommandation personnalisée"
        assert agent.obtenir_contexte("allergies") == ["arachides", "fruits de mer"]

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_workflow_multiple_analyses(self, mock_client_class):
        """Test workflow avec multiples analyses."""
        mock_client = AsyncMock()
        mock_client.appeler = AsyncMock(return_value="Analyse spécifique")
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        
        # Effectuer plusieurs analyses
        reponse1 = await agent.generer_analyse({"data": 1}, "bien_etre")
        reponse2 = await agent.generer_analyse({"data": 2}, "cuisine")
        reponse3 = await agent.generer_analyse({"data": 3}, "budget")
        
        assert reponse1 == "Analyse spécifique"
        assert reponse2 == "Analyse spécifique"
        assert reponse3 == "Analyse spécifique"
        assert mock_client.appeler.call_count == 3

    @pytest.mark.asyncio
    @patch('src.core.ai_agent.ClientIA')
    async def test_workflow_erreur_recovery(self, mock_client_class):
        """Test récupération après erreur."""
        mock_client = AsyncMock()
        # Première erreur, puis succès
        mock_client.appeler = AsyncMock(
            side_effect=[
                Exception("Erreur réseau"),
                "Succès après retry"
            ]
        )
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        
        # Premier appel échoue, retourne message d'erreur
        reponse1 = await agent.analyser("Test 1")
        assert "Erreur" in reponse1
        
        # Deuxième appel réussit
        reponse2 = await agent.analyser("Test 2")
        assert reponse2 == "Succès après retry"
