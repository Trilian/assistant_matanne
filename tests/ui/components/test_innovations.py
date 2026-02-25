"""
Tests pour les innovations 10.x du rapport d'audit.

Tests ciblés pour :
- Recherche globale ⌘K
- Mode focus / zen
- Historique undo
- Widget "Qu'est-ce qu'on mange ?"
- Jules aujourd'hui
- Progressive loading
- Raccourcis clavier
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# TESTS: RECHERCHE GLOBALE
# ═══════════════════════════════════════════════════════════


class TestRechercheGlobaleService:
    """Tests pour RechercheGlobaleService."""

    def test_instance_creation(self):
        """Test création du service."""
        from src.ui.components.recherche_globale import RechercheGlobaleService

        service = RechercheGlobaleService()
        assert service._max_resultats_par_type == 5

    def test_recherche_vide(self):
        """Test recherche avec terme vide."""
        from src.ui.components.recherche_globale import RechercheGlobaleService

        service = RechercheGlobaleService()
        assert service.rechercher("") == []
        assert service.rechercher("a") == []  # < 2 chars

    def test_recherche_types_filtres(self):
        """Test recherche avec types filtrés."""
        from src.ui.components.recherche_globale import (
            RechercheGlobaleService,
            TypeResultat,
        )

        service = RechercheGlobaleService()
        # Ne devrait pas crasher
        resultats = service.rechercher("test", types=[TypeResultat.RECETTE])
        assert isinstance(resultats, list)

    def test_singleton_factory(self):
        """Test factory singleton."""
        from src.ui.components.recherche_globale import get_recherche_globale_service

        s1 = get_recherche_globale_service()
        s2 = get_recherche_globale_service()
        assert s1 is s2


class TestResultatRecherche:
    """Tests pour ResultatRecherche."""

    def test_icone_default(self):
        """Test icône par défaut."""
        from src.ui.components.recherche_globale import ResultatRecherche, TypeResultat

        r = ResultatRecherche(type=TypeResultat.RECETTE, titre="Test")
        assert r.icone_display == "🍳"

    def test_icone_custom(self):
        """Test icône personnalisée."""
        from src.ui.components.recherche_globale import ResultatRecherche, TypeResultat

        r = ResultatRecherche(type=TypeResultat.RECETTE, titre="Test", icone="🎉")
        assert r.icone_display == "🎉"


class TestTypeResultat:
    """Tests pour TypeResultat enum."""

    def test_valeurs(self):
        """Test toutes les valeurs de l'enum."""
        from src.ui.components.recherche_globale import TypeResultat

        assert TypeResultat.RECETTE.value == "recette"
        assert TypeResultat.PRODUIT.value == "produit"
        assert TypeResultat.ACTIVITE.value == "activite"
        assert TypeResultat.INVENTAIRE.value == "inventaire"
        assert TypeResultat.PLANNING.value == "planning"
        assert TypeResultat.JULES.value == "jules"
        assert TypeResultat.NOTE.value == "note"


# ═══════════════════════════════════════════════════════════
# TESTS: MODE FOCUS / ZEN
# ═══════════════════════════════════════════════════════════


class TestModeFocus:
    """Tests pour le mode focus."""

    @patch("streamlit.session_state", {})
    @patch("src.ui.components.mode_focus.get_url_param", return_value=None)
    def test_mode_focus_inactif_par_defaut(self, mock_url):
        """Test que le mode focus est inactif par défaut."""
        from src.ui.components.mode_focus import is_mode_focus

        assert is_mode_focus() is False

    @patch("streamlit.session_state", {"_mode_focus_active": True})
    @patch("src.ui.components.mode_focus.get_url_param", return_value=None)
    def test_mode_focus_via_session(self, mock_url):
        """Test activation via session state."""
        from src.ui.components.mode_focus import is_mode_focus

        assert is_mode_focus() is True

    @patch("streamlit.session_state", {})
    @patch("src.ui.components.mode_focus.get_url_param", return_value="1")
    def test_mode_focus_via_url(self, mock_url):
        """Test activation via URL param."""
        from src.ui.components.mode_focus import is_mode_focus

        assert is_mode_focus() is True

    @patch("streamlit.session_state", {})
    @patch("src.ui.components.mode_focus.set_url_param")
    def test_activer_mode_focus(self, mock_set):
        """Test activation du mode focus."""
        import streamlit as st

        from src.ui.components.mode_focus import activer_mode_focus

        activer_mode_focus()
        assert st.session_state["_mode_focus_active"] is True
        mock_set.assert_called_with("focus", "1")

    @patch("streamlit.session_state", {"_mode_focus_active": True})
    @patch("src.ui.state.url.clear_url_param")
    def test_desactiver_mode_focus(self, mock_clear):
        """Test désactivation du mode focus."""
        import streamlit as st

        from src.ui.components.mode_focus import desactiver_mode_focus

        desactiver_mode_focus()
        assert st.session_state["_mode_focus_active"] is False
        mock_clear.assert_called_with("focus")


# ═══════════════════════════════════════════════════════════
# TESTS: HISTORIQUE UNDO HELPERS
# ═══════════════════════════════════════════════════════════


class TestHistoriqueUndoHelpers:
    """Tests pour les helpers du historique undo."""

    def test_get_action_icone(self):
        """Test icônes d'action."""
        from src.ui.components.historique_undo import _get_action_icone

        assert _get_action_icone("recette_created") == "🍳"
        assert _get_action_icone("recette_deleted") == "🗑️"
        assert _get_action_icone("courses_item_checked") == "✅"
        assert _get_action_icone("unknown_type") == "📝"

    def test_format_temps_relatif_none(self):
        """Test format temps relatif avec None."""
        from src.ui.components.historique_undo import _format_temps_relatif

        assert _format_temps_relatif(None) == "?"

    def test_format_temps_relatif_recent(self):
        """Test format temps relatif pour événement récent."""
        from src.ui.components.historique_undo import _format_temps_relatif

        resultat = _format_temps_relatif(datetime.now())
        assert "instant" in resultat.lower() or "min" in resultat.lower()


# ═══════════════════════════════════════════════════════════
# TESTS: WIDGET QU'EST-CE QU'ON MANGE
# ═══════════════════════════════════════════════════════════


class TestWidgetQCOM:
    """Tests pour le widget Qu'est-ce qu'on mange."""

    @patch("src.core.db.obtenir_contexte_db")
    def test_obtenir_repas_aucun(self, mock_db):
        """Test quand aucun repas planifié."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.ui.components.quest_ce_quon_mange import obtenir_repas_du_jour

        # Ne devrait pas crasher
        result = obtenir_repas_du_jour()
        # Peut retourner None si pas de planning
        assert result is None or isinstance(result, dict)


# ═══════════════════════════════════════════════════════════
# TESTS: JULES AUJOURD'HUI
# ═══════════════════════════════════════════════════════════


class TestJulesAujourdhui:
    """Tests pour le module Jules aujourd'hui."""

    def test_generer_resume_vide(self):
        """Test génération résumé sans données."""
        from src.ui.components.jules_aujourdhui import generer_resume_jules

        resume = generer_resume_jules([], [], [])
        assert "Jules" in resume
        assert date.today().strftime("%d/%m/%Y") in resume

    def test_generer_resume_avec_activites(self):
        """Test génération résumé avec activités."""
        from src.ui.components.jules_aujourdhui import generer_resume_jules

        activites = [
            {
                "titre": "Peinture",
                "type": "eveil",
                "heure": "10:00",
                "duree": 30,
                "notes": "A adoré",
                "humeur": "content",
                "icone": "🎨",
            },
            {
                "titre": "Parc",
                "type": "sortie",
                "heure": "15:00",
                "duree": 60,
                "notes": None,
                "humeur": "content",
                "icone": "🌳",
            },
        ]

        resume = generer_resume_jules(activites, format_export="whatsapp")
        assert "Peinture" in resume
        assert "Parc" in resume
        assert "A adoré" in resume
        assert "Activités" in resume

    def test_generer_resume_avec_repas(self):
        """Test génération résumé avec repas."""
        from src.ui.components.jules_aujourdhui import generer_resume_jules

        repas = [
            {
                "type": "déjeuner",
                "heure": "12:00",
                "aliments": "Purée carottes",
                "quantite": "bien mangé",
                "commentaire": None,
            }
        ]

        resume = generer_resume_jules([], repas, format_export="sms")
        assert "Repas" in resume
        assert "Purée carottes" in resume

    def test_generer_resume_format_sms(self):
        """Test que le format SMS n'a pas d'emoji de section."""
        from src.ui.components.jules_aujourdhui import generer_resume_jules

        resume = generer_resume_jules([], format_export="sms")
        # SMS ne devrait pas avoir les icônes dans les sections
        assert "🎯" not in resume

    def test_get_activite_icone(self):
        """Test mapping icônes activités."""
        from src.ui.components.jules_aujourdhui import _get_activite_icone

        assert _get_activite_icone("motricite") == "🏃"
        assert _get_activite_icone("lecture") == "📚"
        assert _get_activite_icone("sortie") == "🌳"
        assert _get_activite_icone(None) == "📝"
        assert _get_activite_icone("inconnu") == "📝"


# ═══════════════════════════════════════════════════════════
# TESTS: PROGRESSIVE LOADING
# ═══════════════════════════════════════════════════════════


class TestProgressiveLoading:
    """Tests pour le Progressive Loading."""

    def test_etape_chargement_creation(self):
        """Test création d'étape."""
        from src.ui.components.progressive_loading import EtapeChargement

        etape = EtapeChargement(nom="test", fonction=lambda: 42)
        assert etape.nom == "test"
        assert etape.poids == 1
        assert etape.optionnel is False
        assert etape.fonction() == 42

    def test_etape_chargement_optionnel(self):
        """Test étape optionnelle."""
        from src.ui.components.progressive_loading import EtapeChargement

        etape = EtapeChargement(nom="test", fonction=lambda: None, optionnel=True)
        assert etape.optionnel is True

    @patch("streamlit.status")
    @patch("streamlit.progress")
    @patch("streamlit.write")
    def test_progressive_loader_context(self, mock_write, mock_progress, mock_status):
        """Test context manager progressive loader."""
        from src.ui.components.progressive_loading import ProgressiveLoader

        mock_context = MagicMock()
        mock_status.return_value = mock_context
        mock_context.__enter__ = MagicMock(return_value=mock_context)
        mock_context.__exit__ = MagicMock(return_value=False)

        loader = ProgressiveLoader("Test")
        with loader:
            loader.update("étape 1", 1, 2)
            loader.update("étape 2", 2, 2)

        assert loader.erreurs == []


# ═══════════════════════════════════════════════════════════
# TESTS: IMPORTS
# ═══════════════════════════════════════════════════════════


class TestImports:
    """Tests que tous les imports fonctionnent."""

    def test_import_recherche_globale(self):
        """Test import recherche globale."""
        from src.ui.components.recherche_globale import (
            RechercheGlobaleService,
            ResultatRecherche,
            TypeResultat,
            afficher_recherche_globale,
            afficher_recherche_globale_popover,
            get_recherche_globale_service,
            injecter_raccourcis_clavier,
        )

    def test_import_mode_focus(self):
        """Test import mode focus."""
        from src.ui.components.mode_focus import (
            activer_mode_focus,
            desactiver_mode_focus,
            focus_exit_button,
            injecter_css_mode_focus,
            is_mode_focus,
            mode_focus_fab,
            mode_focus_toggle,
            toggle_mode_focus,
        )

    def test_import_historique_undo(self):
        """Test import historique undo."""
        from src.ui.components.historique_undo import (
            afficher_bouton_undo,
            afficher_historique_actions,
        )

    def test_import_qcom(self):
        """Test import qu'est-ce qu'on mange."""
        from src.ui.components.quest_ce_quon_mange import (
            obtenir_repas_du_jour,
            suggerer_repas_ia,
            widget_qcom_compact,
            widget_quest_ce_quon_mange,
        )

    def test_import_jules_aujourdhui(self):
        """Test import jules aujourd'hui."""
        from src.ui.components.jules_aujourdhui import (
            carte_resume_jules,
            generer_resume_jules,
            obtenir_activites_jules_aujourdhui,
            widget_jules_aujourdhui,
            widget_jules_resume_compact,
        )

    def test_import_progressive_loading(self):
        """Test import progressive loading."""
        from src.ui.components.progressive_loading import (
            EtapeChargement,
            ProgressiveLoader,
            charger_avec_progression,
            progressive_loader,
            skeleton_loading,
            status_chargement,
        )

    def test_import_from_components_package(self):
        """Test import depuis le package components."""
        from src.ui.components import (
            EtapeChargement,
            ProgressiveLoader,
            RechercheGlobaleService,
            afficher_bouton_undo,
            afficher_recherche_globale,
            carte_resume_jules,
            focus_exit_button,
            injecter_raccourcis_clavier,
            is_mode_focus,
            mode_focus_toggle,
            widget_jules_aujourdhui,
            widget_quest_ce_quon_mange,
        )
