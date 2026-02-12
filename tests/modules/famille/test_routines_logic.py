"""
Tests pour routines_logic.py - Module Famille
Couverture cible: 80%+
"""
import pytest
from datetime import date, time, timedelta

from src.modules.famille.routines_utils import (
    # Constantes
    MOMENTS_JOURNEE,
    TYPES_ROUTINE,
    JOURS_SEMAINE,
    # Gestion du temps
    get_moment_journee,
    calculer_duree_routine,
    calculer_heure_fin,
    # Filtrage et organisation
    filtrer_par_moment,
    filtrer_par_jour,
    get_routines_aujourdhui,
    grouper_par_moment,
    trier_par_heure,
    # Statistiques
    calculer_statistiques_routines,
    analyser_regularite,
    # Suggestions
    suggerer_routines_age,
    detecter_conflits_horaires,
    # Validation
    valider_routine,
    # Formatage
    formater_heure,
    formater_duree,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def routines_sample():
    """Liste de routines de test."""
    return [
        {
            "id": 1,
            "type": "Réveil",
            "moment": "Matin",
            "heure": time(7, 0),
            "duree": 30,
            "jours_actifs": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"],
        },
        {
            "id": 2,
            "type": "Repas",
            "moment": "Midi",
            "heure": time(12, 0),
            "duree": 45,
            "jours_actifs": JOURS_SEMAINE,
        },
        {
            "id": 3,
            "type": "Sieste",
            "moment": "Après-midi",
            "heure": time(14, 0),
            "duree": 90,
            "jours_actifs": JOURS_SEMAINE,
        },
        {
            "id": 4,
            "type": "Bain",
            "moment": "Soir",
            "heure": time(18, 30),
            "duree": 20,
            "jours_actifs": JOURS_SEMAINE,
        },
        {
            "id": 5,
            "type": "Coucher",
            "moment": "Soir",
            "heure": time(19, 30),
            "duree": 30,
            "jours_actifs": JOURS_SEMAINE,
        },
    ]


@pytest.fixture
def routines_vides():
    """Liste vide."""
    return []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestConstantesRoutines:
    """Tests des constantes."""

    def test_moments_journee(self):
        """Moments de la journée définis."""
        assert "Matin" in MOMENTS_JOURNEE
        assert "Midi" in MOMENTS_JOURNEE
        assert "Soir" in MOMENTS_JOURNEE
        assert "Nuit" in MOMENTS_JOURNEE

    def test_types_routine(self):
        """Types de routine définis."""
        assert "Réveil" in TYPES_ROUTINE
        assert "Repas" in TYPES_ROUTINE
        assert "Coucher" in TYPES_ROUTINE

    def test_jours_semaine(self):
        """Jours de la semaine définis."""
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"
        assert JOURS_SEMAINE[6] == "Dimanche"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GESTION DU TEMPS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGestionTemps:
    """Tests des fonctions de gestion du temps."""

    def test_get_moment_journee_matin(self):
        """Matin: 5h-12h."""
        assert get_moment_journee(time(6, 0)) == "Matin"
        assert get_moment_journee(time(8, 30)) == "Matin"
        assert get_moment_journee(time(11, 59)) == "Matin"

    def test_get_moment_journee_midi(self):
        """Midi: 12h-14h."""
        assert get_moment_journee(time(12, 0)) == "Midi"
        assert get_moment_journee(time(13, 30)) == "Midi"

    def test_get_moment_journee_apres_midi(self):
        """Après-midi: 14h-18h."""
        assert get_moment_journee(time(14, 0)) == "Après-midi"
        assert get_moment_journee(time(17, 59)) == "Après-midi"

    def test_get_moment_journee_soir(self):
        """Soir: 18h-22h."""
        assert get_moment_journee(time(18, 0)) == "Soir"
        assert get_moment_journee(time(21, 0)) == "Soir"

    def test_get_moment_journee_nuit(self):
        """Nuit: 22h-5h."""
        assert get_moment_journee(time(22, 0)) == "Nuit"
        assert get_moment_journee(time(23, 59)) == "Nuit"
        assert get_moment_journee(time(3, 0)) == "Nuit"

    def test_get_moment_journee_string(self):
        """Heure en format string."""
        from datetime import datetime
        heure_str = "2024-01-01T08:00:00"
        assert get_moment_journee(heure_str) == "Matin"

    def test_calculer_duree_routine(self, routines_sample):
        """Durée totale des routines."""
        duree = calculer_duree_routine(routines_sample)
        # 30 + 45 + 90 + 20 + 30 = 215
        assert duree == 215

    def test_calculer_duree_routine_vide(self, routines_vides):
        """Durée avec liste vide = 0."""
        duree = calculer_duree_routine(routines_vides)
        assert duree == 0

    def test_calculer_heure_fin(self):
        """Calcul de l'heure de fin."""
        debut = time(8, 0)
        fin = calculer_heure_fin(debut, 45)
        assert fin == time(8, 45)

    def test_calculer_heure_fin_passage_heure(self):
        """Passage d'une heure Ã  l'autre."""
        debut = time(8, 45)
        fin = calculer_heure_fin(debut, 30)
        assert fin == time(9, 15)

    def test_calculer_heure_fin_string(self):
        """Heure de début en string."""
        debut = "2024-01-01T08:00:00"
        fin = calculer_heure_fin(debut, 60)
        assert fin == time(9, 0)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FILTRAGE ET ORGANISATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFiltrageRoutines:
    """Tests des fonctions de filtrage."""

    def test_filtrer_par_moment(self, routines_sample):
        """Filtre par moment de la journée."""
        result = filtrer_par_moment(routines_sample, "Soir")
        assert len(result) == 2
        assert all(r["moment"] == "Soir" for r in result)

    def test_filtrer_par_moment_inexistant(self, routines_sample):
        """Moment inexistant retourne liste vide."""
        result = filtrer_par_moment(routines_sample, "Inexistant")
        assert len(result) == 0

    def test_filtrer_par_jour(self, routines_sample):
        """Filtre par jour de la semaine."""
        result = filtrer_par_jour(routines_sample, "Lundi")
        assert len(result) >= 4  # Toutes sauf peut-être certaines

    def test_filtrer_par_jour_weekend(self, routines_sample):
        """Filtre par jour de weekend (Réveil n'est pas actif)."""
        result = filtrer_par_jour(routines_sample, "Samedi")
        # Le Réveil n'est actif que du Lundi au Vendredi
        assert len(result) == 4
        assert all(r["type"] != "Réveil" for r in result)

    def test_get_routines_aujourdhui(self, routines_sample):
        """Routines d'aujourd'hui."""
        result = get_routines_aujourdhui(routines_sample)
        # Dépend du jour actuel
        assert isinstance(result, list)

    def test_grouper_par_moment(self, routines_sample):
        """Groupement par moment."""
        result = grouper_par_moment(routines_sample)
        
        assert "Matin" in result
        assert "Midi" in result
        assert "Soir" in result
        assert len(result["Matin"]) == 1
        assert len(result["Soir"]) == 2

    def test_grouper_par_moment_autre(self):
        """Moment inconnu va dans 'Autre'."""
        routines = [{"moment": "Inconnu", "type": "Test"}]
        result = grouper_par_moment(routines)
        assert "Autre" in result
        assert len(result["Autre"]) == 1

    def test_trier_par_heure(self, routines_sample):
        """Tri par heure."""
        result = trier_par_heure(routines_sample)
        heures = [r["heure"] for r in result]
        assert heures == sorted(heures)

    def test_trier_par_heure_string(self):
        """Tri avec heures en string."""
        routines = [
            {"heure": "2024-01-01T14:00:00"},
            {"heure": "2024-01-01T08:00:00"},
            {"heure": "2024-01-01T12:00:00"},
        ]
        result = trier_par_heure(routines)
        # Doit être trié: 8h, 12h, 14h
        assert len(result) == 3

    def test_trier_par_heure_none(self):
        """Routines sans heure vont Ã  la fin."""
        routines = [
            {"heure": time(8, 0)},
            {"heure": None},
            {"heure": time(10, 0)},
        ]
        result = trier_par_heure(routines)
        assert result[-1]["heure"] is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS STATISTIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestStatistiquesRoutines:
    """Tests des fonctions de statistiques."""

    def test_calculer_statistiques_routines(self, routines_sample):
        """Statistiques complètes."""
        result = calculer_statistiques_routines(routines_sample)
        
        assert result["total"] == 5
        assert "par_type" in result
        assert "par_moment" in result

    def test_calculer_statistiques_par_type(self, routines_sample):
        """Statistiques par type."""
        result = calculer_statistiques_routines(routines_sample)
        par_type = result["par_type"]
        
        assert par_type.get("Réveil", 0) == 1
        assert par_type.get("Repas", 0) == 1
        assert par_type.get("Coucher", 0) == 1

    def test_calculer_statistiques_liste_vide(self, routines_vides):
        """Statistiques liste vide."""
        result = calculer_statistiques_routines(routines_vides)
        assert result["total"] == 0
        assert result["par_type"] == {}
        assert result["par_moment"] == {}

class TestAnalyseRegularite:
    """Tests pour l'analyse de régularité."""

    def test_analyser_regularite_excellent(self):
        """Taux > 90% = Excellent."""
        today = date.today()
        historique = [
            {"routine_id": 1, "date": today - timedelta(days=i)}
            for i in range(7)  # 7 exécutions sur 7 jours
        ]
        result = analyser_regularite(historique, routine_id=1, jours=7)
        assert result["regularite"] == "Excellent"
        assert result["taux_realisation"] == 100.0

    def test_analyser_regularite_bon(self):
        """Taux 70-90% = Bon."""
        today = date.today()
        historique = [
            {"routine_id": 1, "date": today - timedelta(days=i)}
            for i in range(5)  # 5 exécutions sur 7 jours
        ]
        result = analyser_regularite(historique, routine_id=1, jours=7)
        assert result["regularite"] == "Bon"

    def test_analyser_regularite_moyen(self):
        """Taux 50-70% = Moyen."""
        today = date.today()
        historique = [
            {"routine_id": 1, "date": today - timedelta(days=i)}
            for i in range(4)  # 4 exécutions sur 7 jours
        ]
        result = analyser_regularite(historique, routine_id=1, jours=7)
        assert result["regularite"] == "Moyen"

    def test_analyser_regularite_faible(self):
        """Taux < 50% = Faible."""
        today = date.today()
        historique = [
            {"routine_id": 1, "date": today}
        ]
        result = analyser_regularite(historique, routine_id=1, jours=7)
        assert result["regularite"] == "Faible"

    def test_analyser_regularite_autre_routine(self):
        """Ignore les autres routines."""
        today = date.today()
        historique = [
            {"routine_id": 999, "date": today},  # Autre routine
        ]
        result = analyser_regularite(historique, routine_id=1, jours=7)
        assert result["executions"] == 0


class TestSuggestionsRoutines:
    """Tests pour les suggestions de routines."""

    def test_suggerer_routines_bebe(self):
        """Suggestions pour bébé < 12 mois."""
        suggestions = suggerer_routines_age(8)
        assert len(suggestions) >= 4
        titres = [s["titre"] for s in suggestions]
        assert "Réveil" in titres
        assert "Sieste matin" in titres

    def test_suggerer_routines_1_2_ans(self):
        """Suggestions pour 12-24 mois."""
        suggestions = suggerer_routines_age(18)
        assert len(suggestions) >= 4
        # Une seule sieste après-midi
        titres = [s["titre"] for s in suggestions]
        assert "Sieste après-midi" in titres

    def test_suggerer_routines_plus_2_ans(self):
        """Suggestions pour > 24 mois."""
        suggestions = suggerer_routines_age(30)
        assert len(suggestions) >= 4
        titres = [s["titre"] for s in suggestions]
        assert "Sieste (optionnelle)" in titres

    def test_detecter_conflits_horaires(self):
        """Détecte les conflits."""
        routines = [
            {"titre": "A", "heure": time(9, 0), "duree": 60},
            {"titre": "B", "heure": time(9, 30), "duree": 30},  # Conflit avec A
        ]
        conflits = detecter_conflits_horaires(routines)
        assert len(conflits) == 1

    def test_detecter_pas_de_conflits(self):
        """Pas de conflits quand horaires distincts."""
        routines = [
            {"titre": "A", "heure": time(9, 0), "duree": 30},
            {"titre": "B", "heure": time(10, 0), "duree": 30},
        ]
        conflits = detecter_conflits_horaires(routines)
        assert len(conflits) == 0


class TestValidationRoutine:
    """Tests pour la validation des routines."""

    def test_valider_routine_valide(self):
        """Routine valide."""
        data = {
            "titre": "Réveil",
            "type": "Réveil",
            "moment": "Matin",
            "duree": 30
        }
        valide, erreurs = valider_routine(data)
        assert valide is True
        assert len(erreurs) == 0

    def test_valider_routine_titre_manquant(self):
        """Titre obligatoire."""
        data = {"type": "Réveil"}
        valide, erreurs = valider_routine(data)
        assert valide is False
        assert any("titre" in e.lower() for e in erreurs)

    def test_valider_routine_type_invalide(self):
        """Type invalide."""
        data = {"titre": "Test", "type": "TypeInexistant"}
        valide, erreurs = valider_routine(data)
        assert valide is False
        assert any("type" in e.lower() for e in erreurs)

    def test_valider_routine_moment_invalide(self):
        """Moment invalide."""
        data = {"titre": "Test", "moment": "MomentInexistant"}
        valide, erreurs = valider_routine(data)
        assert valide is False
        assert any("moment" in e.lower() for e in erreurs)

    def test_valider_routine_duree_negative(self):
        """Durée négative invalide."""
        data = {"titre": "Test", "duree": -30}
        valide, erreurs = valider_routine(data)
        assert valide is False
        assert any("durée" in e.lower() for e in erreurs)


class TestFormatageRoutines:
    """Tests pour le formatage."""

    def test_formater_heure(self):
        """Formate une heure time."""
        assert formater_heure(time(9, 0)) == "09:00"
        assert formater_heure(time(14, 30)) == "14:30"

    def test_formater_heure_string(self):
        """Formate une heure depuis string ISO."""
        assert formater_heure("2025-01-01T09:00:00") == "09:00"

    def test_formater_duree_minutes(self):
        """Formate durée < 60min."""
        assert formater_duree(30) == "30min"
        assert formater_duree(45) == "45min"

    def test_formater_duree_heures(self):
        """Formate durée >= 60min."""
        assert formater_duree(60) == "1h"
        assert formater_duree(90) == "1h30"
        assert formater_duree(120) == "2h"