"""
Tests pour src/modules/maison/jardin_zones.py

Tests complets pour le module Dashboard Zones Jardin (Vue 2600m² avec photos avant/après).
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# TESTS IMPORT
# ═══════════════════════════════════════════════════════════════════════════════


class TestJardinZonesImport:
    """Tests d'import du module jardin_zones."""

    def test_import_module(self):
        """Test import du module."""
        import src.modules.maison.jardin_zones as jardin_zones

        assert jardin_zones is not None

    def test_import_constantes(self):
        """Test import des constantes."""
        from src.modules.maison.jardin_zones import (
            COULEUR_ETAT,
            EMOJI_ZONE,
            LABEL_ETAT,
        )

        assert isinstance(EMOJI_ZONE, dict)
        assert isinstance(COULEUR_ETAT, dict)
        assert isinstance(LABEL_ETAT, dict)

    def test_import_fonctions(self):
        """Test import des fonctions principales."""
        from src.modules.maison.jardin_zones import (
            afficher_carte_zone,
            afficher_conseils_amelioration,
            afficher_detail_zone,
            afficher_vue_ensemble,
            ajouter_photo_zone,
            app,
            charger_zones,
            mettre_a_jour_zone,
        )

        assert callable(charger_zones)
        assert callable(mettre_a_jour_zone)
        assert callable(ajouter_photo_zone)
        assert callable(afficher_carte_zone)
        assert callable(afficher_vue_ensemble)
        assert callable(afficher_detail_zone)
        assert callable(afficher_conseils_amelioration)
        assert callable(app)


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════


class TestJardinZonesConstantes:
    """Tests des constantes du module."""

    def test_emoji_zone_contenu(self):
        """Test que EMOJI_ZONE contient les types attendus."""
        from src.modules.maison.jardin_zones import EMOJI_ZONE

        types_attendus = [
            "pelouse",
            "potager",
            "arbres",
            "piscine",
            "terrasse",
            "compost",
        ]
        for type_zone in types_attendus:
            assert type_zone in EMOJI_ZONE

    def test_couleur_etat_notes(self):
        """Test que COULEUR_ETAT couvre les notes 1-5."""
        from src.modules.maison.jardin_zones import COULEUR_ETAT

        for note in range(1, 6):
            assert note in COULEUR_ETAT
            assert COULEUR_ETAT[note].startswith("#")

    def test_label_etat_notes(self):
        """Test que LABEL_ETAT couvre les notes 1-5."""
        from src.modules.maison.jardin_zones import LABEL_ETAT

        for note in range(1, 6):
            assert note in LABEL_ETAT


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS CHARGER ZONES
# ═══════════════════════════════════════════════════════════════════════════════


class TestChargerZones:
    """Tests pour la fonction charger_zones."""

    @patch("src.modules.maison.jardin_zones.st")
    @patch("src.modules.maison.jardin_zones.obtenir_contexte_db")
    def test_charger_zones_vide(self, mock_ctx, mock_st):
        """Test chargement zones quand base vide."""
        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        # Clear cache avant test
        from src.modules.maison.jardin_zones import charger_zones

        charger_zones.clear()

        result = charger_zones()

        assert result == []

    @patch("src.modules.maison.jardin_zones.st")
    @patch("src.modules.maison.jardin_zones.obtenir_contexte_db")
    def test_charger_zones_avec_donnees(self, mock_ctx, mock_st):
        """Test chargement zones avec données."""
        mock_zone = MagicMock()
        mock_zone.id = 1
        mock_zone.nom = "Pelouse Principale"
        mock_zone.type_zone = "pelouse"
        mock_zone.surface_m2 = 1000
        mock_zone.etat_note = 4
        mock_zone.etat_description = "Bon état"
        mock_zone.objectif = "Entretien régulier"
        mock_zone.prochaine_action = "Tonte"
        mock_zone.date_prochaine_action = date(2026, 3, 1)
        mock_zone.photos_url = ["avant:url1"]
        mock_zone.budget_estime = 100.0

        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = [mock_zone]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.jardin_zones import charger_zones

        charger_zones.clear()

        result = charger_zones()

        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["nom"] == "Pelouse Principale"
        assert result[0]["type_zone"] == "pelouse"
        assert result[0]["surface_m2"] == 1000
        assert result[0]["etat_note"] == 4

    @patch("src.modules.maison.jardin_zones.st")
    @patch("src.modules.maison.jardin_zones.obtenir_contexte_db")
    def test_charger_zones_valeurs_par_defaut(self, mock_ctx, mock_st):
        """Test chargement zones avec valeurs None."""
        mock_zone = MagicMock()
        mock_zone.id = 2
        mock_zone.nom = "Zone Test"
        mock_zone.type_zone = "autre"
        mock_zone.surface_m2 = None
        mock_zone.etat_note = None
        mock_zone.etat_description = None
        mock_zone.objectif = None
        mock_zone.prochaine_action = None
        mock_zone.date_prochaine_action = None
        mock_zone.photos_url = None
        mock_zone.budget_estime = None

        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = [mock_zone]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.jardin_zones import charger_zones

        charger_zones.clear()

        result = charger_zones()

        assert result[0]["surface_m2"] == 0
        assert result[0]["etat_note"] == 3
        assert result[0]["etat_description"] == ""
        assert result[0]["objectif"] == ""
        assert result[0]["prochaine_action"] == ""
        assert result[0]["photos_url"] == []
        assert result[0]["budget_estime"] == 0

    @patch("src.modules.maison.jardin_zones.st")
    @patch("src.modules.maison.jardin_zones.obtenir_contexte_db")
    def test_charger_zones_erreur(self, mock_ctx, mock_st):
        """Test gestion erreur lors du chargement."""
        mock_ctx.return_value.__enter__ = MagicMock(side_effect=Exception("DB Error"))
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.jardin_zones import charger_zones

        charger_zones.clear()

        result = charger_zones()

        assert result == []


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS METTRE A JOUR ZONE
# ═══════════════════════════════════════════════════════════════════════════════


class TestMettreAJourZone:
    """Tests pour la fonction mettre_a_jour_zone."""

    @patch("src.modules.maison.jardin_zones.charger_zones")
    def test_mettre_a_jour_zone_succes(self, mock_charger):
        """Test mise à jour réussie."""
        mock_zone = MagicMock()
        mock_zone.etat_note = 3

        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_zone

        from src.modules.maison.jardin_zones import mettre_a_jour_zone

        result = mettre_a_jour_zone(1, {"etat_note": 5}, db=mock_db)

        assert result is True
        assert mock_zone.etat_note == 5
        mock_db.commit.assert_called_once()
        mock_charger.clear.assert_called()

    @patch("src.modules.maison.jardin_zones.charger_zones")
    def test_mettre_a_jour_zone_non_trouvee(self, mock_charger):
        """Test mise à jour zone inexistante."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        from src.modules.maison.jardin_zones import mettre_a_jour_zone

        result = mettre_a_jour_zone(999, {"etat_note": 5}, db=mock_db)

        assert result is False

    @patch("src.modules.maison.jardin_zones.charger_zones")
    def test_mettre_a_jour_zone_erreur(self, mock_charger):
        """Test gestion erreur lors mise à jour."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.side_effect = Exception("DB Error")

        from src.modules.maison.jardin_zones import mettre_a_jour_zone

        result = mettre_a_jour_zone(1, {"etat_note": 5}, db=mock_db)

        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS AJOUTER PHOTO ZONE
# ═══════════════════════════════════════════════════════════════════════════════


class TestAjouterPhotoZone:
    """Tests pour la fonction ajouter_photo_zone."""

    @patch("src.modules.maison.jardin_zones.charger_zones")
    def test_ajouter_photo_avant_succes(self, mock_charger):
        """Test ajout photo avant."""
        mock_zone = MagicMock()
        mock_zone.photos_url = []

        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_zone

        from src.modules.maison.jardin_zones import ajouter_photo_zone

        result = ajouter_photo_zone(1, "http://example.com/photo.jpg", est_avant=True, db=mock_db)

        assert result is True
        assert mock_zone.photos_url == ["avant:http://example.com/photo.jpg"]
        mock_db.commit.assert_called_once()

    @patch("src.modules.maison.jardin_zones.charger_zones")
    def test_ajouter_photo_apres_succes(self, mock_charger):
        """Test ajout photo après."""
        mock_zone = MagicMock()
        mock_zone.photos_url = []

        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_zone

        from src.modules.maison.jardin_zones import ajouter_photo_zone

        result = ajouter_photo_zone(1, "http://example.com/photo.jpg", est_avant=False, db=mock_db)

        assert result is True
        assert mock_zone.photos_url == ["apres:http://example.com/photo.jpg"]

    @patch("src.modules.maison.jardin_zones.charger_zones")
    def test_ajouter_photo_a_liste_existante(self, mock_charger):
        """Test ajout photo à liste existante."""
        mock_zone = MagicMock()
        mock_zone.photos_url = ["avant:url1"]

        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_zone

        from src.modules.maison.jardin_zones import ajouter_photo_zone

        result = ajouter_photo_zone(1, "url2", est_avant=True, db=mock_db)

        assert result is True
        assert "avant:url2" in mock_zone.photos_url

    @patch("src.modules.maison.jardin_zones.charger_zones")
    def test_ajouter_photo_zone_non_trouvee(self, mock_charger):
        """Test ajout photo zone inexistante."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        from src.modules.maison.jardin_zones import ajouter_photo_zone

        result = ajouter_photo_zone(999, "url", db=mock_db)

        assert result is False

    @patch("src.modules.maison.jardin_zones.charger_zones")
    def test_ajouter_photo_photos_None(self, mock_charger):
        """Test ajout photo quand photos_url est None."""
        mock_zone = MagicMock()
        mock_zone.photos_url = None

        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_zone

        from src.modules.maison.jardin_zones import ajouter_photo_zone

        result = ajouter_photo_zone(1, "url", est_avant=True, db=mock_db)

        assert result is True
        assert mock_zone.photos_url == ["avant:url"]


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS RENDER CARTE ZONE
# ═══════════════════════════════════════════════════════════════════════════════


class TestRenderCarteZone:
    """Tests pour la fonction afficher_carte_zone."""

    @patch("src.modules.maison.jardin_zones.st")
    def test_render_carte_zone_basique(self, mock_st):
        """Test rendu carte zone basique."""
        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        zone = {
            "id": 1,
            "nom": "Pelouse",
            "type_zone": "pelouse",
            "surface_m2": 500,
            "etat_note": 4,
            "etat_description": "Bon état",
            "prochaine_action": "Tonte",
            "photos_url": [],
        }

        from src.modules.maison.jardin_zones import afficher_carte_zone

        afficher_carte_zone(zone)

        mock_st.container.assert_called_once_with(border=True)
        mock_st.progress.assert_called()

    @patch("src.modules.maison.jardin_zones.st")
    def test_render_carte_zone_avec_photos(self, mock_st):
        """Test rendu carte zone avec photos."""
        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col, mock_col]

        zone = {
            "id": 1,
            "nom": "Potager",
            "type_zone": "potager",
            "surface_m2": 100,
            "etat_note": 3,
            "etat_description": "",
            "prochaine_action": "",
            "photos_url": ["avant:url1", "apres:url2"],
        }

        from src.modules.maison.jardin_zones import afficher_carte_zone

        afficher_carte_zone(zone)

        mock_st.container.assert_called()

    @patch("src.modules.maison.jardin_zones.st")
    def test_render_carte_zone_etat_inconnu(self, mock_st):
        """Test rendu carte zone avec état inconnu."""
        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        zone = {
            "id": 1,
            "nom": "Zone Test",
            "type_zone": "inconnu",
            "surface_m2": 0,
            "etat_note": 99,  # Valeur hors range
            "etat_description": "",
            "prochaine_action": "",
            "photos_url": [],
        }

        from src.modules.maison.jardin_zones import afficher_carte_zone

        afficher_carte_zone(zone)

        mock_st.container.assert_called()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS RENDER VUE ENSEMBLE
# ═══════════════════════════════════════════════════════════════════════════════


class TestRenderVueEnsemble:
    """Tests pour la fonction afficher_vue_ensemble."""

    @patch("src.modules.maison.jardin_zones.charger_zones")
    @patch("src.modules.maison.jardin_zones.st")
    def test_render_vue_ensemble_vide(self, mock_st, mock_charger):
        """Test vue d'ensemble sans zones."""
        mock_charger.return_value = []

        from src.modules.maison.jardin_zones import afficher_vue_ensemble

        afficher_vue_ensemble()

        mock_st.warning.assert_called()

    @patch("src.modules.maison.jardin_zones.charger_zones")
    @patch("src.modules.maison.jardin_zones.go")
    @patch("src.modules.maison.jardin_zones.st")
    def test_render_vue_ensemble_avec_zones(self, mock_st, mock_go, mock_charger):
        """Test vue d'ensemble avec zones."""
        mock_charger.return_value = [
            {
                "nom": "Pelouse",
                "type_zone": "pelouse",
                "surface_m2": 1000,
                "etat_note": 4,
                "prochaine_action": "Tonte",
            },
            {
                "nom": "Potager",
                "type_zone": "potager",
                "surface_m2": 100,
                "etat_note": 2,
                "prochaine_action": "Arrosage",
            },
        ]
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]

        mock_fig = MagicMock()
        mock_go.Figure.return_value = mock_fig

        from src.modules.maison.jardin_zones import afficher_vue_ensemble

        afficher_vue_ensemble()

        mock_st.metric.assert_called()
        mock_st.plotly_chart.assert_called()

    @patch("src.modules.maison.jardin_zones.charger_zones")
    @patch("src.modules.maison.jardin_zones.go")
    @patch("src.modules.maison.jardin_zones.st")
    def test_render_vue_ensemble_zones_critiques(self, mock_st, mock_go, mock_charger):
        """Test vue d'ensemble avec alertes zones critiques."""
        mock_charger.return_value = [
            {
                "nom": "Zone Critique",
                "type_zone": "autre",
                "surface_m2": 50,
                "etat_note": 1,  # Critique
                "prochaine_action": "Urgent",
            },
        ]
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]

        mock_fig = MagicMock()
        mock_go.Figure.return_value = mock_fig

        from src.modules.maison.jardin_zones import afficher_vue_ensemble

        afficher_vue_ensemble()

        mock_st.error.assert_called()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS RENDER DETAIL ZONE
# ═══════════════════════════════════════════════════════════════════════════════


class TestRenderDetailZone:
    """Tests pour la fonction afficher_detail_zone."""

    @patch("src.modules.maison.jardin_zones.st")
    def test_render_detail_zone_basique(self, mock_st):
        """Test rendu détail zone basique."""
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col, mock_col]
        mock_st.tabs.return_value = [mock_col, mock_col]

        mock_form = MagicMock()
        mock_form.__enter__ = MagicMock(return_value=mock_form)
        mock_form.__exit__ = MagicMock(return_value=False)
        mock_st.form.return_value = mock_form
        mock_st.form_submit_button.return_value = False

        zone = {
            "id": 1,
            "nom": "Pelouse",
            "type_zone": "pelouse",
            "surface_m2": 500,
            "etat_note": 4,
            "etat_description": "Bon état",
            "objectif": "Garder bien vert",
            "prochaine_action": "Tonte",
            "photos_url": [],
        }

        from src.modules.maison.jardin_zones import afficher_detail_zone

        afficher_detail_zone(zone)

        mock_st.markdown.assert_called()
        mock_st.progress.assert_called()

    @patch("src.modules.maison.jardin_zones.st")
    def test_render_detail_zone_avec_photos(self, mock_st):
        """Test rendu détail zone avec photos avant/après."""
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col, mock_col]
        mock_st.tabs.return_value = [mock_col, mock_col]

        mock_form = MagicMock()
        mock_form.__enter__ = MagicMock(return_value=mock_form)
        mock_form.__exit__ = MagicMock(return_value=False)
        mock_st.form.return_value = mock_form
        mock_st.form_submit_button.return_value = False

        zone = {
            "id": 2,
            "nom": "Potager",
            "type_zone": "potager",
            "surface_m2": 100,
            "etat_note": 3,
            "etat_description": "",
            "objectif": "",
            "prochaine_action": "",
            "photos_url": ["avant:url1", "avant:url2", "apres:url3"],
        }

        from src.modules.maison.jardin_zones import afficher_detail_zone

        afficher_detail_zone(zone)

        mock_st.tabs.assert_called()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS RENDER CONSEILS AMELIORATION
# ═══════════════════════════════════════════════════════════════════════════════


class TestRenderConseilsAmelioration:
    """Tests pour la fonction afficher_conseils_amelioration."""

    @patch("src.modules.maison.jardin_zones.st")
    def test_render_conseils_amelioration(self, mock_st):
        """Test affichage conseils amélioration."""
        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=False)
        mock_st.expander.return_value = mock_expander

        from src.modules.maison.jardin_zones import afficher_conseils_amelioration

        afficher_conseils_amelioration()

        mock_st.markdown.assert_called()
        mock_st.info.assert_called()
        assert mock_st.expander.call_count >= 4


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS APP (POINT D'ENTRÉE)
# ═══════════════════════════════════════════════════════════════════════════════


class TestApp:
    """Tests pour la fonction app (point d'entrée)."""

    @patch("src.modules.maison.jardin_zones.afficher_conseils_amelioration")
    @patch("src.modules.maison.jardin_zones.afficher_detail_zone")
    @patch("src.modules.maison.jardin_zones.afficher_vue_ensemble")
    @patch("src.modules.maison.jardin_zones.afficher_carte_zone")
    @patch("src.modules.maison.jardin_zones.charger_zones")
    @patch("src.modules.maison.jardin_zones.st")
    def test_app_sans_zones(
        self,
        mock_st,
        mock_charger,
        mock_render_carte,
        mock_render_vue,
        mock_render_detail,
        mock_render_conseils,
    ):
        """Test app sans zones configurées."""
        mock_charger.return_value = []
        mock_tab = MagicMock()
        mock_tab.__enter__ = MagicMock(return_value=mock_tab)
        mock_tab.__exit__ = MagicMock(return_value=False)
        mock_st.tabs.return_value = [mock_tab, mock_tab, mock_tab]
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        from src.modules.maison.jardin_zones import app

        app()

        mock_st.title.assert_called_once()
        mock_st.tabs.assert_called_once()
        mock_render_vue.assert_called_once()

    @patch("src.modules.maison.jardin_zones.afficher_conseils_amelioration")
    @patch("src.modules.maison.jardin_zones.afficher_detail_zone")
    @patch("src.modules.maison.jardin_zones.afficher_vue_ensemble")
    @patch("src.modules.maison.jardin_zones.afficher_carte_zone")
    @patch("src.modules.maison.jardin_zones.charger_zones")
    @patch("src.modules.maison.jardin_zones.st")
    def test_app_avec_zones(
        self,
        mock_st,
        mock_charger,
        mock_render_carte,
        mock_render_vue,
        mock_render_detail,
        mock_render_conseils,
    ):
        """Test app avec zones configurées."""
        mock_charger.return_value = [
            {
                "id": 1,
                "nom": "Pelouse",
                "type_zone": "pelouse",
                "surface_m2": 1000,
                "etat_note": 4,
                "etat_description": "",
                "objectif": "",
                "prochaine_action": "Tonte",
                "photos_url": [],
            },
            {
                "id": 2,
                "nom": "Potager",
                "type_zone": "potager",
                "surface_m2": 100,
                "etat_note": 3,
                "etat_description": "",
                "objectif": "",
                "prochaine_action": "",
                "photos_url": [],
            },
        ]

        mock_tab = MagicMock()
        mock_tab.__enter__ = MagicMock(return_value=mock_tab)
        mock_tab.__exit__ = MagicMock(return_value=False)
        mock_st.tabs.return_value = [mock_tab, mock_tab, mock_tab]

        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col, mock_col]

        mock_st.selectbox.return_value = "Pelouse"

        from src.modules.maison.jardin_zones import app

        app()

        mock_st.title.assert_called_once_with("🌳 Jardin - Dashboard Zones")
        assert mock_render_carte.call_count == 2  # 2 zones
        mock_render_detail.assert_called_once()
        mock_render_conseils.assert_called_once()

    @patch("src.modules.maison.jardin_zones.afficher_conseils_amelioration")
    @patch("src.modules.maison.jardin_zones.afficher_detail_zone")
    @patch("src.modules.maison.jardin_zones.afficher_vue_ensemble")
    @patch("src.modules.maison.jardin_zones.afficher_carte_zone")
    @patch("src.modules.maison.jardin_zones.charger_zones")
    @patch("src.modules.maison.jardin_zones.st")
    def test_app_selection_zone(
        self,
        mock_st,
        mock_charger,
        mock_render_carte,
        mock_render_vue,
        mock_render_detail,
        mock_render_conseils,
    ):
        """Test app avec sélection d'une zone."""
        zones = [
            {
                "id": 1,
                "nom": "Pelouse",
                "type_zone": "pelouse",
                "surface_m2": 1000,
                "etat_note": 4,
                "etat_description": "",
                "objectif": "",
                "prochaine_action": "",
                "photos_url": [],
            },
        ]
        mock_charger.return_value = zones

        mock_tab = MagicMock()
        mock_tab.__enter__ = MagicMock(return_value=mock_tab)
        mock_tab.__exit__ = MagicMock(return_value=False)
        mock_st.tabs.return_value = [mock_tab, mock_tab, mock_tab]

        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [mock_col, mock_col]

        mock_st.selectbox.return_value = "Pelouse"

        from src.modules.maison.jardin_zones import app

        app()

        mock_st.selectbox.assert_called()
        mock_render_detail.assert_called_once_with(zones[0])


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION LÉGERS
# ═══════════════════════════════════════════════════════════════════════════════


class TestJardinZonesIntegration:
    """Tests d'intégration légers."""

    @patch("src.modules.maison.jardin_zones.st")
    @patch("src.modules.maison.jardin_zones.obtenir_contexte_db")
    def test_workflow_complet_lecture(self, mock_ctx, mock_st):
        """Test workflow lecture zones."""
        mock_zone = MagicMock()
        mock_zone.id = 1
        mock_zone.nom = "Test"
        mock_zone.type_zone = "pelouse"
        mock_zone.surface_m2 = 100
        mock_zone.etat_note = 3
        mock_zone.etat_description = ""
        mock_zone.objectif = ""
        mock_zone.prochaine_action = ""
        mock_zone.date_prochaine_action = None
        mock_zone.photos_url = []
        mock_zone.budget_estime = None

        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = [mock_zone]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.jardin_zones import charger_zones

        charger_zones.clear()

        result = charger_zones()

        assert len(result) == 1
        assert result[0]["nom"] == "Test"
