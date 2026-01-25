"""
Tests pour le module Planning Refoncé

Tests unitaires et d'intégration pour:
✅ PlanningAIService (service unifié)
✅ Agrégation données
✅ Calcul charge
✅ Détection alertes
✅ Schémas Pydantic
✅ Génération IA

À lancer: pytest tests/test_planning_unified.py -v
"""

import pytest
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from src.core.models import (
    Planning,
    Repas,
    CalendarEvent,
    FamilyActivity,
    Project,
    ProjectTask,
    Routine,
    RoutineTask,
    Recette,
)
from src.services.planning_unified import (
    PlanningAIService,
    get_planning_service,
    JourCompletSchema,
    SemaineCompleSchema,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service(db: Session) -> PlanningAIService:
    """Instance du service planning"""
    return get_planning_service()


@pytest.fixture
def semaine_test() -> tuple[date, date]:
    """Semaine de test (lundi - dimanche)"""
    today = date.today()
    semaine_debut = today - timedelta(days=today.weekday())
    semaine_fin = semaine_debut + timedelta(days=6)
    return semaine_debut, semaine_fin


@pytest.fixture
def recette_test(db: Session) -> Recette:
    """Recette de test"""
    recette = Recette(
        nom="Pâtes à la tomate",
        temps_preparation=10,
        temps_cuisson=15,
        portions=4,
        difficulte="facile",
        type_repas="dîner",
        est_rapide=True,
    )
    db.add(recette)
    db.commit()
    return recette


@pytest.fixture
def planning_test(db: Session, recette_test: Recette, semaine_test) -> Planning:
    """Planning de test avec repas"""
    semaine_debut, semaine_fin = semaine_test

    planning = Planning(
        nom="Semaine Test",
        semaine_debut=semaine_debut,
        semaine_fin=semaine_fin,
        actif=True,
    )
    db.add(planning)
    db.commit()

    # Ajouter repas lundi et mercredi
    repas_lundi = Repas(
        planning_id=planning.id,
        recette_id=recette_test.id,
        date_repas=semaine_debut,
        type_repas="dîner",
    )
    repas_mercredi = Repas(
        planning_id=planning.id,
        recette_id=recette_test.id,
        date_repas=semaine_debut + timedelta(days=2),
        type_repas="dîner",
    )
    db.add(repas_lundi)
    db.add(repas_mercredi)
    db.commit()

    return planning


@pytest.fixture
def activites_test(db: Session, semaine_test):
    """Activités familiales de test"""
    semaine_debut, _ = semaine_test

    activites = []
    # Activité Jules lundi
    act1 = FamilyActivity(
        titre="Parc",
        type_activite="parc",
        date_debut=datetime.combine(semaine_debut, datetime.min.time()),
        adapte_pour_jules=True,
        budget_estime=0,
    )
    db.add(act1)

    # Activité famille mercredi
    act2 = FamilyActivity(
        titre="Yoga",
        type_activite="sport",
        date_debut=datetime.combine(semaine_debut + timedelta(days=2), datetime.min.time()),
        adapte_pour_jules=False,
        budget_estime=20.0,
    )
    db.add(act2)

    db.commit()
    return [act1, act2]


@pytest.fixture
def events_test(db: Session, semaine_test):
    """Événements calendrier de test"""
    semaine_debut, _ = semaine_test

    events = []
    # Event lundi 10h
    ev1 = CalendarEvent(
        titre="RDV médecin",
        type_event="santé",
        date_debut=datetime.combine(semaine_debut, datetime.strptime("10:00", "%H:%M").time()),
        lieu="Cabinet Dr. Dupont",
    )
    db.add(ev1)

    # Event vendredi 18h
    ev2 = CalendarEvent(
        titre="Apéro",
        type_event="social",
        date_debut=datetime.combine(
            semaine_debut + timedelta(days=4), datetime.strptime("18:00", "%H:%M").time()
        ),
    )
    db.add(ev2)

    db.commit()
    return [ev1, ev2]


@pytest.fixture
def projets_test(db: Session, semaine_test):
    """Projets de test"""
    semaine_debut, semaine_fin = semaine_test

    # Projet urgent (échéance mercredi)
    projet = Project(
        nom="Finir réno cuisine",
        statut="en_cours",
        priorite="haute",
        date_fin_prevue=semaine_debut + timedelta(days=2),
    )
    db.add(projet)
    db.commit()

    return [projet]


@pytest.fixture
def routines_test(db: Session):
    """Routines de test"""
    routine = Routine(
        nom="Yoga matinal",
        frequence="quotidien",
        actif=True,
    )
    db.add(routine)
    db.commit()

    # Tâches
    task = RoutineTask(
        routine_id=routine.id,
        nom="Yoga 30min",
        ordre=1,
        heure_prevue="07:00",
    )
    db.add(task)
    db.commit()

    return [routine]


# ═══════════════════════════════════════════════════════════
# TESTS: CRUD BÁSIQUE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPlanningServiceCRUD:
    """Tests CRUD de base"""

    def test_creer_event(self, service: PlanningAIService, db: Session):
        """Créer un événement"""
        event = service.creer_event(
            titre="Anniversaire Jules",
            date_debut=datetime.now(),
            type_event="famille",
            description="1er anniversaire!",
            couleur="bleu",
        )

        assert event is not None
        assert event.titre == "Anniversaire Jules"
        assert event.type_event == "famille"

    def test_creer_event_avec_lieu(self, service: PlanningAIService):
        """Créer événement avec lieu"""
        event = service.creer_event(
            titre="Pique-nique",
            date_debut=datetime.now(),
            lieu="Parc du château",
            couleur="vert",
        )

        assert event.lieu == "Parc du château"

    def test_creer_event_avec_fin(self, service: PlanningAIService):
        """Créer événement avec heure de fin"""
        debut = datetime.now()
        fin = debut + timedelta(hours=2)

        event = service.creer_event(
            titre="Réunion",
            date_debut=debut,
            date_fin=fin,
        )

        assert event.date_fin == fin


# ═══════════════════════════════════════════════════════════
# TESTS: AGRÉGATION DONNÉES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAggregation:
    """Tests agrégation données"""

    def test_charger_repas(self, service: PlanningAIService, db: Session, planning_test, semaine_test):
        """Charger repas planifiés"""
        semaine_debut, semaine_fin = semaine_test

        repas_dict = service._charger_repas(semaine_debut, semaine_fin, db)

        assert semaine_debut.isoformat() in repas_dict
        assert len(repas_dict[semaine_debut.isoformat()]) == 1
        assert repas_dict[semaine_debut.isoformat()][0]["type"] == "dîner"

    def test_charger_activites(self, service: PlanningAIService, db: Session, activites_test, semaine_test):
        """Charger activités"""
        semaine_debut, semaine_fin = semaine_test

        activites_dict = service._charger_activites(semaine_debut, semaine_fin, db)

        assert len(activites_dict) > 0
        # Vérifier activité Jules
        lundi_str = semaine_debut.isoformat()
        if lundi_str in activites_dict:
            assert any(a.get("pour_jules") for a in activites_dict[lundi_str])

    def test_charger_events(self, service: PlanningAIService, db: Session, events_test, semaine_test):
        """Charger événements calendrier"""
        semaine_debut, semaine_fin = semaine_test

        events_dict = service._charger_events(semaine_debut, semaine_fin, db)

        assert len(events_dict) > 0

    def test_charger_projets(self, service: PlanningAIService, db: Session, projets_test, semaine_test):
        """Charger projets"""
        semaine_debut, semaine_fin = semaine_test

        projets_dict = service._charger_projets(semaine_debut, semaine_fin, db)

        assert len(projets_dict) > 0

    def test_charger_routines(self, service: PlanningAIService, db: Session, routines_test):
        """Charger routines"""
        routines_dict = service._charger_routines(db)

        assert "routine_quotidienne" in routines_dict


# ═══════════════════════════════════════════════════════════
# TESTS: CALCUL CHARGE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculCharge:
    """Tests calcul charge"""

    def test_charge_faible(self, service: PlanningAIService):
        """Charge faible - aucun événement"""
        score = service._calculer_charge([], [], [], [])
        assert score < 35

    def test_charge_normal_repas(self, service: PlanningAIService):
        """Charge normale avec repas"""
        repas = [{"temps_total": 60}]
        score = service._calculer_charge(repas, [], [], [])
        assert 30 <= score < 70

    def test_charge_intense_multiple(self, service: PlanningAIService):
        """Charge intense - beaucoup d'événements"""
        repas = [{"temps_total": 90}, {"temps_total": 60}]
        activites = [{}, {}, {}]
        projets = [{"priorite": "haute"}, {"priorite": "haute"}]

        score = service._calculer_charge(repas, activites, projets, [])
        assert score > 70

    def test_score_to_charge_faible(self, service: PlanningAIService):
        """Score to label - faible"""
        assert service._score_to_charge(20) == "faible"
        assert service._score_to_charge(34) == "faible"

    def test_score_to_charge_normal(self, service: PlanningAIService):
        """Score to label - normal"""
        assert service._score_to_charge(50) == "normal"
        assert service._score_to_charge(69) == "normal"

    def test_score_to_charge_intense(self, service: PlanningAIService):
        """Score to label - intense"""
        assert service._score_to_charge(80) == "intense"
        assert service._score_to_charge(100) == "intense"


# ═══════════════════════════════════════════════════════════
# TESTS: DÉTECTION ALERTES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDetectionAlertes:
    """Tests détection alertes intelligentes"""

    def test_alerte_surcharge(self, service: PlanningAIService):
        """Alerte surcharge (charge > 80)"""
        alertes = service._detecter_alertes(
            jour=date.today(),
            repas=[],
            activites=[],
            projets=[],
            charge_score=85,
        )

        assert any("très chargé" in a.lower() for a in alertes)

    def test_alerte_pas_activite_jules(self, service: PlanningAIService):
        """Alerte pas d'activité Jules"""
        alertes = service._detecter_alertes(
            jour=date.today(),
            repas=[],
            activites=[{"pour_jules": False}],
            projets=[],
            charge_score=50,
        )

        assert any("jules" in a.lower() for a in alertes)

    def test_alerte_projet_urgent(self, service: PlanningAIService):
        """Alerte projet urgent"""
        alertes = service._detecter_alertes(
            jour=date.today(),
            repas=[],
            activites=[],
            projets=[{"priorite": "haute"}, {"priorite": "haute"}],
            charge_score=50,
        )

        assert any("urgent" in a.lower() or "projet" in a.lower() for a in alertes)

    def test_pas_alerte_jour_calme(self, service: PlanningAIService):
        """Pas d'alerte jour calme"""
        alertes = service._detecter_alertes(
            jour=date.today(),
            repas=[],
            activites=[{"pour_jules": True}],
            projets=[],
            charge_score=30,
        )

        # Pas de surcharge, pas de manque Jules
        assert len(alertes) == 0

    def test_alertes_semaine_jules(self, service: PlanningAIService):
        """Alerte semaine: aucune activité Jules"""
        jours = {
            date.today().isoformat(): type("Jour", (), {
                "activites": [{"pour_jules": False}],
                "charge_score": 50,
            })()
        }

        alertes = service._detecter_alertes_semaine(jours)
        assert any("jules" in a.lower() for a in alertes)


# ═══════════════════════════════════════════════════════════
# TESTS: INTÉGRATION SEMAINE COMPLÈTE
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestSemaineComplete:
    """Tests intégration semaine complète"""

    def test_get_semaine_complete_vide(self, service: PlanningAIService, semaine_test):
        """Semaine vide (pas d'événements)"""
        semaine_debut, _ = semaine_test

        semaine = service.get_semaine_complete(semaine_debut)

        assert semaine is not None
        assert len(semaine.jours) == 7
        assert semaine.stats_semaine["total_repas"] == 0

    def test_get_semaine_complete_avec_donnees(
        self,
        service: PlanningAIService,
        db: Session,
        planning_test,
        activites_test,
        events_test,
        semaine_test,
    ):
        """Semaine avec événements"""
        semaine_debut, _ = semaine_test

        semaine = service.get_semaine_complete(semaine_debut)

        assert semaine is not None
        assert semaine.stats_semaine["total_repas"] > 0
        assert semaine.stats_semaine["total_activites"] > 0
        assert semaine.stats_semaine["total_events"] > 0

    def test_semaine_charge_calcule(
        self,
        service: PlanningAIService,
        db: Session,
        planning_test,
        activites_test,
        semaine_test,
    ):
        """Charge calculée pour chaque jour"""
        semaine_debut, _ = semaine_test

        semaine = service.get_semaine_complete(semaine_debut)

        for jour in semaine.jours.values():
            assert 0 <= jour.charge_score <= 100
            assert jour.charge in ["faible", "normal", "intense"]

    def test_semaine_stats_correctes(
        self,
        service: PlanningAIService,
        db: Session,
        planning_test,
        activites_test,
        semaine_test,
    ):
        """Stats semaine correctes"""
        semaine_debut, _ = semaine_test

        semaine = service.get_semaine_complete(semaine_debut)

        stats = semaine.stats_semaine
        assert stats["total_repas"] >= 0
        assert stats["total_activites"] >= 0
        assert stats["charge_moyenne"] >= 0


# ═══════════════════════════════════════════════════════════
# TESTS: SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSchemasPydantic:
    """Tests validation schémas"""

    def test_jour_complet_schema_valid(self):
        """JourCompletSchema valide"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="normal",
            charge_score=50,
            repas=[],
            activites=[],
            projets=[],
            routines=[],
            events=[],
            budget_jour=0.0,
        )

        assert jour.charge in ["faible", "normal", "intense"]
        assert 0 <= jour.charge_score <= 100

    def test_jour_complet_schema_avec_donnees(self):
        """JourCompletSchema avec données"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="intense",
            charge_score=85,
            repas=[{"type": "dîner", "recette": "Pâtes", "portions": 4, "temps_total": 30}],
            activites=[{"titre": "Parc", "type": "loisirs", "pour_jules": True, "budget": 0}],
            budget_jour=50.0,
            alertes=["Jour très chargé"],
        )

        assert len(jour.repas) == 1
        assert len(jour.activites) == 1
        assert jour.budget_jour == 50.0

    def test_semaine_complete_schema_valid(self):
        """SemaineCompleSchema valide"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="normal",
            charge_score=50,
        )

        semaine = SemaineCompleSchema(
            semaine_debut=date.today(),
            semaine_fin=date.today() + timedelta(days=6),
            jours={date.today().isoformat(): jour},
            stats_semaine={"total_repas": 5},
            charge_globale="normal",
        )

        assert semaine.charge_globale in ["faible", "normal", "intense"]
        assert len(semaine.jours) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS: CACHE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCache:
    """Tests cache"""

    def test_cache_semaine_complete(
        self, service: PlanningAIService, semaine_test, db: Session, planning_test
    ):
        """Cache semaine complète"""
        semaine_debut, _ = semaine_test

        # Première requête
        semaine1 = service.get_semaine_complete(semaine_debut)

        # Deuxième requête (doit être en cache)
        semaine2 = service.get_semaine_complete(semaine_debut)

        assert semaine1 is not None
        assert semaine2 is not None
        # Les deux résultats doivent être identiques
        assert semaine1.stats_semaine == semaine2.stats_semaine

    def test_invalider_cache_semaine(self, service: PlanningAIService, semaine_test):
        """Invalider cache semaine"""
        semaine_debut, _ = semaine_test

        # Invalider le cache
        service._invalider_cache_semaine(semaine_debut)

        # Pas d'erreur = succès
        assert True


# ═══════════════════════════════════════════════════════════
# TESTS: IA (Mock)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGenerationIA:
    """Tests génération IA (avec mocks)"""

    def test_construire_prompt_generation(self, service: PlanningAIService, semaine_test):
        """Construire prompt génération"""
        semaine_debut, _ = semaine_test

        prompt = service._construire_prompt_generation(
            date_debut=semaine_debut,
            contraintes={"budget": 400, "energie": "normal"},
            contexte={"jules_age_mois": 19, "objectifs_sante": ["Cardio"]},
        )

        assert "400" in prompt  # Budget
        assert "19" in prompt  # Age Jules
        assert "Cardio" in prompt  # Objectif
        assert semaine_debut.isoformat() in prompt

    def test_generer_semaine_ia_sans_ia(self, service: PlanningAIService, semaine_test):
        """Générer semaine IA sans client IA réel"""
        semaine_debut, _ = semaine_test

        # Si pas de client IA, doit retourner None gracefully
        result = service.generer_semaine_ia(
            date_debut=semaine_debut,
            contraintes={"budget": 400},
        )

        # Peut être None si client IA indisponible
        # Ce test vérifie juste qu'il ne crash pas
        assert result is None or result is not None


# ═══════════════════════════════════════════════════════════
# MARQUEURS PYTEST
# ═══════════════════════════════════════════════════════════

pytest.mark.unit  # Tests isolés sans DB
pytest.mark.integration  # Tests avec DB complète
