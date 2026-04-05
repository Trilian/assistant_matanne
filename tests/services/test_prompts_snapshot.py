"""
Snapshot tests pour les prompts IA.

Utilise syrupy pour figer les prompts et détecter les régressions.
Premier run : `pytest tests/services/test_prompts_snapshot.py --snapshot-update -v`
Runs suivants : `pytest tests/services/test_prompts_snapshot.py -v` (vérifie contre snapshots)
"""

import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


# ═══════════════════════════════════════════════════════════════
# 1. SYSTEM PROMPTS — Chat IA multi-contexte
# ═══════════════════════════════════════════════════════════════


class TestSystemPromptsSnapshot:
    """Snapshot des SYSTEM_PROMPTS pour chaque contexte chat."""

    @pytest.mark.unit
    def test_system_prompt_cuisine(self, snapshot):
        from src.services.utilitaires.chat.chat_ai import SYSTEM_PROMPTS

        assert SYSTEM_PROMPTS["cuisine"] == snapshot

    @pytest.mark.unit
    def test_system_prompt_famille(self, snapshot):
        from src.services.utilitaires.chat.chat_ai import SYSTEM_PROMPTS

        assert SYSTEM_PROMPTS["famille"] == snapshot

    @pytest.mark.unit
    def test_system_prompt_maison(self, snapshot):
        from src.services.utilitaires.chat.chat_ai import SYSTEM_PROMPTS

        assert SYSTEM_PROMPTS["maison"] == snapshot

    @pytest.mark.unit
    def test_system_prompt_budget(self, snapshot):
        from src.services.utilitaires.chat.chat_ai import SYSTEM_PROMPTS

        assert SYSTEM_PROMPTS["budget"] == snapshot

    @pytest.mark.unit
    def test_system_prompt_general(self, snapshot):
        from src.services.utilitaires.chat.chat_ai import SYSTEM_PROMPTS

        assert SYSTEM_PROMPTS["general"] == snapshot

    @pytest.mark.unit
    def test_system_prompt_nutrition(self, snapshot):
        from src.services.utilitaires.chat.chat_ai import SYSTEM_PROMPTS

        assert SYSTEM_PROMPTS["nutrition"] == snapshot

    @pytest.mark.unit
    def test_actions_rapides_completude(self, snapshot):
        """Vérifie que toutes les actions rapides sont définies."""
        from src.services.utilitaires.chat.chat_ai import ACTIONS_RAPIDES

        cles = sorted(ACTIONS_RAPIDES.keys())
        assert cles == snapshot


# ═══════════════════════════════════════════════════════════════
# 2. PROMPT BATCH COOKING
# ═══════════════════════════════════════════════════════════════


class TestPromptBatchCookingSnapshot:
    """Snapshot du prompt batch cooking détaillé."""

    @pytest.mark.unit
    def test_prompt_batch_cooking_sans_jules(self, snapshot):
        from src.services.cuisine.batch_cooking.batch_cooking_ia import _construire_prompt_detail

        planning = {
            "Lundi": {
                "midi": {"nom": "Pâtes bolognaise", "est_rechauffe": False},
                "soir": {"nom": "Soupe de légumes", "est_rechauffe": False},
            },
        }

        result = _construire_prompt_detail(
            planning_data=planning,
            type_session="Dimanche après-midi",
            avec_jules=False,
            robots_section="- Thermomix TM6\n- Robot pâtissier",
        )
        assert result == snapshot

    @pytest.mark.unit
    def test_prompt_batch_cooking_avec_jules(self, snapshot):
        from src.services.cuisine.batch_cooking.batch_cooking_ia import _construire_prompt_detail

        planning = {
            "Mardi": {
                "midi": {"nom": "Gratin dauphinois", "est_rechauffe": False},
                "soir": {"nom": "Salade composée", "est_rechauffe": False},
            },
        }

        result = _construire_prompt_detail(
            planning_data=planning,
            type_session="Samedi matin",
            avec_jules=True,
            robots_section="- Mixeur plongeant",
        )
        assert result == snapshot


# ═══════════════════════════════════════════════════════════════
# 3. PROMPT SUGGESTIONS RESTES
# ═══════════════════════════════════════════════════════════════


class TestPromptRestesSnapshot:
    """Snapshot du prompt de suggestion de recettes à partir de restes."""

    @pytest.mark.unit
    def test_prompt_restes_basique(self, snapshot):
        from src.services.cuisine.suggestions.restes import (
            _construire_prompt_restes,
            ResteDisponible,
        )

        restes = [
            ResteDisponible(nom="Poulet cuit", quantite_approx="200g", etat="bon"),
            ResteDisponible(nom="Riz", quantite_approx="1 bol", etat="bon"),
            ResteDisponible(nom="Carottes cuites", quantite_approx="3 pièces", etat="à consommer"),
        ]

        result = _construire_prompt_restes(restes)
        assert result == snapshot


# ═══════════════════════════════════════════════════════════════
# 4. PROMPT BILAN MENSUEL
# ═══════════════════════════════════════════════════════════════


class TestPromptBilanMensuelSnapshot:
    """Snapshot du prompt de bilan mensuel."""

    @pytest.mark.unit
    def test_prompt_bilan_mensuel(self, snapshot):
        from src.services.rapports.bilan_mensuel import obtenir_bilan_mensuel_service

        service = obtenir_bilan_mensuel_service()

        donnees = {
            "depenses": {
                "total": 2450,
                "par_categorie": {
                    "Alimentation": 650,
                    "Logement": 800,
                    "Transport": 200,
                    "Loisirs": 150,
                },
            },
            "repas": {"total_planifies": 42},
            "activites": {"total": 8, "noms": ["Parc", "Piscine", "Bibliothèque"]},
            "entretien": {"taches_completees": 12, "taches_en_retard": 3},
        }

        from datetime import date

        result = service._construire_prompt(donnees, date(2026, 3, 1))
        assert result == snapshot


# ═══════════════════════════════════════════════════════════════
# 5. PROMPTS JEUX (PARIS + LOTO)
# ═══════════════════════════════════════════════════════════════


class TestPromptsJeuxSnapshot:
    """Snapshot des prompts d'analyse jeux."""

    @pytest.mark.unit
    def test_prompt_paris_sportifs(self, snapshot):
        from src.services.jeux._internal.ai_service import JeuxAIService

        service = JeuxAIService.__new__(JeuxAIService)

        opportunites = [
            {"marche": "ML PSG vs Lyon", "value": 2.50, "serie": 8, "frequence": 0.15},
            {"marche": "1X Marseille", "value": 1.80, "serie": 5, "frequence": 0.22},
            {"marche": "O2.5 Monaco", "value": 1.50, "serie": 3, "frequence": 0.35},
        ]

        result = service._construire_prompt_paris(opportunites, "Ligue 1")
        assert result == snapshot

    @pytest.mark.unit
    def test_prompt_loto_principaux(self, snapshot):
        from src.services.jeux._internal.ai_service import JeuxAIService

        service = JeuxAIService.__new__(JeuxAIService)

        numeros = [
            {"numero": 7, "value": 3.20, "serie": 45, "frequence": 0.08},
            {"numero": 22, "value": 2.80, "serie": 38, "frequence": 0.09},
            {"numero": 41, "value": 2.50, "serie": 32, "frequence": 0.10},
        ]

        result = service._construire_prompt_loto(numeros, "principal")
        assert result == snapshot

    @pytest.mark.unit
    def test_prompt_loto_chance(self, snapshot):
        from src.services.jeux._internal.ai_service import JeuxAIService

        service = JeuxAIService.__new__(JeuxAIService)

        numeros = [
            {"numero": 3, "value": 1.80, "serie": 15, "frequence": 0.09},
        ]

        result = service._construire_prompt_loto(numeros, "chance")
        assert result == snapshot


# ═══════════════════════════════════════════════════════════════
# 6. PROMPT IMAGES — Query optimisée
# ═══════════════════════════════════════════════════════════════


class TestPromptImagesSnapshot:
    """Snapshot des prompts de génération d'images culinaires."""

    @pytest.mark.unit
    def test_query_recette_dessert(self, snapshot):
        from src.services.integrations.images.prompts import _construire_query_optimisee

        result = _construire_query_optimisee(
            "Tarte aux pommes",
            [{"nom": "Pommes"}, {"nom": "Pâte feuilletée"}],
            "dessert",
        )
        assert result == snapshot

    @pytest.mark.unit
    def test_query_recette_soupe(self, snapshot):
        from src.services.integrations.images.prompts import _construire_query_optimisee

        result = _construire_query_optimisee(
            "Soupe de potiron",
            [{"nom": "Potiron"}, {"nom": "Crème fraîche"}],
            "soupe",
        )
        assert result == snapshot

    @pytest.mark.unit
    def test_query_recette_plat_general(self, snapshot):
        from src.services.integrations.images.prompts import _construire_query_optimisee

        result = _construire_query_optimisee(
            "Poulet rôti",
            [{"nom": "Poulet"}, {"nom": "Thym"}],
            "plat",
        )
        assert result == snapshot


# ═══════════════════════════════════════════════════════════════
# 7. AI PROMPTS MIXIN — Build JSON/System prompts
# ═══════════════════════════════════════════════════════════════


class TestAIPromptsMixinSnapshot:
    """Snapshot des méthodes de construction de prompts du mixin."""

    @pytest.mark.unit
    def test_build_json_prompt(self, snapshot):
        from src.services.core.base.ai_prompts import AIPromptsMixin

        mixin = AIPromptsMixin()
        result = mixin.build_json_prompt(
            context="Famille française, 2 adultes, 1 enfant de 3 ans",
            task="Génère un planning de repas pour la semaine",
            json_schema='[{"jour": "Lundi", "midi": "...", "soir": "..."}]',
            constraints=[
                "Pas de poisson le lundi",
                "Recettes rapides en semaine (30 min max)",
                "Au moins 2 repas végétariens",
            ],
        )
        assert result == snapshot

    @pytest.mark.unit
    def test_build_system_prompt(self, snapshot):
        from src.services.core.base.ai_prompts import AIPromptsMixin

        mixin = AIPromptsMixin()
        result = mixin.build_system_prompt(
            role="un expert culinaire familial",
            expertise=[
                "Cuisine française et méditerranéenne",
                "Nutrition infantile",
                "Batch cooking et meal prep",
            ],
            rules=[
                "Toujours proposer des alternatives pour les allergies",
                "Privilégier les produits de saison",
            ],
        )
        assert result == snapshot
