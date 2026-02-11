"""
Tests pour src/services/suggestions/service.py
Cible: >80% couverture du service de suggestions IA
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from src.services.suggestions.service import (
    ServiceSuggestions,
    obtenir_service_suggestions,
    get_suggestions_ia_service,
    SuggestionsIAService,
)
from src.services.suggestions.types import (
    ProfilCulinaire,
    ContexteSuggestion,
    SuggestionRecette,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_client_ia():
    """Mock du client IA."""
    client = Mock()
    client.generer.return_value = '[{"nom": "Recette Test", "description": "Desc", "temps_minutes": 30, "pourquoi": "Rapide"}]'
    return client


@pytest.fixture
def mock_analyseur():
    """Mock de l'analyseur IA."""
    analyseur = Mock()
    analyseur.extraire_json.return_value = [
        {"nom": "Recette Test", "description": "Desc", "temps_minutes": 30, "pourquoi": "Rapide"}
    ]
    return analyseur


@pytest.fixture
def mock_cache():
    """Mock du cache."""
    return Mock()


@pytest.fixture
def service_suggestions(mock_client_ia, mock_analyseur, mock_cache):
    """Instance du service avec mocks."""
    with patch("src.services.suggestions.service.ClientIA", return_value=mock_client_ia):
        with patch("src.services.suggestions.service.AnalyseurIA", return_value=mock_analyseur):
            with patch("src.services.suggestions.service.obtenir_cache", return_value=mock_cache):
                service = ServiceSuggestions()
                service.client_ia = mock_client_ia
                service.analyseur = mock_analyseur
                service.cache = mock_cache
                return service


@pytest.fixture
def mock_session():
    """Session DB mockée."""
    session = Mock()
    session.query.return_value.filter.return_value.all.return_value = []
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.filter_by.return_value.first.return_value = None
    session.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = None
    session.query.return_value.all.return_value = []
    session.query.return_value.options.return_value.all.return_value = []
    return session


@pytest.fixture
def sample_profil():
    """Profil culinaire d'exemple."""
    return ProfilCulinaire(
        categories_preferees=["italien", "asiatique"],
        ingredients_frequents=["tomate", "oignon", "ail"],
        difficulte_moyenne="facile",
        temps_moyen_minutes=30,
        nb_portions_habituel=4,
        recettes_favorites=[1, 2, 3],
        jours_depuis_derniere_recette={1: 5, 2: 10, 3: 20},
    )


@pytest.fixture
def sample_contexte():
    """Contexte de suggestion d'exemple."""
    return ContexteSuggestion(
        type_repas="dîner",
        nb_personnes=4,
        temps_disponible_minutes=60,
        ingredients_disponibles=["tomate", "pâtes", "parmesan"],
        ingredients_a_utiliser=["tomate"],
        saison="été",
    )


@pytest.fixture
def mock_recette():
    """Recette mockée."""
    recette = Mock()
    recette.id = 1
    recette.nom = "Pâtes à la tomate"
    recette.categorie = "italien"
    recette.difficulte = "facile"
    recette.temps_preparation = 20
    recette.temps_cuisson = 15
    recette.portions = 4
    
    # Mock des ingrédients
    ingredient1 = Mock()
    ingredient1.nom = "tomate"
    ingredient_rel1 = Mock()
    ingredient_rel1.ingredient = ingredient1
    
    ingredient2 = Mock()
    ingredient2.nom = "pâtes"
    ingredient_rel2 = Mock()
    ingredient_rel2.ingredient = ingredient2
    
    recette.ingredients = [ingredient_rel1, ingredient_rel2]
    
    return recette


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION ET FACTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceSuggestionsInit:
    """Tests pour l'initialisation du service."""

    def test_init(self):
        """Vérifie l'initialisation."""
        with patch("src.services.suggestions.service.ClientIA"):
            with patch("src.services.suggestions.service.AnalyseurIA"):
                with patch("src.services.suggestions.service.obtenir_cache"):
                    service = ServiceSuggestions()
                    assert service.client_ia is not None
                    assert service.analyseur is not None
                    assert service.cache is not None

    def test_factory_obtenir_service(self):
        """Vérifie la factory obtenir_service_suggestions."""
        with patch("src.services.suggestions.service.ClientIA"):
            with patch("src.services.suggestions.service.AnalyseurIA"):
                with patch("src.services.suggestions.service.obtenir_cache"):
                    # Reset le singleton
                    import src.services.suggestions.service as svc_module
                    svc_module._suggestions_service = None
                    
                    service1 = obtenir_service_suggestions()
                    service2 = obtenir_service_suggestions()
                    
                    assert isinstance(service1, ServiceSuggestions)
                    assert service1 is service2  # Singleton

    def test_alias_compatibilite(self):
        """Vérifie les alias de compatibilité."""
        assert SuggestionsIAService is ServiceSuggestions
        assert get_suggestions_ia_service is obtenir_service_suggestions


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSER PROFIL CULINAIRE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAnalyserProfilCulinaire:
    """Tests pour analyser_profil_culinaire."""

    def test_profil_vide_sans_historique(self, service_suggestions, mock_session):
        """Vérifie le profil vide quand pas d'historique."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            profil = service_suggestions.analyser_profil_culinaire(session=mock_session)
            
        assert isinstance(profil, ProfilCulinaire)
        assert profil.categories_preferees == []
        assert profil.ingredients_frequents == []

    def test_profil_avec_historique(self, service_suggestions, mock_session, mock_recette):
        """Vérifie l'analyse avec historique."""
        # Mock de l'historique
        historique1 = Mock()
        historique1.recette_id = 1
        historique1.date_cuisson = datetime.now().date() - timedelta(days=5)
        
        historique2 = Mock()
        historique2.recette_id = 1
        historique2.date_cuisson = datetime.now().date() - timedelta(days=10)
        
        historique3 = Mock()
        historique3.recette_id = 1
        historique3.date_cuisson = datetime.now().date() - timedelta(days=15)
        
        mock_session.query.return_value.filter.return_value.all.return_value = [
            historique1, historique2, historique3
        ]
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_recette
        mock_session.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = historique1
        
        with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            profil = service_suggestions.analyser_profil_culinaire(session=mock_session)
        
        assert isinstance(profil, ProfilCulinaire)
        # Vérifier que l'analyse a été faite (même si les valeurs dépendent du mock)


# ═══════════════════════════════════════════════════════════
# TESTS CONSTRUIRE CONTEXTE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestConstruireContexte:
    """Tests pour construire_contexte."""

    def test_contexte_minimal(self, service_suggestions, mock_session):
        """Vérifie la construction du contexte minimal."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            contexte = service_suggestions.construire_contexte(session=mock_session)
        
        assert isinstance(contexte, ContexteSuggestion)
        assert contexte.type_repas == "dîner"
        assert contexte.nb_personnes == 4
        assert contexte.temps_disponible_minutes == 60
        assert contexte.saison in ["printemps", "été", "automne", "hiver"]

    def test_contexte_avec_parametres(self, service_suggestions, mock_session):
        """Vérifie la construction du contexte avec paramètres."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            contexte = service_suggestions.construire_contexte(
                type_repas="déjeuner",
                nb_personnes=2,
                temps_minutes=30,
                session=mock_session
            )
        
        assert contexte.type_repas == "déjeuner"
        assert contexte.nb_personnes == 2
        assert contexte.temps_disponible_minutes == 30

    def test_contexte_avec_stock(self, service_suggestions, mock_session):
        """Vérifie la construction du contexte avec stock."""
        # Mock des articles en stock
        article1 = Mock()
        article1.nom = "tomate"
        article1.date_peremption = None
        
        article2 = Mock()
        article2.nom = "lait"
        article2.date_peremption = datetime.now() + timedelta(days=2)  # Périme bientôt
        
        mock_session.query.return_value.filter.return_value.all.return_value = [
            article1, article2
        ]
        
        with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)
            
            contexte = service_suggestions.construire_contexte(session=mock_session)
        
        assert "tomate" in contexte.ingredients_disponibles
        assert "lait" in contexte.ingredients_disponibles
        assert "lait" in contexte.ingredients_a_utiliser

    def test_saison_printemps(self, service_suggestions, mock_session):
        """Vérifie la détection du printemps."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        with patch("src.services.suggestions.service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 4, 15)
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_ctx:
                mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
                mock_ctx.return_value.__exit__ = Mock(return_value=False)
                
                contexte = service_suggestions.construire_contexte(session=mock_session)
        
        assert contexte.saison == "printemps"


# ═══════════════════════════════════════════════════════════
# TESTS SUGGERER RECETTES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSuggererRecettes:
    """Tests pour suggerer_recettes."""

    def test_pas_de_recettes(self, service_suggestions, mock_session):
        """Vérifie quand pas de recettes."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.options.return_value.all.return_value = []
        
        with patch.object(service_suggestions, "construire_contexte") as mock_ctx:
            mock_ctx.return_value = ContexteSuggestion()
            with patch.object(service_suggestions, "analyser_profil_culinaire") as mock_profil:
                mock_profil.return_value = ProfilCulinaire()
                
                with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_db:
                    mock_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_db.return_value.__exit__ = Mock(return_value=False)
                    
                    result = service_suggestions.suggerer_recettes(session=mock_session)
        
        assert result == []

    def test_suggestions_generees(self, service_suggestions, mock_session, mock_recette, sample_contexte, sample_profil):
        """Vérifie la génération de suggestions."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.options.return_value.all.return_value = [mock_recette]
        
        with patch.object(service_suggestions, "construire_contexte", return_value=sample_contexte):
            with patch.object(service_suggestions, "analyser_profil_culinaire", return_value=sample_profil):
                with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_db:
                    mock_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_db.return_value.__exit__ = Mock(return_value=False)
                    
                    result = service_suggestions.suggerer_recettes(
                        contexte=sample_contexte,
                        session=mock_session
                    )
        
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER SCORE RECETTE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculerScoreRecette:
    """Tests pour _calculer_score_recette."""

    def test_score_base(self, service_suggestions, mock_recette, sample_contexte, sample_profil):
        """Vérifie le score de base."""
        score, raisons, tags = service_suggestions._calculer_score_recette(
            mock_recette, sample_contexte, sample_profil
        )
        assert score >= 0
        assert isinstance(raisons, list)
        assert isinstance(tags, list)

    def test_bonus_categorie_preferee(self, service_suggestions, mock_recette, sample_contexte, sample_profil):
        """Vérifie le bonus catégorie préférée."""
        mock_recette.categorie = "italien"  # Dans les préférées
        
        score_prefere, _, tags_prefere = service_suggestions._calculer_score_recette(
            mock_recette, sample_contexte, sample_profil
        )
        
        mock_recette.categorie = "autre"  # Pas dans les préférées
        score_autre, _, _ = service_suggestions._calculer_score_recette(
            mock_recette, sample_contexte, sample_profil
        )
        
        assert score_prefere > score_autre
        assert "favori" in tags_prefere

    def test_bonus_temps_adapte(self, service_suggestions, mock_recette, sample_contexte, sample_profil):
        """Vérifie le bonus temps adapté."""
        mock_recette.temps_preparation = 30  # Adapté à 60 min dispo
        score_adapte, _, tags = service_suggestions._calculer_score_recette(
            mock_recette, sample_contexte, sample_profil
        )
        
        mock_recette.temps_preparation = 120  # Trop long
        score_long, _, _ = service_suggestions._calculer_score_recette(
            mock_recette, sample_contexte, sample_profil
        )
        
        assert score_adapte > score_long
        assert "rapide" in tags

    def test_bonus_ingredients_prioritaires(self, service_suggestions, mock_recette, sample_profil):
        """Vérifie le bonus ingrédients prioritaires."""
        contexte_avec = ContexteSuggestion(
            ingredients_a_utiliser=["tomate"],  # La recette a des tomates
            ingredients_disponibles=["tomate", "pâtes"]
        )
        
        contexte_sans = ContexteSuggestion(
            ingredients_a_utiliser=["chocolat"],  # Pas dans la recette
            ingredients_disponibles=["tomate", "pâtes"]
        )
        
        score_avec, _, tags_avec = service_suggestions._calculer_score_recette(
            mock_recette, contexte_avec, sample_profil
        )
        score_sans, _, _ = service_suggestions._calculer_score_recette(
            mock_recette, contexte_sans, sample_profil
        )
        
        assert score_avec > score_sans
        assert "anti-gaspi" in tags_avec

    def test_malus_repetition_recente(self, service_suggestions, mock_recette, sample_contexte):
        """Vérifie le malus pour répétition récente."""
        profil_recent = ProfilCulinaire(
            jours_depuis_derniere_recette={1: 3}  # Préparée il y a 3 jours
        )
        profil_ancien = ProfilCulinaire(
            jours_depuis_derniere_recette={1: 30}  # Préparée il y a 30 jours
        )
        
        score_recent, _, _ = service_suggestions._calculer_score_recette(
            mock_recette, sample_contexte, profil_recent
        )
        score_ancien, _, _ = service_suggestions._calculer_score_recette(
            mock_recette, sample_contexte, profil_ancien
        )
        
        assert score_ancien > score_recent

    def test_bonus_decouverte(self, service_suggestions, mock_recette, sample_contexte):
        """Vérifie le bonus découverte."""
        profil_connue = ProfilCulinaire(
            jours_depuis_derniere_recette={1: 10}  # Déjà préparée
        )
        profil_nouvelle = ProfilCulinaire(
            jours_depuis_derniere_recette={}  # Jamais préparée
        )
        
        score_connue, _, _ = service_suggestions._calculer_score_recette(
            mock_recette, sample_contexte, profil_connue
        )
        score_nouvelle, _, tags = service_suggestions._calculer_score_recette(
            mock_recette, sample_contexte, profil_nouvelle
        )
        
        assert "découverte" in tags


# ═══════════════════════════════════════════════════════════
# TESTS TROUVER INGREDIENTS MANQUANTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTrouverIngredientsManquants:
    """Tests pour _trouver_ingredients_manquants."""

    def test_tous_disponibles(self, service_suggestions, mock_recette):
        """Vérifie quand tous les ingrédients sont disponibles."""
        disponibles = ["tomate", "pâtes"]
        
        manquants = service_suggestions._trouver_ingredients_manquants(
            mock_recette, disponibles
        )
        
        assert manquants == []

    def test_ingredients_manquants(self, service_suggestions, mock_recette):
        """Vérifie la détection des manquants."""
        disponibles = ["tomate"]
        
        manquants = service_suggestions._trouver_ingredients_manquants(
            mock_recette, disponibles
        )
        
        assert "pâtes" in manquants

    def test_recette_sans_ingredients(self, service_suggestions):
        """Vérifie avec recette sans ingrédients."""
        recette_sans = Mock()
        del recette_sans.ingredients
        
        manquants = service_suggestions._trouver_ingredients_manquants(
            recette_sans, ["tomate"]
        )
        
        assert manquants == []


# ═══════════════════════════════════════════════════════════
# TESTS MIXER SUGGESTIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestMixerSuggestions:
    """Tests pour _mixer_suggestions."""

    def test_mix_vide(self, service_suggestions):
        """Vérifie avec liste vide."""
        result = service_suggestions._mixer_suggestions([], 5)
        assert result == []

    def test_mix_ratio(self, service_suggestions):
        """Vérifie le ratio 60/40."""
        favoris = [SuggestionRecette(nom=f"Fav{i}", est_nouvelle=False) for i in range(5)]
        decouvertes = [SuggestionRecette(nom=f"Dec{i}", est_nouvelle=True) for i in range(5)]
        suggestions = favoris + decouvertes
        
        result = service_suggestions._mixer_suggestions(suggestions, 5)
        
        assert len(result) == 5
        # Vérifier le mix (3 favoris, 2 découvertes idéalement)
        nb_fav = sum(1 for s in result if not s.est_nouvelle)
        nb_dec = sum(1 for s in result if s.est_nouvelle)
        assert nb_fav >= 2  # Au moins quelques favoris
        assert nb_dec >= 1  # Au moins quelques découvertes

    def test_mix_incomplete(self, service_suggestions):
        """Vérifie avec pas assez de favoris ou découvertes."""
        suggestions = [SuggestionRecette(nom=f"S{i}", est_nouvelle=False) for i in range(3)]
        
        result = service_suggestions._mixer_suggestions(suggestions, 5)
        
        assert len(result) == 3  # Tout ce qu'on a


# ═══════════════════════════════════════════════════════════
# TESTS SUGGERER AVEC IA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSuggererAvecIA:
    """Tests pour suggerer_avec_ia."""

    def test_suggestion_ia_success(self, service_suggestions, mock_session, sample_contexte, sample_profil):
        """Vérifie la suggestion IA réussie."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        with patch.object(service_suggestions, "construire_contexte", return_value=sample_contexte):
            with patch.object(service_suggestions, "analyser_profil_culinaire", return_value=sample_profil):
                with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_db:
                    mock_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_db.return_value.__exit__ = Mock(return_value=False)
                    
                    result = service_suggestions.suggerer_avec_ia(
                        requete_utilisateur="Quelque chose de rapide",
                        session=mock_session
                    )
        
        assert isinstance(result, list)
        # Le mock retourne les suggestions

    def test_suggestion_ia_erreur(self, service_suggestions, mock_session, sample_contexte, sample_profil):
        """Vérifie la gestion d'erreur IA."""
        service_suggestions.client_ia.generer.side_effect = Exception("Erreur IA")
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        with patch.object(service_suggestions, "construire_contexte", return_value=sample_contexte):
            with patch.object(service_suggestions, "analyser_profil_culinaire", return_value=sample_profil):
                with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_db:
                    mock_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_db.return_value.__exit__ = Mock(return_value=False)
                    
                    result = service_suggestions.suggerer_avec_ia(
                        requete_utilisateur="Test",
                        session=mock_session
                    )
        
        assert result == []

    def test_suggestion_ia_json_invalide(self, service_suggestions, mock_session, sample_contexte, sample_profil):
        """Vérifie avec JSON invalide."""
        service_suggestions.analyseur.extraire_json.return_value = "not a list"
        mock_session.query.return_value.filter.return_value.all.return_value = []
        
        with patch.object(service_suggestions, "construire_contexte", return_value=sample_contexte):
            with patch.object(service_suggestions, "analyser_profil_culinaire", return_value=sample_profil):
                with patch("src.services.suggestions.service.obtenir_contexte_db") as mock_db:
                    mock_db.return_value.__enter__ = Mock(return_value=mock_session)
                    mock_db.return_value.__exit__ = Mock(return_value=False)
                    
                    result = service_suggestions.suggerer_avec_ia(
                        requete_utilisateur="Test",
                        session=mock_session
                    )
        
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS TYPES PYDANTIC
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProfilCulinaire:
    """Tests pour le type ProfilCulinaire."""

    def test_creation_defaut(self):
        """Vérifie les valeurs par défaut."""
        profil = ProfilCulinaire()
        assert profil.categories_preferees == []
        assert profil.ingredients_frequents == []
        assert profil.difficulte_moyenne == "moyen"
        assert profil.temps_moyen_minutes == 45
        assert profil.nb_portions_habituel == 4

    def test_creation_complete(self):
        """Vérifie la création avec valeurs."""
        profil = ProfilCulinaire(
            categories_preferees=["italien"],
            ingredients_frequents=["tomate"],
            difficulte_moyenne="facile",
            temps_moyen_minutes=30,
            nb_portions_habituel=2,
            recettes_favorites=[1, 2],
            jours_depuis_derniere_recette={1: 5},
        )
        assert profil.categories_preferees == ["italien"]
        assert len(profil.recettes_favorites) == 2


@pytest.mark.unit
class TestContexteSuggestion:
    """Tests pour le type ContexteSuggestion."""

    def test_creation_defaut(self):
        """Vérifie les valeurs par défaut."""
        ctx = ContexteSuggestion()
        assert ctx.type_repas == "dîner"
        assert ctx.nb_personnes == 4
        assert ctx.temps_disponible_minutes == 60
        assert ctx.budget == "normal"

    def test_creation_complete(self):
        """Vérifie la création avec valeurs."""
        ctx = ContexteSuggestion(
            type_repas="déjeuner",
            nb_personnes=2,
            temps_disponible_minutes=30,
            ingredients_disponibles=["tomate"],
            ingredients_a_utiliser=["lait"],
            contraintes=["vegetarien"],
            saison="été",
            budget="économique",
        )
        assert ctx.type_repas == "déjeuner"
        assert len(ctx.ingredients_disponibles) == 1


@pytest.mark.unit
class TestSuggestionRecette:
    """Tests pour le type SuggestionRecette."""

    def test_creation_defaut(self):
        """Vérifie les valeurs par défaut."""
        sugg = SuggestionRecette()
        assert sugg.recette_id is None
        assert sugg.nom == ""
        assert sugg.score == 0.0
        assert sugg.est_nouvelle is False

    def test_creation_complete(self):
        """Vérifie la création avec valeurs."""
        sugg = SuggestionRecette(
            recette_id=1,
            nom="Pâtes",
            raison="Rapide",
            score=85.0,
            tags=["rapide", "italien"],
            temps_preparation=20,
            difficulte="facile",
            ingredients_manquants=["parmesan"],
            est_nouvelle=True,
        )
        assert sugg.recette_id == 1
        assert sugg.score == 85.0
        assert "rapide" in sugg.tags
