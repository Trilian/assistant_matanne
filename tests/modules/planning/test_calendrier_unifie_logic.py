"""
Tests pour calendrier_unifie_logic.py - Module Planning
Couverture cible: 80%+
"""

from datetime import date, time, timedelta

import pytest

from src.modules.planning.calendrier_unifie.utils import (
    COULEUR_TYPE,
    EMOJI_TYPE,
    JOURS_SEMAINE,
    JOURS_SEMAINE_COURT,
    # Dataclasses
    EvenementCalendrier,
    JourCalendrier,
    SemaineCalendrier,
    TypeEvenement,
    # Fonctions de calcul
    get_debut_semaine,
    get_jours_semaine,
    get_semaine_precedente,
    get_semaine_suivante,
)

# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantesCalendrier:
    """Tests des constantes."""

    def test_jours_semaine_complet(self):
        """7 jours de la semaine."""
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"
        assert JOURS_SEMAINE[6] == "Dimanche"

    def test_jours_semaine_court(self):
        """Abréviations des jours."""
        assert len(JOURS_SEMAINE_COURT) == 7
        assert JOURS_SEMAINE_COURT[0] == "Lun"
        assert JOURS_SEMAINE_COURT[6] == "Dim"

    def test_type_evenement_values(self):
        """Types d'événements définis."""
        assert TypeEvenement.REPAS_MIDI.value == "repas_midi"
        assert TypeEvenement.REPAS_SOIR.value == "repas_soir"
        assert TypeEvenement.BATCH_COOKING.value == "batch_cooking"
        assert TypeEvenement.COURSES.value == "courses"

    def test_emoji_type_complet(self):
        """Emojis pour chaque type."""
        for evt_type in TypeEvenement:
            assert evt_type in EMOJI_TYPE

    def test_couleur_type_complet(self):
        """Couleurs pour chaque type."""
        for evt_type in TypeEvenement:
            assert evt_type in COULEUR_TYPE
            # Couleurs en format hex
            assert COULEUR_TYPE[evt_type].startswith("#")


# ═══════════════════════════════════════════════════════════
# TESTS EVENEMENT CALENDRIER
# ═══════════════════════════════════════════════════════════


class TestEvenementCalendrier:
    """Tests de la dataclass EvenementCalendrier."""

    def test_creation_evenement_minimal(self):
        """Création avec paramètres minimaux."""
        evt = EvenementCalendrier(
            id="repas_midi_1",
            type=TypeEvenement.REPAS_MIDI,
            titre="Poulet rôti",
            date_jour=date.today(),
        )

        assert evt.id == "repas_midi_1"
        assert evt.type == TypeEvenement.REPAS_MIDI
        assert evt.titre == "Poulet rôti"
        assert evt.date_jour == date.today()

    def test_creation_evenement_complet(self):
        """Création avec tous les paramètres."""
        evt = EvenementCalendrier(
            id="activite_1",
            type=TypeEvenement.ACTIVITE,
            titre="Parc",
            date_jour=date.today(),
            heure_debut=time(10, 0),
            heure_fin=time(12, 0),
            description="Sortie au parc",
            lieu="Parc municipal",
            participants=["Jules", "Papa", "Maman"],
            pour_jules=True,
            budget=5.0,
            notes="Prévoir goûter",
        )

        assert evt.lieu == "Parc municipal"
        assert len(evt.participants) == 3
        assert evt.pour_jules is True
        assert evt.budget == 5.0

    def test_emoji_property(self):
        """Property emoji."""
        evt = EvenementCalendrier(
            id="test", type=TypeEvenement.BATCH_COOKING, titre="Test", date_jour=date.today()
        )
        assert evt.emoji == EMOJI_TYPE[TypeEvenement.BATCH_COOKING]
        assert evt.emoji == "🍳"

    def test_couleur_property(self):
        """Property couleur."""
        evt = EvenementCalendrier(
            id="test", type=TypeEvenement.COURSES, titre="Test", date_jour=date.today()
        )
        assert evt.couleur == COULEUR_TYPE[TypeEvenement.COURSES]

    def test_heure_str_property(self):
        """Property heure_str."""
        evt = EvenementCalendrier(
            id="test",
            type=TypeEvenement.RDV_MEDICAL,
            titre="Test",
            date_jour=date.today(),
            heure_debut=time(14, 30),
        )
        assert evt.heure_str == "14:30"

    def test_heure_str_none(self):
        """heure_str quand pas d'heure."""
        evt = EvenementCalendrier(
            id="test", type=TypeEvenement.ACTIVITE, titre="Test", date_jour=date.today()
        )
        assert evt.heure_str == ""


# ═══════════════════════════════════════════════════════════
# TESTS JOUR CALENDRIER
# ═══════════════════════════════════════════════════════════


class TestJourCalendrier:
    """Tests de la dataclass JourCalendrier."""

    @pytest.fixture
    def jour_avec_evenements(self):
        """Jour avec plusieurs événements."""
        return JourCalendrier(
            date_jour=date.today(),
            evenements=[
                EvenementCalendrier(
                    id="repas_midi_1",
                    type=TypeEvenement.REPAS_MIDI,
                    titre="Pâtes carbonara",
                    date_jour=date.today(),
                ),
                EvenementCalendrier(
                    id="repas_soir_1",
                    type=TypeEvenement.REPAS_SOIR,
                    titre="Salade composée",
                    date_jour=date.today(),
                ),
                EvenementCalendrier(
                    id="activite_1",
                    type=TypeEvenement.ACTIVITE,
                    titre="Parc",
                    date_jour=date.today(),
                ),
                EvenementCalendrier(
                    id="courses_1",
                    type=TypeEvenement.COURSES,
                    titre="Courses Carrefour",
                    date_jour=date.today(),
                ),
                EvenementCalendrier(
                    id="menage_1",
                    type=TypeEvenement.MENAGE,
                    titre="Ménage cuisine",
                    date_jour=date.today(),
                ),
            ],
        )

    def test_creation_jour_vide(self):
        """Création d'un jour vide."""
        jour = JourCalendrier(date_jour=date.today())
        assert jour.date_jour == date.today()
        assert len(jour.evenements) == 0

    def test_est_aujourdhui(self):
        """Property est_aujourdhui."""
        jour_aujourd = JourCalendrier(date_jour=date.today())
        jour_demain = JourCalendrier(date_jour=date.today() + timedelta(days=1))

        assert jour_aujourd.est_aujourdhui is True
        assert jour_demain.est_aujourdhui is False

    def test_jour_semaine(self):
        """Property jour_semaine."""
        # Le 2 janvier 2024 était un mardi
        jour = JourCalendrier(date_jour=date(2024, 1, 2))
        assert jour.jour_semaine == "Mardi"

    def test_jour_semaine_court(self):
        """Property jour_semaine_court."""
        jour = JourCalendrier(date_jour=date(2024, 1, 2))
        assert jour.jour_semaine_court == "Mar"

    def test_repas_midi(self, jour_avec_evenements):
        """Property repas_midi."""
        assert jour_avec_evenements.repas_midi is not None
        assert jour_avec_evenements.repas_midi.titre == "Pâtes carbonara"

    def test_repas_soir(self, jour_avec_evenements):
        """Property repas_soir."""
        assert jour_avec_evenements.repas_soir is not None
        assert jour_avec_evenements.repas_soir.titre == "Salade composée"

    def test_courses(self, jour_avec_evenements):
        """Property courses."""
        courses = jour_avec_evenements.courses
        assert len(courses) == 1
        assert courses[0].titre == "Courses Carrefour"

    def test_activites(self, jour_avec_evenements):
        """Property activites."""
        activites = jour_avec_evenements.activites
        assert len(activites) == 1
        assert activites[0].titre == "Parc"

    def test_taches_menage(self, jour_avec_evenements):
        """Property taches_menage."""
        taches = jour_avec_evenements.taches_menage
        assert len(taches) == 1

    def test_nb_evenements(self, jour_avec_evenements):
        """Property nb_evenements."""
        assert jour_avec_evenements.nb_evenements == 5

    def test_est_vide(self):
        """Property est_vide."""
        jour_vide = JourCalendrier(date_jour=date.today())
        jour_avec = JourCalendrier(
            date_jour=date.today(),
            evenements=[
                EvenementCalendrier(
                    id="test", type=TypeEvenement.ACTIVITE, titre="Test", date_jour=date.today()
                )
            ],
        )

        assert jour_vide.est_vide is True
        assert jour_avec.est_vide is False

    def test_a_repas_planifies(self, jour_avec_evenements):
        """Property a_repas_planifies."""
        assert jour_avec_evenements.a_repas_planifies is True

        jour_sans_repas = JourCalendrier(date_jour=date.today())
        assert jour_sans_repas.a_repas_planifies is False


# ═══════════════════════════════════════════════════════════
# TESTS SEMAINE CALENDRIER
# ═══════════════════════════════════════════════════════════


class TestSemaineCalendrier:
    """Tests de la dataclass SemaineCalendrier."""

    @pytest.fixture
    def semaine_sample(self):
        """Semaine avec quelques jours remplis."""
        lundi = date(2024, 1, 1)  # Lundi 1er janvier 2024
        jours = []

        for i in range(7):
            jour_date = lundi + timedelta(days=i)
            evenements = []

            # Repas midi tous les jours
            evenements.append(
                EvenementCalendrier(
                    id=f"repas_midi_{i}",
                    type=TypeEvenement.REPAS_MIDI,
                    titre=f"Déjeuner {i + 1}",
                    date_jour=jour_date,
                )
            )

            # Dîner seulement certains jours
            if i in [0, 2, 4, 6]:
                evenements.append(
                    EvenementCalendrier(
                        id=f"repas_soir_{i}",
                        type=TypeEvenement.REPAS_SOIR,
                        titre=f"Dîner {i + 1}",
                        date_jour=jour_date,
                    )
                )

            # Batch cooking le dimanche
            if i == 6:
                evenements.append(
                    EvenementCalendrier(
                        id="batch_1",
                        type=TypeEvenement.BATCH_COOKING,
                        titre="Batch cooking",
                        date_jour=jour_date,
                    )
                )

            jours.append(JourCalendrier(date_jour=jour_date, evenements=evenements))

        return SemaineCalendrier(date_debut=lundi, jours=jours)

    def test_creation_semaine(self, semaine_sample):
        """Création d'une semaine."""
        assert semaine_sample.date_debut == date(2024, 1, 1)
        assert len(semaine_sample.jours) == 7

    def test_date_fin(self, semaine_sample):
        """Property date_fin."""
        assert semaine_sample.date_fin == date(2024, 1, 7)  # Dimanche

    def test_titre(self, semaine_sample):
        """Property titre."""
        titre = semaine_sample.titre
        assert "01/01" in titre
        assert "07/01" in titre

    def test_nb_repas_planifies(self, semaine_sample):
        """Property nb_repas_planifies."""
        # 7 midis + 4 soirs = 11 repas
        assert semaine_sample.nb_repas_planifies == 11

    def test_nb_sessions_batch(self, semaine_sample):
        """Property nb_sessions_batch."""
        assert semaine_sample.nb_sessions_batch == 1


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS DE CALCUL
# ═══════════════════════════════════════════════════════════


class TestFonctionsCalcul:
    """Tests des fonctions de calcul de dates."""

    def test_get_debut_semaine_lundi(self):
        """Début de semaine pour un lundi = ce lundi."""
        lundi = date(2024, 1, 1)  # Lundi
        assert get_debut_semaine(lundi) == lundi

    def test_get_debut_semaine_mercredi(self):
        """Début de semaine pour un mercredi = le lundi précédent."""
        mercredi = date(2024, 1, 3)  # Mercredi
        assert get_debut_semaine(mercredi) == date(2024, 1, 1)  # Lundi

    def test_get_debut_semaine_dimanche(self):
        """Début de semaine pour un dimanche = le lundi précédent."""
        dimanche = date(2024, 1, 7)  # Dimanche
        assert get_debut_semaine(dimanche) == date(2024, 1, 1)

    def test_get_jours_semaine(self):
        """Liste des 7 jours."""
        lundi = date(2024, 1, 1)
        jours = get_jours_semaine(lundi)

        assert len(jours) == 7
        assert jours[0] == lundi  # Lundi
        assert jours[6] == date(2024, 1, 7)  # Dimanche

    def test_get_jours_semaine_depuis_mercredi(self):
        """Liste des jours depuis un mercredi = commence au lundi."""
        mercredi = date(2024, 1, 3)
        jours = get_jours_semaine(mercredi)

        assert jours[0] == date(2024, 1, 1)  # Lundi

    def test_get_semaine_precedente(self):
        """Semaine précédente."""
        lundi = date(2024, 1, 8)
        precedente = get_semaine_precedente(lundi)

        assert precedente == date(2024, 1, 1)

    def test_get_semaine_suivante(self):
        """Semaine suivante."""
        lundi = date(2024, 1, 1)
        suivante = get_semaine_suivante(lundi)

        assert suivante == date(2024, 1, 8)

    def test_navigation_semaines_coherente(self):
        """Navigation avant/arrière cohérente."""
        lundi = date(2024, 1, 15)

        # Aller à la semaine précédente puis suivante = retour à l'origine
        precedente = get_semaine_precedente(lundi)
        retour = get_semaine_suivante(precedente)

        assert retour == lundi
