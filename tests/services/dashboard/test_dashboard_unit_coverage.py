"""Tests unitaires ciblés pour renforcer la couverture du scope dashboard."""

from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from src.services.dashboard.anomalies_financieres import ServiceAnomaliesFinancieres
from src.services.dashboard.badges_triggers import (
    BadgesTriggersService,
    obtenir_catalogue_badges,
)
from src.services.dashboard.points_famille import PointsFamilleService
from src.services.dashboard.resume_famille_ia import ResumeFamilleIAService
from src.services.dashboard.score_bienetre import ScoreBienEtreService
from src.services.dashboard.service import AccueilDataService


class QueryStub:
    def __init__(self, *, all_result=None, scalar_result=None, first_result=None):
        self._all_result = all_result if all_result is not None else []
        self._scalar_result = scalar_result
        self._first_result = first_result

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def all(self):
        return self._all_result

    def scalar(self):
        return self._scalar_result

    def first(self):
        return self._first_result


class SessionStub:
    def __init__(self, queries):
        self._queries = list(queries)
        self.added = []
        self.commit_count = 0

    def query(self, *args, **kwargs):
        return self._queries.pop(0)

    def add(self, item):
        self.added.append(item)

    def commit(self):
        self.commit_count += 1


class DummyPointsModel:
    user_id = object()
    semaine_debut = object()

    def __init__(self, user_id=None, semaine_debut=None):
        self.user_id = user_id
        self.semaine_debut = semaine_debut
        self.points_sport = 0
        self.points_alimentation = 0
        self.points_anti_gaspi = 0
        self.total_points = 0
        self.details = {}


class DummyBadgeModel:
    user_id = object()
    badge_type = object()
    acquis_le = object()

    def __init__(self, user_id=None, badge_type=None, badge_label=None, acquis_le=None, meta=None):
        self.user_id = user_id
        self.badge_type = badge_type
        self.badge_label = badge_label
        self.acquis_le = acquis_le
        self.meta = meta or {}


class DummyProfilModel:
    id = object()


class TestAnomaliesFinancieresCoverage:
    def test_detecter_anomalies_trie_et_qualifie_les_variations(self):
        service = object.__new__(ServiceAnomaliesFinancieres)
        donnees = {
            "2026-03": {"courses": 180.0, "energie": 220.0, "loisirs": 50.0},
            "2026-02": {"courses": 100.0, "energie": 120.0, "loisirs": 45.0},
            "2026-01": {"courses": 100.0, "energie": 100.0, "loisirs": 40.0},
        }

        with (
            patch.object(service, "_collecter_depenses", return_value=donnees),
            patch.object(
                service,
                "_generer_resume_ia",
                return_value={"resume": "Deux derives detectees", "recommandations": ["Agir"]},
            ),
        ):
            resultat = service.detecter_anomalies(date(2026, 3, 20))

        assert resultat["total_anomalies"] == 2
        assert resultat["anomalies"][0]["categorie"] == "energie"
        assert resultat["anomalies"][0]["niveau"] == "critique"
        assert resultat["anomalies"][1]["categorie"] == "courses"
        assert resultat["resume_ia"] == "Deux derives detectees"

    def test_generer_resume_ia_sans_anomalie_retourne_un_fallback_stable(self):
        service = object.__new__(ServiceAnomaliesFinancieres)

        resultat = service._generer_resume_ia([], "2026-03")

        assert "Aucune derive" in resultat["resume"]
        assert resultat["recommandations"]

    def test_generer_resume_ia_retombe_sur_un_resume_local_si_ia_absente(self):
        service = object.__new__(ServiceAnomaliesFinancieres)
        anomalies = [
            {
                "categorie": "courses",
                "variation_pct": 63.0,
            }
        ]

        with patch.object(service, "call_with_json_parsing_sync", return_value=None):
            resultat = service._generer_resume_ia(anomalies, "2026-03")

        assert "courses" in resultat["resume"]
        assert len(resultat["recommandations"]) == 3


class TestScoreBienEtreCoverage:
    def test_calculer_periode_agrege_repas_activites_et_garmin(self):
        service = ScoreBienEtreService()
        debut = date(2026, 3, 16)
        fin = date(2026, 3, 22)
        repas = [
            SimpleNamespace(
                recette=SimpleNamespace(type_proteines="Poulet", categorie=None, calories=320, lipides=10)
            ),
            SimpleNamespace(
                recette=SimpleNamespace(type_proteines=None, categorie="Vegetarien", calories=720, lipides=15)
            ),
        ]
        activites = [
            SimpleNamespace(type_activite="Sport collectif"),
            SimpleNamespace(type_activite="Piscine"),
            SimpleNamespace(type_activite="Lecture"),
        ]
        garmin_activites = [SimpleNamespace(), SimpleNamespace()]
        garmin_summaries = [
            SimpleNamespace(calories_actives=700),
            SimpleNamespace(calories_actives=900),
        ]
        db = SessionStub(
            [
                QueryStub(all_result=repas),
                QueryStub(all_result=activites),
                QueryStub(all_result=garmin_activites),
                QueryStub(all_result=garmin_summaries),
            ]
        )

        resultat = service._calculer_periode(debut, fin, db)

        assert resultat["score_global"] > 0
        assert resultat["diversite_alimentaire_score"] > 0
        assert resultat["details"]["nb_repas_analyses"] == 2
        assert resultat["details"]["nb_activites_sportives"] == 2
        assert resultat["details"]["calories_actives_garmin"] == 1600

    def test_calculer_score_ajoute_tendance_et_periode(self):
        service = ScoreBienEtreService()

        with patch.object(
            service,
            "_calculer_periode",
            side_effect=[{"score_global": 68}, {"score_global": 53}],
        ):
            resultat = service.calculer_score(db=object())

        assert resultat["score_global"] == 68
        assert resultat["trend_semaine_precedente"] == 15
        assert set(resultat["periode"]) == {"debut", "fin"}


class TestResumeHebdoCoverage:
    def test_generer_resume_hebdo_retourne_le_fallback_local_si_l_ia_ne_repond_pas(self):
        service = object.__new__(ResumeFamilleIAService)
        contexte = {
            "periode": {"debut": "2026-03-16", "fin": "2026-03-22"},
            "planning": {"repas_planifies_7j": 9, "activites_7j": 2, "evenements_7j": 1},
            "inventaire": {"stock_bas": 2, "peremptions_7j": 1},
            "budget": {"depenses_mois": 430.0},
            "score_jules": {"total_points": 50},
            "meteo": {"conditions": [], "tendance": "soleil"},
        }

        with (
            patch.object(service, "_collecter_contexte", return_value=contexte),
            patch.object(service, "call_with_json_parsing_sync", return_value=None),
        ):
            resultat = service.generer_resume_hebdo(date(2026, 3, 18))

        assert resultat["contexte"] == contexte
        assert resultat["score_semaine"] > 0
        assert "repas planifies" in resultat["resume"]
        assert len(resultat["recommandations"]) == 3


class TestAccueilDataCoverage:
    def test_get_taches_en_retard_formate_les_taches(self):
        service = AccueilDataService()
        today = date.today()
        taches = [
            SimpleNamespace(nom="Nettoyer filtre", prochaine_fois=today - timedelta(days=2)),
            SimpleNamespace(nom="Vider gouttiere", prochaine_fois=today - timedelta(days=5)),
        ]
        db = SessionStub([QueryStub(all_result=taches)])

        resultat = service.get_taches_en_retard(limit=2, db=db)

        assert [item["nom"] for item in resultat] == ["Nettoyer filtre", "Vider gouttiere"]
        assert resultat[0]["jours_retard"] == 2


class TestPointsFamilleCoverage:
    def test_sauvegarder_points_hebdo_cree_snapshot_et_badges(self):
        service = PointsFamilleService()
        profil = SimpleNamespace(id=7)
        db = SessionStub(
            [
                QueryStub(first_result=None),
                QueryStub(first_result=None),
                QueryStub(first_result=None),
                QueryStub(first_result=None),
            ]
        )

        service._sauvegarder_points_hebdo(
            db=db,
            semaine_debut=date(2026, 3, 17),
            points_sport=210,
            points_alimentation=240,
            points_anti_gaspi=200,
            total=650,
            badges=["Bougeotte", "Assiette futée", "Zéro gaspi"],
            details={"score_bien_etre": 80},
            profils=[profil],
            points_model=DummyPointsModel,
            badge_model=DummyBadgeModel,
        )

        assert db.commit_count == 1
        assert len(db.added) == 4
        snapshot = db.added[0]
        assert snapshot.total_points == 650
        assert snapshot.points_alimentation == 240

    def test_calculer_points_agrege_scores_et_persiste_un_snapshot(self):
        service = PointsFamilleService()
        profil = SimpleNamespace(id=3)
        activites = [SimpleNamespace(), SimpleNamespace()]
        resumes = [
            SimpleNamespace(pas=6000, calories_actives=1200),
            SimpleNamespace(pas=7000, calories_actives=1300),
        ]
        db = SessionStub(
            [
                QueryStub(all_result=activites),
                QueryStub(all_result=resumes),
                QueryStub(scalar_result=0),
                QueryStub(all_result=[profil]),
                QueryStub(first_result=None),
                QueryStub(first_result=None),
                QueryStub(first_result=None),
                QueryStub(first_result=None),
            ]
        )
        faux_score_service = SimpleNamespace(calculer_score=lambda: {"score_global": 80})

        with (
            patch("src.core.models.PointsUtilisateur", DummyPointsModel),
            patch("src.core.models.BadgeUtilisateur", DummyBadgeModel),
            patch("src.core.models.ProfilUtilisateur", DummyProfilModel),
            patch(
                "src.services.dashboard.score_bienetre.get_score_bien_etre_service",
                return_value=faux_score_service,
            ),
        ):
            resultat = service.calculer_points(db=db)

        assert resultat["sport"] >= 180
        assert resultat["alimentation"] == 240
        assert resultat["anti_gaspi"] == 200
        assert set(resultat["badges"]) == {"Bougeotte", "Assiette futée", "Zéro gaspi"}
        assert db.commit_count == 1


class TestBadgesTriggersCoverage:
    def test_catalogue_badges_expose_les_metadonnees(self):
        catalogue = obtenir_catalogue_badges()

        assert any(item["badge_type"] == "bougeotte" for item in catalogue)
        assert all("emoji" in item for item in catalogue)

    def test_jours_consecutifs_pas_gere_les_series_et_ruptures(self):
        resumes = [
            SimpleNamespace(date=date(2026, 3, 1), pas=9000),
            SimpleNamespace(date=date(2026, 3, 2), pas=9500),
            SimpleNamespace(date=date(2026, 3, 4), pas=10000),
            SimpleNamespace(date=date(2026, 3, 5), pas=11000),
            SimpleNamespace(date=date(2026, 3, 6), pas=4000),
        ]

        assert BadgesTriggersService._jours_consecutifs_pas(resumes, seuil=8000) == 2

    def test_obtenir_badges_utilisateur_marque_les_badges_obtenus(self):
        service = BadgesTriggersService()
        badges = [
            SimpleNamespace(badge_type="bougeotte", acquis_le=date(2026, 3, 20)),
            SimpleNamespace(badge_type="bougeotte", acquis_le=date(2026, 3, 19)),
            SimpleNamespace(badge_type="zero_gaspi", acquis_le=date(2026, 3, 18)),
        ]
        db = SessionStub([QueryStub(all_result=badges)])

        resultat = service.obtenir_badges_utilisateur(user_id=1, db=db)
        bougeotte = next(item for item in resultat if item["badge_type"] == "bougeotte")
        zero_gaspi = next(item for item in resultat if item["badge_type"] == "zero_gaspi")

        assert bougeotte["obtenu"] is True
        assert bougeotte["nb_obtenu"] == 2
        assert zero_gaspi["obtenu"] is True

    def test_obtenir_historique_points_reinverse_l_ordre_chronologique(self):
        service = BadgesTriggersService()
        historique = [
            SimpleNamespace(
                semaine_debut=date(2026, 3, 24),
                points_sport=120,
                points_alimentation=180,
                points_anti_gaspi=170,
                total_points=470,
                details={"score": 1},
            ),
            SimpleNamespace(
                semaine_debut=date(2026, 3, 17),
                points_sport=110,
                points_alimentation=150,
                points_anti_gaspi=160,
                total_points=420,
                details={"score": 2},
            ),
        ]
        db = SessionStub([QueryStub(all_result=historique)])

        resultat = service.obtenir_historique_points(user_id=1, nb_semaines=2, db=db)

        assert resultat[0]["semaine_debut"] == "2026-03-17"
        assert resultat[1]["semaine_debut"] == "2026-03-24"

    def test_evaluer_et_attribuer_recompense_les_badges_attendus(self):
        service = BadgesTriggersService()
        profil = SimpleNamespace(id=11)
        today = date.today()
        resumes = [
            SimpleNamespace(date=today - timedelta(days=offset), pas=12500, calories_actives=500)
            for offset in range(7)
        ]
        activites = [
            SimpleNamespace(type_activite="course"),
            SimpleNamespace(type_activite="velo"),
            SimpleNamespace(type_activite="natation"),
            SimpleNamespace(type_activite="randonnee"),
        ]
        repas = [
            SimpleNamespace(type_repas="dejeuner"),
            SimpleNamespace(type_repas="diner"),
            SimpleNamespace(type_repas="petit_dejeuner"),
            SimpleNamespace(type_repas="collation"),
            SimpleNamespace(type_repas="brunch"),
        ]
        requetes = [
            QueryStub(all_result=[profil]),
            QueryStub(all_result=resumes),
            QueryStub(all_result=activites),
            QueryStub(scalar_result=0),
            QueryStub(scalar_result=5),
            QueryStub(all_result=repas),
            *[QueryStub(first_result=None) for _ in range(12)],
        ]
        db = SessionStub(requetes)
        faux_score_service = SimpleNamespace(calculer_score=lambda: {"score_global": 80})

        with (
            patch("src.core.models.BadgeUtilisateur", DummyBadgeModel),
            patch("src.core.models.ProfilUtilisateur", DummyProfilModel),
            patch(
                "src.services.dashboard.score_bienetre.get_score_bien_etre_service",
                return_value=faux_score_service,
            ),
        ):
            resultat = service.evaluer_et_attribuer(db=db)

        assert len(resultat) >= 8
        assert any(item["badge_type"] == "marcheur_regulier" for item in resultat)
        assert any(item["badge_type"] == "zero_gaspi" for item in resultat)
        assert db.commit_count == 1
