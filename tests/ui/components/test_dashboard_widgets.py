"""
Tests complets pour src/ui/components/dashboard_widgets.py
Couverture cible: >80%
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

# ═══════════════════════════════════════════════════════════
# GRAPHIQUE REPARTITION REPAS
# ═══════════════════════════════════════════════════════════


class TestGraphiqueRepartitionRepas:
    """Tests pour graphique_repartition_repas."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.components.dashboard_widgets import graphique_repartition_repas

        assert graphique_repartition_repas is not None

    def test_empty_data(self):
        """Test avec données vides."""
        from src.ui.components.dashboard_widgets import graphique_repartition_repas

        result = graphique_repartition_repas([])
        assert result is None

    def test_with_data(self):
        """Test avec données valides."""
        from src.ui.components.dashboard_widgets import graphique_repartition_repas

        data = [
            {"type_repas": "déjeuner"},
            {"type_repas": "déjeuner"},
            {"type_repas": "dîner"},
            {"type_repas": "petit_déjeuner"},
        ]

        result = graphique_repartition_repas(data)

        assert result is not None
        # Vérifier que c'est une figure Plotly
        assert hasattr(result, "update_layout")

    def test_unknown_type(self):
        """Test avec type de repas inconnu."""
        from src.ui.components.dashboard_widgets import graphique_repartition_repas

        data = [{"type_repas": "brunch"}]

        result = graphique_repartition_repas(data)
        assert result is not None

    def test_missing_type(self):
        """Test avec type_repas manquant."""
        from src.ui.components.dashboard_widgets import graphique_repartition_repas

        data = [{"autre": "valeur"}]  # Pas de type_repas

        result = graphique_repartition_repas(data)
        assert result is not None


# ═══════════════════════════════════════════════════════════
# GRAPHIQUE INVENTAIRE CATEGORIES
# ═══════════════════════════════════════════════════════════


class TestGraphiqueInventaireCategories:
    """Tests pour graphique_inventaire_categories."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.components.dashboard_widgets import graphique_inventaire_categories

        assert graphique_inventaire_categories is not None

    def test_empty_data(self):
        """Test avec données vides."""
        from src.ui.components.dashboard_widgets import graphique_inventaire_categories

        result = graphique_inventaire_categories([])
        assert result is None

    def test_with_data(self):
        """Test avec données valides."""
        from src.ui.components.dashboard_widgets import graphique_inventaire_categories

        data = [
            {"categorie": "Fruits", "statut": "ok"},
            {"categorie": "Fruits", "statut": "critique"},
            {"categorie": "Légumes", "statut": "ok"},
            {"categorie": "Viandes", "statut": "sous_seuil"},
        ]

        result = graphique_inventaire_categories(data)

        assert result is not None
        assert hasattr(result, "update_layout")

    def test_missing_categorie(self):
        """Test avec catégorie manquante."""
        from src.ui.components.dashboard_widgets import graphique_inventaire_categories

        data = [{"statut": "ok"}]  # Pas de catégorie â†’ "Autre"

        result = graphique_inventaire_categories(data)
        assert result is not None

    def test_many_categories(self):
        """Test avec beaucoup de catégories (max 8)."""
        from src.ui.components.dashboard_widgets import graphique_inventaire_categories

        # Plus de 8 catégories
        data = [{"categorie": f"Cat{i}", "statut": "ok"} for i in range(15)]

        result = graphique_inventaire_categories(data)
        assert result is not None


# ═══════════════════════════════════════════════════════════
# GRAPHIQUE ACTIVITE SEMAINE
# ═══════════════════════════════════════════════════════════


class TestGraphiqueActiviteSemaine:
    """Tests pour graphique_activite_semaine."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.components.dashboard_widgets import graphique_activite_semaine

        assert graphique_activite_semaine is not None

    def test_empty_data(self):
        """Test avec données vides - génère données vides."""
        from src.ui.components.dashboard_widgets import graphique_activite_semaine

        result = graphique_activite_semaine([])

        # Retourne une figure même avec données vides
        assert result is not None

    def test_with_data(self):
        """Test avec données valides."""
        from src.ui.components.dashboard_widgets import graphique_activite_semaine

        today = date.today()
        data = [
            {"date": today - timedelta(days=i), "count": i * 2, "type": "action"} for i in range(7)
        ]

        result = graphique_activite_semaine(data)

        assert result is not None
        assert hasattr(result, "update_layout")

    def test_with_string_dates(self):
        """Test avec dates en string ISO."""
        from src.ui.components.dashboard_widgets import graphique_activite_semaine

        today = date.today()
        data = [{"date": (today - timedelta(days=i)).isoformat(), "count": 5} for i in range(3)]

        result = graphique_activite_semaine(data)
        assert result is not None


# ═══════════════════════════════════════════════════════════
# GRAPHIQUE PROGRESSION OBJECTIFS
# ═══════════════════════════════════════════════════════════


class TestGraphiqueProgressionObjectifs:
    """Tests pour graphique_progression_objectifs."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.components.dashboard_widgets import graphique_progression_objectifs

        assert graphique_progression_objectifs is not None

    def test_empty_data(self):
        """Test avec données vides."""
        from src.ui.components.dashboard_widgets import graphique_progression_objectifs

        result = graphique_progression_objectifs([])
        assert result is None

    def test_with_data(self):
        """Test avec données valides."""
        from src.ui.components.dashboard_widgets import graphique_progression_objectifs

        data = [
            {"nom": "Recettes créées", "actuel": 8, "cible": 10},
            {"nom": "Repas planifiés", "actuel": 5, "cible": 7},
            {"nom": "Courses faites", "actuel": 2, "cible": 10},
        ]

        result = graphique_progression_objectifs(data)

        assert result is not None
        assert hasattr(result, "update_layout")

    def test_over_100_percent(self):
        """Test avec progression > 100%."""
        from src.ui.components.dashboard_widgets import graphique_progression_objectifs

        data = [{"nom": "Dépassé", "actuel": 15, "cible": 10}]  # 150%

        result = graphique_progression_objectifs(data)
        assert result is not None

    def test_missing_values(self):
        """Test avec valeurs manquantes."""
        from src.ui.components.dashboard_widgets import graphique_progression_objectifs

        data = [{"nom": "Test"}]  # Pas actuel ni cible

        result = graphique_progression_objectifs(data)
        assert result is not None


# ═══════════════════════════════════════════════════════════
# CARTE METRIQUE AVANCEE
# ═══════════════════════════════════════════════════════════


class TestCarteMetriqueAvancee:
    """Tests pour carte_metrique_avancee."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.components.dashboard_widgets import carte_metrique_avancee

        assert carte_metrique_avancee is not None

    @patch("streamlit.markdown")
    @patch("streamlit.button", return_value=False)
    def test_basic_call(self, mock_btn, mock_md):
        """Test appel basique."""
        from src.ui.components.dashboard_widgets import carte_metrique_avancee

        carte_metrique_avancee(titre="Recettes", valeur=42, icone="ðŸ½ï¸")

        mock_md.assert_called_once()
        assert "Recettes" in mock_md.call_args[0][0]
        assert "42" in mock_md.call_args[0][0]

    @patch("streamlit.markdown")
    @patch("streamlit.button", return_value=False)
    def test_with_delta_positive(self, mock_btn, mock_md):
        """Test avec delta positif."""
        from src.ui.components.dashboard_widgets import carte_metrique_avancee

        carte_metrique_avancee(
            titre="Total", valeur=100, icone="ðŸ“Š", delta="+5", delta_positif=True
        )

        html = mock_md.call_args[0][0]
        assert "+5" in html
        assert "â†‘" in html

    @patch("streamlit.markdown")
    @patch("streamlit.button", return_value=False)
    def test_with_delta_negative(self, mock_btn, mock_md):
        """Test avec delta négatif."""
        from src.ui.components.dashboard_widgets import carte_metrique_avancee

        carte_metrique_avancee(
            titre="Stock", valeur=50, icone="ðŸ“¦", delta="-10", delta_positif=False
        )

        html = mock_md.call_args[0][0]
        assert "-10" in html
        assert "â†“" in html

    @patch("streamlit.markdown")
    @patch("streamlit.button", return_value=False)
    def test_with_sous_titre(self, mock_btn, mock_md):
        """Test avec sous-titre."""
        from src.ui.components.dashboard_widgets import carte_metrique_avancee

        carte_metrique_avancee(
            titre="Titre", valeur="Val", icone="ðŸ“Œ", sous_titre="Description ici"
        )

        html = mock_md.call_args[0][0]
        assert "Description ici" in html

    @patch("streamlit.markdown")
    @patch("streamlit.button", return_value=True)
    @patch("streamlit.rerun")
    def test_with_lien_module(self, mock_rerun, mock_btn, mock_md):
        """Test avec lien vers module."""
        from src.ui.components.dashboard_widgets import carte_metrique_avancee

        with patch("src.core.state.GestionnaireEtat") as _mock_etat:
            try:
                carte_metrique_avancee(
                    titre="Recettes", valeur=10, icone="ðŸ½ï¸", lien_module="cuisine"
                )
            except Exception:
                pass

        mock_btn.assert_called_once()


# ═══════════════════════════════════════════════════════════
# INDICATEUR SANTE SYSTEME
# ═══════════════════════════════════════════════════════════


class TestIndicateurSanteSysteme:
    """Tests pour indicateur_sante_systeme."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.components.dashboard_widgets import indicateur_sante_systeme

        assert indicateur_sante_systeme is not None

    @patch("src.core.database.verifier_connexion", return_value=True)
    @patch("src.core.cache_multi.obtenir_cache")
    def test_all_ok(self, mock_cache, mock_db):
        """Test avec tout OK."""
        from src.ui.components.dashboard_widgets import indicateur_sante_systeme

        mock_cache.return_value.get_stats.return_value = {"hit_rate": "85%"}

        result = indicateur_sante_systeme()

        assert result["global"] == "ok"
        assert len(result["details"]) >= 1

    @patch("src.core.database.verifier_connexion", return_value=False)
    @patch("src.core.cache_multi.obtenir_cache")
    def test_db_disconnected(self, mock_cache, mock_db):
        """Test avec DB déconnectée."""
        from src.ui.components.dashboard_widgets import indicateur_sante_systeme

        mock_cache.return_value.get_stats.return_value = {"hit_rate": "50%"}

        result = indicateur_sante_systeme()

        assert result["global"] == "error"

    @patch("src.core.database.verifier_connexion", side_effect=Exception("DB Error"))
    @patch("src.core.cache_multi.obtenir_cache")
    def test_db_exception(self, mock_cache, mock_db):
        """Test avec exception DB."""
        from src.ui.components.dashboard_widgets import indicateur_sante_systeme

        mock_cache.return_value.get_stats.return_value = {"hit_rate": "50%"}

        result = indicateur_sante_systeme()

        assert result["global"] == "error"

    @patch("src.core.database.verifier_connexion", return_value=True)
    @patch("src.core.cache_multi.obtenir_cache")
    def test_cache_warning(self, mock_cache, mock_db):
        """Test avec cache en warning."""
        from src.ui.components.dashboard_widgets import indicateur_sante_systeme

        mock_cache.return_value.get_stats.return_value = {"hit_rate": "50%"}

        result = indicateur_sante_systeme()

        # Le global peut être ok ou warning selon cache
        assert result["global"] in ["ok", "warning"]

    @patch("src.core.database.verifier_connexion", return_value=True)
    @patch("src.core.cache_multi.obtenir_cache", side_effect=Exception("Cache Error"))
    def test_cache_exception(self, mock_cache, mock_db):
        """Test avec exception cache."""
        from src.ui.components.dashboard_widgets import indicateur_sante_systeme

        result = indicateur_sante_systeme()

        # Devrait gérer l'exception gracieusement
        assert "details" in result


# ═══════════════════════════════════════════════════════════
# AFFICHER SANTE SYSTEME
# ═══════════════════════════════════════════════════════════


class TestAfficherSanteSysteme:
    """Tests pour afficher_sante_systeme."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.components.dashboard_widgets import afficher_sante_systeme

        assert afficher_sante_systeme is not None

    @patch("streamlit.expander")
    @patch("streamlit.write")
    def test_display(self, mock_write, mock_expander):
        """Test affichage."""
        from src.ui.components.dashboard_widgets import afficher_sante_systeme

        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock()

        with patch("src.ui.components.dashboard_widgets.indicateur_sante_systeme") as mock_ind:
            mock_ind.return_value = {
                "global": "ok",
                "details": [{"nom": "DB", "status": "ok", "message": "OK"}],
            }

            afficher_sante_systeme()

        mock_expander.assert_called_once()


# ═══════════════════════════════════════════════════════════
# AFFICHER TIMELINE ACTIVITES
# ═══════════════════════════════════════════════════════════


class TestAfficherTimelineActivites:
    """Tests pour afficher_timeline_activites."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.components.dashboard_widgets import afficher_timeline_activites

        assert afficher_timeline_activites is not None

    @patch("streamlit.info")
    @patch("streamlit.markdown")
    def test_empty_data(self, mock_md, mock_info):
        """Test avec données vides."""
        from src.ui.components.dashboard_widgets import afficher_timeline_activites

        afficher_timeline_activites([])

        mock_info.assert_called_once()

    @patch("streamlit.markdown")
    def test_with_datetime(self, mock_md):
        """Test avec datetime."""
        from src.ui.components.dashboard_widgets import afficher_timeline_activites

        activites = [
            {"date": datetime.now(), "action": "Ajout recette", "type": "recette"},
            {"date": datetime.now(), "action": "Mise à jour", "type": "inventaire"},
        ]

        afficher_timeline_activites(activites)

        # Le titre + 2 activités
        assert mock_md.call_count >= 3

    @patch("streamlit.markdown")
    def test_with_string_date(self, mock_md):
        """Test avec date en string."""
        from src.ui.components.dashboard_widgets import afficher_timeline_activites

        activites = [
            {"date": "2026-02-11 10:30", "action": "Action", "type": "courses"},
        ]

        afficher_timeline_activites(activites)

        assert mock_md.call_count >= 2

    @patch("streamlit.markdown")
    def test_max_items(self, mock_md):
        """Test limite d'items."""
        from src.ui.components.dashboard_widgets import afficher_timeline_activites

        activites = [
            {"date": datetime.now(), "action": f"Action {i}", "type": "planning"} for i in range(10)
        ]

        afficher_timeline_activites(activites, max_items=3)

        # Titre + 3 items max
        assert mock_md.call_count == 4

    @patch("streamlit.markdown")
    def test_unknown_type(self, mock_md):
        """Test avec type inconnu."""
        from src.ui.components.dashboard_widgets import afficher_timeline_activites

        activites = [{"date": datetime.now(), "action": "Test", "type": "unknown"}]

        afficher_timeline_activites(activites)

        # Icône par défaut ðŸ“Œ


# ═══════════════════════════════════════════════════════════
# WIDGET JULES APERCU
# ═══════════════════════════════════════════════════════════


class TestWidgetJulesApercu:
    """Tests pour widget_jules_apercu."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.components.dashboard_widgets import widget_jules_apercu

        assert widget_jules_apercu is not None

    @patch("streamlit.markdown")
    def test_display(self, mock_md):
        """Test affichage."""
        from src.ui.components.dashboard_widgets import widget_jules_apercu

        widget_jules_apercu()

        mock_md.assert_called_once()
        html = mock_md.call_args[0][0]
        assert "Jules" in html
        assert "mois" in html


# ═══════════════════════════════════════════════════════════
# WIDGET METEO JOUR
# ═══════════════════════════════════════════════════════════


class TestWidgetMeteoJour:
    """Tests pour widget_meteo_jour."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.components.dashboard_widgets import widget_meteo_jour

        assert widget_meteo_jour is not None

    @patch("streamlit.markdown")
    def test_display(self, mock_md):
        """Test affichage."""
        from src.ui.components.dashboard_widgets import widget_meteo_jour

        widget_meteo_jour()

        mock_md.assert_called_once()
        html = mock_md.call_args[0][0]
        assert "°C" in html
