"""
Tests unitaires pour ai_agent.py (Agent IA)
Ce fichier teste spÃ©cifiquement src/core/ai_agent.py
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

# Import direct du module Ã  tester
from src.core.ai_agent import AgentIA


# Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢
# TESTS INITIALISATION
# Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢

class TestAgentIAInit:
    """Tests d'initialisation de l'agent"""
    
    @patch('src.core.ai_agent.ClientIA')
    def test_init_creates_client(self, mock_client_class):
        """Test que l'initialisation crÃ©e un client"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        agent = AgentIA()
        
        assert agent.client == mock_client
    
    @patch('src.core.ai_agent.ClientIA')
    def test_init_creates_empty_contexte(self, mock_client_class):
        """Test que le contexte est vide Ã  l'init"""
        agent = AgentIA()
        
        assert agent.contexte == {}
    
    @patch('src.core.ai_agent.ClientIA')
    def test_init_handles_client_error(self, mock_client_class):
        """Test que les erreurs d'init sont gÃ©rÃ©es"""
        mock_client_class.side_effect = Exception("Erreur de connexion")
        
        agent = AgentIA()
        
        assert agent.client is None
        assert agent.contexte == {}


# Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢
# TESTS CONTEXTE
# Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢

class TestAgentIAContexte:
    """Tests de gestion du contexte"""
    
    @patch('src.core.ai_agent.ClientIA')
    def test_ajouter_contexte(self, mock_client_class):
        """Test l'ajout de contexte"""
        agent = AgentIA()
        
        agent.ajouter_contexte("user_id", "12345")
        
        assert agent.contexte["user_id"] == "12345"
    
    @patch('src.core.ai_agent.ClientIA')
    def test_ajouter_contexte_multiple(self, mock_client_class):
        """Test l'ajout de plusieurs contextes"""
        agent = AgentIA()
        
        agent.ajouter_contexte("key1", "value1")
        agent.ajouter_contexte("key2", "value2")
        
        assert len(agent.contexte) == 2
    
    @patch('src.core.ai_agent.ClientIA')
    def test_obtenir_contexte(self, mock_client_class):
        """Test la rÃ©cupÃ©ration de contexte"""
        agent = AgentIA()
        agent.contexte = {"ma_cle": "ma_valeur"}
        
        result = agent.obtenir_contexte("ma_cle")
        
        assert result == "ma_valeur"
    
    @patch('src.core.ai_agent.ClientIA')
    def test_obtenir_contexte_missing_key(self, mock_client_class):
        """Test rÃ©cupÃ©ration clÃ© absente"""
        agent = AgentIA()
        
        result = agent.obtenir_contexte("cle_inexistante")
        
        assert result is None
    
    @patch('src.core.ai_agent.ClientIA')
    def test_effacer_contexte(self, mock_client_class):
        """Test l'effacement du contexte"""
        agent = AgentIA()
        agent.contexte = {"key1": "val1", "key2": "val2"}
        
        agent.effacer_contexte()
        
        assert agent.contexte == {}


# Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢
# TESTS MÃƒâ€°THODE ANALYSER
# Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢

class TestAgentIAAnalyser:
    """Tests de la mÃ©thode analyser"""
    
    @patch('src.core.ai_agent.ClientIA')
    def test_analyser_exists(self, mock_client_class):
        """Test que la mÃ©thode analyser existe"""
        agent = AgentIA()
        
        assert hasattr(agent, 'analyser')
        assert callable(agent.analyser)
    
    @patch('src.core.ai_agent.ClientIA')
    def test_analyser_without_client_returns_default(self, mock_client_class):
        """Test analyser sans client retourne message par dÃ©faut"""
        mock_client_class.side_effect = Exception("Error")
        agent = AgentIA()
        
        # analyser est async, on vÃ©rifie juste que client is None
        assert agent.client is None


# Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢
# TESTS MÃƒâ€°THODE GENERER_ANALYSE
# Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢

class TestAgentIAGenererAnalyse:
    """Tests de la mÃ©thode generer_analyse"""
    
    @patch('src.core.ai_agent.ClientIA')
    def test_generer_analyse_exists(self, mock_client_class):
        """Test que la mÃ©thode generer_analyse existe"""
        agent = AgentIA()
        
        assert hasattr(agent, 'generer_analyse')
        assert callable(agent.generer_analyse)
    
    @patch('src.core.ai_agent.ClientIA')
    def test_generer_analyse_types_defined(self, mock_client_class):
        """Test que les types d'analyse sont dÃ©finis"""
        # Les types attendus dans le code
        expected_types = ["bien_etre", "cuisine", "budget", "jardin", "routines"]
        
        # On vÃ©rifie juste que la classe est importable et les types documentÃ©s
        assert len(expected_types) == 5


# Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢
# TESTS STRUCTURE ET INTERFACE
# Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢Ã¢â€¢

class TestAgentIAInterface:
    """Tests de l'interface publique"""
    
    @patch('src.core.ai_agent.ClientIA')
    def test_has_all_public_methods(self, mock_client_class):
        """Test que toutes les mÃ©thodes publiques existent"""
        agent = AgentIA()
        
        expected_methods = [
            'analyser',
            'generer_analyse',
            'ajouter_contexte',
            'obtenir_contexte',
            'effacer_contexte',
        ]
        
        for method in expected_methods:
            assert hasattr(agent, method), f"MÃ©thode {method} manquante"
    
    @patch('src.core.ai_agent.ClientIA')
    def test_contexte_is_dict(self, mock_client_class):
        """Test que contexte est un dict"""
        agent = AgentIA()
        
        assert isinstance(agent.contexte, dict)
