"""
Tests comprehensifs pour src/modules/planning/calendrier_unifie/utils.py
Objectif: Augmenter la couverture de 32.58% à 80%+
"""

from datetime import date, datetime, time, timedelta
from unittest.mock import Mock

import pytest

from src.modules.planning.calendrier_unifie.utils import (
    COULEUR_TYPE,
    EMOJI_TYPE,
    EvenementCalendrier,
    JourCalendrier,
    SemaineCalendrier,
    TypeEvenement,
    agreger_evenements_jour,
    construire_semaine_calendrier,
    convertir_activite_en_evenement,
    convertir_event_calendrier_en_evenement,
    convertir_repas_en_evenement,
    convertir_session_batch_en_evenement,
    convertir_tache_menage_en_evenement,
    creer_evenement_courses,
    generer_html_semaine_pour_impression,
    generer_taches_menage_semaine,
    generer_texte_semaine_pour_impression,
    get_jours_semaine,
    get_semaine_precedente,
    get_semaine_suivante,
)

# ═══════════════════════════════════════════════════════════
# TESTS TYPEEVENEMENT ENUM
# ═══════════════════════════════════════════════════════════


class TestTypeEvenement:
    """Tests pour l'enum TypeEvenement."""

    def test_tous_les_types_existent(self):
        """Verifie que tous les types attendus existent."""
        types_attendus = [
            "repas_midi",
            "repas_soir",
            "gouter",
            "batch_cooking",
            "courses",
            "activite",
            "rdv_medical",
            "rdv_autre",
            "routine",
            "menage",
            "jardin",
            "entretien",
            "evenement",
        ]
        for type_val in types_attendus:
            assert TypeEvenement(type_val) is not None

    def test_type_string_enum(self):
        """Verifie que TypeEvenement herite de str."""
        assert isinstance(TypeEvenement.REPAS_MIDI, str)
        assert TypeEvenement.REPAS_MIDI == "repas_midi"


# ═══════════════════════════════════════════════════════════
# TESTS EVENEMENTCALENDRIER DATACLASS
# ═══════════════════════════════════════════════════════════


class TestEvenementCalendrier:
    """Tests pour la dataclass EvenementCalendrier."""

    def test_creation_minimale(self):
        """Test de creation avec parametres minimaux."""
        evt = EvenementCalendrier(
            id="test_1", type=TypeEvenement.REPAS_MIDI, titre="Test repas", date_jour=date.today()
        )
        assert evt.id == "test_1"
        assert evt.type == TypeEvenement.REPAS_MIDI
        assert evt.titre == "Test repas"
        assert evt.participants == []
        assert evt.termine is False

    def test_creation_complete(self):
        """Test de creation avec tous les parametres."""
        evt = EvenementCalendrier(
            id="test_2",
            type=TypeEvenement.BATCH_COOKING,
            titre="Batch du dimanche",
            date_jour=date(2024, 1, 15),
            heure_debut=time(14, 0),
            heure_fin=time(17, 0),
            description="Preparation semaine",
            lieu="Cuisine",
            participants=["Alice", "Bob"],
            pour_jules=True,
            version_jules="Version adaptee",
            budget=50.0,
            magasin="Carrefour",
            recette_id=1,
            session_id=2,
            termine=True,
            notes="Notes importantes",
        )
        assert evt.heure_debut == time(14, 0)
        assert evt.budget == 50.0
        assert "Alice" in evt.participants
        assert evt.pour_jules is True

    def test_emoji_property(self):
        """Test de la property emoji."""
        for type_evt in TypeEvenement:
            evt = EvenementCalendrier(
                id=f"test_{type_evt.value}", type=type_evt, titre="Test", date_jour=date.today()
            )
            assert evt.emoji == EMOJI_TYPE.get(type_evt, "📝Œ")

    def test_couleur_property(self):
        """Test de la property couleur."""
        for type_evt in TypeEvenement:
            evt = EvenementCalendrier(
                id=f"test_{type_evt.value}", type=type_evt, titre="Test", date_jour=date.today()
            )
            assert evt.couleur == COULEUR_TYPE.get(type_evt, "#90A4AE")

    def test_heure_str_avec_heure(self):
        """Test de la property heure_str avec heure definie."""
        evt = EvenementCalendrier(
            id="test_1",
            type=TypeEvenement.ACTIVITE,
            titre="Activite",
            date_jour=date.today(),
            heure_debut=time(14, 30),
        )
        assert evt.heure_str == "14:30"

    def test_heure_str_sans_heure(self):
        """Test de la property heure_str sans heure."""
        evt = EvenementCalendrier(
            id="test_1", type=TypeEvenement.ACTIVITE, titre="Activite", date_jour=date.today()
        )
        assert evt.heure_str == ""


# ═══════════════════════════════════════════════════════════
# TESTS JOURCALENDRIER DATACLASS
# ═══════════════════════════════════════════════════════════


class TestJourCalendrier:
    """Tests pour la dataclass JourCalendrier."""

    @pytest.fixture
    def jour_avec_evenements(self):
        """Fixture: jour avec plusieurs types d'evenements."""
        evenements = [
            EvenementCalendrier(
                id="repas_1",
                type=TypeEvenement.REPAS_MIDI,
                titre="Dejeuner",
                date_jour=date.today(),
            ),
            EvenementCalendrier(
                id="repas_2", type=TypeEvenement.REPAS_SOIR, titre="Diner", date_jour=date.today()
            ),
            EvenementCalendrier(
                id="gouter_1", type=TypeEvenement.GOUTER, titre="Gouter", date_jour=date.today()
            ),
            EvenementCalendrier(
                id="batch_1",
                type=TypeEvenement.BATCH_COOKING,
                titre="Batch",
                date_jour=date.today(),
            ),
            EvenementCalendrier(
                id="courses_1",
                type=TypeEvenement.COURSES,
                titre="Carrefour",
                date_jour=date.today(),
            ),
            EvenementCalendrier(
                id="courses_2", type=TypeEvenement.COURSES, titre="Lidl", date_jour=date.today()
            ),
            EvenementCalendrier(
                id="activite_1",
                type=TypeEvenement.ACTIVITE,
                titre="Piscine",
                date_jour=date.today(),
            ),
            EvenementCalendrier(
                id="rdv_1", type=TypeEvenement.RDV_MEDICAL, titre="Pediatre", date_jour=date.today()
            ),
            EvenementCalendrier(
                id="rdv_2", type=TypeEvenement.RDV_AUTRE, titre="Banque", date_jour=date.today()
            ),
            EvenementCalendrier(
                id="menage_1", type=TypeEvenement.MENAGE, titre="Aspirateur", date_jour=date.today()
            ),
            EvenementCalendrier(
                id="jardin_1", type=TypeEvenement.JARDIN, titre="Tonte", date_jour=date.today()
            ),
            EvenementCalendrier(
                id="entretien_1",
                type=TypeEvenement.ENTRETIEN,
                titre="Plomberie",
                date_jour=date.today(),
            ),
            EvenementCalendrier(
                id="routine_1",
                type=TypeEvenement.ROUTINE,
                titre="Routine matin",
                date_jour=date.today(),
            ),
        ]
        return JourCalendrier(date_jour=date.today(), evenements=evenements)

    def test_creation_jour_vide(self):
        """Test creation jour sans evenements."""
        jour = JourCalendrier(date_jour=date.today())
        assert jour.evenements == []
        assert jour.est_vide is True

    def test_est_aujourdhui_vrai(self):
        """Test property est_aujourdhui pour aujourd'hui."""
        jour = JourCalendrier(date_jour=date.today())
        assert jour.est_aujourdhui is True

    def test_est_aujourdhui_faux(self):
        """Test property est_aujourdhui pour autre jour."""
        jour = JourCalendrier(date_jour=date.today() - timedelta(days=1))
        assert jour.est_aujourdhui is False

    def test_jour_semaine(self):
        """Test property jour_semaine."""
        # Lundi 15 janvier 2024
        jour = JourCalendrier(date_jour=date(2024, 1, 15))
        assert jour.jour_semaine == "Lundi"

    def test_jour_semaine_court(self):
        """Test property jour_semaine_court."""
        jour = JourCalendrier(date_jour=date(2024, 1, 15))
        assert jour.jour_semaine_court == "Lun"

    def test_repas_midi(self, jour_avec_evenements):
        """Test property repas_midi."""
        assert jour_avec_evenements.repas_midi is not None
        assert jour_avec_evenements.repas_midi.titre == "Dejeuner"

    def test_repas_midi_absent(self):
        """Test property repas_midi quand absent."""
        jour = JourCalendrier(date_jour=date.today())
        assert jour.repas_midi is None

    def test_repas_soir(self, jour_avec_evenements):
        """Test property repas_soir."""
        assert jour_avec_evenements.repas_soir is not None
        assert jour_avec_evenements.repas_soir.titre == "Diner"

    def test_gouter(self, jour_avec_evenements):
        """Test property gouter."""
        assert jour_avec_evenements.gouter is not None
        assert jour_avec_evenements.gouter.titre == "Gouter"

    def test_batch_cooking(self, jour_avec_evenements):
        """Test property batch_cooking."""
        assert jour_avec_evenements.batch_cooking is not None
        assert jour_avec_evenements.batch_cooking.titre == "Batch"

    def test_courses(self, jour_avec_evenements):
        """Test property courses."""
        assert len(jour_avec_evenements.courses) == 2

    def test_activites(self, jour_avec_evenements):
        """Test property activites."""
        assert len(jour_avec_evenements.activites) == 1
        assert jour_avec_evenements.activites[0].titre == "Piscine"

    def test_rdv(self, jour_avec_evenements):
        """Test property rdv."""
        assert len(jour_avec_evenements.rdv) == 2

    def test_taches_menage(self, jour_avec_evenements):
        """Test property taches_menage."""
        taches = jour_avec_evenements.taches_menage
        assert len(taches) == 2  # MENAGE + ENTRETIEN

    def test_taches_jardin(self, jour_avec_evenements):
        """Test property taches_jardin."""
        taches = jour_avec_evenements.taches_jardin
        assert len(taches) == 1
        assert taches[0].titre == "Tonte"

    def test_autres_evenements(self, jour_avec_evenements):
        """Test property autres_evenements."""
        autres = jour_avec_evenements.autres_evenements
        # ROUTINE n'est pas dans les types principaux
        assert len(autres) == 1
        assert autres[0].type == TypeEvenement.ROUTINE

    def test_nb_evenements(self, jour_avec_evenements):
        """Test property nb_evenements."""
        assert jour_avec_evenements.nb_evenements == 13

    def test_a_repas_planifies(self, jour_avec_evenements):
        """Test property a_repas_planifies."""
        assert jour_avec_evenements.a_repas_planifies is True

    def test_a_repas_planifies_faux(self):
        """Test property a_repas_planifies quand False."""
        jour = JourCalendrier(date_jour=date.today())
        assert jour.a_repas_planifies is False


# ═══════════════════════════════════════════════════════════
# TESTS SEMAINECALENDRIER DATACLASS
# ═══════════════════════════════════════════════════════════


class TestSemaineCalendrier:
    """Tests pour la dataclass SemaineCalendrier."""

    @pytest.fixture
    def semaine_complete(self):
        """Fixture: semaine avec jours et evenements."""
        lundi = date(2024, 1, 15)  # Un lundi
        jours = []
        for i in range(7):
            jour_date = lundi + timedelta(days=i)
            evenements = []
            # Ajouter repas midi et soir pour certains jours
            if i < 5:  # Lun-Ven
                evenements.append(
                    EvenementCalendrier(
                        id=f"midi_{i}",
                        type=TypeEvenement.REPAS_MIDI,
                        titre=f"Dejeuner {i}",
                        date_jour=jour_date,
                    )
                )
            if i < 4:  # Lun-Jeu
                evenements.append(
                    EvenementCalendrier(
                        id=f"soir_{i}",
                        type=TypeEvenement.REPAS_SOIR,
                        titre=f"Diner {i}",
                        date_jour=jour_date,
                    )
                )
            # Batch cooking le dimanche
            if i == 6:
                evenements.append(
                    EvenementCalendrier(
                        id="batch_1",
                        type=TypeEvenement.BATCH_COOKING,
                        titre="Batch",
                        date_jour=jour_date,
                    )
                )
            # Courses le samedi
            if i == 5:
                evenements.append(
                    EvenementCalendrier(
                        id="courses_1",
                        type=TypeEvenement.COURSES,
                        titre="Carrefour",
                        date_jour=jour_date,
                    )
                )
                evenements.append(
                    EvenementCalendrier(
                        id="courses_2",
                        type=TypeEvenement.COURSES,
                        titre="Lidl",
                        date_jour=jour_date,
                    )
                )
            # Activite le mercredi
            if i == 2:
                evenements.append(
                    EvenementCalendrier(
                        id="activite_1",
                        type=TypeEvenement.ACTIVITE,
                        titre="Piscine",
                        date_jour=jour_date,
                    )
                )
            jours.append(JourCalendrier(date_jour=jour_date, evenements=evenements))
        return SemaineCalendrier(date_debut=lundi, jours=jours)

    def test_creation_semaine_vide(self):
        """Test creation semaine sans jours."""
        semaine = SemaineCalendrier(date_debut=date(2024, 1, 15))
        assert semaine.jours == []

    def test_date_fin(self):
        """Test property date_fin."""
        semaine = SemaineCalendrier(date_debut=date(2024, 1, 15))  # Lundi
        assert semaine.date_fin == date(2024, 1, 21)  # Dimanche

    def test_titre(self):
        """Test property titre."""
        semaine = SemaineCalendrier(date_debut=date(2024, 1, 15))
        assert "15/01" in semaine.titre
        assert "21/01/2024" in semaine.titre

    def test_nb_repas_planifies(self, semaine_complete):
        """Test property nb_repas_planifies."""
        # 5 midi + 4 soir = 9
        assert semaine_complete.nb_repas_planifies == 9

    def test_nb_sessions_batch(self, semaine_complete):
        """Test property nb_sessions_batch."""
        assert semaine_complete.nb_sessions_batch == 1

    def test_nb_courses(self, semaine_complete):
        """Test property nb_courses."""
        assert semaine_complete.nb_courses == 2

    def test_nb_activites(self, semaine_complete):
        """Test property nb_activites."""
        assert semaine_complete.nb_activites == 1


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS DE NAVIGATION
# ═══════════════════════════════════════════════════════════


class TestFonctionsNavigation:
    """Tests pour les fonctions de navigation semaine."""

    def test_get_jours_semaine(self):
        """Test get_jours_semaine retourne 7 jours."""
        jours = get_jours_semaine(date(2024, 1, 17))  # Mercredi
        assert len(jours) == 7
        assert jours[0].weekday() == 0  # Premier jour est Lundi
        assert jours[-1].weekday() == 6  # Dernier jour est Dimanche

    def test_get_semaine_precedente(self):
        """Test get_semaine_precedente."""
        resultat = get_semaine_precedente(date(2024, 1, 17))
        # Devrait retourner le lundi de la semaine precedente
        assert resultat == date(2024, 1, 8)

    def test_get_semaine_suivante(self):
        """Test get_semaine_suivante."""
        resultat = get_semaine_suivante(date(2024, 1, 17))
        # Devrait retourner le lundi de la semaine suivante
        assert resultat == date(2024, 1, 22)


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION REPAS
# ═══════════════════════════════════════════════════════════


class TestConvertirRepas:
    """Tests pour convertir_repas_en_evenement."""

    def test_repas_none(self):
        """Test avec repas None."""
        result = convertir_repas_en_evenement(None)
        assert result is None

    def test_repas_diner(self):
        """Test conversion repas dîner."""
        repas = Mock()
        repas.id = 1
        repas.type_repas = "dîner"
        repas.date_repas = date(2024, 1, 15)
        repas.recette = Mock()
        repas.recette.nom = "Poulet rôti"
        repas.recette.id = 10
        repas.recette.instructions_bebe = "Couper en petits morceaux"
        repas.prepare = True
        repas.notes = "Recette familiale"

        result = convertir_repas_en_evenement(repas)

        assert result is not None
        assert result.type == TypeEvenement.REPAS_SOIR
        assert result.titre == "Poulet rôti"
        assert result.recette_id == 10
        assert result.version_jules == "Couper en petits morceaux"
        assert result.termine is True

    def test_repas_dejeuner(self):
        """Test conversion repas dejeuner."""
        repas = Mock()
        repas.id = 2
        repas.type_repas = "déjeuner"
        repas.date_repas = date(2024, 1, 15)
        repas.recette = None

        result = convertir_repas_en_evenement(repas)

        assert result is not None
        assert result.type == TypeEvenement.REPAS_MIDI
        assert result.titre == "Repas non defini"

    def test_repas_sans_recette(self):
        """Test conversion repas sans recette liee."""
        repas = Mock()
        repas.id = 3
        repas.type_repas = "déjeuner"
        repas.date_repas = date(2024, 1, 15)
        repas.recette = None

        result = convertir_repas_en_evenement(repas)

        assert result is not None
        assert result.titre == "Repas non defini"

    def test_repas_exception(self):
        """Test gestion exception lors de la conversion."""
        repas = Mock()
        repas.id = 4
        repas.type_repas = "déjeuner"
        # Provoque une erreur
        type(repas).date_repas = property(lambda self: (_ for _ in ()).throw(Exception("Error")))

        result = convertir_repas_en_evenement(repas)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION SESSION BATCH
# ═══════════════════════════════════════════════════════════


class TestConvertirSessionBatch:
    """Tests pour convertir_session_batch_en_evenement."""

    def test_session_none(self):
        """Test avec session None."""
        result = convertir_session_batch_en_evenement(None)
        assert result is None

    def test_session_complete(self):
        """Test conversion session complete."""
        session = Mock()
        session.id = 1
        session.date_session = date(2024, 1, 14)  # Dimanche
        session.heure_debut = time(14, 0)
        session.recettes_planifiees = ["Recette1", "Recette2", "Recette3"]
        session.avec_jules = True
        session.statut = "terminee"
        session.notes = "Tres bien passe"

        result = convertir_session_batch_en_evenement(session)

        assert result is not None
        assert result.type == TypeEvenement.BATCH_COOKING
        assert "3 plats" in result.titre
        assert result.heure_debut == time(14, 0)
        assert result.pour_jules is True
        assert result.termine is True

    def test_session_sans_recettes(self):
        """Test conversion session sans recettes."""
        session = Mock()
        session.id = 2
        session.date_session = date(2024, 1, 14)
        session.heure_debut = None  # Pas d'heure specifiee
        session.recettes_planifiees = []
        session.avec_jules = False
        session.statut = "planifiee"
        session.notes = None

        result = convertir_session_batch_en_evenement(session)

        assert result is not None
        assert result.titre == "Session Batch Cooking"
        # heure_debut reste None si non specifie dans le Mock (pas d'attribut heure_debut)
        assert result.heure_debut is None

    def test_session_exception(self):
        """Test gestion exception."""
        session = Mock()
        type(session).id = property(lambda self: (_ for _ in ()).throw(Exception("Error")))

        result = convertir_session_batch_en_evenement(session)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION ACTIVITE
# ═══════════════════════════════════════════════════════════


class TestConvertirActivite:
    """Tests pour convertir_activite_en_evenement."""

    def test_activite_none(self):
        """Test avec activite None."""
        result = convertir_activite_en_evenement(None)
        assert result is None

    def test_activite_standard(self):
        """Test conversion activite standard."""
        activite = Mock()
        activite.id = 1
        activite.titre = "Piscine"
        activite.type_activite = "loisir"
        activite.date_prevue = date(2024, 1, 17)
        activite.heure_debut = time(14, 0)
        activite.lieu = "Centre aquatique"
        activite.pour_jules = True
        activite.cout_estime = 15.50
        activite.statut = "planifie"
        activite.notes = "Maillot pret"

        result = convertir_activite_en_evenement(activite)

        assert result is not None
        assert result.type == TypeEvenement.ACTIVITE
        assert result.titre == "Piscine"
        assert result.lieu == "Centre aquatique"
        assert result.budget == 15.50

    def test_activite_medicale(self):
        """Test conversion activite medicale."""
        activite = Mock()
        activite.id = 2
        activite.titre = "Pediatre"
        activite.type_activite = "medical"
        activite.date_prevue = date(2024, 1, 18)
        activite.heure_debut = time(10, 30)
        activite.lieu = "Cabinet Dr Martin"
        activite.pour_jules = True
        activite.cout_estime = None
        activite.statut = "termine"
        activite.notes = None

        result = convertir_activite_en_evenement(activite)

        assert result is not None
        assert result.type == TypeEvenement.RDV_MEDICAL
        assert result.termine is True

    def test_activite_sante(self):
        """Test conversion activite de type sante."""
        activite = Mock()
        activite.id = 3
        activite.titre = "Visite"
        activite.type_activite = "sante"
        activite.date_prevue = date(2024, 1, 19)

        result = convertir_activite_en_evenement(activite)

        assert result is not None
        assert result.type == TypeEvenement.RDV_MEDICAL

    def test_activite_exception(self):
        """Test gestion exception."""
        activite = Mock()
        type(activite).id = property(lambda self: (_ for _ in ()).throw(Exception("Error")))

        result = convertir_activite_en_evenement(activite)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION EVENT CALENDRIER
# ═══════════════════════════════════════════════════════════


class TestConvertirEventCalendrier:
    """Tests pour convertir_event_calendrier_en_evenement."""

    def test_event_none(self):
        """Test avec event None."""
        result = convertir_event_calendrier_en_evenement(None)
        assert result is None

    def test_event_standard(self):
        """Test conversion event standard."""
        event = Mock()
        event.id = 1
        event.titre = "Reunion famille"
        event.type_event = "autre"
        event.date_debut = datetime(2024, 1, 20, 15, 0)
        event.lieu = "Maison grand-mere"
        event.description = "Anniversaire"
        event.termine = False

        result = convertir_event_calendrier_en_evenement(event)

        assert result is not None
        assert result.type == TypeEvenement.EVENEMENT
        assert result.titre == "Reunion famille"
        assert result.heure_debut == time(15, 0)
        assert result.date_jour == date(2024, 1, 20)

    def test_event_medical(self):
        """Test conversion event medical."""
        event = Mock()
        event.id = 2
        event.titre = "RDV dentiste"
        event.type_event = "medical"
        event.date_debut = date(2024, 1, 22)  # Date sans heure
        event.lieu = "Cabinet"
        event.description = None
        event.termine = True

        result = convertir_event_calendrier_en_evenement(event)

        assert result is not None
        assert result.type == TypeEvenement.RDV_MEDICAL
        assert result.heure_debut is None  # Pas d'heure pour date seule

    def test_event_courses(self):
        """Test conversion event courses."""
        event = Mock()
        event.id = 3
        event.titre = "Courses"
        event.type_event = "courses"
        event.date_debut = datetime(2024, 1, 21, 10, 0)
        event.lieu = "Centre commercial"

        result = convertir_event_calendrier_en_evenement(event)

        assert result is not None
        assert result.type == TypeEvenement.COURSES

    def test_event_exception(self):
        """Test gestion exception."""
        event = Mock()
        type(event).id = property(lambda self: (_ for _ in ()).throw(Exception("Error")))

        result = convertir_event_calendrier_en_evenement(event)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION TACHE MENAGE
# ═══════════════════════════════════════════════════════════


class TestConvertirTacheMenage:
    """Tests pour convertir_tache_menage_en_evenement."""

    def test_tache_none(self):
        """Test avec tache None."""
        result = convertir_tache_menage_en_evenement(None)
        assert result is None

    def test_tache_menage(self):
        """Test conversion tache menage."""
        tache = Mock()
        tache.id = 1
        tache.nom = "Aspirateur salon"
        tache.categorie = "menage"
        tache.prochaine_fois = date(2024, 1, 16)
        tache.responsable = "Alice"
        tache.duree_minutes = 30
        tache.description = "Faire le salon"
        tache.fait = False
        tache.notes = None

        result = convertir_tache_menage_en_evenement(tache)

        assert result is not None
        assert result.type == TypeEvenement.MENAGE
        assert "Alice" in result.titre
        assert "30min" in result.description

    def test_tache_jardin(self):
        """Test conversion tache jardin."""
        tache = Mock()
        tache.id = 2
        tache.nom = "Tonte pelouse"
        tache.categorie = "jardin"
        tache.prochaine_fois = date(2024, 1, 20)
        tache.responsable = None
        tache.duree_minutes = 60
        tache.description = "Jardin avant"
        tache.fait = False
        tache.notes = None

        result = convertir_tache_menage_en_evenement(tache)

        assert result is not None
        assert result.type == TypeEvenement.JARDIN

    def test_tache_entretien(self):
        """Test conversion tache entretien."""
        tache = Mock()
        tache.id = 3
        tache.nom = "Reparation fuite"
        tache.categorie = "plomberie"  # Ni menage, ni jardin
        tache.prochaine_fois = date(2024, 1, 17)
        tache.responsable = None
        tache.duree_minutes = None
        tache.description = ""
        tache.fait = True
        tache.notes = "Urgent"

        result = convertir_tache_menage_en_evenement(tache)

        assert result is not None
        assert result.type == TypeEvenement.ENTRETIEN
        assert result.termine is True

    def test_tache_en_retard(self):
        """Test conversion tache en retard."""
        tache = Mock()
        tache.id = 4
        tache.nom = "Menage retard"
        tache.categorie = "menage"
        tache.prochaine_fois = date.today() - timedelta(days=3)
        tache.responsable = None
        tache.duree_minutes = None
        tache.description = ""
        tache.fait = False
        tache.notes = None

        result = convertir_tache_menage_en_evenement(tache)

        assert result is not None
        assert "EN RETARD" in result.notes

    def test_tache_exception(self):
        """Test gestion exception."""
        tache = Mock()
        type(tache).id = property(lambda self: (_ for _ in ()).throw(Exception("Error")))

        result = convertir_tache_menage_en_evenement(tache)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS GENERATION TACHES MENAGE SEMAINE
# ═══════════════════════════════════════════════════════════


class TestGenererTachesMenageSemaine:
    """Tests pour generer_taches_menage_semaine."""

    def test_liste_vide(self):
        """Test avec liste vide."""
        result = generer_taches_menage_semaine([], date(2024, 1, 15), date(2024, 1, 21))
        assert result == {}

    def test_tache_non_integree(self):
        """Test tache non integree au planning."""
        tache = Mock()
        tache.integrer_planning = False

        result = generer_taches_menage_semaine([tache], date(2024, 1, 15), date(2024, 1, 21))
        assert result == {}

    def test_tache_avec_prochaine_fois_dans_semaine(self):
        """Test tache avec prochaine_fois dans la semaine."""
        tache = Mock()
        tache.id = 1
        tache.integrer_planning = True
        tache.prochaine_fois = date(2024, 1, 17)  # Mercredi
        tache.frequence_jours = None
        tache.nom = "Test"
        tache.categorie = "menage"
        tache.responsable = None
        tache.duree_minutes = None
        tache.description = ""
        tache.fait = False
        tache.notes = None

        result = generer_taches_menage_semaine([tache], date(2024, 1, 15), date(2024, 1, 21))

        assert date(2024, 1, 17) in result
        assert len(result[date(2024, 1, 17)]) == 1

    def test_tache_recurrente_hebdomadaire(self):
        """Test tache recurrente sans prochaine_fois."""
        tache = Mock()
        tache.id = 3  # id modulo 7 = 3 => jeudi
        tache.integrer_planning = True
        tache.prochaine_fois = None
        tache.frequence_jours = 7  # Hebdomadaire
        tache.nom = "Hebdo"
        tache.categorie = "menage"
        tache.responsable = None
        tache.duree_minutes = None
        tache.description = ""
        tache.fait = False
        tache.notes = None

        result = generer_taches_menage_semaine(
            [tache],
            date(2024, 1, 15),
            date(2024, 1, 21),  # Lundi-Dimanche
        )

        # id=3 % 7 = 3 => lundi + 3 = jeudi
        assert date(2024, 1, 18) in result  # Jeudi


# ═══════════════════════════════════════════════════════════
# TESTS CREATION EVENEMENT COURSES
# ═══════════════════════════════════════════════════════════


class TestCreerEvenementCourses:
    """Tests pour creer_evenement_courses."""

    def test_creation_basique(self):
        """Test creation evenement courses basique."""
        result = creer_evenement_courses(date_jour=date(2024, 1, 20), magasin="Carrefour")

        assert result.type == TypeEvenement.COURSES
        assert result.titre == "Courses Carrefour"
        assert result.magasin == "Carrefour"
        assert result.date_jour == date(2024, 1, 20)

    def test_creation_avec_heure(self):
        """Test creation avec heure."""
        result = creer_evenement_courses(
            date_jour=date(2024, 1, 20), magasin="Lidl", heure=time(10, 0)
        )

        assert result.heure_debut == time(10, 0)

    def test_creation_avec_id(self):
        """Test creation avec id source."""
        result = creer_evenement_courses(date_jour=date(2024, 1, 20), magasin="Aldi", id_source=42)

        assert "42" in result.id


# ═══════════════════════════════════════════════════════════
# TESTS AGREGATION EVENEMENTS JOUR
# ═══════════════════════════════════════════════════════════


class TestAgregerEvenementsJour:
    """Tests pour agreger_evenements_jour."""

    def test_jour_vide(self):
        """Test agregation jour sans donnees."""
        result = agreger_evenements_jour(date(2024, 1, 15))

        assert result.date_jour == date(2024, 1, 15)
        assert result.evenements == []

    def test_jour_avec_repas(self):
        """Test agregation avec repas."""
        repas = Mock()
        repas.id = 1
        repas.date_repas = date(2024, 1, 15)
        repas.type_repas = "déjeuner"
        repas.recette = Mock()
        repas.recette.nom = "Pates"
        repas.recette.id = 10
        repas.recette.instructions_bebe = None

        result = agreger_evenements_jour(date_jour=date(2024, 1, 15), repas=[repas])

        assert len(result.evenements) == 1
        assert result.evenements[0].type == TypeEvenement.REPAS_MIDI

    def test_jour_avec_taches_menage(self):
        """Test agregation avec taches menage pre-converties."""
        tache_evt = EvenementCalendrier(
            id="menage_1",
            type=TypeEvenement.MENAGE,
            titre="Aspirateur",
            date_jour=date(2024, 1, 15),
        )

        result = agreger_evenements_jour(date_jour=date(2024, 1, 15), taches_menage=[tache_evt])

        assert len(result.evenements) == 1
        assert result.evenements[0].type == TypeEvenement.MENAGE

    def test_jour_avec_courses_planifiees(self):
        """Test agregation avec courses planifiees."""
        courses = [
            {"date": date(2024, 1, 15), "magasin": "Carrefour", "heure": time(10, 0)},
            {"date": date(2024, 1, 15), "magasin": "Lidl", "heure": None},
        ]

        result = agreger_evenements_jour(date_jour=date(2024, 1, 15), courses_planifiees=courses)

        assert len(result.evenements) == 2

    def test_tri_par_heure(self):
        """Test tri des evenements par heure."""
        tache1 = EvenementCalendrier(
            id="evt_1",
            type=TypeEvenement.ACTIVITE,
            titre="Tard",
            date_jour=date(2024, 1, 15),
            heure_debut=time(18, 0),
        )
        tache2 = EvenementCalendrier(
            id="evt_2",
            type=TypeEvenement.ACTIVITE,
            titre="Tot",
            date_jour=date(2024, 1, 15),
            heure_debut=time(9, 0),
        )

        result = agreger_evenements_jour(
            date_jour=date(2024, 1, 15), taches_menage=[tache1, tache2]
        )

        # Le premier devrait etre celui a 9h
        assert result.evenements[0].titre == "Tot"


# ═══════════════════════════════════════════════════════════
# TESTS CONSTRUCTION SEMAINE CALENDRIER
# ═══════════════════════════════════════════════════════════


class TestConstruireSemaineCalendrier:
    """Tests pour construire_semaine_calendrier."""

    def test_semaine_vide(self):
        """Test construction semaine sans donnees."""
        result = construire_semaine_calendrier(date(2024, 1, 17))  # Mercredi

        assert result.date_debut.weekday() == 0  # Lundi
        assert len(result.jours) == 7

    def test_semaine_avec_taches_menage(self):
        """Test construction avec taches menage."""
        tache = Mock()
        tache.id = 1
        tache.integrer_planning = True
        tache.prochaine_fois = date(2024, 1, 17)
        tache.frequence_jours = None
        tache.nom = "Menage"
        tache.categorie = "menage"
        tache.responsable = None
        tache.duree_minutes = None
        tache.description = ""
        tache.fait = False
        tache.notes = None

        result = construire_semaine_calendrier(date_debut=date(2024, 1, 15), taches_menage=[tache])

        # Verifier que la tache est presente le mercredi (index 2)
        jour_mercredi = result.jours[2]
        assert len(jour_mercredi.evenements) == 1


# ═══════════════════════════════════════════════════════════
# TESTS GENERATION TEXTE POUR IMPRESSION
# ═══════════════════════════════════════════════════════════


class TestGenererTexteSemaine:
    """Tests pour generer_texte_semaine_pour_impression."""

    @pytest.fixture
    def semaine_test(self):
        """Fixture: semaine avec contenu pour impression."""
        lundi = date(2024, 1, 15)
        jours = []

        # Jour avec repas
        jour1_evts = [
            EvenementCalendrier(
                id="midi_1",
                type=TypeEvenement.REPAS_MIDI,
                titre="Poulet",
                date_jour=lundi,
                version_jules="Morceaux tendres",
            ),
            EvenementCalendrier(
                id="soir_1",
                type=TypeEvenement.REPAS_SOIR,
                titre="Poisson",
                date_jour=lundi,
                version_jules="En puree",
            ),
            EvenementCalendrier(
                id="gouter_1", type=TypeEvenement.GOUTER, titre="Compote", date_jour=lundi
            ),
        ]
        jours.append(JourCalendrier(date_jour=lundi, evenements=jour1_evts))

        # Jour avec batch et courses
        jour2 = lundi + timedelta(days=1)
        jour2_evts = [
            EvenementCalendrier(
                id="batch_1",
                type=TypeEvenement.BATCH_COOKING,
                titre="Batch",
                date_jour=jour2,
                heure_debut=time(14, 0),
            ),
            EvenementCalendrier(
                id="courses_1",
                type=TypeEvenement.COURSES,
                titre="Courses Carrefour",
                date_jour=jour2,
                magasin="Carrefour",
                heure_debut=time(10, 0),
            ),
        ]
        jours.append(JourCalendrier(date_jour=jour2, evenements=jour2_evts))

        # Jour avec activite et rdv
        jour3 = lundi + timedelta(days=2)
        jour3_evts = [
            EvenementCalendrier(
                id="activite_1",
                type=TypeEvenement.ACTIVITE,
                titre="Piscine",
                date_jour=jour3,
                heure_debut=time(15, 0),
            ),
            EvenementCalendrier(
                id="rdv_1",
                type=TypeEvenement.RDV_MEDICAL,
                titre="Pediatre",
                date_jour=jour3,
                heure_debut=time(10, 0),
            ),
            EvenementCalendrier(
                id="rdv_2",
                type=TypeEvenement.RDV_AUTRE,
                titre="Banque",
                date_jour=jour3,
                heure_debut=time(11, 0),
            ),
        ]
        jours.append(JourCalendrier(date_jour=jour3, evenements=jour3_evts))

        # Jours vides
        for i in range(3, 7):
            jour = lundi + timedelta(days=i)
            jours.append(JourCalendrier(date_jour=jour, evenements=[]))

        return SemaineCalendrier(date_debut=lundi, jours=jours)

    def test_generation_texte(self, semaine_test):
        """Test generation texte basique."""
        texte = generer_texte_semaine_pour_impression(semaine_test)

        assert "SEMAINE DU" in texte
        assert "Poulet" in texte
        assert "Jules" in texte  # Version Jules
        assert "Poisson" in texte
        assert "BATCH COOKING" in texte
        assert "Courses" in texte
        assert "Piscine" in texte
        assert "Pediatre" in texte
        assert "(rien de planifie)" in texte  # Jours vides

    def test_generation_texte_semaine_vide(self):
        """Test generation texte semaine vide."""
        semaine = SemaineCalendrier(
            date_debut=date(2024, 1, 15),
            jours=[
                JourCalendrier(date_jour=date(2024, 1, 15) + timedelta(days=i)) for i in range(7)
            ],
        )

        texte = generer_texte_semaine_pour_impression(semaine)

        # Tous les jours sont vides
        assert texte.count("(rien de planifie)") == 7


# ═══════════════════════════════════════════════════════════
# TESTS GENERATION HTML POUR IMPRESSION
# ═══════════════════════════════════════════════════════════


class TestGenererHtmlSemaine:
    """Tests pour generer_html_semaine_pour_impression."""

    @pytest.fixture
    def semaine_html_test(self):
        """Fixture: semaine pour test HTML."""
        lundi = date(2024, 1, 15)
        jours = []

        jour1_evts = [
            EvenementCalendrier(
                id="midi_1",
                type=TypeEvenement.REPAS_MIDI,
                titre="Poulet",
                date_jour=lundi,
                version_jules="Couper en petits morceaux pour Jules",
            ),
            EvenementCalendrier(
                id="soir_1",
                type=TypeEvenement.REPAS_SOIR,
                titre="Poisson",
                date_jour=lundi,
                version_jules="Enlever les aretes",
            ),
            EvenementCalendrier(
                id="batch_1",
                type=TypeEvenement.BATCH_COOKING,
                titre="Batch",
                date_jour=lundi,
                heure_debut=time(14, 0),
            ),
            EvenementCalendrier(
                id="courses_1",
                type=TypeEvenement.COURSES,
                titre="Courses",
                date_jour=lundi,
                magasin="Lidl",
                heure_debut=time(10, 0),
            ),
            EvenementCalendrier(
                id="rdv_1",
                type=TypeEvenement.RDV_MEDICAL,
                titre="Medecin",
                date_jour=lundi,
                heure_debut=time(9, 0),
            ),
        ]
        jours.append(JourCalendrier(date_jour=lundi, evenements=jour1_evts))

        # Remaining days
        for i in range(1, 7):
            jour = lundi + timedelta(days=i)
            jours.append(JourCalendrier(date_jour=jour, evenements=[]))

        return SemaineCalendrier(date_debut=lundi, jours=jours)

    def test_generation_html(self, semaine_html_test):
        """Test generation HTML basique."""
        html = generer_html_semaine_pour_impression(semaine_html_test)

        assert "<html>" in html
        assert "<style>" in html
        assert "SEMAINE DU" in html
        assert "Poulet" in html
        assert "Poisson" in html
        assert "Batch Cooking" in html
        assert "👶" in html  # Version Jules
        assert "🏥" in html  # RDV medical

    def test_generation_html_structure(self, semaine_html_test):
        """Test structure HTML valide."""
        html = generer_html_semaine_pour_impression(semaine_html_test)

        assert html.count("<html>") == 1
        assert html.count("</html>") == 1
        assert html.count("<body>") == 1
        assert html.count("</body>") == 1
        assert 'class="jour"' in html
