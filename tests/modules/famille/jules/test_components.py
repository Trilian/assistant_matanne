"""
Tests unitaires pour src/modules/famille/jules/components.py
"""

from datetime import date
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class SessionStateMock(dict):
    """Mock de session_state Streamlit"""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def setup_mock_st(mock_st: MagicMock, session_data: dict | None = None) -> None:
    """Configure le mock streamlit avec les valeurs par defaut"""

    def mock_columns(n, **kwargs):
        count = n if isinstance(n, int) else len(n)
        return [MagicMock() for _ in range(count)]

    mock_st.columns.side_effect = mock_columns
    mock_st.session_state = SessionStateMock(session_data or {})
    mock_st.tabs.return_value = [MagicMock() for _ in range(4)]
    mock_st.button.return_value = False
    mock_st.form.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.form_submit_button.return_value = False
    mock_st.container.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.spinner.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.selectbox.return_value = "Tous"
    mock_st.text_input.return_value = ""
    mock_st.text_area.return_value = ""
    mock_st.number_input.return_value = 0.0


def create_mock_achat(
    id_: int,
    nom: str,
    categorie: str,
    priorite: str = "moyenne",
    prix_estime: float = None,
    taille: str = None,
    description: str = None,
    achete: bool = False,
):
    """Cree un mock d'achat AchatFamille"""
    mock = MagicMock()
    mock.id = id_
    mock.nom = nom
    mock.categorie = categorie
    mock.priorite = priorite
    mock.prix_estime = prix_estime
    mock.taille = taille
    mock.description = description
    mock.achete = achete
    mock.date_achat = None
    return mock


class TestRenderDashboard:
    """Tests pour afficher_dashboard"""

    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_taille_vetements")
    @patch("src.modules.famille.jules.components.get_achats_jules_en_attente")
    def test_dashboard_basic(self, mock_achats, mock_tailles, mock_age, mock_st):
        """Test affichage basique du dashboard"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 24, "semaines": 104}
        mock_tailles.return_value = {"vetements": "2 ans", "chaussures": "24"}
        mock_achats.return_value = []

        from src.modules.famille.jules.components import afficher_dashboard

        afficher_dashboard()

        mock_st.subheader.assert_called_once_with("📊 Dashboard")
        mock_st.metric.assert_any_call("🎂 Âge", "24 mois", "104 semaines")
        mock_st.metric.assert_any_call("👕 Taille vêtements", "2 ans")
        mock_st.metric.assert_any_call("👟 Pointure", "24")

    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_taille_vetements")
    @patch("src.modules.famille.jules.components.get_achats_jules_en_attente")
    def test_dashboard_with_achats(self, mock_achats, mock_tailles, mock_age, mock_st):
        """Test affichage dashboard avec des achats suggeres"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_tailles.return_value = {"vetements": "18-24 mois", "chaussures": "22"}

        achat1 = MagicMock()
        achat1.nom = "Chaussures"
        achat1.categorie = "jules_vetements"
        achat1.priorite = "urgent"

        achat2 = MagicMock()
        achat2.nom = "Jouet"
        achat2.categorie = "jules_jouets"
        achat2.priorite = "basse"

        mock_achats.return_value = [achat1, achat2]

        from src.modules.famille.jules.components import afficher_dashboard

        afficher_dashboard()

        mock_st.markdown.assert_any_call("---")
        mock_st.markdown.assert_any_call("**🛒 Achats suggeres:**")
        assert mock_st.write.call_count >= 2

    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_taille_vetements")
    @patch("src.modules.famille.jules.components.get_achats_jules_en_attente")
    def test_dashboard_with_haute_priorite(self, mock_achats, mock_tailles, mock_age, mock_st):
        """Test affichage dashboard avec haute priorite"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_tailles.return_value = {"vetements": "18-24 mois", "chaussures": "22"}

        achat = MagicMock()
        achat.nom = "Article urgent"
        achat.categorie = "jules_vetements"
        achat.priorite = "haute"
        mock_achats.return_value = [achat]

        from src.modules.famille.jules.components import afficher_dashboard

        afficher_dashboard()

        # Verifie que l'emoji rouge est utilise pour haute priorite
        calls = [str(c) for c in mock_st.write.call_args_list]
        assert any("🔴" in str(c) for c in calls)


class TestRenderActivites:
    """Tests pour afficher_activites"""

    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_activites_pour_age")
    def test_activites_basic(self, mock_activites, mock_age, mock_st):
        """Test affichage basique des activites"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_activites.return_value = [
            {
                "nom": "Peinture",
                "emoji": "🎨",
                "duree": "20 min",
                "description": "Peinture libre",
                "interieur": True,
            }
        ]

        from src.modules.famille.jules.components import afficher_activites

        afficher_activites()

        mock_st.subheader.assert_called_once_with("🎨 Activites du jour")
        mock_st.selectbox.assert_called()

    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_activites_pour_age")
    def test_activites_filter_interieur(self, mock_activites, mock_age, mock_st):
        """Test filtre interieur"""
        setup_mock_st(mock_st)
        mock_st.selectbox.return_value = "Interieur"
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_activites.return_value = [
            {
                "nom": "Peinture",
                "emoji": "🎨",
                "duree": "20 min",
                "description": "Int",
                "interieur": True,
            },
            {
                "nom": "Ballon",
                "emoji": "⚽",
                "duree": "30 min",
                "description": "Ext",
                "interieur": False,
            },
        ]

        from src.modules.famille.jules.components import afficher_activites

        afficher_activites()

        # Verifie que les activites sont filtrees
        assert mock_st.container.call_count >= 1

    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_activites_pour_age")
    def test_activites_filter_exterieur(self, mock_activites, mock_age, mock_st):
        """Test filtre exterieur - Line 66"""
        setup_mock_st(mock_st)
        mock_st.selectbox.return_value = "Exterieur"
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_activites.return_value = [
            {
                "nom": "Peinture",
                "emoji": "🎨",
                "duree": "20 min",
                "description": "Int",
                "interieur": True,
            },
            {
                "nom": "Ballon",
                "emoji": "⚽",
                "duree": "30 min",
                "description": "Ext",
                "interieur": False,
            },
        ]

        from src.modules.famille.jules.components import afficher_activites

        afficher_activites()

        # Le filtre exterieur doit filtrer les activites interieures
        mock_st.subheader.assert_called_once()

    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_activites_pour_age")
    def test_activites_button_suggestions_ia(self, mock_activites, mock_age, mock_st):
        """Test bouton suggestions IA - Line 60"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_activites.return_value = []

        # Simuler click sur le bouton IA
        mock_st.button.side_effect = [True, False]  # Premier bouton IA clicked

        from src.modules.famille.jules.components import afficher_activites

        afficher_activites()

        assert mock_st.session_state.get("jules_show_ai_activities") == True

    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_activites_pour_age")
    def test_activites_done_button(self, mock_activites, mock_age, mock_st):
        """Test bouton Fait - Line 78"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_activites.return_value = [
            {
                "nom": "Peinture",
                "emoji": "🎨",
                "duree": "20 min",
                "description": "Test",
                "interieur": True,
            }
        ]

        # Simuler: premier bouton (IA) = False, deuxieme (Fait) = True
        mock_st.button.side_effect = [False, True]

        from src.modules.famille.jules.components import afficher_activites

        afficher_activites()

        mock_st.success.assert_called_once_with("Super ! 🎉")

    @patch("src.modules.famille.jules.components.JulesAIService")
    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_activites_pour_age")
    def test_activites_show_ai_suggestions(
        self, mock_activites, mock_age, mock_st, mock_ai_service
    ):
        """Test affichage suggestions IA via streaming - Lines 82-98"""
        setup_mock_st(mock_st, {"jules_show_ai_activities": True})
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_activites.return_value = []

        # Mock AI service avec streaming
        mock_service_instance = MagicMock()
        mock_stream = MagicMock()
        mock_service_instance.stream_activites = MagicMock(return_value=mock_stream)
        mock_ai_service.return_value = mock_service_instance

        # Bouton Fermer = False
        mock_st.button.return_value = False

        from src.modules.famille.jules.components import afficher_activites

        afficher_activites()

        mock_st.markdown.assert_any_call("---")
        mock_st.markdown.assert_any_call("**🤖 Suggestions IA:**")
        mock_st.write_stream.assert_called_once_with(mock_stream)

    @patch("src.modules.famille.jules.components.JulesAIService")
    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_activites_pour_age")
    def test_activites_ai_error(self, mock_activites, mock_age, mock_st, mock_ai_service):
        """Test erreur IA dans suggestions"""
        setup_mock_st(mock_st, {"jules_show_ai_activities": True})
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_activites.return_value = []

        # Mock AI service avec erreur streaming
        mock_service_instance = MagicMock()
        mock_service_instance.stream_activites = MagicMock(side_effect=Exception("Erreur API"))
        mock_ai_service.return_value = mock_service_instance

        from src.modules.famille.jules.components import afficher_activites

        afficher_activites()

        # Verifie qu'une erreur est affichee
        error_calls = [c for c in mock_st.error.call_args_list]
        assert len(error_calls) > 0

    @patch("src.modules.famille.jules.components.JulesAIService")
    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_activites_pour_age")
    def test_activites_fermer_button(self, mock_activites, mock_age, mock_st, mock_ai_service):
        """Test bouton Fermer suggestions IA"""
        session_data = {"jules_show_ai_activities": True}
        setup_mock_st(mock_st, session_data)
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_activites.return_value = []

        # Mock AI service avec streaming
        mock_service_instance = MagicMock()
        mock_stream = MagicMock()
        mock_service_instance.stream_activites = MagicMock(return_value=mock_stream)
        mock_ai_service.return_value = mock_service_instance

        # Simuler click sur Fermer (2e bouton apres IA)
        mock_st.button.side_effect = [False, True]

        from src.modules.famille.jules.components import afficher_activites

        afficher_activites()

        assert mock_st.session_state.get("jules_show_ai_activities") == False
        mock_st.rerun.assert_called_once()


class TestRenderShopping:
    """Tests pour afficher_shopping"""

    @patch("src.modules.famille.jules.components.afficher_form_ajout_achat")
    @patch("src.modules.famille.jules.components.afficher_achats_categorie")
    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_taille_vetements")
    def test_shopping_basic(self, mock_tailles, mock_age, mock_st, mock_render_achats, mock_form):
        """Test affichage basique du shopping"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_tailles.return_value = {"vetements": "18-24 mois", "chaussures": "22"}

        from src.modules.famille.jules.components import afficher_shopping

        afficher_shopping()

        mock_st.subheader.assert_called_once_with("🛒 Shopping Jules")
        mock_st.tabs.assert_called_once()
        # Verifie que afficher_achats_categorie est appele pour chaque categorie
        assert mock_render_achats.call_count == 3

    @patch("src.modules.famille.jules.components.JulesAIService")
    @patch("src.modules.famille.jules.components.afficher_form_ajout_achat")
    @patch("src.modules.famille.jules.components.afficher_achats_categorie")
    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_taille_vetements")
    def test_shopping_suggerer_jouets(
        self, mock_tailles, mock_age, mock_st, mock_render_achats, mock_form, mock_ai_service
    ):
        """Test bouton suggerer jouets - Lines 124-132"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_tailles.return_value = {"vetements": "18-24 mois", "chaussures": "22"}

        # Simuler click sur le bouton suggerer jouets
        mock_st.button.return_value = True

        # Mock AI service avec streaming
        mock_service_instance = MagicMock()
        mock_stream = MagicMock()
        mock_service_instance.stream_jouets = MagicMock(return_value=mock_stream)
        mock_ai_service.return_value = mock_service_instance

        from src.modules.famille.jules.components import afficher_shopping

        afficher_shopping()

        mock_st.write_stream.assert_called_once_with(mock_stream)

    @patch("src.modules.famille.jules.components.JulesAIService")
    @patch("src.modules.famille.jules.components.afficher_form_ajout_achat")
    @patch("src.modules.famille.jules.components.afficher_achats_categorie")
    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_taille_vetements")
    def test_shopping_suggerer_jouets_error(
        self, mock_tailles, mock_age, mock_st, mock_render_achats, mock_form, mock_ai_service
    ):
        """Test erreur lors de la suggestion de jouets"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_tailles.return_value = {"vetements": "18-24 mois", "chaussures": "22"}

        mock_st.button.return_value = True

        # Mock AI avec erreur streaming
        mock_service_instance = MagicMock()
        mock_service_instance.stream_jouets = MagicMock(side_effect=Exception("Erreur API"))
        mock_ai_service.return_value = mock_service_instance

        from src.modules.famille.jules.components import afficher_shopping

        afficher_shopping()

        error_calls = [c for c in mock_st.error.call_args_list]
        assert len(error_calls) > 0


class TestRenderAchatsCategorie:
    """Tests pour afficher_achats_categorie"""

    @patch("src.modules.famille.jules.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.jules.components.st")
    def test_achats_categorie_empty(self, mock_st, mock_factory):
        """Test affichage sans achats"""
        setup_mock_st(mock_st)

        mock_service = MagicMock()
        mock_factory.return_value = mock_service
        mock_service.lister_par_categorie.return_value = []

        from src.modules.famille.jules.components import afficher_achats_categorie

        afficher_achats_categorie("jules_vetements")

        mock_st.caption.assert_called_with("Aucun article en attente")

    @patch("src.modules.famille.jules.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.jules.components.st")
    def test_achats_categorie_with_items(self, mock_st, mock_factory):
        """Test affichage avec des achats"""
        setup_mock_st(mock_st)

        achat = create_mock_achat(1, "Pantalon", "jules_vetements", "haute", 25.0, "24M", "Bleu")

        mock_service = MagicMock()
        mock_factory.return_value = mock_service
        mock_service.lister_par_categorie.return_value = [achat]

        from src.modules.famille.jules.components import afficher_achats_categorie

        afficher_achats_categorie("jules_vetements")

        mock_st.container.assert_called()
        # Verifie que le nom et les details sont affiches
        markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
        assert any("Pantalon" in str(c) for c in markdown_calls)

    @patch("src.modules.famille.jules.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.jules.components.st")
    def test_achats_categorie_buy_button(self, mock_st, mock_factory):
        """Test bouton acheter - Lines 179-185"""
        setup_mock_st(mock_st)

        achat = create_mock_achat(1, "Pantalon", "jules_vetements", "haute", 25.0)

        mock_service = MagicMock()
        mock_factory.return_value = mock_service
        mock_service.lister_par_categorie.return_value = [achat]

        # Simuler click sur le bouton acheter
        mock_st.button.return_value = True

        from src.modules.famille.jules.components import afficher_achats_categorie

        afficher_achats_categorie("jules_vetements")

        # Verifie que le service marque l'achat comme achete
        mock_service.marquer_achete.assert_called_once_with(achat.id)
        mock_st.success.assert_called_with("Achete!")
        mock_st.rerun.assert_called_once()

    @patch("src.modules.famille.jules.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.jules.components.st")
    def test_achats_categorie_priorite_emojis(self, mock_st, mock_factory):
        """Test emojis de priorite correctement affiches"""
        setup_mock_st(mock_st)
        mock_st.button.return_value = False

        achats = [
            create_mock_achat(1, "Urgent", "jules_vetements", "urgent"),
            create_mock_achat(2, "Haute", "jules_vetements", "haute"),
            create_mock_achat(3, "Moyenne", "jules_vetements", "moyenne"),
            create_mock_achat(4, "Basse", "jules_vetements", "basse"),
        ]

        mock_service = MagicMock()
        mock_factory.return_value = mock_service
        mock_service.lister_par_categorie.return_value = achats

        from src.modules.famille.jules.components import afficher_achats_categorie

        afficher_achats_categorie("jules_vetements")

        markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
        # Verifie les emojis de priorite
        assert any("🔴" in str(c) for c in markdown_calls)  # urgent
        assert any("🟠" in str(c) for c in markdown_calls)  # haute
        assert any("🟡" in str(c) for c in markdown_calls)  # moyenne
        assert any("🟢" in str(c) for c in markdown_calls)  # basse

    @patch("src.modules.famille.jules.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.jules.components.st")
    def test_achats_categorie_exception(self, mock_st, mock_factory):
        """Test gestion des erreurs"""
        setup_mock_st(mock_st)

        mock_factory.return_value.lister_par_categorie.side_effect = Exception("DB Error")

        from src.modules.famille.jules.components import afficher_achats_categorie

        afficher_achats_categorie("jules_vetements")

        mock_st.error.assert_called()

    @patch("src.modules.famille.jules.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.jules.components.st")
    def test_achats_categorie_unknown_priorite(self, mock_st, mock_factory):
        """Test priorite inconnue utilise emoji par defaut"""
        setup_mock_st(mock_st)
        mock_st.button.return_value = False

        achat = create_mock_achat(1, "Test", "jules_vetements", "inconnue")

        mock_service = MagicMock()
        mock_factory.return_value = mock_service
        mock_service.lister_par_categorie.return_value = [achat]

        from src.modules.famille.jules.components import afficher_achats_categorie

        afficher_achats_categorie("jules_vetements")

        markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
        assert any("⚪" in str(c) for c in markdown_calls)


class TestRenderFormAjoutAchat:
    """Tests pour afficher_form_ajout_achat"""

    @patch("src.modules.famille.jules.components.st")
    def test_form_display(self, mock_st):
        """Test affichage du formulaire"""
        setup_mock_st(mock_st)

        from src.modules.famille.jules.components import afficher_form_ajout_achat

        afficher_form_ajout_achat()

        mock_st.form.assert_called_once_with("add_purchase_jules")
        mock_st.text_input.assert_called()
        mock_st.selectbox.assert_called()
        mock_st.number_input.assert_called()

    @patch("src.modules.famille.jules.components.st")
    def test_form_submit_no_name(self, mock_st):
        """Test soumission sans nom - erreur"""
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = ""

        from src.modules.famille.jules.components import afficher_form_ajout_achat

        afficher_form_ajout_achat()

        mock_st.error.assert_called_with("Nom requis")

    @patch("src.modules.famille.jules.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.jules.components.st")
    def test_form_submit_success(self, mock_st, mock_factory):
        """Test soumission reussie - Lines 221-238"""
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True

        # Simuler les entrees utilisateur
        mock_st.text_input.side_effect = ["Article Test", "24M", "http://example.com"]
        mock_st.text_area.return_value = "Description test"
        mock_st.number_input.return_value = 50.0
        mock_st.selectbox.side_effect = [("jules_vetements", "👕 Vêtements"), "haute"]

        mock_service = MagicMock()
        mock_factory.return_value = mock_service

        from src.modules.famille.jules.components import afficher_form_ajout_achat

        afficher_form_ajout_achat()

        mock_service.ajouter_achat.assert_called_once()
        mock_st.success.assert_called()
        mock_st.rerun.assert_called_once()

    @patch("src.modules.famille.jules.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.jules.components.st")
    def test_form_submit_minimal(self, mock_st, mock_factory):
        """Test soumission avec donnees minimales"""
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True

        # Seulement le nom, le reste est vide/default
        mock_st.text_input.side_effect = ["Jouet Simple", "", ""]
        mock_st.text_area.return_value = ""
        mock_st.number_input.return_value = 0.0
        mock_st.selectbox.side_effect = [("jules_jouets", "🧸 Jouets"), "moyenne"]

        mock_service = MagicMock()
        mock_factory.return_value = mock_service

        from src.modules.famille.jules.components import afficher_form_ajout_achat

        afficher_form_ajout_achat()

        # Verifie que l'achat est cree via le service
        mock_service.ajouter_achat.assert_called_once()
        call_kwargs = mock_service.ajouter_achat.call_args
        assert call_kwargs[1]["nom"] == "Jouet Simple"

    @patch("src.modules.famille.jules.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.jules.components.st")
    def test_form_submit_exception(self, mock_st, mock_factory):
        """Test exception lors de la soumission - Line 258"""
        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.side_effect = ["Article", "", ""]
        mock_st.text_area.return_value = ""
        mock_st.number_input.return_value = 0.0
        mock_st.selectbox.side_effect = [("jules_vetements", "👕 Vêtements"), "moyenne"]

        # Simuler une erreur de service
        mock_factory.return_value.ajouter_achat.side_effect = Exception("DB Error")

        from src.modules.famille.jules.components import afficher_form_ajout_achat

        afficher_form_ajout_achat()

        mock_st.error.assert_called()


class TestRenderConseils:
    """Tests pour afficher_conseils"""

    @patch(
        "src.modules.famille.jules.components.CATEGORIES_CONSEILS",
        {
            "moteur": {"emoji": "🏃", "titre": "Motricite"},
            "langage": {"emoji": "💬", "titre": "Langage"},
            "social": {"emoji": "🤝", "titre": "Social"},
        },
    )
    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    def test_conseils_basic(self, mock_age, mock_st):
        """Test affichage basique des conseils"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 19, "semaines": 82}

        from src.modules.famille.jules.components import afficher_conseils

        afficher_conseils()

        mock_st.subheader.assert_called_once_with("💡 Conseils Developpement")
        mock_st.caption.assert_called()

    @patch(
        "src.modules.famille.jules.components.CATEGORIES_CONSEILS",
        {"moteur": {"emoji": "🏃", "titre": "Motricite"}},
    )
    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    def test_conseils_button_click(self, mock_age, mock_st):
        """Test clic sur bouton theme"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_st.button.return_value = True

        from src.modules.famille.jules.components import afficher_conseils

        afficher_conseils()

        assert mock_st.session_state.get("jules_conseil_theme") == "moteur"

    @patch("src.modules.famille.jules.components.JulesAIService")
    @patch(
        "src.modules.famille.jules.components.CATEGORIES_CONSEILS",
        {"moteur": {"emoji": "🏃", "titre": "Motricite"}},
    )
    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    def test_conseils_ai_generation(self, mock_age, mock_st, mock_ai_service):
        """Test generation conseil IA - Lines 273-275"""
        setup_mock_st(mock_st, {"jules_conseil_theme": "moteur"})
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_st.button.return_value = False

        # Mock AI service avec streaming
        mock_service_instance = MagicMock()
        mock_stream = MagicMock()
        mock_service_instance.stream_conseil = MagicMock(return_value=mock_stream)
        mock_ai_service.return_value = mock_service_instance

        from src.modules.famille.jules.components import afficher_conseils

        afficher_conseils()

        mock_st.markdown.assert_any_call("---")
        mock_st.markdown.assert_any_call("### 🏃 Motricite")
        mock_st.write_stream.assert_called_once_with(mock_stream)

    @patch("src.modules.famille.jules.components.JulesAIService")
    @patch(
        "src.modules.famille.jules.components.CATEGORIES_CONSEILS",
        {"moteur": {"emoji": "🏃", "titre": "Motricite"}},
    )
    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    def test_conseils_ai_error(self, mock_age, mock_st, mock_ai_service):
        """Test erreur generation conseil IA"""
        setup_mock_st(mock_st, {"jules_conseil_theme": "moteur"})
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_st.button.return_value = False

        # Mock AI avec erreur streaming
        mock_service_instance = MagicMock()
        mock_service_instance.stream_conseil = MagicMock(side_effect=Exception("Erreur API"))
        mock_ai_service.return_value = mock_service_instance

        from src.modules.famille.jules.components import afficher_conseils

        afficher_conseils()

        mock_st.error.assert_called()


class TestEdgeCases:
    """Tests pour les cas limites"""

    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_taille_vetements")
    @patch("src.modules.famille.jules.components.get_achats_jules_en_attente")
    def test_dashboard_more_than_3_achats(self, mock_achats, mock_tailles, mock_age, mock_st):
        """Test que seulement 3 achats sont affiches"""
        setup_mock_st(mock_st)
        mock_age.return_value = {"mois": 19, "semaines": 82}
        mock_tailles.return_value = {"vetements": "18-24 mois", "chaussures": "22"}

        # 5 achats mais seulement 3 doivent etre affiches
        achats = []
        for i in range(5):
            a = MagicMock()
            a.nom = f"Achat {i}"
            a.categorie = "jules_vetements"
            a.priorite = "moyenne"
            achats.append(a)
        mock_achats.return_value = achats

        from src.modules.famille.jules.components import afficher_dashboard

        afficher_dashboard()

        # Seulement 3 achats doivent etre ecrits
        assert mock_st.write.call_count == 3

    @patch("src.modules.famille.jules.components.obtenir_service_achats_famille")
    @patch("src.modules.famille.jules.components.st")
    def test_achats_sans_prix(self, mock_st, mock_factory):
        """Test affichage achats sans prix estime"""
        setup_mock_st(mock_st)
        mock_st.button.return_value = False

        achat = create_mock_achat(
            1,
            "Article",
            "jules_vetements",
            "moyenne",
            prix_estime=None,
            taille=None,
            description=None,
        )

        mock_service = MagicMock()
        mock_factory.return_value = mock_service
        mock_service.lister_par_categorie.return_value = [achat]

        from src.modules.famille.jules.components import afficher_achats_categorie

        afficher_achats_categorie("jules_vetements")

        # Pas d'erreur, le prix n'est pas affiche
        assert not mock_st.error.called

    @patch("src.modules.famille.jules.components.st")
    @patch("src.modules.famille.jules.components.get_age_jules")
    @patch("src.modules.famille.jules.components.get_activites_pour_age")
    def test_activites_sans_interieur_key(self, mock_activites, mock_age, mock_st):
        """Test activites sans cle interieur"""
        setup_mock_st(mock_st)
        mock_st.selectbox.return_value = "Interieur"
        mock_age.return_value = {"mois": 19, "semaines": 82}

        # Activite sans la cle 'interieur'
        mock_activites.return_value = [
            {"nom": "Test", "emoji": "🎨", "duree": "10 min", "description": "Desc"}
        ]

        from src.modules.famille.jules.components import afficher_activites

        afficher_activites()

        # Doit utiliser la valeur par defaut True
        mock_st.container.assert_called()
