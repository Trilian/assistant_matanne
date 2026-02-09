"""
Tests pour src/domains/famille/ui/jules/

Couverture ciblée: 80%
- helpers.py: get_age_jules, get_activites_pour_age, get_taille_vetements, get_achats_jules_en_attente
- ai_service.py: JulesAIService
- components.py: render_dashboard, render_activites, render_shopping, render_conseils
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import date, timedelta
from contextlib import contextmanager

from tests.fixtures.ui_mocks import (
    create_streamlit_mock,
    create_ui_test_context,
    assert_streamlit_called,
    assert_metric_displayed,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def mock_st():
    """Mock Streamlit configuré pour famille."""
    return create_ui_test_context("famille")


@contextmanager
def mock_db_context(return_value=None):
    """Mock pour get_db_context."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = return_value
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    
    @contextmanager
    def context():
        yield mock_db
    
    with patch("src.domains.famille.ui.jules.helpers.get_db_context", context):
        yield mock_db


@pytest.fixture
def mock_child_profile():
    """Mock de ChildProfile Jules."""
    profile = MagicMock()
    profile.name = "Jules"
    profile.actif = True
    profile.date_of_birth = date(2024, 6, 22)
    return profile


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS
# ═══════════════════════════════════════════════════════════

class TestJulesHelpers:
    """Tests pour jules/helpers.py"""
    
    def test_import_helpers(self):
        """Vérifie que les helpers s'importent."""
        from src.domains.famille.ui.jules.helpers import (
            get_age_jules,
            get_activites_pour_age,
            get_taille_vetements,
            get_achats_jules_en_attente,
        )
        assert callable(get_age_jules)
        assert callable(get_activites_pour_age)
        assert callable(get_taille_vetements)
        assert callable(get_achats_jules_en_attente)
    
    def test_get_age_jules_with_profile(self, mock_child_profile):
        """Test get_age_jules avec un profil trouvé."""
        from src.domains.famille.ui.jules.helpers import get_age_jules
        
        with mock_db_context(mock_child_profile):
            result = get_age_jules()
        
        assert "mois" in result
        assert "semaines" in result
        assert "jours" in result
        assert "date_naissance" in result
        assert isinstance(result["mois"], int)
        assert result["mois"] >= 0
    
    def test_get_age_jules_without_profile(self):
        """Test get_age_jules sans profil (valeur par défaut)."""
        from src.domains.famille.ui.jules.helpers import get_age_jules
        
        with mock_db_context(None):
            result = get_age_jules()
        
        assert "mois" in result
        assert result["date_naissance"] == date(2024, 6, 22)
    
    def test_get_age_jules_db_error(self):
        """Test get_age_jules avec erreur DB."""
        from src.domains.famille.ui.jules.helpers import get_age_jules
        
        with patch("src.domains.famille.ui.jules.helpers.get_db_context", 
                   side_effect=Exception("DB Error")):
            result = get_age_jules()
        
        # Doit retourner valeur par défaut sans lever d'exception
        assert "mois" in result
    
    def test_get_activites_pour_age_18_24(self):
        """Test activités pour 18-24 mois."""
        from src.domains.famille.ui.jules.helpers import get_activites_pour_age
        
        result = get_activites_pour_age(19)
        
        assert isinstance(result, list)
        assert len(result) > 0
        # Vérifier structure d'une activité
        if result:
            act = result[0]
            assert "nom" in act
            assert "emoji" in act
            assert "duree" in act
    
    def test_get_activites_pour_age_24_36(self):
        """Test activités pour 24-36 mois."""
        from src.domains.famille.ui.jules.helpers import get_activites_pour_age
        
        result = get_activites_pour_age(28)
        
        assert isinstance(result, list)
    
    def test_get_activites_pour_age_out_of_range(self):
        """Test activités pour âge hors plage (retourne défaut)."""
        from src.domains.famille.ui.jules.helpers import get_activites_pour_age
        
        result = get_activites_pour_age(50)
        
        # Doit retourner la plage par défaut
        assert isinstance(result, list)
    
    def test_get_taille_vetements_18_24(self):
        """Test tailles pour 18-24 mois."""
        from src.domains.famille.ui.jules.helpers import get_taille_vetements
        
        result = get_taille_vetements(19)
        
        assert "vetements" in result
        assert "chaussures" in result
        assert result["vetements"] == "86-92"
        assert result["chaussures"] == "22-23"
    
    def test_get_taille_vetements_12_18(self):
        """Test tailles pour 12-18 mois."""
        from src.domains.famille.ui.jules.helpers import get_taille_vetements
        
        result = get_taille_vetements(15)
        
        assert "vetements" in result
        assert "chaussures" in result
    
    def test_get_taille_vetements_24_36(self):
        """Test tailles pour 24-36 mois."""
        from src.domains.famille.ui.jules.helpers import get_taille_vetements
        
        result = get_taille_vetements(30)
        
        assert "vetements" in result
    
    def test_get_taille_vetements_default(self):
        """Test tailles hors plage (défaut)."""
        from src.domains.famille.ui.jules.helpers import get_taille_vetements
        
        result = get_taille_vetements(50)
        
        assert result["vetements"] == "86-92"
        assert result["chaussures"] == "22-23"
    
    def test_get_achats_jules_en_attente_empty(self):
        """Test get_achats_jules_en_attente sans résultats."""
        from src.domains.famille.ui.jules.helpers import get_achats_jules_en_attente
        
        with mock_db_context():
            result = get_achats_jules_en_attente()
        
        assert result == []
    
    def test_get_achats_jules_en_attente_with_items(self):
        """Test get_achats_jules_en_attente avec résultats."""
        from src.domains.famille.ui.jules.helpers import get_achats_jules_en_attente
        
        mock_purchases = [MagicMock(), MagicMock()]
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_purchases
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch("src.domains.famille.ui.jules.helpers.get_db_context", context):
            result = get_achats_jules_en_attente()
        
        assert len(result) == 2
    
    def test_get_achats_jules_en_attente_db_error(self):
        """Test get_achats_jules_en_attente avec erreur DB."""
        from src.domains.famille.ui.jules.helpers import get_achats_jules_en_attente
        
        with patch("src.domains.famille.ui.jules.helpers.get_db_context", 
                   side_effect=Exception("DB Error")):
            result = get_achats_jules_en_attente()
        
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS AI SERVICE
# ═══════════════════════════════════════════════════════════

class TestJulesAIService:
    """Tests pour jules/ai_service.py"""
    
    def test_import_ai_service(self):
        """Vérifie l'import du service IA."""
        from src.domains.famille.ui.jules.ai_service import JulesAIService
        assert JulesAIService is not None
    
    def test_service_initialization(self):
        """Test l'initialisation du service."""
        from src.domains.famille.ui.jules.ai_service import JulesAIService
        
        with patch("src.domains.famille.ui.jules.ai_service.ClientIA"):
            service = JulesAIService()
        
        assert service is not None
        assert service.service_name == "jules_ai"
    
    @pytest.mark.asyncio
    async def test_suggerer_activites(self):
        """Test suggérer des activités."""
        from src.domains.famille.ui.jules.ai_service import JulesAIService
        
        mock_response = "🎯 Activité test\n⏱️ 15min"
        
        with patch("src.domains.famille.ui.jules.ai_service.ClientIA") as mock_client:
            service = JulesAIService()
            service.call_with_cache = AsyncMock(return_value=mock_response)
            
            result = await service.suggerer_activites(19, "intérieur", 3)
        
        assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_conseil_developpement(self):
        """Test conseil de développement."""
        from src.domains.famille.ui.jules.ai_service import JulesAIService
        
        mock_response = "Conseil test"
        
        with patch("src.domains.famille.ui.jules.ai_service.ClientIA"):
            service = JulesAIService()
            service.call_with_cache = AsyncMock(return_value=mock_response)
            
            result = await service.conseil_developpement(19, "proprete")
        
        assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_suggerer_jouets(self):
        """Test suggérer des jouets."""
        from src.domains.famille.ui.jules.ai_service import JulesAIService
        
        mock_response = "🎁 Jouet test"
        
        with patch("src.domains.famille.ui.jules.ai_service.ClientIA"):
            service = JulesAIService()
            service.call_with_cache = AsyncMock(return_value=mock_response)
            
            result = await service.suggerer_jouets(19, budget=30)
        
        assert result == mock_response


# ═══════════════════════════════════════════════════════════
# TESTS COMPONENTS
# ═══════════════════════════════════════════════════════════

class TestJulesComponents:
    """Tests pour jules/components.py"""
    
    def test_import_components(self):
        """Vérifie l'import des composants."""
        from src.domains.famille.ui.jules.components import (
            render_dashboard,
            render_activites,
            render_shopping,
            render_conseils,
        )
        assert callable(render_dashboard)
        assert callable(render_activites)
        assert callable(render_shopping)
        assert callable(render_conseils)
    
    def test_render_dashboard(self, mock_st):
        """Test render_dashboard affiche les metrics."""
        from src.domains.famille.ui.jules import components
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_age_jules", return_value={
                "mois": 19, "semaines": 82, "jours": 574, "date_naissance": date(2024, 6, 22)
            }):
                with patch.object(components, "get_taille_vetements", return_value={
                    "vetements": "86-92", "chaussures": "22-23"
                }):
                    with patch.object(components, "get_achats_jules_en_attente", return_value=[]):
                        components.render_dashboard()
        
        # Vérifie que les éléments UI sont appelés
        mock_st.subheader.assert_called()
        assert mock_st.columns.called
        assert mock_st.metric.called
    
    def test_render_activites(self, mock_st):
        """Test render_activites affiche les activités."""
        from src.domains.famille.ui.jules import components
        
        mock_activities = [
            {"nom": "Pâte à modeler", "emoji": "🎨", "duree": "20min", "interieur": True, "description": "Test"}
        ]
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_age_jules", return_value={"mois": 19}):
                with patch.object(components, "get_activites_pour_age", return_value=mock_activities):
                    components.render_activites()
        
        mock_st.subheader.assert_called()
        assert mock_st.selectbox.called
    
    def test_render_shopping(self, mock_st):
        """Test render_shopping affiche les tabs."""
        from src.domains.famille.ui.jules import components
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_age_jules", return_value={"mois": 19}):
                with patch.object(components, "get_taille_vetements", return_value={
                    "vetements": "86-92", "chaussures": "22-23"
                }):
                    with patch.object(components, "render_achats_categorie", MagicMock()):
                        with patch.object(components, "render_form_ajout_achat", MagicMock()):
                            components.render_shopping()
        
        mock_st.subheader.assert_called()
        assert mock_st.tabs.called
        mock_st.info.assert_called()
    
    def test_render_conseils(self, mock_st):
        """Test render_conseils affiche les thèmes."""
        from src.domains.famille.ui.jules import components
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_age_jules", return_value={"mois": 19}):
                components.render_conseils()
        
        mock_st.subheader.assert_called()
        mock_st.caption.assert_called()
        assert mock_st.columns.called


# ═══════════════════════════════════════════════════════════
# TESTS MODULE APP
# ═══════════════════════════════════════════════════════════

class TestJulesApp:
    """Tests pour jules/__init__.py (app entry point)"""
    
    def test_import_app(self):
        """Vérifie l'import de app."""
        from src.domains.famille.ui.jules import app
        assert callable(app)
    
    def test_app_renders(self, mock_st):
        """Test que app() s'exécute sans erreur."""
        from src.domains.famille.ui import jules
        
        with patch.object(jules, "st", mock_st):
            with patch.object(jules, "get_age_jules", return_value={
                "mois": 19, "semaines": 82, "jours": 574, "date_naissance": date(2024, 6, 22)
            }):
                with patch.object(jules, "render_dashboard", MagicMock()):
                    with patch.object(jules, "render_activites", MagicMock()):
                        with patch.object(jules, "render_shopping", MagicMock()):
                            with patch.object(jules, "render_conseils", MagicMock()):
                                jules.app()
        
        mock_st.title.assert_called()
        assert mock_st.tabs.called


# ═══════════════════════════════════════════════════════════
# TESTS COMPONENTS ADDITIONAL (pour render_achats_categorie, render_form_ajout_achat)
# ═══════════════════════════════════════════════════════════

class TestJulesComponentsAdvanced:
    """Tests avancés pour jules/components.py"""
    
    def test_render_achats_categorie_empty(self, mock_st):
        """Test render_achats_categorie sans résultats."""
        from src.domains.famille.ui.jules import components
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_db_context", context):
                components.render_achats_categorie("jules_vetements")
        
        mock_st.caption.assert_called()
    
    def test_render_achats_categorie_with_data(self, mock_st):
        """Test render_achats_categorie avec résultats."""
        from src.domains.famille.ui.jules import components
        
        mock_achat = MagicMock()
        mock_achat.id = 1
        mock_achat.nom = "T-shirt"
        mock_achat.priorite = "urgent"
        mock_achat.taille = "86"
        mock_achat.description = "Bleu"
        mock_achat.prix_estime = 15.0
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_achat]
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_db_context", context):
                components.render_achats_categorie("jules_vetements")
        
        assert mock_st.container.called
        assert mock_st.columns.called
    
    def test_render_achats_categorie_db_error(self, mock_st):
        """Test render_achats_categorie avec erreur DB."""
        from src.domains.famille.ui.jules import components
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_db_context", side_effect=Exception("DB Error")):
                components.render_achats_categorie("jules_vetements")
        
        mock_st.error.assert_called()
    
    def test_render_form_ajout_achat(self, mock_st):
        """Test render_form_ajout_achat rendu du formulaire."""
        from src.domains.famille.ui.jules import components
        
        # Simuler form_submit_button retourne False (formulaire non soumis)
        mock_st.form_submit_button.return_value = False
        
        with patch.object(components, "st", mock_st):
            components.render_form_ajout_achat()
        
        mock_st.form.assert_called()
        mock_st.text_input.assert_called()
        mock_st.selectbox.assert_called()
    
    def test_render_form_ajout_achat_submit_empty(self, mock_st):
        """Test render_form_ajout_achat avec soumission vide."""
        from src.domains.famille.ui.jules import components
        
        # Simuler form_submit_button retourne True
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = ""  # Nom vide
        
        with patch.object(components, "st", mock_st):
            components.render_form_ajout_achat()
        
        mock_st.error.assert_called()
    
    def test_render_form_ajout_achat_submit_valid(self, mock_st):
        """Test render_form_ajout_achat avec soumission valide."""
        from src.domains.famille.ui.jules import components
        
        # Simuler form_submit_button retourne True
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.side_effect = ["T-shirt bébé", "86", "https://example.com"]
        mock_st.selectbox.side_effect = [("jules_vetements", "👕 Vêtements"), "moyenne"]
        mock_st.number_input.return_value = 15.0
        mock_st.text_area.return_value = "Notes test"
        
        mock_db = MagicMock()
        
        @contextmanager
        def context():
            yield mock_db
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_db_context", context):
                components.render_form_ajout_achat()
        
        # Vérifier que l'achat a été ajouté
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
        mock_st.success.assert_called()
    
    def test_render_conseils_ai_call(self, mock_st):
        """Test render_conseils avec appel IA."""
        from src.domains.famille.ui.jules import components
        
        mock_st.button.return_value = True  # Bouton cliqué
        
        with patch.object(components, "st", mock_st):
            with patch.object(components, "get_age_jules", return_value={"mois": 19}):
                with patch.object(components, "JulesAIService") as mock_ai:
                    mock_service = MagicMock()
                    mock_ai.return_value = mock_service
                    components.render_conseils()


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTS
# ═══════════════════════════════════════════════════════════

class TestJulesConstants:
    """Tests pour jules/_common.py constants"""
    
    def test_import_constants(self):
        """Vérifie l'import des constantes."""
        from src.domains.famille.ui.jules._common import (
            ACTIVITES_PAR_AGE,
            TAILLES_PAR_AGE,
            CATEGORIES_CONSEILS,
        )
        
        assert isinstance(ACTIVITES_PAR_AGE, dict)
        assert isinstance(TAILLES_PAR_AGE, dict)
        assert isinstance(CATEGORIES_CONSEILS, dict)
    
    def test_activites_structure(self):
        """Vérifie la structure des activités."""
        from src.domains.famille.ui.jules._common import ACTIVITES_PAR_AGE
        
        for (min_age, max_age), activites in ACTIVITES_PAR_AGE.items():
            assert isinstance(min_age, int)
            assert isinstance(max_age, int)
            assert min_age < max_age
            assert isinstance(activites, list)
            
            for act in activites:
                assert "nom" in act
                assert "emoji" in act
    
    def test_tailles_structure(self):
        """Vérifie la structure des tailles."""
        from src.domains.famille.ui.jules._common import TAILLES_PAR_AGE
        
        for (min_age, max_age), tailles in TAILLES_PAR_AGE.items():
            assert isinstance(min_age, int)
            assert "vetements" in tailles
            assert "chaussures" in tailles
    
    def test_conseils_structure(self):
        """Vérifie la structure des conseils."""
        from src.domains.famille.ui.jules._common import CATEGORIES_CONSEILS
        
        assert "proprete" in CATEGORIES_CONSEILS
        assert "sommeil" in CATEGORIES_CONSEILS
        assert "alimentation" in CATEGORIES_CONSEILS
        
        for key, info in CATEGORIES_CONSEILS.items():
            assert "emoji" in info
            assert "titre" in info
