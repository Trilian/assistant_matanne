"""
Tests pour src/services/famille/resume_hebdo.py — ServiceResumeHebdo.

Couvre:
- Calcul des dates de semaine
- Calcul du score hebdomadaire
- Génération du narratif fallback (sans IA)
- Est-ce lundi (est_jour_resume)
- Modèles Pydantic
- Factory singleton
"""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.services.famille.resume_hebdo import (
    ResumeActivites,
    ResumeBudget,
    ResumeHebdomadaire,
    ResumeRepas,
    ResumeTaches,
    ServiceResumeHebdo,
    obtenir_service_resume_hebdo,
)


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    def test_obtenir_service_retourne_instance(self):
        s = obtenir_service_resume_hebdo()
        assert isinstance(s, ServiceResumeHebdo)

    def test_singleton(self):
        s1 = obtenir_service_resume_hebdo()
        s2 = obtenir_service_resume_hebdo()
        assert s1 is s2


# ═══════════════════════════════════════════════════════════
# MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════


class TestModelesResume:
    def test_resume_repas_defaut(self):
        r = ResumeRepas()
        assert r.nb_repas_planifies == 0
        assert r.nb_repas_realises == 0
        assert r.recettes_populaires == []
        assert r.taux_realisation == 0.0

    def test_resume_budget_defaut(self):
        b = ResumeBudget()
        assert b.total_depenses == 0.0
        assert b.tendance == "stable"
        assert b.budget_restant is None

    def test_resume_activites_defaut(self):
        a = ResumeActivites()
        assert a.nb_activites == 0
        assert a.temps_total_heures == 0.0

    def test_resume_taches_defaut(self):
        t = ResumeTaches()
        assert t.nb_taches_realisees == 0
        assert t.nb_taches_en_retard == 0

    def test_resume_hebdomadaire_complet(self):
        rh = ResumeHebdomadaire(
            repas=ResumeRepas(nb_repas_planifies=10, nb_repas_realises=8, taux_realisation=0.8),
            budget=ResumeBudget(total_depenses=150.0, tendance="hausse"),
            activites=ResumeActivites(nb_activites=3, temps_total_heures=6.0),
            taches=ResumeTaches(nb_taches_realisees=15, nb_taches_en_retard=2),
            resume_narratif="Bonne semaine en famille.",
            score_semaine=75,
        )
        assert rh.score_semaine == 75
        assert rh.repas.taux_realisation == 0.8
        assert rh.budget.tendance == "hausse"


# ═══════════════════════════════════════════════════════════
# CALCUL DATES SEMAINE
# ═══════════════════════════════════════════════════════════


class TestCalculerDatesSemaine:
    def test_retourne_lundi_et_dimanche(self):
        service = ServiceResumeHebdo.__new__(ServiceResumeHebdo)
        debut, fin = service._calculer_dates_semaine()
        assert debut.weekday() == 0  # lundi
        assert fin.weekday() == 6    # dimanche
        assert (fin - debut).days == 6

    def test_semaine_precedente_par_defaut(self):
        service = ServiceResumeHebdo.__new__(ServiceResumeHebdo)
        debut, fin = service._calculer_dates_semaine()
        today = date.today()
        assert fin < today or fin <= today  # la semaine passée

    def test_avec_reference_specifique(self):
        service = ServiceResumeHebdo.__new__(ServiceResumeHebdo)
        ref = date(2026, 3, 25)  # mercredi — la semaine précédente est retournée
        debut, fin = service._calculer_dates_semaine(reference=ref)
        assert debut.weekday() == 0  # lundi
        assert fin.weekday() == 6   # dimanche
        assert fin < ref             # la semaine retournée précède la référence


# ═══════════════════════════════════════════════════════════
# CALCUL DU SCORE
# ═══════════════════════════════════════════════════════════


class TestCalculerScore:
    def test_score_entre_0_et_100(self):
        service = ServiceResumeHebdo.__new__(ServiceResumeHebdo)
        resume = ResumeHebdomadaire(
            repas=ResumeRepas(nb_repas_planifies=14, nb_repas_realises=10, taux_realisation=0.71),
            budget=ResumeBudget(total_depenses=200.0, tendance="stable"),
            activites=ResumeActivites(nb_activites=2),
            taches=ResumeTaches(nb_taches_realisees=10, nb_taches_en_retard=1),
        )
        score = service._calculer_score(resume)
        assert 0 <= score <= 100

    def test_score_eleve_bonne_semaine(self):
        service = ServiceResumeHebdo.__new__(ServiceResumeHebdo)
        resume = ResumeHebdomadaire(
            repas=ResumeRepas(nb_repas_planifies=14, nb_repas_realises=14, taux_realisation=1.0),
            budget=ResumeBudget(total_depenses=100.0, tendance="baisse"),
            activites=ResumeActivites(nb_activites=5, temps_total_heures=10.0),
            taches=ResumeTaches(nb_taches_realisees=20, nb_taches_en_retard=0),
        )
        score = service._calculer_score(resume)
        assert score >= 50

    def test_score_faible_mauvaise_semaine(self):
        service = ServiceResumeHebdo.__new__(ServiceResumeHebdo)
        resume = ResumeHebdomadaire(
            repas=ResumeRepas(nb_repas_planifies=0, nb_repas_realises=0, taux_realisation=0.0),
            budget=ResumeBudget(total_depenses=500.0, tendance="hausse"),
            activites=ResumeActivites(nb_activites=0),
            taches=ResumeTaches(nb_taches_realisees=0, nb_taches_en_retard=10),
        )
        score = service._calculer_score(resume)
        assert score <= 80  # pas parfait


# ═══════════════════════════════════════════════════════════
# NARRATIF FALLBACK
# ═══════════════════════════════════════════════════════════


class TestGenererNarratifFallback:
    def test_retourne_chaine_non_vide(self):
        service = ServiceResumeHebdo.__new__(ServiceResumeHebdo)
        resume = ResumeHebdomadaire(
            repas=ResumeRepas(nb_repas_planifies=10, nb_repas_realises=8),
            budget=ResumeBudget(total_depenses=150.0),
            activites=ResumeActivites(nb_activites=2),
            taches=ResumeTaches(nb_taches_realisees=5),
        )
        narratif = service._generer_narratif_fallback(resume)
        assert isinstance(narratif, str)
        assert len(narratif) > 20

    def test_contient_infos_repas(self):
        service = ServiceResumeHebdo.__new__(ServiceResumeHebdo)
        resume = ResumeHebdomadaire(
            repas=ResumeRepas(nb_repas_planifies=14, nb_repas_realises=12),
            budget=ResumeBudget(),
            activites=ResumeActivites(),
            taches=ResumeTaches(),
        )
        narratif = service._generer_narratif_fallback(resume)
        # Le narratif doit mentionner les repas ou le planning
        assert any(w in narratif.lower() for w in ["repas", "planif", "semaine", "réalisé"])


# ═══════════════════════════════════════════════════════════
# EST JOUR RESUME
# ═══════════════════════════════════════════════════════════


class TestEstJourResume:
    def test_retourne_bool(self):
        service = ServiceResumeHebdo.__new__(ServiceResumeHebdo)
        result = service.est_jour_resume()
        assert isinstance(result, bool)

    def test_vrai_si_lundi(self):
        service = ServiceResumeHebdo.__new__(ServiceResumeHebdo)
        monday = date(2026, 3, 23)  # un lundi
        with patch("src.services.famille.resume_hebdo.date") as mock_date:
            mock_date.today.return_value = monday
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            result = service.est_jour_resume()
            assert result is True

    def test_faux_si_pas_lundi(self):
        service = ServiceResumeHebdo.__new__(ServiceResumeHebdo)
        # Aujourd'hui est mardi 25 mars 2026
        tuesday = date(2026, 3, 25)
        with patch("src.services.famille.resume_hebdo.date") as mock_date:
            mock_date.today.return_value = tuesday
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            result = service.est_jour_resume()
            assert result is False
