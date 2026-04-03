"""
Tests pour src/services/planning/suggestions.py

Couverture: créneaux libres, scoring, suggestions IA.
"""

from datetime import date, time, timedelta
from types import SimpleNamespace

import pytest

from src.services.planning.suggestions import (
    DUREE_MIN_CRENEAU,
    HEURE_DEBUT_JOURNEE,
    HEURE_FIN_JOURNEE,
    SEUIL_CHARGE_BASSE,
    SEUIL_CHARGE_HAUTE,
    CreneauLibre,
    ServiceSuggestions,
    SuggestionPlanning,
)

# ═══════════════════════════════════════════════════════════
# HELPERS — Mock JourCalendrier léger
# ═══════════════════════════════════════════════════════════


def _jour(
    d: date,
    events: list[dict] | None = None,
    charge: int = 30,
    repas_midi: bool = False,
    repas_soir: bool = False,
    batch: bool = False,
):
    """Crée un objet jour simulé pour les tests."""
    evts = []
    for e in events or []:
        evts.append(
            SimpleNamespace(
                titre=e.get("titre", ""),
                heure_debut=e.get("heure_debut"),
                heure_fin=e.get("heure_fin"),
                type=e.get("type", "autre"),
                pour_jules=e.get("pour_jules", False),
            )
        )

    return SimpleNamespace(
        date_jour=d,
        jour_semaine=["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][
            d.weekday()
        ],
        evenements=evts,
        charge_score=charge,
        repas_midi=repas_midi,
        repas_soir=repas_soir,
        batch_cooking=batch,
        jours_speciaux=[],
    )


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class TestCreneauLibre:
    def test_creation(self):
        c = CreneauLibre(
            date_jour=date(2026, 3, 1),
            heure_debut=time(10, 0),
            heure_fin=time(12, 0),
            duree_minutes=120,
            score_qualite=80,
            raison="matinée idéale",
        )
        assert c.duree_minutes == 120
        assert c.score_qualite == 80

    def test_duree_str_heures(self):
        c = CreneauLibre(date.today(), time(10, 0), time(12, 0), 120, 50)
        assert c.duree_str == "2h"

    def test_duree_str_heures_minutes(self):
        c = CreneauLibre(date.today(), time(10, 0), time(11, 30), 90, 50)
        assert c.duree_str == "1h30"

    def test_duree_str_minutes(self):
        c = CreneauLibre(date.today(), time(10, 0), time(10, 45), 45, 50)
        assert c.duree_str == "45min"

    def test_horaire_str(self):
        c = CreneauLibre(date.today(), time(10, 0), time(12, 0), 120, 50)
        assert c.horaire_str == "10:00–12:00"


class TestSuggestionPlanning:
    def test_creation(self):
        s = SuggestionPlanning(
            titre="Test",
            description="Description",
            priorite=4,
            categories=["test"],
        )
        assert s.priorite == 4

    def test_emoji_priorite(self):
        assert SuggestionPlanning("", "", 5).emoji_priorite == "🔴"
        assert SuggestionPlanning("", "", 4).emoji_priorite == "🟠"
        assert SuggestionPlanning("", "", 3).emoji_priorite == "🟡"
        assert SuggestionPlanning("", "", 2).emoji_priorite == "🟢"
        assert SuggestionPlanning("", "", 1).emoji_priorite == "🔵"


# ═══════════════════════════════════════════════════════════
# SERVICE — CRÉNEAUX LIBRES
# ═══════════════════════════════════════════════════════════


class TestServiceCreneaux:
    """Tests de l'identification des créneaux libres."""

    @pytest.fixture
    def service(self):
        return ServiceSuggestions()

    def test_jour_vide_creneau_complet(self, service):
        """Un jour sans événement = un grand créneau libre."""
        jour = _jour(date(2026, 3, 2))  # Lundi
        creneaux = service.creneaux_libres([jour])
        assert len(creneaux) >= 1
        # La durée totale devrait couvrir toute la journée
        duree_totale = sum(c.duree_minutes for c in creneaux)
        journee_min = (HEURE_FIN_JOURNEE.hour - HEURE_DEBUT_JOURNEE.hour) * 60
        assert duree_totale == journee_min

    def test_jour_plein_pas_de_creneau(self, service):
        """Jour rempli → pas de créneau libre > duree_min."""
        # Remplir toutes les heures de 7h à 21h
        events = []
        for h in range(7, 21):
            events.append(
                {
                    "titre": f"Evt {h}h",
                    "heure_debut": time(h, 0),
                    "heure_fin": time(h + 1, 0),
                }
            )
        jour = _jour(date(2026, 3, 2), events=events, charge=90)
        creneaux = service.creneaux_libres([jour], duree_min=30)
        assert len(creneaux) == 0

    def test_creneau_entre_events(self, service):
        """Un trou entre deux événements est identifié."""
        events = [
            {"titre": "A", "heure_debut": time(9, 0), "heure_fin": time(10, 0)},
            {"titre": "B", "heure_debut": time(12, 0), "heure_fin": time(13, 0)},
        ]
        jour = _jour(date(2026, 3, 2), events=events)
        creneaux = service.creneaux_libres([jour])

        # Devrait y avoir un créneau entre 10h et 12h
        creneaux_10_12 = [
            c for c in creneaux if c.heure_debut >= time(10, 0) and c.heure_fin <= time(12, 0)
        ]
        assert len(creneaux_10_12) >= 1
        assert creneaux_10_12[0].duree_minutes == 120

    def test_duree_min_filtre(self, service):
        """Petits trous sous le seuil minimum ne sont pas inclus."""
        events = [
            {"titre": "A", "heure_debut": time(10, 0), "heure_fin": time(10, 50)},
            {"titre": "B", "heure_debut": time(11, 0), "heure_fin": time(12, 0)},
        ]
        jour = _jour(date(2026, 3, 2), events=events)
        # Le trou de 10 minutes (10:50-11:00) ne devrait pas apparaître
        creneaux = service.creneaux_libres([jour], duree_min=30)
        creneaux_10min = [c for c in creneaux if c.duree_minutes == 10]
        assert len(creneaux_10min) == 0

    def test_score_qualite_range(self, service):
        """Tous les scores sont entre 0 et 100."""
        jour = _jour(date(2026, 3, 2))
        creneaux = service.creneaux_libres([jour])
        for c in creneaux:
            assert 0 <= c.score_qualite <= 100

    def test_tries_par_qualite(self, service):
        """Créneaux triés par score décroissant."""
        jours = [
            _jour(date(2026, 3, 2), charge=10),
            _jour(date(2026, 3, 3), charge=80),
        ]
        creneaux = service.creneaux_libres(jours)
        for i in range(len(creneaux) - 1):
            assert (
                creneaux[i].score_qualite >= creneaux[i + 1].score_qualite
                or creneaux[i].date_jour <= creneaux[i + 1].date_jour
            )

    def test_event_sans_heure_fin_estime_1h(self, service):
        """Événement sans heure de fin → estimé à 1h."""
        events = [
            {"titre": "A", "heure_debut": time(10, 0)},
        ]
        jour = _jour(date(2026, 3, 2), events=events)
        creneaux = service.creneaux_libres([jour])
        # Aucun créneau ne devrait recouvrir 10:00-11:00
        for c in creneaux:
            assert not (c.heure_debut < time(11, 0) and c.heure_fin > time(10, 0))


# ═══════════════════════════════════════════════════════════
# SERVICE — SUGGESTIONS
# ═══════════════════════════════════════════════════════════


class TestServiceSuggestions:
    """Tests des suggestions de planning."""

    @pytest.fixture
    def service(self):
        return ServiceSuggestions()

    def test_reequilibrage_suggestion(self, service):
        """Proposition de rééquilibrage jour chargé → jour vide."""
        jours = [
            _jour(date(2026, 3, 2), charge=80),  # Lundi chargé
            _jour(date(2026, 3, 3), charge=10),  # Mardi léger
        ]
        suggestions = service.suggestions_planning(jours)
        reequilibrages = [s for s in suggestions if "equilibrage" in s.categories]
        assert len(reequilibrages) >= 1

    def test_pas_reequilibrage_si_equilibre(self, service):
        """Pas de suggestion si tous les jours sont similaires."""
        jours = [
            _jour(date(2026, 3, 2), charge=40),
            _jour(date(2026, 3, 3), charge=45),
        ]
        suggestions = service.suggestions_planning(jours)
        reequilibrages = [s for s in suggestions if "equilibrage" in s.categories]
        assert len(reequilibrages) == 0

    def test_suggestion_repas_manquants(self, service):
        """Suggère de planifier les repas manquants."""
        jours = [_jour(date(2026, 3, 2 + i), repas_midi=False, repas_soir=False) for i in range(7)]
        suggestions = service.suggestions_planning(jours)
        repas = [s for s in suggestions if "repas" in s.categories]
        assert len(repas) >= 1

    def test_suggestion_batch_cooking(self, service):
        """Suggère du batch cooking si repas planifiés mais pas de batch."""
        jours = [
            _jour(date(2026, 3, 2 + i), repas_midi=True, repas_soir=True, batch=False)
            for i in range(7)
        ]
        suggestions = service.suggestions_planning(jours)
        batch = [s for s in suggestions if "batch" in s.categories]
        assert len(batch) >= 1

    def test_suggestion_activites_jules(self, service):
        """Suggère des activités Jules si peu présent."""
        jours = [_jour(date(2026, 3, 2 + i)) for i in range(7)]
        suggestions = service.suggestions_planning(jours)
        jules = [s for s in suggestions if "jules" in s.categories]
        assert len(jules) >= 1

    def test_suggestions_triees_par_priorite(self, service):
        """Suggestions triées par priorité décroissante."""
        jours = [
            _jour(date(2026, 3, 2), charge=80),
            _jour(date(2026, 3, 3), charge=10),
        ]
        suggestions = service.suggestions_planning(jours)
        for i in range(len(suggestions) - 1):
            assert suggestions[i].priorite >= suggestions[i + 1].priorite

    def test_suggestion_garde_creche_fermee(self, service):
        """Suggestion de garde quand crèche fermée."""
        jour = _jour(date(2026, 8, 3))
        # Simuler un jour spécial crèche
        jour.jours_speciaux = [SimpleNamespace(type="creche", titre="Crèche fermée (Été)")]
        suggestions = service.suggestions_planning([jour])
        garde = [s for s in suggestions if "garde" in s.categories]
        assert len(garde) >= 1


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    def test_heures_journee(self):
        assert HEURE_DEBUT_JOURNEE == time(7, 0)
        assert HEURE_FIN_JOURNEE == time(21, 0)

    def test_duree_min(self):
        assert DUREE_MIN_CRENEAU == 30

    def test_seuils_charge(self):
        assert SEUIL_CHARGE_HAUTE == 60
        assert SEUIL_CHARGE_BASSE == 20
