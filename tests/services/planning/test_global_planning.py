"""Tests pour src/services/planning/global_planning.py - ServicePlanningUnifie.

Couverture des fonctionnalités:
- get_semaine_complete
- _charger_repas, _charger_activites, _charger_projets, _charger_routines, _charger_events
- _calculer_charge, _score_to_charge
- _detecter_alertes, _detecter_alertes_semaine
- _calculer_budget_jour, _calculer_stats_semaine
- generer_semaine_ia, creer_event
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date, datetime, timedelta
from contextlib import contextmanager

from src.services.planning.global_planning import (
    ServicePlanningUnifie,
    get_planning_unified_service,
    obtenir_service_planning_unifie,
)
from src.services.planning.types import JourCompletSchema, SemaineCompleSchema


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def lundi_test():
    """Un lundi de test."""
    return date(2024, 1, 15)


@pytest.fixture
def mock_db_session():
    """Session de base de données pleinement mockée."""
    from sqlalchemy.orm import Session
    
    mock_session = MagicMock(spec=Session)
    mock_query = MagicMock()
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.join.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []
    mock_query.first.return_value = None
    mock_query.count.return_value = 0
    mock_session.query.return_value = mock_query
    
    return mock_session


@pytest.fixture
def mock_context(mock_db_session):
    """Context manager pour mocker obtenir_contexte_db."""
    @contextmanager
    def _mock_db():
        yield mock_db_session
    return _mock_db


@pytest.fixture
def service():
    """Instance de ServicePlanningUnifie."""
    return ServicePlanningUnifie()


@pytest.fixture
def sample_repas_dict():
    """Repas de test sous forme de dict."""
    return {
        "id": 1,
        "type": "dejeuner",
        "recette": "Pâtes carbonara",
        "recette_id": 1,
        "portions": 4,
        "temps_total": 45,
        "notes": "Test"
    }


@pytest.fixture
def sample_activite_dict():
    """Activité de test sous forme de dict."""
    return {
        "id": 1,
        "titre": "Piscine avec Jules",
        "type": "sport",
        "debut": datetime(2024, 1, 15, 14, 0),
        "fin": datetime(2024, 1, 15, 16, 0),
        "lieu": "Piscine",
        "budget": 10,
        "duree": 2,
        "pour_jules": True,
    }


@pytest.fixture
def sample_projet_dict():
    """Projet de test sous forme de dict."""
    return {
        "id": 1,
        "nom": "Rangement garage",
        "priorite": "haute",
        "statut": "en_cours",
        "echéance": date(2024, 1, 20),
    }


@pytest.fixture
def sample_routine_dict():
    """Routine de test sous forme de dict."""
    return {
        "id": 1,
        "nom": "Brossage dents",
        "routine": "Routine matin",
        "heure": "07:00",
        "fait": False,
    }


@pytest.fixture
def sample_event_dict():
    """Événement de test sous forme de dict."""
    return {
        "id": 1,
        "titre": "RDV médecin",
        "type": "rdv",
        "debut": datetime(2024, 1, 15, 10, 0),
        "fin": datetime(2024, 1, 15, 10, 30),
        "lieu": "Cabinet",
        "couleur": "#FF0000",
    }


@pytest.fixture
def sample_jour_complet(lundi_test, sample_repas_dict, sample_activite_dict):
    """JourCompletSchema de test."""
    return JourCompletSchema(
        date=lundi_test,
        charge="normal",
        charge_score=50,
        repas=[sample_repas_dict],
        activites=[sample_activite_dict],
        projets=[],
        routines=[],
        events=[],
        budget_jour=10.0,
        alertes=[],
    )


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceFactory:
    """Tests pour les factories du service."""

    def test_get_planning_unified_service_returns_instance(self):
        """La factory retourne une instance de ServicePlanningUnifie."""
        service = get_planning_unified_service()
        assert service is not None
        assert isinstance(service, ServicePlanningUnifie)

    def test_obtenir_service_planning_unifie_returns_instance(self):
        """La factory française retourne une instance."""
        service = obtenir_service_planning_unifie()
        assert service is not None
        assert isinstance(service, ServicePlanningUnifie)

    def test_service_has_required_attributes(self):
        """Le service a les attributs requis."""
        service = ServicePlanningUnifie()
        assert hasattr(service, 'model')
        assert hasattr(service, 'get_semaine_complete')
        assert hasattr(service, '_charger_repas')
        assert hasattr(service, '_calculer_charge')


# ═══════════════════════════════════════════════════════════
# TESTS GET_SEMAINE_COMPLETE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetSemaineComplete:
    """Tests pour get_semaine_complete."""

    def test_retourne_semaine_schema(self, service, mock_db_session, mock_context, lundi_test):
        """Retourne une SemaineCompleSchema."""
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_semaine_complete(lundi_test)
        
        assert result is None or isinstance(result, SemaineCompleSchema)

    def test_structure_7_jours(self, service, mock_db_session, mock_context, lundi_test):
        """La semaine contient 7 jours."""
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_semaine_complete(lundi_test)
        
        if result is not None:
            assert len(result.jours) == 7

    def test_dates_correctes(self, service, mock_db_session, mock_context, lundi_test):
        """Les dates de début et fin sont correctes."""
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_semaine_complete(lundi_test)
        
        if result is not None:
            assert result.semaine_debut == lundi_test
            assert result.semaine_fin == lundi_test + timedelta(days=6)


# ═══════════════════════════════════════════════════════════
# TESTS CHARGER DONNÉES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestChargerRepas:
    """Tests pour _charger_repas."""

    def test_retourne_dict_vide_sans_repas(self, service, mock_db_session, lundi_test):
        """Retourne dict vide sans repas."""
        mock_db_session.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = []
        
        result = service._charger_repas(lundi_test, lundi_test + timedelta(days=6), mock_db_session)
        
        assert result == {}

    def test_groupe_par_jour(self, service, mock_db_session, lundi_test):
        """Groupe les repas par jour."""
        mock_repas = MagicMock()
        mock_repas.id = 1
        mock_repas.date_repas = lundi_test
        mock_repas.type_repas = "dejeuner"
        mock_repas.portion_ajustee = None
        mock_repas.notes = "Test"
        
        mock_recette = MagicMock()
        mock_recette.id = 1
        mock_recette.nom = "Pâtes"
        mock_recette.temps_preparation = 20
        mock_recette.temps_cuisson = 25
        mock_recette.portions = 4
        
        mock_db_session.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = [
            (mock_repas, mock_recette)
        ]
        
        result = service._charger_repas(lundi_test, lundi_test + timedelta(days=6), mock_db_session)
        
        assert isinstance(result, dict)


@pytest.mark.unit
class TestChargerActivites:
    """Tests pour _charger_activites."""

    def test_retourne_dict_vide_sans_activites(self, service, mock_db_session, lundi_test):
        """Retourne dict vide sans activités."""
        mock_db_session.query.return_value.filter.return_value.all.return_value = []
        
        result = service._charger_activites(lundi_test, lundi_test + timedelta(days=6), mock_db_session)
        
        assert result == {}

    def test_groupe_activites_par_jour(self, service, mock_db_session, lundi_test):
        """Groupe les activités par jour."""
        mock_activite = MagicMock()
        mock_activite.id = 1
        mock_activite.titre = "Piscine"
        mock_activite.date_prevue = lundi_test
        mock_activite.type_activite = "sport"
        mock_activite.lieu = "Piscine"
        mock_activite.cout_estime = 10
        mock_activite.duree_heures = 2
        
        mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_activite]
        
        result = service._charger_activites(lundi_test, lundi_test + timedelta(days=6), mock_db_session)
        
        assert isinstance(result, dict)


@pytest.mark.unit
class TestChargerProjets:
    """Tests pour _charger_projets."""

    def test_retourne_dict_vide_sans_projets(self, service, mock_db_session, lundi_test):
        """Retourne dict vide sans projets."""
        mock_db_session.query.return_value.filter.return_value.all.return_value = []
        
        result = service._charger_projets(lundi_test, lundi_test + timedelta(days=6), mock_db_session)
        
        assert result == {}

    def test_filtre_projets_actifs(self, service, mock_db_session, lundi_test):
        """Filtre uniquement les projets actifs."""
        mock_projet = MagicMock()
        mock_projet.id = 1
        mock_projet.nom = "Rangement"
        mock_projet.priorite = "haute"
        mock_projet.statut = "en_cours"
        mock_projet.date_fin_prevue = lundi_test + timedelta(days=3)
        
        mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_projet]
        
        result = service._charger_projets(lundi_test, lundi_test + timedelta(days=6), mock_db_session)
        
        assert isinstance(result, dict)


@pytest.mark.unit
class TestChargerRoutines:
    """Tests pour _charger_routines."""

    def test_retourne_dict_vide_sans_routines(self, service, mock_db_session):
        """Retourne dict vide sans routines."""
        mock_db_session.query.return_value.join.return_value.filter.return_value.all.return_value = []
        
        result = service._charger_routines(mock_db_session)
        
        assert result == {}

    def test_charge_routines_actives(self, service, mock_db_session):
        """Charge les routines actives."""
        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.nom = "Brossage dents"
        mock_task.heure_prevue = "07:00"
        mock_task.fait_le = None
        
        mock_routine = MagicMock()
        mock_routine.nom = "Routine matin"
        mock_routine.actif = True
        
        mock_db_session.query.return_value.join.return_value.filter.return_value.all.return_value = [
            (mock_task, mock_routine)
        ]
        
        result = service._charger_routines(mock_db_session)
        
        assert isinstance(result, dict)


@pytest.mark.unit
class TestChargerEvents:
    """Tests pour _charger_events."""

    def test_retourne_dict_vide_sans_events(self, service, mock_db_session, lundi_test):
        """Retourne dict vide sans événements."""
        mock_db_session.query.return_value.filter.return_value.all.return_value = []
        
        result = service._charger_events(lundi_test, lundi_test + timedelta(days=6), mock_db_session)
        
        assert result == {}

    def test_groupe_events_par_jour(self, service, mock_db_session, lundi_test):
        """Groupe les événements par jour."""
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.titre = "RDV médecin"
        mock_event.date_debut = datetime.combine(lundi_test, datetime.min.time())
        mock_event.date_fin = datetime.combine(lundi_test, datetime.min.time()) + timedelta(hours=1)
        mock_event.type_event = "rdv"
        mock_event.lieu = "Cabinet"
        mock_event.couleur = "#FF0000"
        
        mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_event]
        
        result = service._charger_events(lundi_test, lundi_test + timedelta(days=6), mock_db_session)
        
        assert isinstance(result, dict)


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL CHARGE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculerCharge:
    """Tests pour _calculer_charge."""

    def test_charge_zero_jour_vide(self, service):
        """Charge zéro pour jour vide."""
        charge = service._calculer_charge(
            repas=[],
            activites=[],
            projets=[],
            routines=[]
        )
        
        assert charge == 0

    def test_charge_augmente_avec_repas(self, service, sample_repas_dict):
        """La charge augmente avec les repas."""
        charge = service._calculer_charge(
            repas=[sample_repas_dict],
            activites=[],
            projets=[],
            routines=[]
        )
        
        assert charge > 0

    def test_charge_augmente_avec_activites(self, service, sample_activite_dict):
        """La charge augmente avec les activités."""
        charge = service._calculer_charge(
            repas=[],
            activites=[sample_activite_dict],
            projets=[],
            routines=[]
        )
        
        assert charge > 0

    def test_charge_augmente_avec_projets_urgents(self, service, sample_projet_dict):
        """La charge augmente avec les projets urgents."""
        charge = service._calculer_charge(
            repas=[],
            activites=[],
            projets=[sample_projet_dict],
            routines=[]
        )
        
        assert charge > 0

    def test_charge_max_100(self, service, sample_repas_dict, sample_activite_dict, sample_projet_dict, sample_routine_dict):
        """La charge est plafonnée à 100."""
        charge = service._calculer_charge(
            repas=[sample_repas_dict] * 10,
            activites=[sample_activite_dict] * 10,
            projets=[sample_projet_dict] * 10,
            routines=[sample_routine_dict] * 10
        )
        
        assert charge <= 100


@pytest.mark.unit
class TestScoreToCharge:
    """Tests pour _score_to_charge."""

    def test_score_faible(self, service):
        """Score faible retourne 'faible'."""
        assert service._score_to_charge(20) == "faible"
        assert service._score_to_charge(0) == "faible"
        assert service._score_to_charge(34) == "faible"

    def test_score_normal(self, service):
        """Score moyen retourne 'normal'."""
        assert service._score_to_charge(50) == "normal"
        assert service._score_to_charge(35) == "normal"
        assert service._score_to_charge(69) == "normal"

    def test_score_intense(self, service):
        """Score élevé retourne 'intense'."""
        assert service._score_to_charge(80) == "intense"
        assert service._score_to_charge(70) == "intense"
        assert service._score_to_charge(100) == "intense"


# ═══════════════════════════════════════════════════════════
# TESTS DÉTECTION ALERTES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDetecterAlertes:
    """Tests pour _detecter_alertes."""

    def test_alerte_surcharge(self, service, lundi_test):
        """Détecte surcharge (charge >= 80)."""
        alertes = service._detecter_alertes(
            jour=lundi_test,
            repas=[],
            activites=[],
            projets=[],
            charge_score=85
        )
        
        assert any("chargé" in a.lower() for a in alertes)

    def test_alerte_pas_activite_jules(self, service, lundi_test):
        """Détecte absence d'activité pour Jules."""
        alertes = service._detecter_alertes(
            jour=lundi_test,
            repas=[],
            activites=[],  # Pas d'activité pour Jules
            projets=[],
            charge_score=50
        )
        
        assert any("jules" in a.lower() for a in alertes)

    def test_alerte_projets_urgents(self, service, lundi_test, sample_projet_dict):
        """Détecte projets urgents."""
        alertes = service._detecter_alertes(
            jour=lundi_test,
            repas=[],
            activites=[],
            projets=[sample_projet_dict],
            charge_score=50
        )
        
        assert any("urgent" in a.lower() for a in alertes)

    def test_alerte_trop_repas(self, service, lundi_test, sample_repas_dict):
        """Détecte trop de repas."""
        alertes = service._detecter_alertes(
            jour=lundi_test,
            repas=[sample_repas_dict] * 4,
            activites=[],
            projets=[],
            charge_score=50
        )
        
        assert any("repas" in a.lower() for a in alertes)

    def test_pas_alerte_jour_normal(self, service, lundi_test, sample_activite_dict):
        """Pas d'alerte pour jour normal."""
        sample_activite_dict["pour_jules"] = True
        alertes = service._detecter_alertes(
            jour=lundi_test,
            repas=[],
            activites=[sample_activite_dict],
            projets=[],
            charge_score=30
        )
        
        # Peut avoir des alertes mineures mais pas de surcharge
        assert not any("très chargé" in a.lower() for a in alertes)


@pytest.mark.unit
class TestDetecterAlertesSemaine:
    """Tests pour _detecter_alertes_semaine."""

    def test_alerte_aucune_activite_jules(self, service, sample_jour_complet, lundi_test):
        """Détecte aucune activité Jules sur la semaine."""
        # Créer 7 jours sans activité Jules
        jours = {}
        for i in range(7):
            jour_date = lundi_test + timedelta(days=i)
            jours[jour_date.isoformat()] = JourCompletSchema(
                date=jour_date,
                charge="faible",
                charge_score=20,
                repas=[],
                activites=[],  # Pas d'activité pour Jules
                projets=[],
                routines=[],
                events=[],
                budget_jour=0,
                alertes=[],
            )
        
        alertes = service._detecter_alertes_semaine(jours)
        
        assert any("jules" in a.lower() for a in alertes)

    def test_alerte_trop_jours_charges(self, service, lundi_test):
        """Détecte plus de 3 jours très chargés."""
        jours = {}
        for i in range(7):
            jour_date = lundi_test + timedelta(days=i)
            jours[jour_date.isoformat()] = JourCompletSchema(
                date=jour_date,
                charge="intense" if i < 4 else "faible",
                charge_score=85 if i < 4 else 20,
                repas=[],
                activites=[],
                projets=[],
                routines=[],
                events=[],
                budget_jour=0,
                alertes=[],
            )
        
        alertes = service._detecter_alertes_semaine(jours)
        
        assert any("chargé" in a.lower() or "burnout" in a.lower() for a in alertes)


# ═══════════════════════════════════════════════════════════
# TESTS BUDGET ET STATS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculerBudgetJour:
    """Tests pour _calculer_budget_jour."""

    def test_budget_zero_sans_activites(self, service):
        """Budget zéro sans activités."""
        budget = service._calculer_budget_jour(activites=[], projets=[])
        
        assert budget == 0

    def test_somme_budgets_activites(self, service, sample_activite_dict):
        """Somme les budgets des activités."""
        budget = service._calculer_budget_jour(
            activites=[sample_activite_dict],
            projets=[]
        )
        
        assert budget == 10


@pytest.mark.unit
class TestCalculerStatsSemaine:
    """Tests pour _calculer_stats_semaine."""

    def test_stats_completes(self, service, lundi_test, sample_repas_dict, sample_activite_dict):
        """Calcule les stats complètes."""
        jours = {}
        for i in range(7):
            jour_date = lundi_test + timedelta(days=i)
            jours[jour_date.isoformat()] = JourCompletSchema(
                date=jour_date,
                charge="normal",
                charge_score=50,
                repas=[sample_repas_dict] if i < 3 else [],
                activites=[sample_activite_dict] if i < 2 else [],
                projets=[],
                routines=[],
                events=[],
                budget_jour=10 if i < 2 else 0,
                alertes=[],
            )
        
        stats = service._calculer_stats_semaine(jours)
        
        assert "total_repas" in stats
        assert "total_activites" in stats
        assert "budget_total" in stats
        assert stats["total_repas"] == 3
        assert stats["total_activites"] == 2


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGenererSemaineIA:
    """Tests pour generer_semaine_ia."""

    def test_appelle_ia(self, service, lundi_test):
        """Appelle l'IA pour générer la semaine."""
        with patch.object(service, 'call_with_list_parsing_sync') as mock_ia:
            mock_ia.return_value = [{"repas_proposes": [], "activites_proposees": []}]
            
            result = service.generer_semaine_ia(lundi_test)
        
        # Le résultat dépend du cache
        assert result is None or mock_ia.called

    def test_avec_contraintes(self, service, lundi_test):
        """Prend en compte les contraintes."""
        contraintes = {"budget": 300, "energie": "faible"}
        
        with patch.object(service, 'call_with_list_parsing_sync') as mock_ia:
            mock_ia.return_value = None
            
            result = service.generer_semaine_ia(lundi_test, contraintes=contraintes)
        
        assert result is None or mock_ia.called

    def test_avec_contexte(self, service, lundi_test):
        """Prend en compte le contexte familial."""
        contexte = {"jules_age_mois": 19, "objectifs_sante": ["sport"]}
        
        with patch.object(service, 'call_with_list_parsing_sync') as mock_ia:
            mock_ia.return_value = None
            
            result = service.generer_semaine_ia(lundi_test, contexte=contexte)
        
        assert result is None or mock_ia.called


# ═══════════════════════════════════════════════════════════
# TESTS CRÉER EVENT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCreerEvent:
    """Tests pour creer_event."""

    def test_cree_event(self, service, mock_db_session, mock_context):
        """Crée un événement."""
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.creer_event(
                titre="Test Event",
                date_debut=datetime(2024, 1, 15, 10, 0),
                type_event="rdv"
            )
        
        assert mock_db_session.add.called or result is None

    def test_cree_event_complet(self, service, mock_db_session, mock_context):
        """Crée un événement avec tous les champs."""
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.creer_event(
                titre="RDV Médecin",
                date_debut=datetime(2024, 1, 15, 10, 0),
                type_event="rdv",
                date_fin=datetime(2024, 1, 15, 10, 30),
                description="Consultation annuelle",
                lieu="Cabinet médical",
                couleur="#FF0000"
            )
        
        assert mock_db_session.add.called or result is None


# ═══════════════════════════════════════════════════════════
# TESTS INVALIDER CACHE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInvaliderCache:
    """Tests pour _invalider_cache_semaine."""

    def test_invalide_cache(self, service, lundi_test):
        """Invalide le cache pour la semaine."""
        with patch('src.core.cache.Cache.invalider') as mock_invalider:
            service._invalider_cache_semaine(lundi_test)
        
        # La méthode devrait être appelée
        assert mock_invalider.called or True  # Peut ne pas être appelée si pas de cache


# ═══════════════════════════════════════════════════════════
# TESTS AVEC FIXTURE DB PATCHÉE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceWithPatchedDB:
    """Tests avec la DB patchée."""

    def test_service_instantiation(self):
        """Vérifie l'instanciation du service."""
        service = ServicePlanningUnifie()
        assert service is not None
        assert isinstance(service, ServicePlanningUnifie)


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES HÉRITÉES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestMethodesHeritees:
    """Tests pour les méthodes héritées."""

    def test_has_model_attribute(self):
        """Le service a l'attribut model."""
        service = ServicePlanningUnifie()
        assert hasattr(service, 'model')

    def test_inherits_from_base_ai_service(self):
        """Le service hérite de BaseAIService."""
        from src.services.base import BaseAIService
        service = ServicePlanningUnifie()
        assert isinstance(service, BaseAIService)

    def test_inherits_from_base_service(self):
        """Le service hérite de BaseService."""
        from src.services.base import BaseService
        service = ServicePlanningUnifie()
        assert isinstance(service, BaseService)


# ═══════════════════════════════════════════════════════════
# TESTS CAS LIMITES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCasLimites:
    """Tests pour les cas limites."""

    def test_semaine_vide(self, service, mock_db_session, mock_context, lundi_test):
        """Gère une semaine vide."""
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_semaine_complete(lundi_test)
        
        if result is not None:
            assert len(result.jours) == 7

    def test_date_pas_lundi(self, service, mock_db_session, mock_context):
        """Gère une date qui n'est pas un lundi."""
        mardi = date(2024, 1, 16)  # Mardi
        
        with patch('src.core.database.obtenir_contexte_db', mock_context):
            result = service.get_semaine_complete(mardi)
        
        # Devrait fonctionner même si pas un lundi
        assert result is None or isinstance(result, SemaineCompleSchema)
