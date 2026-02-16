"""
Tests pour le service TempsEntretienService.

Tests:
- Gestion des sessions (start/stop/cancel)
- Calcul des statistiques
- Analyse IA (suggestions, recommandations)
"""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.maison.schemas import (
    AnalyseTempsRequest,
    RecommandationMateriel,
    ResumeTempsHebdo,
    SessionTravail,
    StatistiqueTempsActivite,
    SuggestionOptimisation,
    TypeActiviteEntretien,
)
from src.services.maison.temps_entretien_service import (
    CATEGORIES_ACTIVITES,
    ICONES_ACTIVITES,
    TempsEntretienService,
    get_temps_entretien_service,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    """Service temps entretien pour tests."""
    return TempsEntretienService()


@pytest.fixture
def service_avec_historique(service):
    """Service avec historique de sessions."""
    # Simuler quelques sessions passées
    now = datetime.now()

    # Session tonte d'hier
    session1 = SessionTravail(
        id=100,
        type_activite=TypeActiviteEntretien.TONTE,
        zone_id=1,
        debut=now - timedelta(days=1, hours=2),
        fin=now - timedelta(days=1, hours=1),
        duree_minutes=60,
        satisfaction=4,
        date_creation=now - timedelta(days=1),
    )
    service._historique.append(session1)

    # Session ménage d'aujourd'hui
    session2 = SessionTravail(
        id=101,
        type_activite=TypeActiviteEntretien.ASPIRATEUR,
        piece_id=5,
        debut=now - timedelta(hours=3),
        fin=now - timedelta(hours=2, minutes=30),
        duree_minutes=30,
        satisfaction=5,
        date_creation=now - timedelta(hours=3),
    )
    service._historique.append(session2)

    # Session arrosage il y a 3 jours
    session3 = SessionTravail(
        id=102,
        type_activite=TypeActiviteEntretien.ARROSAGE,
        zone_id=2,
        debut=now - timedelta(days=3, hours=1),
        fin=now - timedelta(days=3),
        duree_minutes=15,
        date_creation=now - timedelta(days=3),
    )
    service._historique.append(session3)

    service._prochain_id = 200
    return service


# ═══════════════════════════════════════════════════════════
# TESTS SESSIONS
# ═══════════════════════════════════════════════════════════


class TestGestionSessions:
    """Tests pour la gestion des sessions de travail."""

    def test_demarrer_session(self, service):
        """Test démarrage d'une session."""
        session = service.demarrer_session(
            type_activite=TypeActiviteEntretien.TONTE,
            zone_id=1,
            description="Tonte pelouse avant",
        )

        assert session.id == 1
        assert session.type_activite == TypeActiviteEntretien.TONTE
        assert session.zone_id == 1
        assert session.fin is None
        assert session.duree_minutes is None
        assert session.description == "Tonte pelouse avant"

    def test_demarrer_plusieurs_sessions(self, service):
        """Test démarrage de plusieurs sessions."""
        s1 = service.demarrer_session(TypeActiviteEntretien.TONTE)
        s2 = service.demarrer_session(TypeActiviteEntretien.ARROSAGE)

        assert s1.id == 1
        assert s2.id == 2
        assert len(service._sessions_actives) == 2

    def test_arreter_session(self, service):
        """Test arrêt d'une session."""
        session = service.demarrer_session(TypeActiviteEntretien.ASPIRATEUR)
        session_id = session.id

        # Attendre un peu pour avoir une durée
        import time

        time.sleep(0.1)

        result = service.arreter_session(
            session_id,
            notes="Fait rapidement",
            satisfaction=5,
        )

        assert result.fin is not None
        assert result.duree_minutes is not None
        assert result.notes == "Fait rapidement"
        assert result.satisfaction == 5
        assert session_id not in service._sessions_actives
        assert len(service._historique) == 1

    def test_arreter_session_inexistante(self, service):
        """Test erreur si session inexistante."""
        with pytest.raises(ValueError, match="non trouvée"):
            service.arreter_session(999)

    def test_annuler_session(self, service):
        """Test annulation de session."""
        session = service.demarrer_session(TypeActiviteEntretien.BRICOLAGE)
        session_id = session.id

        result = service.annuler_session(session_id)

        assert result is True
        assert session_id not in service._sessions_actives
        assert len(service._historique) == 0  # Pas ajoutée à l'historique

    def test_annuler_session_inexistante(self, service):
        """Test annulation session inexistante."""
        result = service.annuler_session(999)
        assert result is False

    def test_lister_sessions_actives(self, service):
        """Test liste des sessions actives."""
        service.demarrer_session(TypeActiviteEntretien.TONTE)
        service.demarrer_session(TypeActiviteEntretien.ARROSAGE)

        actives = service.lister_sessions_actives()

        assert len(actives) == 2
        assert all(s.duree_minutes is not None for s in actives)

    def test_obtenir_session_active(self, service):
        """Test récupération d'une session active."""
        session = service.demarrer_session(TypeActiviteEntretien.LESSIVE)

        result = service.obtenir_session_active(session.id)

        assert result is not None
        assert result.id == session.id

    def test_obtenir_session_inactive(self, service):
        """Test récupération session inexistante."""
        result = service.obtenir_session_active(999)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestStatistiques:
    """Tests pour le calcul des statistiques."""

    def test_statistiques_activite(self, service_avec_historique):
        """Test calcul des stats par activité."""
        stats = service_avec_historique.obtenir_statistiques_activite(periode_jours=30)

        assert len(stats) == 3  # tonte, aspirateur, arrosage

        # Vérifier tonte (60 min)
        stat_tonte = next(
            (s for s in stats if s.type_activite == TypeActiviteEntretien.TONTE), None
        )
        assert stat_tonte is not None
        assert stat_tonte.temps_total_minutes == 60
        assert stat_tonte.nb_sessions == 1

    def test_statistiques_activite_vide(self, service):
        """Test stats sans historique."""
        stats = service.obtenir_statistiques_activite()
        assert len(stats) == 0

    def test_statistiques_zone(self, service_avec_historique):
        """Test calcul des stats par zone."""
        stats = service_avec_historique.obtenir_statistiques_zone(periode_jours=30)

        assert len(stats) >= 2  # Au moins zone_id=1, zone_id=2

    def test_resume_semaine(self, service_avec_historique):
        """Test génération du résumé hebdomadaire."""
        resume = service_avec_historique.obtenir_resume_semaine()

        assert isinstance(resume, ResumeTempsHebdo)
        assert resume.temps_total_minutes >= 0
        assert resume.semaine_debut is not None
        assert resume.semaine_fin is not None

    def test_resume_semaine_vide(self, service):
        """Test résumé sans données."""
        resume = service.obtenir_resume_semaine()

        assert resume.temps_total_minutes == 0
        assert resume.nb_sessions == 0

    def test_obtenir_historique(self, service_avec_historique):
        """Test récupération de l'historique."""
        historique = service_avec_historique.obtenir_historique(limite=10)

        assert len(historique) == 3
        # Trié par date décroissante
        assert historique[0].debut > historique[-1].debut

    def test_obtenir_historique_filtre(self, service_avec_historique):
        """Test historique filtré par type."""
        historique = service_avec_historique.obtenir_historique(
            type_activite=TypeActiviteEntretien.TONTE
        )

        assert len(historique) == 1
        assert historique[0].type_activite == TypeActiviteEntretien.TONTE


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSE IA
# ═══════════════════════════════════════════════════════════


class TestAnalyseIA:
    """Tests pour l'analyse IA."""

    @pytest.mark.asyncio
    async def test_analyser_temps_ia(self, service_avec_historique):
        """Test analyse IA complète."""
        request = AnalyseTempsRequest(
            periode="semaine",
            inclure_suggestions=True,
            inclure_materiel=True,
        )

        # Mock les appels IA
        with (
            patch.object(service_avec_historique, "_generer_suggestions_ia") as mock_sugg,
            patch.object(
                service_avec_historique, "_generer_recommandations_materiel_ia"
            ) as mock_mat,
            patch.object(service_avec_historique, "_generer_resume_ia") as mock_resume,
        ):
            mock_sugg.return_value = [
                SuggestionOptimisation(
                    titre="Test suggestion",
                    description="Description test",
                    type_suggestion="regroupement",
                )
            ]
            mock_mat.return_value = []
            mock_resume.return_value = "Résumé de test"

            result = await service_avec_historique.analyser_temps_ia(request)

            assert result.periode_analysee == "semaine"
            assert result.resume_textuel == "Résumé de test"
            assert len(result.suggestions_optimisation) == 1

    def test_suggestions_par_defaut(self, service):
        """Test suggestions par défaut."""
        suggestions = service._suggestions_par_defaut()

        assert len(suggestions) >= 2
        assert all(isinstance(s, SuggestionOptimisation) for s in suggestions)

    def test_recommandations_par_defaut(self, service):
        """Test recommandations matériel par défaut."""
        recommandations = service._recommandations_par_defaut()

        assert len(recommandations) >= 2
        assert all(isinstance(r, RecommandationMateriel) for r in recommandations)

    def test_calculer_score_efficacite(self, service_avec_historique):
        """Test calcul du score d'efficacité."""
        stats = service_avec_historique.obtenir_statistiques_activite()
        resume = service_avec_historique.obtenir_resume_semaine()

        score = service_avec_historique._calculer_score_efficacite(stats, resume)

        assert 0 <= score <= 100

    def test_suggerer_objectif(self, service):
        """Test suggestion d'objectif hebdo."""
        # 700 min sur 7 jours = 100 min/jour = 700/semaine
        objectif = service._suggerer_objectif(temps_actuel=700, jours=7)

        # Devrait suggérer ~630 min (-10%)
        assert 600 <= objectif <= 700


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    """Tests pour la factory du service."""

    def test_get_temps_entretien_service(self):
        """Test obtention du service."""
        service = get_temps_entretien_service()

        assert isinstance(service, TempsEntretienService)

    def test_singleton(self):
        """Test que c'est un singleton."""
        s1 = get_temps_entretien_service()
        s2 = get_temps_entretien_service()

        assert s1 is s2


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes du module."""

    def test_icones_activites(self):
        """Test que toutes les activités ont une icône."""
        for activite in TypeActiviteEntretien:
            assert activite in ICONES_ACTIVITES
            assert ICONES_ACTIVITES[activite]  # Non vide

    def test_categories_activites(self):
        """Test que les catégories couvrent toutes les activités."""
        toutes_activites = set()
        for cat_activites in CATEGORIES_ACTIVITES.values():
            toutes_activites.update(cat_activites)

        # Vérifier qu'on a au moins les principales
        assert TypeActiviteEntretien.TONTE in toutes_activites
        assert TypeActiviteEntretien.ASPIRATEUR in toutes_activites
        assert TypeActiviteEntretien.BRICOLAGE in toutes_activites
