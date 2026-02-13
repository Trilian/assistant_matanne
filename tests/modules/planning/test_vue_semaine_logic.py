"""
Tests pour vue_semaine_logic.py - Module Planning
Couverture cible: 80%+
"""

from datetime import date, time

import pytest

from src.modules.planning.vue_semaine_utils import (
    HEURES_JOURNEE,
    # Constantes
    JOURS_SEMAINE,
    # Analyse
    calculer_charge_semaine,
    detecter_conflits_horaires,
    filtrer_evenements_jour,
    # Filtrage
    filtrer_evenements_semaine,
    # Navigation
    get_debut_semaine,
    get_fin_semaine,
    get_jours_semaine,
    get_numero_semaine,
    get_semaine_precedente,
    get_semaine_suivante,
    grouper_evenements_par_jour,
    trier_evenements_par_heure,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def date_lundi():
    """Un lundi connu (6 janvier 2025)."""
    return date(2025, 1, 6)  # C'est un lundi


@pytest.fixture
def date_mercredi():
    """Un mercredi connu."""
    return date(2025, 1, 8)


@pytest.fixture
def evenements_semaine():
    """Événements de test sur une semaine."""
    return [
        {"id": 1, "titre": "Réunion", "date": date(2025, 1, 6), "heure": time(9, 0), "duree": 60},
        {"id": 2, "titre": "Déjeuner", "date": date(2025, 1, 6), "heure": time(12, 0), "duree": 60},
        {"id": 3, "titre": "Sport", "date": date(2025, 1, 7), "heure": time(18, 0), "duree": 90},
        {"id": 4, "titre": "Médecin", "date": date(2025, 1, 8), "heure": time(14, 30), "duree": 30},
        {
            "id": 5,
            "titre": "Shopping",
            "date": date(2025, 1, 11),
            "heure": time(10, 0),
            "duree": 120,
        },
    ]


@pytest.fixture
def evenements_conflits():
    """Événements avec conflits horaires."""
    return [
        {"id": 1, "titre": "Réunion A", "date": date(2025, 1, 6), "heure": time(9, 0), "duree": 60},
        {
            "id": 2,
            "titre": "Réunion B",
            "date": date(2025, 1, 6),
            "heure": time(9, 30),
            "duree": 30,
        },  # Conflit avec A
        {
            "id": 3,
            "titre": "Déjeuner",
            "date": date(2025, 1, 6),
            "heure": time(12, 0),
            "duree": 60,
        },  # Pas de conflit
    ]


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes."""

    def test_jours_semaine_complet(self):
        """7 jours dans la semaine."""
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"
        assert JOURS_SEMAINE[-1] == "Dimanche"

    def test_heures_journee(self):
        """24 heures dans une journée."""
        assert len(HEURES_JOURNEE) == 24
        assert HEURES_JOURNEE[0] == 0
        assert HEURES_JOURNEE[-1] == 23


# ═══════════════════════════════════════════════════════════
# TESTS NAVIGATION
# ═══════════════════════════════════════════════════════════


class TestNavigation:
    """Tests pour les fonctions de navigation."""

    def test_get_debut_semaine_lundi(self, date_lundi):
        """Lundi = début de semaine."""
        debut = get_debut_semaine(date_lundi)
        assert debut == date_lundi
        assert debut.weekday() == 0  # Lundi

    def test_get_debut_semaine_mercredi(self, date_mercredi):
        """Mercredi -> retourne le lundi."""
        debut = get_debut_semaine(date_mercredi)
        assert debut == date(2025, 1, 6)
        assert debut.weekday() == 0

    def test_get_debut_semaine_default(self):
        """Par défaut, utilise today()."""
        debut = get_debut_semaine()
        assert debut.weekday() == 0  # Toujours un lundi

    def test_get_fin_semaine(self, date_lundi):
        """Fin de semaine = dimanche."""
        fin = get_fin_semaine(date_lundi)
        assert fin == date(2025, 1, 12)
        assert fin.weekday() == 6  # Dimanche

    def test_get_jours_semaine(self, date_lundi):
        """Retourne 7 jours."""
        jours = get_jours_semaine(date_lundi)
        assert len(jours) == 7
        assert jours[0] == date_lundi
        assert jours[-1] == date(2025, 1, 12)

    def test_get_semaine_precedente(self, date_lundi):
        """Semaine précédente = -7 jours."""
        precedente = get_semaine_precedente(date_lundi)
        assert precedente == date(2024, 12, 30)

    def test_get_semaine_suivante(self, date_lundi):
        """Semaine suivante = +7 jours."""
        suivante = get_semaine_suivante(date_lundi)
        assert suivante == date(2025, 1, 13)

    def test_get_numero_semaine(self, date_lundi):
        """Numéro de semaine dans l'année."""
        num = get_numero_semaine(date_lundi)
        assert num == 2  # 6 janvier 2025 est en semaine 2


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE
# ═══════════════════════════════════════════════════════════


class TestFiltrage:
    """Tests pour les fonctions de filtrage."""

    def test_filtrer_evenements_semaine(self, evenements_semaine, date_lundi):
        """Filtre les événements de la semaine."""
        resultat = filtrer_evenements_semaine(evenements_semaine, date_lundi)
        assert len(resultat) == 5  # Tous sont dans la semaine du 6-12 janvier

    def test_filtrer_evenements_semaine_exclut_autre_semaine(self, date_lundi):
        """N'inclut pas les événements d'une autre semaine."""
        evenements = [
            {"id": 1, "titre": "Cette semaine", "date": date(2025, 1, 6)},
            {"id": 2, "titre": "Autre semaine", "date": date(2025, 1, 20)},
        ]
        resultat = filtrer_evenements_semaine(evenements, date_lundi)
        assert len(resultat) == 1
        assert resultat[0]["titre"] == "Cette semaine"

    def test_filtrer_evenements_semaine_date_string(self, date_lundi):
        """Supporte les dates en format string."""
        evenements = [
            {"id": 1, "titre": "Test", "date": "2025-01-06"},
        ]
        resultat = filtrer_evenements_semaine(evenements, date_lundi)
        assert len(resultat) == 1

    def test_filtrer_evenements_jour(self, evenements_semaine, date_lundi):
        """Filtre les événements d'un jour."""
        resultat = filtrer_evenements_jour(evenements_semaine, date_lundi)
        assert len(resultat) == 2  # Réunion et Déjeuner

    def test_grouper_evenements_par_jour(self, evenements_semaine):
        """Groupe les événements par jour."""
        groupes = grouper_evenements_par_jour(evenements_semaine)
        assert len(groupes) == 4  # 4 jours différents
        assert len(groupes[date(2025, 1, 6)]) == 2

    def test_trier_evenements_par_heure(self):
        """Trie par heure."""
        evenements = [
            {"titre": "Tard", "heure": time(18, 0)},
            {"titre": "Tôt", "heure": time(8, 0)},
            {"titre": "Midi", "heure": time(12, 0)},
        ]
        tries = trier_evenements_par_heure(evenements)
        assert tries[0]["titre"] == "Tôt"
        assert tries[1]["titre"] == "Midi"
        assert tries[2]["titre"] == "Tard"

    def test_trier_evenements_sans_heure(self):
        """Événements sans heure au début."""
        evenements = [
            {"titre": "Avec heure", "heure": time(10, 0)},
            {"titre": "Sans heure", "heure": None},
        ]
        tries = trier_evenements_par_heure(evenements)
        assert tries[0]["titre"] == "Sans heure"


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSE
# ═══════════════════════════════════════════════════════════


class TestAnalyse:
    """Tests pour les fonctions d'analyse."""

    def test_calculer_charge_semaine(self, evenements_semaine, date_lundi):
        """Calcule la charge de la semaine."""
        charge = calculer_charge_semaine(evenements_semaine, date_lundi)
        assert charge["total_evenements"] == 5
        assert charge["jours_libres"] == 3  # Jeudi, Vendredi, Dimanche
        assert charge["charge_moyenne"] == pytest.approx(5 / 7)

    def test_calculer_charge_semaine_jour_plus_charge(self, evenements_semaine, date_lundi):
        """Identifie le jour le plus chargé."""
        charge = calculer_charge_semaine(evenements_semaine, date_lundi)
        jour_charge, nb = charge["jour_plus_charge"]
        assert jour_charge == date(2025, 1, 6)  # Lundi avec 2 événements
        assert nb == 2

    def test_detecter_conflits_horaires(self, evenements_conflits):
        """Détecte les conflits."""
        conflits = detecter_conflits_horaires(evenements_conflits)
        assert len(conflits) == 1
        evt1, evt2 = conflits[0]
        assert evt1["titre"] == "Réunion A"
        assert evt2["titre"] == "Réunion B"

    def test_detecter_conflits_pas_de_conflit(self, evenements_semaine):
        """Pas de conflits dans les données normales."""
        conflits = detecter_conflits_horaires(evenements_semaine)
        assert len(conflits) == 0

    def test_detecter_conflits_sans_heure(self):
        """Ignore les événements sans heure."""
        evenements = [
            {"titre": "Sans heure", "date": date(2025, 1, 6), "heure": None},
            {"titre": "Avec heure", "date": date(2025, 1, 6), "heure": time(10, 0)},
        ]
        conflits = detecter_conflits_horaires(evenements)
        assert len(conflits) == 0
