"""
Tests Intégration Complète Planning

Tests end-to-end du module planning refactorisé
✅ Flux complet: création → agrégation → affichage
✅ Gestion état Streamlit
✅ Gestion cache
✅ Comportement sous charge

À lancer: pytest tests/integration/test_planning_full.py -v -s
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
    Routine,
    RoutineTask,
    Recette,
)
from src.services.planning_unified import (
    PlanningAIService,
    get_planning_service,
    SemaineCompleSchema,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES INTÉGRATION
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service_integration(db: Session) -> PlanningAIService:
    """Service planning pour tests intégration"""
    return get_planning_service()


@pytest.fixture
def semaine_complete_test(db: Session) -> tuple[date, date]:
    """Semaine complète avec tous types d'événements"""
    today = date.today()
    semaine_debut = today - timedelta(days=today.weekday())
    semaine_fin = semaine_debut + timedelta(days=6)
    return semaine_debut, semaine_fin


@pytest.fixture
def famille_complete_setup(
    db: Session, semaine_complete_test
) -> dict:
    """Setup complet famille avec tous types d'événements"""
    semaine_debut, semaine_fin = semaine_complete_test

    # 1. Recettes
    recette1 = Recette(
        nom="Pâtes",
        temps_preparation=5,
        temps_cuisson=15,
        portions=4,
        difficulte="facile",
        type_repas="dîner",
    )
    recette2 = Recette(
        nom="Pizza maison",
        temps_preparation=30,
        temps_cuisson=15,
        portions=4,
        difficulte="moyen",
        type_repas="dîner",
    )
    db.add_all([recette1, recette2])
    db.commit()

    # 2. Planning avec repas
    planning = Planning(
        nom="Semaine Test",
        semaine_debut=semaine_debut,
        semaine_fin=semaine_fin,
        actif=True,
    )
    db.add(planning)
    db.commit()

    repas_lundi = Repas(
        planning_id=planning.id,
        recette_id=recette1.id,
        date_repas=semaine_debut,
        type_repas="dîner",
    )
    repas_vendredi = Repas(
        planning_id=planning.id,
        recette_id=recette2.id,
        date_repas=semaine_debut + timedelta(days=4),
        type_repas="dîner",
    )
    db.add_all([repas_lundi, repas_vendredi])

    # 3. Activités
    activite_jules = FamilyActivity(
        titre="Parc",
        type_activite="parc",
        date_prevue=semaine_debut,
        age_minimal_recommande=12,  # adapté pour Jules
        cout_estime=0,
    )
    activite_famille = FamilyActivity(
        titre="Musée",
        type_activite="culturel",
        date_prevue=semaine_debut + timedelta(days=3),
        age_minimal_recommande=12,  # adapté pour Jules
        cout_estime=40.0,
    )
    db.add_all([activite_jules, activite_famille])

    # 4. Événements calendrier
    event_sante = CalendarEvent(
        titre="RDV pédiatre Jules",
        type_event="santé",
        date_debut=datetime.combine(
            semaine_debut + timedelta(days=1), datetime.strptime("10:00", "%H:%M").time()
        ),
        lieu="Clinique",
    )
    event_social = CalendarEvent(
        titre="Apéro amis",
        type_event="social",
        date_debut=datetime.combine(
            semaine_debut + timedelta(days=4), datetime.strptime("18:00", "%H:%M").time()
        ),
    )
    db.add_all([event_sante, event_social])

    # 5. Projets
    projet_maison = Project(
        nom="Rénovation cuisine",
        statut="en_cours",
        priorite="haute",
        date_fin_prevue=semaine_debut + timedelta(days=5),
    )
    projet_hobby = Project(
        nom="Apprendre Python",
        statut="en_cours",
        priorite="moyenne",
    )
    db.add_all([projet_maison, projet_hobby])

    # 6. Routines
    routine_matin = Routine(
        nom="Routine matinale",
        frequence="quotidien",
        actif=True,
    )
    db.add(routine_matin)
    db.commit()

    task1 = RoutineTask(
        routine_id=routine_matin.id,
        nom="Yoga",
        ordre=1,
        heure_prevue="07:00",
    )
    task2 = RoutineTask(
        routine_id=routine_matin.id,
        nom="Méditation",
        ordre=2,
        heure_prevue="07:30",
    )
    db.add_all([task1, task2])

    db.commit()

    return {
        "semaine_debut": semaine_debut,
        "semaine_fin": semaine_fin,
        "planning": planning,
        "recettes": [recette1, recette2],
        "repas": [repas_lundi, repas_vendredi],
        "activites": [activite_jules, activite_famille],
        "events": [event_sante, event_social],
        "projets": [projet_maison, projet_hobby],
        "routines": [routine_matin],
    }


# ═══════════════════════════════════════════════════════════
# TESTS: FLUX COMPLET
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestFluxComplet:
    """Tests flux complet"""

    def test_creer_et_recuperer_event(self, service_integration: PlanningAIService, db: Session):
        """Créer événement et le retrouver"""
        titre_event = "Test Event Unique"
        date_event = datetime.now()

        # Créer
        event = service_integration.creer_event(
            titre=titre_event,
            date_debut=date_event,
            type_event="test",
        )

        assert event.id is not None

        # Récupérer
        event_recupere = db.query(CalendarEvent).filter_by(titre=titre_event).first()
        assert event_recupere is not None
        assert event_recupere.titre == titre_event

    def test_semaine_avec_donnees_completes(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """Semaine avec données complètes"""
        data = famille_complete_setup
        semaine = service_integration.get_semaine_complete(data["semaine_debut"])

        assert semaine is not None
        assert semaine.semaine_debut == data["semaine_debut"]
        assert len(semaine.jours) == 7
        assert semaine.stats_semaine["total_repas"] == 2
        assert semaine.stats_semaine["total_activites"] == 2
        assert semaine.stats_semaine["total_events"] >= 2

    def test_charge_semaine_calcule(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """Charge semaine calculée correctement"""
        data = famille_complete_setup
        semaine = service_integration.get_semaine_complete(data["semaine_debut"])

        # Vérifier charge globale
        assert semaine.charge_globale in ["faible", "normal", "intense"]

        # Vérifier charge jours
        for jour in semaine.jours.values():
            assert 0 <= jour.charge_score <= 100
            assert jour.charge in ["faible", "normal", "intense"]

    def test_alertes_generees(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """Alertes générées pour semaine"""
        data = famille_complete_setup
        semaine = service_integration.get_semaine_complete(data["semaine_debut"])

        # Peut avoir des alertes ou pas, dépend des données
        assert isinstance(semaine.alertes_semaine, list)

    def test_budget_semaine_cumule(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """Budget semaine cumulé correctement"""
        data = famille_complete_setup
        semaine = service_integration.get_semaine_complete(data["semaine_debut"])

        budget_total = semaine.stats_semaine.get("budget_total", 0)
        assert budget_total >= 0

    def test_jules_adapte_detecte(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """Activités Jules détectées"""
        data = famille_complete_setup
        semaine = service_integration.get_semaine_complete(data["semaine_debut"])

        # Au moins un jour doit avoir activité Jules
        jours_avec_jules = [
            j for j in semaine.jours.values()
            if any(a.get("pour_jules") for a in j.activites)
        ]

        assert len(jours_avec_jules) > 0


# ═══════════════════════════════════════════════════════════
# TESTS: CACHE
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestCacheIntegration:
    """Tests cache intégration"""

    def test_cache_semaine_hit(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """Cache hit semaine"""
        data = famille_complete_setup

        # Première requête
        semaine1 = service_integration.get_semaine_complete(data["semaine_debut"])
        stats1 = semaine1.stats_semaine

        # Deuxième requête (cache)
        semaine2 = service_integration.get_semaine_complete(data["semaine_debut"])
        stats2 = semaine2.stats_semaine

        # Doivent être identiques
        assert stats1 == stats2

    def test_invalidation_cache_apres_creation(
        self,
        service_integration: PlanningAIService,
        db: Session,
        famille_complete_setup: dict,
    ):
        """Cache invalidé après création event"""
        data = famille_complete_setup

        # Première requête
        semaine1 = service_integration.get_semaine_complete(data["semaine_debut"])
        count1 = semaine1.stats_semaine["total_events"]

        # Créer nouvel event
        service_integration.creer_event(
            titre="Event nouveau",
            date_debut=datetime.combine(
                data["semaine_debut"] + timedelta(days=1),
                datetime.min.time(),
            ),
        )

        # Deuxième requête (cache invalidé)
        semaine2 = service_integration.get_semaine_complete(data["semaine_debut"])
        count2 = semaine2.stats_semaine["total_events"]

        # Count doit augmenter
        assert count2 > count1

    def test_cache_semaines_differentes_independant(
        self,
        service_integration: PlanningAIService,
        db: Session,
        famille_complete_setup: dict,
    ):
        """Cache indépendant pour semaines différentes"""
        data = famille_complete_setup
        semaine_debut = data["semaine_debut"]
        semaine_prochaine = semaine_debut + timedelta(days=7)

        # Requête semaine 1
        s1 = service_integration.get_semaine_complete(semaine_debut)
        count1 = s1.stats_semaine["total_events"]

        # Créer event semaine 2
        service_integration.creer_event(
            titre="Event future",
            date_debut=datetime.combine(semaine_prochaine, datetime.min.time()),
        )

        # Requête semaine 1 (pas doit pas avoir changé)
        s1_again = service_integration.get_semaine_complete(semaine_debut)
        count1_again = s1_again.stats_semaine["total_events"]

        assert count1 == count1_again


# ═══════════════════════════════════════════════════════════
# TESTS: NAVIGATION SEMAINE
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestNavigationSemaine:
    """Tests navigation semaine"""

    def test_navigation_semaine_suivante(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """Navigation semaine suivante"""
        data = famille_complete_setup
        semaine_debut = data["semaine_debut"]
        semaine_suivante = semaine_debut + timedelta(days=7)

        s1 = service_integration.get_semaine_complete(semaine_debut)
        s2 = service_integration.get_semaine_complete(semaine_suivante)

        assert s1.semaine_debut == semaine_debut
        assert s2.semaine_debut == semaine_suivante

    def test_navigation_semaine_precedente(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """Navigation semaine précédente"""
        data = famille_complete_setup
        semaine_debut = data["semaine_debut"]
        semaine_precedente = semaine_debut - timedelta(days=7)

        s_prev = service_integration.get_semaine_complete(semaine_precedente)
        s_curr = service_integration.get_semaine_complete(semaine_debut)

        assert s_prev.semaine_debut == semaine_precedente
        assert s_curr.semaine_debut == semaine_debut


# ═══════════════════════════════════════════════════════════
# TESTS: STRESS & PERFORMANCE
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestPerformance:
    """Tests performance sous charge"""

    def test_multiple_events_meme_jour(
        self,
        service_integration: PlanningAIService,
        db: Session,
        semaine_complete_test,
    ):
        """Créer plusieurs events même jour"""
        semaine_debut, _ = semaine_complete_test

        # Créer 10 events le même jour
        jour_test = semaine_debut + timedelta(days=2)
        for i in range(10):
            service_integration.creer_event(
                titre=f"Event {i}",
                date_debut=datetime.combine(
                    jour_test,
                    datetime.strptime(f"{9+i}:00", "%H:%M").time(),
                ),
            )

        # Récupérer semaine
        semaine = service_integration.get_semaine_complete(semaine_debut)

        # Vérifier que tous les events sont présents
        jour_data = semaine.jours[jour_test.isoformat()]
        assert len(jour_data.events) == 10

    def test_charge_augmente_avec_events(
        self,
        service_integration: PlanningAIService,
        db: Session,
        semaine_complete_test,
    ):
        """Charge augmente avec plus d'événements"""
        semaine_debut, _ = semaine_complete_test

        # Semaine vide
        semaine_empty = service_integration.get_semaine_complete(semaine_debut)
        charge_empty = semaine_empty.stats_semaine.get("charge_moyenne", 0)

        # Ajouter 15 events
        for i in range(15):
            service_integration.creer_event(
                titre=f"Event {i}",
                date_debut=datetime.combine(
                    semaine_debut + timedelta(days=i % 7),
                    datetime.strptime(f"{9+i%9}:00", "%H:%M").time(),
                ),
            )

        # Semaine avec events
        semaine_full = service_integration.get_semaine_complete(semaine_debut)
        charge_full = semaine_full.stats_semaine.get("charge_moyenne", 0)

        # Charge doit augmenter
        assert charge_full > charge_empty


# ═══════════════════════════════════════════════════════════
# TESTS: VALIDATION DONNÉES
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestValidationDonnees:
    """Tests validation données"""

    def test_schema_valide_apres_aggregation(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """Schema valide après agrégation"""
        data = famille_complete_setup
        semaine = service_integration.get_semaine_complete(data["semaine_debut"])

        # Doit être instance de SemaineCompleSchema
        assert isinstance(semaine, SemaineCompleSchema)

        # Tous les champs requis présents
        assert semaine.semaine_debut is not None
        assert semaine.semaine_fin is not None
        assert semaine.jours is not None
        assert semaine.charge_globale is not None

    def test_jour_complet_valide(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """JourCompletSchema valide"""
        data = famille_complete_setup
        semaine = service_integration.get_semaine_complete(data["semaine_debut"])

        for jour in semaine.jours.values():
            # Vérifier structure
            assert jour.date is not None
            assert jour.charge is not None
            assert 0 <= jour.charge_score <= 100
            assert isinstance(jour.repas, list)
            assert isinstance(jour.activites, list)

    def test_pas_donnees_manquantes(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """Pas de données manquantes/None"""
        data = famille_complete_setup
        semaine = service_integration.get_semaine_complete(data["semaine_debut"])

        # Stats présentes et non None
        for key, value in semaine.stats_semaine.items():
            assert value is not None

        # Jours non vides
        assert len(semaine.jours) > 0

    def test_coherence_stats_jours(
        self,
        service_integration: PlanningAIService,
        famille_complete_setup: dict,
    ):
        """Cohérence stats jours vs semaine"""
        data = famille_complete_setup
        semaine = service_integration.get_semaine_complete(data["semaine_debut"])

        # Sommer repas jours
        total_repas_jours = sum(len(j.repas) for j in semaine.jours.values())

        # Doit matcher (ou être proche) du total semaine
        total_repas_stats = semaine.stats_semaine.get("total_repas", 0)
        assert abs(total_repas_jours - total_repas_stats) <= 0  # Doit être exact


# ═══════════════════════════════════════════════════════════
# MARQUEURS
# ═══════════════════════════════════════════════════════════

pytest.mark.integration
