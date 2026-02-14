"""
Tests comprehensifs pour src/modules/planning/vue_semaine_utils.py
Objectif: Augmenter la couverture de 60.19% à 80%+
"""

from datetime import date, time, timedelta

from src.modules.planning.vue_semaine_utils import (
    HEURES_JOURNEE,
    calculer_charge_semaine,
    calculer_statistiques_semaine,
    calculer_temps_libre,
    detecter_conflits_horaires,
    filtrer_evenements_jour,
    filtrer_evenements_semaine,
    formater_heure,
    formater_periode_semaine,
    get_jours_semaine,
    get_numero_semaine,
    get_semaine_precedente,
    get_semaine_suivante,
    grouper_evenements_par_jour,
    suggerer_creneaux_libres,
    trier_evenements_par_heure,
)

# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes."""

    def test_heures_journee(self):
        """Test liste des heures."""
        assert len(HEURES_JOURNEE) == 24
        assert HEURES_JOURNEE[0] == 0
        assert HEURES_JOURNEE[-1] == 23


# ═══════════════════════════════════════════════════════════
# TESTS NAVIGATION SEMAINE
# ═══════════════════════════════════════════════════════════


class TestNavigationSemaine:
    """Tests pour les fonctions de navigation."""

    def test_get_jours_semaine_defaults(self):
        """Test get_jours_semaine sans argument."""
        jours = get_jours_semaine()
        assert len(jours) == 7
        assert jours[0].weekday() == 0  # Lundi

    def test_get_jours_semaine_date_specifiee(self):
        """Test get_jours_semaine avec date specifiee."""
        jours = get_jours_semaine(date(2024, 1, 17))  # Mercredi
        assert len(jours) == 7
        assert jours[0] == date(2024, 1, 15)  # Lundi

    def test_get_semaine_precedente(self):
        """Test get_semaine_precedente."""
        resultat = get_semaine_precedente(date(2024, 1, 17))
        assert resultat == date(2024, 1, 10)

    def test_get_semaine_suivante(self):
        """Test get_semaine_suivante."""
        resultat = get_semaine_suivante(date(2024, 1, 17))
        assert resultat == date(2024, 1, 24)

    def test_get_numero_semaine_defaults(self):
        """Test get_numero_semaine sans argument."""
        numero = get_numero_semaine()
        assert 1 <= numero <= 53

    def test_get_numero_semaine_date_specifiee(self):
        """Test get_numero_semaine avec date specifiee."""
        # 15 janvier 2024 est semaine 3
        numero = get_numero_semaine(date(2024, 1, 15))
        assert numero == 3


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE EVENEMENTS
# ═══════════════════════════════════════════════════════════


class TestFiltrageEvenements:
    """Tests pour les fonctions de filtrage."""

    def test_filtrer_evenements_semaine_vide(self):
        """Test filtrage liste vide."""
        result = filtrer_evenements_semaine([])
        assert result == []

    def test_filtrer_evenements_semaine_string_date(self):
        """Test filtrage avec dates string."""
        # Date dans la semaine courante
        aujourd_hui = date.today()
        lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())

        evenements = [
            {"date": lundi.isoformat(), "titre": "Lundi"},
            {"date": (lundi + timedelta(days=3)).isoformat(), "titre": "Jeudi"},
            {"date": (lundi + timedelta(days=10)).isoformat(), "titre": "Hors semaine"},
        ]

        result = filtrer_evenements_semaine(evenements, aujourd_hui)

        assert len(result) == 2

    def test_filtrer_evenements_semaine_date_objets(self):
        """Test filtrage avec dates objets."""
        aujourd_hui = date.today()
        lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())

        evenements = [{"date": lundi, "titre": "Test"}]

        result = filtrer_evenements_semaine(evenements, aujourd_hui)

        assert len(result) == 1

    def test_filtrer_evenements_jour_vide(self):
        """Test filtrage jour liste vide."""
        result = filtrer_evenements_jour([], date.today())
        assert result == []

    def test_filtrer_evenements_jour_match(self):
        """Test filtrage jour avec correspondance."""
        aujourd_hui = date.today()

        evenements = [
            {"date": aujourd_hui.isoformat(), "titre": "Aujourd'hui"},
            {"date": (aujourd_hui + timedelta(days=1)).isoformat(), "titre": "Demain"},
        ]

        result = filtrer_evenements_jour(evenements, aujourd_hui)

        assert len(result) == 1
        assert result[0]["titre"] == "Aujourd'hui"

    def test_filtrer_evenements_jour_date_objet(self):
        """Test filtrage jour avec date objet."""
        aujourd_hui = date.today()
        evenements = [{"date": aujourd_hui, "titre": "Test"}]

        result = filtrer_evenements_jour(evenements, aujourd_hui)

        assert len(result) == 1

    def test_grouper_evenements_par_jour_vide(self):
        """Test groupement liste vide."""
        result = grouper_evenements_par_jour([])
        assert result == {}

    def test_grouper_evenements_par_jour(self):
        """Test groupement par jour."""
        jour1 = date(2024, 1, 15)
        jour2 = date(2024, 1, 16)

        evenements = [
            {"date": jour1.isoformat(), "titre": "Event 1"},
            {"date": jour1.isoformat(), "titre": "Event 2"},
            {"date": jour2.isoformat(), "titre": "Event 3"},
        ]

        result = grouper_evenements_par_jour(evenements)

        assert len(result) == 2
        assert len(result[jour1]) == 2
        assert len(result[jour2]) == 1

    def test_trier_evenements_par_heure_vide(self):
        """Test tri liste vide."""
        result = trier_evenements_par_heure([])
        assert result == []

    def test_trier_evenements_par_heure_sans_heure(self):
        """Test tri evenements sans heure."""
        evenements = [{"titre": "Sans heure"}]

        result = trier_evenements_par_heure(evenements)

        assert len(result) == 1

    def test_trier_evenements_par_heure_time_objet(self):
        """Test tri avec time objets."""
        evenements = [
            {"titre": "Tard", "heure": time(18, 0)},
            {"titre": "Tot", "heure": time(9, 0)},
        ]

        result = trier_evenements_par_heure(evenements)

        assert result[0]["titre"] == "Tot"
        assert result[1]["titre"] == "Tard"

    def test_trier_evenements_par_heure_string(self):
        """Test tri avec heures string."""
        evenements = [
            {"titre": "Tard", "heure": "2024-01-15T18:00:00"},
            {"titre": "Tot", "heure": "2024-01-15T09:00:00"},
        ]

        result = trier_evenements_par_heure(evenements)

        assert result[0]["titre"] == "Tot"


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSE SEMAINE
# ═══════════════════════════════════════════════════════════


class TestAnalyseSemaine:
    """Tests pour les fonctions d'analyse."""

    def test_calculer_charge_semaine_vide(self):
        """Test charge semaine vide."""
        result = calculer_charge_semaine([])

        assert result["total_evenements"] == 0
        assert result["jours_libres"] == 7
        assert result["charge_moyenne"] == 0

    def test_calculer_charge_semaine_avec_evenements(self):
        """Test charge avec evenements."""
        aujourd_hui = date.today()
        lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())

        evenements = [
            {"date": lundi.isoformat(), "titre": "Event 1"},
            {"date": lundi.isoformat(), "titre": "Event 2"},
            {"date": (lundi + timedelta(days=1)).isoformat(), "titre": "Event 3"},
        ]

        result = calculer_charge_semaine(evenements, aujourd_hui)

        assert result["total_evenements"] == 3
        assert result["jours_libres"] == 5  # 7 - 2 jours avec events
        assert result["jour_plus_charge"] is not None
        assert result["jour_plus_charge"][1] == 2  # Lundi a 2 events

    def test_detecter_conflits_horaires_vide(self):
        """Test detection conflits liste vide."""
        result = detecter_conflits_horaires([])
        assert result == []

    def test_detecter_conflits_horaires_pas_conflit(self):
        """Test sans conflits."""
        jour = date(2024, 1, 15)
        evenements = [
            {"date": jour.isoformat(), "heure": time(9, 0), "duree": 60},
            {"date": jour.isoformat(), "heure": time(11, 0), "duree": 60},
        ]

        result = detecter_conflits_horaires(evenements)

        assert len(result) == 0

    def test_detecter_conflits_horaires_conflit(self):
        """Test avec conflit detecte."""
        jour = date(2024, 1, 15)
        evenements = [
            {"date": jour.isoformat(), "heure": time(9, 0), "duree": 120},  # 9h-11h
            {"date": jour.isoformat(), "heure": time(10, 0), "duree": 60},  # 10h-11h (conflit!)
        ]

        result = detecter_conflits_horaires(evenements)

        assert len(result) == 1

    def test_detecter_conflits_horaires_sans_heure(self):
        """Test evenements sans heure ignores."""
        jour = date(2024, 1, 15)
        evenements = [
            {"date": jour.isoformat(), "heure": None},
            {"date": jour.isoformat(), "heure": time(10, 0)},
        ]

        result = detecter_conflits_horaires(evenements)

        assert len(result) == 0

    def test_detecter_conflits_horaires_heure_string(self):
        """Test avec heures string."""
        jour = date(2024, 1, 15)
        evenements = [
            {"date": jour.isoformat(), "heure": "2024-01-15T09:00:00", "duree": 120},
            {"date": jour.isoformat(), "heure": "2024-01-15T10:00:00", "duree": 60},
        ]

        result = detecter_conflits_horaires(evenements)

        assert len(result) == 1


# ═══════════════════════════════════════════════════════════
# TESTS TEMPS LIBRE ET STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestTempsLibreStatistiques:
    """Tests pour calcul temps libre et statistiques."""

    def test_calculer_temps_libre_vide(self):
        """Test temps libre sans evenements."""
        result = calculer_temps_libre([])

        assert len(result) == 7
        # Chaque jour a 960 min (16h de veille)
        for _jour, temps in result.items():
            assert temps == 960

    def test_calculer_temps_libre_avec_evenements(self):
        """Test temps libre avec evenements."""
        aujourd_hui = date.today()
        lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())

        evenements = [
            {"date": lundi.isoformat(), "duree": 60},  # 1h
            {"date": lundi.isoformat(), "duree": 120},  # 2h
        ]

        result = calculer_temps_libre(evenements, aujourd_hui)

        # Lundi: 960 - 60 - 120 = 780 min
        assert result[lundi] == 780

    def test_calculer_statistiques_semaine_vide(self):
        """Test statistiques semaine vide."""
        result = calculer_statistiques_semaine([])

        assert result["total"] == 0
        assert result["par_type"] == {}
        assert result["duree_totale"] == 0
        assert result["duree_moyenne"] == 0

    def test_calculer_statistiques_semaine_avec_evenements(self):
        """Test statistiques avec evenements."""
        aujourd_hui = date.today()
        lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())

        evenements = [
            {"date": lundi.isoformat(), "type": "reunion", "duree": 60},
            {"date": lundi.isoformat(), "type": "reunion", "duree": 90},
            {"date": (lundi + timedelta(days=1)).isoformat(), "type": "formation", "duree": 120},
        ]

        result = calculer_statistiques_semaine(evenements, aujourd_hui)

        assert result["total"] == 3
        assert result["par_type"]["reunion"] == 2
        assert result["par_type"]["formation"] == 1
        assert result["duree_totale"] == 270  # 60 + 90 + 120
        assert result["duree_moyenne"] == 90  # 270 / 3


# ═══════════════════════════════════════════════════════════
# TESTS SUGGESTIONS CRENEAUX
# ═══════════════════════════════════════════════════════════


class TestSuggererCreneaux:
    """Tests pour suggerer_creneaux_libres."""

    def test_suggerer_creneaux_jour_vide(self):
        """Test suggestions jour vide."""
        jour = date(2024, 1, 15)
        result = suggerer_creneaux_libres([], jour, duree_minutes=60)

        # Tout le jour 8h-20h est libre (720 min)
        assert len(result) == 1
        assert result[0]["debut"] == time(8, 0)
        assert result[0]["fin"] == time(20, 0)
        assert result[0]["duree"] == 720

    def test_suggerer_creneaux_avec_evenements(self):
        """Test suggestions avec evenements."""
        jour = date(2024, 1, 15)
        evenements = [
            {"date": jour.isoformat(), "heure": time(10, 0), "duree": 60},  # 10h-11h
            {"date": jour.isoformat(), "heure": time(14, 0), "duree": 120},  # 14h-16h
        ]

        result = suggerer_creneaux_libres(evenements, jour, duree_minutes=60)

        # Creneaux: 8h-10h (120min), 11h-14h (180min), 16h-20h (240min)
        assert len(result) == 3

    def test_suggerer_creneaux_aucun_suffisant(self):
        """Test quand aucun creneau suffisant."""
        jour = date(2024, 1, 15)
        # Remplir toute la journee
        evenements = [
            {"date": jour.isoformat(), "heure": time(8, 0), "duree": 720},  # 8h-20h
        ]

        result = suggerer_creneaux_libres(evenements, jour, duree_minutes=60)

        assert len(result) == 0

    def test_suggerer_creneaux_evenement_sans_heure(self):
        """Test evenements sans heure ignores."""
        jour = date(2024, 1, 15)
        evenements = [
            {"date": jour.isoformat(), "heure": None},
        ]

        result = suggerer_creneaux_libres(evenements, jour, duree_minutes=60)

        # Journee libre
        assert len(result) == 1

    def test_suggerer_creneaux_heure_string(self):
        """Test avec heures string."""
        jour = date(2024, 1, 15)
        evenements = [
            {"date": jour.isoformat(), "heure": "2024-01-15T10:00:00", "duree": 60},
        ]

        result = suggerer_creneaux_libres(evenements, jour, duree_minutes=60)

        # 8h-10h et 11h-20h
        assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# TESTS FORMATAGE
# ═══════════════════════════════════════════════════════════


class TestFormatage:
    """Tests pour fonctions de formatage."""

    def test_formater_periode_semaine_defaults(self):
        """Test formatage periode sans argument."""
        result = formater_periode_semaine()

        assert "Semaine" in result
        assert "/" in result  # Format date

    def test_formater_periode_semaine_date_specifiee(self):
        """Test formatage periode avec date."""
        result = formater_periode_semaine(date(2024, 1, 17))

        assert "Semaine 3" in result
        assert "15/01" in result  # Lundi
        assert "21/01/2024" in result  # Dimanche

    def test_formater_heure_time_objet(self):
        """Test formatage heure avec time objet."""
        result = formater_heure(time(14, 30))

        assert result == "14:30"

    def test_formater_heure_string(self):
        """Test formatage heure avec string."""
        result = formater_heure("2024-01-15T14:30:00")

        assert result == "14:30"

    def test_formater_heure_minuit(self):
        """Test formatage minuit."""
        result = formater_heure(time(0, 0))

        assert result == "00:00"


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests pour cas limites."""

    def test_filtrer_tous_evenements_hors_semaine(self):
        """Test filtrage quand tous hors semaine."""
        aujourd_hui = date.today()
        mois_prochain = aujourd_hui + timedelta(days=60)

        evenements = [{"date": mois_prochain.isoformat()}]

        result = filtrer_evenements_semaine(evenements, aujourd_hui)

        assert len(result) == 0

    def test_grouper_evenements_un_seul_jour(self):
        """Test groupement un seul jour."""
        jour = date(2024, 1, 15)
        evenements = [
            {"date": jour.isoformat()},
            {"date": jour.isoformat()},
            {"date": jour.isoformat()},
        ]

        result = grouper_evenements_par_jour(evenements)

        assert len(result) == 1
        assert len(result[jour]) == 3

    def test_conflit_meme_heure_exacte(self):
        """Test conflit a exactement la meme heure."""
        jour = date(2024, 1, 15)
        evenements = [
            {"date": jour.isoformat(), "heure": time(10, 0), "duree": 60},
            {"date": jour.isoformat(), "heure": time(10, 0), "duree": 60},
        ]

        result = detecter_conflits_horaires(evenements)

        assert len(result) == 1

    def test_pas_conflit_consecutif(self):
        """Test pas de conflit pour evenements consecutifs."""
        jour = date(2024, 1, 15)
        evenements = [
            {"date": jour.isoformat(), "heure": time(10, 0), "duree": 60},  # 10h-11h
            {"date": jour.isoformat(), "heure": time(11, 0), "duree": 60},  # 11h-12h
        ]

        result = detecter_conflits_horaires(evenements)

        assert len(result) == 0

    def test_temps_libre_negatif_protection(self):
        """Test protection contre temps libre negatif."""
        aujourd_hui = date.today()
        lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())

        # Plus de duree que possible dans une journee
        evenements = [{"date": lundi.isoformat(), "duree": 2000}]

        result = calculer_temps_libre(evenements, aujourd_hui)

        # Ne doit pas etre negatif
        assert result[lundi] == 0
