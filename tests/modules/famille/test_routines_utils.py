"""
Tests pour src/modules/famille/routines_utils.py

Tests complets des fonctions utilitaires de routines familiales.
"""

from datetime import time

import pytest

from src.modules.famille.routines_utils import (
    JOURS_SEMAINE,
    MOMENTS_JOURNEE,
    analyser_regularite,
    calculer_duree_routine,
    calculer_heure_fin,
    calculer_statistiques_routines,
    detecter_conflits_horaires,
    filtrer_par_jour,
    filtrer_par_moment,
    get_moment_journee,
    grouper_par_moment,
    trier_par_heure,
)


class TestConstantes:
    """Tests pour les constantes du module."""

    def test_jours_semaine_complets(self):
        assert len(JOURS_SEMAINE) == 7
        assert "Lundi" in JOURS_SEMAINE
        assert "Dimanche" in JOURS_SEMAINE

    def test_moments_journee_complets(self):
        assert len(MOMENTS_JOURNEE) == 5
        assert "Matin" in MOMENTS_JOURNEE
        assert "Soir" in MOMENTS_JOURNEE


class TestGetMomentJournee:
    """Tests pour get_moment_journee."""

    def test_matin_debut(self):
        assert get_moment_journee(time(5, 0)) == "Matin"

    def test_matin_milieu(self):
        assert get_moment_journee(time(8, 30)) == "Matin"

    def test_matin_fin(self):
        assert get_moment_journee(time(11, 59)) == "Matin"

    def test_midi_debut(self):
        assert get_moment_journee(time(12, 0)) == "Midi"

    def test_midi_fin(self):
        assert get_moment_journee(time(13, 59)) == "Midi"

    def test_apres_midi_debut(self):
        assert get_moment_journee(time(14, 0)) == "Après-midi"

    def test_apres_midi_fin(self):
        assert get_moment_journee(time(17, 59)) == "Après-midi"

    def test_soir_debut(self):
        assert get_moment_journee(time(18, 0)) == "Soir"

    def test_soir_fin(self):
        assert get_moment_journee(time(21, 59)) == "Soir"

    def test_nuit_debut(self):
        assert get_moment_journee(time(22, 0)) == "Nuit"

    def test_nuit_minuit(self):
        assert get_moment_journee(time(0, 0)) == "Nuit"

    def test_nuit_fin(self):
        assert get_moment_journee(time(4, 59)) == "Nuit"

    def test_string_iso_format(self):
        assert get_moment_journee("2024-01-15T08:30:00") == "Matin"

    def test_none_retourne_inconnu(self):
        assert get_moment_journee(None) == "Inconnu"


class TestCalculerDureeRoutine:
    """Tests pour calculer_duree_routine."""

    def test_liste_vide(self):
        assert calculer_duree_routine([]) == 0

    def test_une_routine(self):
        routines = [{"duree": 30}]
        assert calculer_duree_routine(routines) == 30

    def test_plusieurs_routines(self):
        routines = [
            {"duree": 15},
            {"duree": 30},
            {"duree": 45},
        ]
        assert calculer_duree_routine(routines) == 90

    def test_routine_sans_duree(self):
        routines = [{"titre": "Test"}, {"duree": 30}]
        assert calculer_duree_routine(routines) == 30

    def test_durees_nulles(self):
        routines = [{"duree": 0}, {"duree": 0}]
        assert calculer_duree_routine(routines) == 0


class TestCalculerHeureFin:
    """Tests pour calculer_heure_fin."""

    def test_calcul_simple(self):
        fin = calculer_heure_fin(time(8, 0), 30)
        assert fin == time(8, 30)

    def test_passage_heure(self):
        fin = calculer_heure_fin(time(8, 45), 30)
        assert fin == time(9, 15)

    def test_duree_zero(self):
        fin = calculer_heure_fin(time(12, 0), 0)
        assert fin == time(12, 0)

    def test_longue_duree(self):
        fin = calculer_heure_fin(time(10, 0), 120)
        assert fin == time(12, 0)

    def test_string_iso_input(self):
        fin = calculer_heure_fin("2024-01-15T08:00:00", 60)
        assert fin == time(9, 0)

    def test_none_raise_error(self):
        with pytest.raises(ValueError):
            calculer_heure_fin(None, 30)


class TestFiltrerParMoment:
    """Tests pour filtrer_par_moment."""

    @pytest.fixture
    def routines_exemple(self):
        return [
            {"titre": "Réveil", "moment": "Matin"},
            {"titre": "Sieste", "moment": "Après-midi"},
            {"titre": "Dîner", "moment": "Soir"},
            {"titre": "Petit-déj", "moment": "Matin"},
        ]

    def test_filtre_matin(self, routines_exemple):
        resultat = filtrer_par_moment(routines_exemple, "Matin")
        assert len(resultat) == 2
        assert all(r["moment"] == "Matin" for r in resultat)

    def test_filtre_aucun_resultat(self, routines_exemple):
        resultat = filtrer_par_moment(routines_exemple, "Nuit")
        assert len(resultat) == 0

    def test_liste_vide(self):
        assert filtrer_par_moment([], "Matin") == []


class TestFiltrerParJour:
    """Tests pour filtrer_par_jour."""

    @pytest.fixture
    def routines_exemple(self):
        return [
            {"titre": "École", "jours_actifs": ["Lundi", "Mardi", "Mercredi"]},
            {"titre": "Sport", "jours_actifs": ["Samedi"]},
            {"titre": "Routine quotidienne"},  # Par défaut: tous les jours
        ]

    def test_filtre_lundi(self, routines_exemple):
        resultat = filtrer_par_jour(routines_exemple, "Lundi")
        titres = [r["titre"] for r in resultat]
        assert "École" in titres
        assert "Routine quotidienne" in titres
        assert "Sport" not in titres

    def test_filtre_samedi(self, routines_exemple):
        resultat = filtrer_par_jour(routines_exemple, "Samedi")
        titres = [r["titre"] for r in resultat]
        assert "Sport" in titres
        assert "Routine quotidienne" in titres


class TestTrierParHeure:
    """Tests pour trier_par_heure."""

    def test_tri_croissant(self):
        routines = [
            {"titre": "C", "heure": time(12, 0)},
            {"titre": "A", "heure": time(8, 0)},
            {"titre": "B", "heure": time(10, 0)},
        ]
        resultat = trier_par_heure(routines)
        assert [r["titre"] for r in resultat] == ["A", "B", "C"]

    def test_sans_heure_a_la_fin(self):
        routines = [
            {"titre": "Avec", "heure": time(8, 0)},
            {"titre": "Sans"},
        ]
        resultat = trier_par_heure(routines)
        assert resultat[0]["titre"] == "Avec"
        assert resultat[1]["titre"] == "Sans"

    def test_liste_vide(self):
        assert trier_par_heure([]) == []


class TestGrouperParMoment:
    """Tests pour grouper_par_moment."""

    def test_groupement_basique(self):
        routines = [
            {"titre": "R1", "moment": "Matin"},
            {"titre": "R2", "moment": "Soir"},
            {"titre": "R3", "moment": "Matin"},
        ]
        groupes = grouper_par_moment(routines)
        assert len(groupes["Matin"]) == 2
        assert len(groupes["Soir"]) == 1

    def test_moment_inconnu_devient_autre(self):
        routines = [{"titre": "Test", "moment": "Inconnu"}]
        groupes = grouper_par_moment(routines)
        assert "Autre" in groupes

    def test_liste_vide(self):
        assert grouper_par_moment([]) == {}


class TestCalculerStatistiquesRoutines:
    """Tests pour calculer_statistiques_routines."""

    def test_liste_vide(self):
        stats = calculer_statistiques_routines([])
        assert stats["total"] == 0
        assert stats["par_type"] == {}
        assert stats["par_moment"] == {}

    def test_stats_completes(self):
        routines = [
            {"type": "Repas", "moment": "Matin"},
            {"type": "Repas", "moment": "Midi"},
            {"type": "Sieste", "moment": "Après-midi"},
        ]
        stats = calculer_statistiques_routines(routines)
        assert stats["total"] == 3
        assert stats["par_type"]["Repas"] == 2
        assert stats["par_type"]["Sieste"] == 1
        assert stats["par_moment"]["Matin"] == 1


class TestDetecterConflitsHoraires:
    """Tests pour detecter_conflits_horaires."""

    def test_pas_de_conflit(self):
        routines = [
            {"titre": "A", "heure": time(8, 0), "duree": 30},
            {"titre": "B", "heure": time(9, 0), "duree": 30},
        ]
        conflits = detecter_conflits_horaires(routines)
        assert len(conflits) == 0

    def test_conflit_detecte(self):
        routines = [
            {"titre": "A", "heure": time(8, 0), "duree": 60},
            {"titre": "B", "heure": time(8, 30), "duree": 30},
        ]
        conflits = detecter_conflits_horaires(routines)
        assert len(conflits) == 1
        assert conflits[0]["routine_a"] == "A"
        assert conflits[0]["routine_b"] == "B"

    def test_sans_heure_ignore(self):
        routines = [
            {"titre": "A", "heure": time(8, 0), "duree": 60},
            {"titre": "B", "duree": 30},
        ]
        conflits = detecter_conflits_horaires(routines)
        assert len(conflits) == 0


class TestAnalyserRegularite:
    """Tests pour analyser_regularite."""

    def test_excellent(self):
        historique = [{"routine_id": 1, "date": f"2024-01-{i:02d}"} for i in range(1, 8)]
        resultat = analyser_regularite(historique, routine_id=1, jours=7)
        assert resultat["executions"] == 7
        assert resultat["regularite"] == "Excellent"
        assert resultat["taux_realisation"] == 100.0

    def test_bon(self):
        historique = [{"routine_id": 1, "date": f"2024-01-{i:02d}"} for i in range(1, 6)]
        resultat = analyser_regularite(historique, routine_id=1, jours=7)
        assert resultat["regularite"] == "Bon"

    def test_moyen(self):
        historique = [{"routine_id": 1, "date": f"2024-01-{i:02d}"} for i in range(1, 5)]
        resultat = analyser_regularite(historique, routine_id=1, jours=7)
        assert resultat["regularite"] == "Moyen"

    def test_faible(self):
        historique = [{"routine_id": 1, "date": "2024-01-01"}]
        resultat = analyser_regularite(historique, routine_id=1, jours=7)
        assert resultat["regularite"] == "Faible"

    def test_aucune_execution(self):
        resultat = analyser_regularite([], routine_id=1, jours=7)
        assert resultat["executions"] == 0
        assert resultat["regularite"] == "Faible"

    def test_autre_routine_ignoree(self):
        historique = [{"routine_id": 2, "date": "2024-01-01"}]
        resultat = analyser_regularite(historique, routine_id=1, jours=7)
        assert resultat["executions"] == 0
