"""
Tests de couverture complémentaires pour vue_semaine_logic.py
Objectif: atteindre 80%+ de couverture
Couvre les lignes non testées
"""
import pytest
from datetime import date, time, datetime, timedelta

from src.domains.planning.logic.vue_semaine_logic import (
    calculer_temps_libre,
    calculer_statistiques_semaine,
    suggerer_creneaux_libres,
    formater_periode_semaine,
    formater_heure,
    filtrer_evenements_semaine,
    filtrer_evenements_jour,
    trier_evenements_par_heure,
    detecter_conflits_horaires,
)


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER_TEMPS_LIBRE
# ═══════════════════════════════════════════════════════════

class TestCalculerTempsLibre:
    """Tests pour calculer_temps_libre."""

    def test_temps_libre_journee_vide(self):
        """Journée vide = 960 min de temps libre."""
        date_ref = date(2026, 2, 9)  # Un lundi
        
        result = calculer_temps_libre([], date_ref)
        
        assert len(result) == 7  # 7 jours
        for jour, temps in result.items():
            assert temps == 960  # 16h de veille

    def test_temps_libre_avec_evenements(self):
        """Journée avec événements réduit le temps libre."""
        date_ref = date(2026, 2, 9)  # Un lundi
        evenements = [
            {"date": date_ref, "heure": time(9, 0), "duree": 60},
            {"date": date_ref, "heure": time(14, 0), "duree": 120},
        ]
        
        result = calculer_temps_libre(evenements, date_ref)
        
        # Lundi devrait avoir 960 - 60 - 120 = 780 min
        assert result[date_ref] == 780

    def test_temps_libre_multiple_jours(self):
        """Événements sur plusieurs jours."""
        date_ref = date(2026, 2, 9)  # Un lundi
        mardi = date_ref + timedelta(days=1)
        
        evenements = [
            {"date": date_ref, "heure": time(9, 0), "duree": 60},
            {"date": mardi, "heure": time(10, 0), "duree": 90},
        ]
        
        result = calculer_temps_libre(evenements, date_ref)
        
        assert result[date_ref] == 900  # 960 - 60
        assert result[mardi] == 870  # 960 - 90


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER_STATISTIQUES_SEMAINE
# ═══════════════════════════════════════════════════════════

class TestCalculerStatistiquesSemaine:
    """Tests pour calculer_statistiques_semaine."""

    def test_statistiques_semaine_vide(self):
        """Semaine vide retourne stats à zéro."""
        result = calculer_statistiques_semaine([], date(2026, 2, 9))
        
        assert result["total"] == 0
        assert result["par_type"] == {}
        assert result["duree_totale"] == 0
        assert result["duree_moyenne"] == 0

    def test_statistiques_avec_evenements(self):
        """Calcul statistiques avec événements."""
        date_ref = date(2026, 2, 9)
        evenements = [
            {"date": date_ref, "type": "Réunion", "duree": 60},
            {"date": date_ref, "type": "Réunion", "duree": 30},
            {"date": date_ref + timedelta(days=1), "type": "Formation", "duree": 120},
        ]
        
        result = calculer_statistiques_semaine(evenements, date_ref)
        
        assert result["total"] == 3
        assert result["par_type"]["Réunion"] == 2
        assert result["par_type"]["Formation"] == 1
        assert result["duree_totale"] == 210
        assert result["duree_moyenne"] == 70

    def test_statistiques_type_autre(self):
        """Événement sans type utilisé 'Autre'."""
        date_ref = date(2026, 2, 9)
        evenements = [
            {"date": date_ref, "duree": 60},
        ]
        
        result = calculer_statistiques_semaine(evenements, date_ref)
        
        assert result["par_type"]["Autre"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS SUGGERER_CRENEAUX_LIBRES
# ═══════════════════════════════════════════════════════════

class TestSuggererCreneauxLibres:
    """Tests pour suggerer_creneaux_libres."""

    def test_creneaux_libres_journee_vide(self):
        """Journée vide = un grand créneau libre."""
        jour = date(2026, 2, 9)
        
        result = suggerer_creneaux_libres([], jour, 60)
        
        assert len(result) == 1
        assert result[0]["debut"] == time(8, 0)
        assert result[0]["fin"] == time(20, 0)
        assert result[0]["duree"] == 720  # 12h = 720 min

    def test_creneaux_libres_avec_evenements(self):
        """Créneaux autour des événements."""
        jour = date(2026, 2, 9)
        evenements = [
            {"date": jour, "heure": time(10, 0), "duree": 60},
        ]
        
        result = suggerer_creneaux_libres(evenements, jour, 60)
        
        # Devrait avoir 2 créneaux: 8h-10h et 11h-20h
        assert len(result) == 2
        assert result[0]["debut"] == time(8, 0)
        assert result[0]["fin"] == time(10, 0)
        assert result[1]["debut"] == time(11, 0)
        assert result[1]["fin"] == time(20, 0)

    def test_creneaux_libres_plusieurs_evenements(self):
        """Multiple événements créent plusieurs créneaux."""
        jour = date(2026, 2, 9)
        evenements = [
            {"date": jour, "heure": time(9, 0), "duree": 60},
            {"date": jour, "heure": time(14, 0), "duree": 120},
        ]
        
        result = suggerer_creneaux_libres(evenements, jour, 60)
        
        # Créneaux: 8h-9h, 10h-14h, 16h-20h
        assert len(result) == 3

    def test_creneaux_libres_duree_minimale(self):
        """Filtre créneaux trop courts."""
        jour = date(2026, 2, 9)
        evenements = [
            {"date": jour, "heure": time(8, 30), "duree": 60},
        ]
        
        result = suggerer_creneaux_libres(evenements, jour, 60)
        
        # Le créneau 8h-8h30 (30 min) ne devrait pas apparaître
        for creneau in result:
            assert creneau["duree"] >= 60

    def test_creneaux_libres_heure_string(self):
        """Gère les heures en format string."""
        jour = date(2026, 2, 9)
        evenements = [
            {"date": jour, "heure": "2026-02-09T10:00:00", "duree": 60},
        ]
        
        result = suggerer_creneaux_libres(evenements, jour, 60)
        
        assert len(result) >= 1

    def test_creneaux_libres_evenement_sans_heure(self):
        """Ignore événements sans heure."""
        jour = date(2026, 2, 9)
        evenements = [
            {"date": jour, "duree": 60},  # Pas d'heure
        ]
        
        result = suggerer_creneaux_libres(evenements, jour, 60)
        
        # Devrait retourner le créneau complet
        assert len(result) == 1
        assert result[0]["duree"] == 720


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER_PERIODE_SEMAINE
# ═══════════════════════════════════════════════════════════

class TestFormaterPeriodeSemaine:
    """Tests pour formater_periode_semaine."""

    def test_formater_periode_date_specifique(self):
        """Formate période avec date spécifique."""
        date_ref = date(2026, 2, 9)  # Un lundi
        
        result = formater_periode_semaine(date_ref)
        
        assert "Semaine" in result
        assert "09/02" in result
        assert "15/02" in result

    def test_formater_periode_sans_date(self):
        """Formate période sans date (utilise aujourd'hui)."""
        result = formater_periode_semaine()
        
        assert "Semaine" in result
        assert "/" in result  # Format date


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER_HEURE  
# ═══════════════════════════════════════════════════════════

class TestFormaterHeure:
    """Tests pour formater_heure."""

    def test_formater_heure_time(self):
        """Formate un objet time."""
        result = formater_heure(time(14, 30))
        
        assert result == "14:30"

    def test_formater_heure_string(self):
        """Formate une heure en string."""
        result = formater_heure("2026-02-09T14:30:00")
        
        assert result == "14:30"

    def test_formater_heure_minuit(self):
        """Formate minuit."""
        result = formater_heure(time(0, 0))
        
        assert result == "00:00"

    def test_formater_heure_fin_journee(self):
        """Formate fin de journée."""
        result = formater_heure(time(23, 59))
        
        assert result == "23:59"


# ═══════════════════════════════════════════════════════════
# TESTS DETECTER_CONFLITS_HORAIRES EDGE CASES
# ═══════════════════════════════════════════════════════════

class TestDetecterConflitsHorairesEdgeCases:
    """Tests edge cases pour detecter_conflits_horaires."""

    def test_conflit_avec_heure_string(self):
        """Détecte conflit avec heures en string."""
        jour = date(2026, 2, 9)
        evenements = [
            {"date": jour, "heure": "2026-02-09T09:00:00", "duree": 120},
            {"date": jour, "heure": "2026-02-09T10:00:00", "duree": 60},
        ]
        
        result = detecter_conflits_horaires(evenements)
        
        assert len(result) == 1  # Un conflit

    def test_pas_conflit_evenements_consecutifs(self):
        """Pas de conflit si événements sont consécutifs."""
        jour = date(2026, 2, 9)
        evenements = [
            {"date": jour, "heure": time(9, 0), "duree": 60},
            {"date": jour, "heure": time(10, 0), "duree": 60},
        ]
        
        result = detecter_conflits_horaires(evenements)
        
        assert len(result) == 0


# ═══════════════════════════════════════════════════════════
# TESTS TRIER_EVENEMENTS_PAR_HEURE
# ═══════════════════════════════════════════════════════════

class TestTrierEvenementsParHeure:
    """Tests pour trier_evenements_par_heure."""

    def test_trier_avec_heures_string(self):
        """Trie avec des heures en string."""
        evenements = [
            {"nom": "B", "heure": "2026-02-09T14:00:00"},
            {"nom": "A", "heure": "2026-02-09T09:00:00"},
        ]
        
        result = trier_evenements_par_heure(evenements)
        
        assert result[0]["nom"] == "A"
        assert result[1]["nom"] == "B"

    def test_trier_avec_heures_mixtes(self):
        """Trie avec mix time et string."""
        evenements = [
            {"nom": "B", "heure": time(14, 0)},
            {"nom": "A", "heure": "2026-02-09T09:00:00"},
        ]
        
        result = trier_evenements_par_heure(evenements)
        
        assert result[0]["nom"] == "A"
        assert result[1]["nom"] == "B"
