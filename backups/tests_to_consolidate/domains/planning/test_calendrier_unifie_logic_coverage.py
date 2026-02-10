"""
Tests de couverture pour calendrier_unifie_logic.py
Objectif: Atteindre ≥80% de couverture
"""

import pytest
from datetime import date, datetime, time, timedelta
from dataclasses import dataclass
from typing import Optional, List
from unittest.mock import MagicMock, patch

from src.domains.planning.logic.calendrier_unifie_logic import (
    # Constantes
    TypeEvenement,
    EMOJI_TYPE,
    COULEUR_TYPE,
    JOURS_SEMAINE,
    JOURS_SEMAINE_COURT,
    # Dataclasses
    EvenementCalendrier,
    JourCalendrier,
    SemaineCalendrier,
    # Fonctions date
    get_debut_semaine,
    get_fin_semaine,
    get_jours_semaine,
    get_semaine_precedente,
    get_semaine_suivante,
    # Conversion
    convertir_repas_en_evenement,
    convertir_session_batch_en_evenement,
    convertir_activite_en_evenement,
    convertir_event_calendrier_en_evenement,
    convertir_tache_menage_en_evenement,
    # Génération
    generer_taches_menage_semaine,
    creer_evenement_courses,
    # Agrégation
    agreger_evenements_jour,
    construire_semaine_calendrier,
    # Export
    generer_texte_semaine_pour_impression,
    generer_html_semaine_pour_impression,
)


# ═══════════════════════════════════════════════════════════
# TESTS EVENEMENT CALENDRIER DATACLASS
# ═══════════════════════════════════════════════════════════


class TestEvenementCalendrier:
    """Tests pour la dataclass EvenementCalendrier."""
    
    def test_creation_basique(self):
        """Crée un événement avec valeurs minimales."""
        evt = EvenementCalendrier(
            id="test_1",
            type=TypeEvenement.REPAS_MIDI,
            titre="Déjeuner",
            date_jour=date(2024, 1, 15)
        )
        assert evt.id == "test_1"
        assert evt.type == TypeEvenement.REPAS_MIDI
        assert evt.titre == "Déjeuner"
        assert evt.date_jour == date(2024, 1, 15)
        
    def test_emoji_property(self):
        """Vérifie la propriété emoji."""
        evt = EvenementCalendrier(
            id="test", type=TypeEvenement.BATCH_COOKING,
            titre="Test", date_jour=date.today()
        )
        assert evt.emoji == "🍳"
        
    def test_emoji_tous_types(self):
        """Vérifie emoji pour tous les types."""
        for type_evt in TypeEvenement:
            evt = EvenementCalendrier(
                id="test", type=type_evt,
                titre="Test", date_jour=date.today()
            )
            assert evt.emoji in EMOJI_TYPE.values() or evt.emoji == "📌"
            
    def test_couleur_property(self):
        """Vérifie la propriété couleur."""
        evt = EvenementCalendrier(
            id="test", type=TypeEvenement.COURSES,
            titre="Test", date_jour=date.today()
        )
        assert evt.couleur == "#4DD0E1"
        
    def test_heure_str_avec_heure(self):
        """Vérifie format heure quand définie."""
        evt = EvenementCalendrier(
            id="test", type=TypeEvenement.ACTIVITE,
            titre="Test", date_jour=date.today(),
            heure_debut=time(14, 30)
        )
        assert evt.heure_str == "14:30"
        
    def test_heure_str_sans_heure(self):
        """Vérifie format heure quand non définie."""
        evt = EvenementCalendrier(
            id="test", type=TypeEvenement.ACTIVITE,
            titre="Test", date_jour=date.today()
        )
        assert evt.heure_str == ""
        
    def test_tous_champs_optionnels(self):
        """Événement avec tous les champs optionnels."""
        evt = EvenementCalendrier(
            id="full_1",
            type=TypeEvenement.RDV_MEDICAL,
            titre="RDV Pédiatre",
            date_jour=date(2024, 2, 1),
            heure_debut=time(10, 0),
            heure_fin=time(10, 30),
            description="Visite vaccin",
            lieu="Cabinet Dr Martin",
            participants=["Papa", "Maman", "Jules"],
            pour_jules=True,
            version_jules="Apporter carnet de santé",
            budget=50.0,
            recette_id=None,
            session_id=None,
            terminé=False,
            notes="Prévoir 15 min avant"
        )
        assert evt.lieu == "Cabinet Dr Martin"
        assert len(evt.participants) == 3
        assert evt.budget == 50.0


# ═══════════════════════════════════════════════════════════
# TESTS JOUR CALENDRIER DATACLASS
# ═══════════════════════════════════════════════════════════


class TestJourCalendrier:
    """Tests pour la dataclass JourCalendrier."""
    
    @pytest.fixture
    def jour_avec_evenements(self):
        """Crée un jour avec divers événements."""
        return JourCalendrier(
            date_jour=date(2024, 1, 15),  # Lundi
            evenements=[
                EvenementCalendrier(
                    id="repas_1", type=TypeEvenement.REPAS_MIDI,
                    titre="Pâtes", date_jour=date(2024, 1, 15)
                ),
                EvenementCalendrier(
                    id="repas_2", type=TypeEvenement.REPAS_SOIR,
                    titre="Salade", date_jour=date(2024, 1, 15)
                ),
                EvenementCalendrier(
                    id="gouter_1", type=TypeEvenement.GOUTER,
                    titre="Gâteau", date_jour=date(2024, 1, 15)
                ),
                EvenementCalendrier(
                    id="batch_1", type=TypeEvenement.BATCH_COOKING,
                    titre="Batch", date_jour=date(2024, 1, 15)
                ),
                EvenementCalendrier(
                    id="courses_1", type=TypeEvenement.COURSES,
                    titre="Courses Carrefour", date_jour=date(2024, 1, 15)
                ),
                EvenementCalendrier(
                    id="act_1", type=TypeEvenement.ACTIVITE,
                    titre="Parc", date_jour=date(2024, 1, 15)
                ),
                EvenementCalendrier(
                    id="rdv_1", type=TypeEvenement.RDV_MEDICAL,
                    titre="Vaccin", date_jour=date(2024, 1, 15)
                ),
                EvenementCalendrier(
                    id="rdv_2", type=TypeEvenement.RDV_AUTRE,
                    titre="Réunion", date_jour=date(2024, 1, 15)
                ),
                EvenementCalendrier(
                    id="menage_1", type=TypeEvenement.MENAGE,
                    titre="Aspirateur", date_jour=date(2024, 1, 15)
                ),
                EvenementCalendrier(
                    id="jardin_1", type=TypeEvenement.JARDIN,
                    titre="Arrosage", date_jour=date(2024, 1, 15)
                ),
                EvenementCalendrier(
                    id="entretien_1", type=TypeEvenement.ENTRETIEN,
                    titre="Chaudière", date_jour=date(2024, 1, 15)
                ),
                EvenementCalendrier(
                    id="evt_1", type=TypeEvenement.EVENEMENT,
                    titre="Autre", date_jour=date(2024, 1, 15)
                ),
            ]
        )
    
    def test_jour_semaine(self):
        """Vérifie le jour de la semaine."""
        jour = JourCalendrier(date_jour=date(2024, 1, 15))  # Lundi
        assert jour.jour_semaine == "Lundi"
        
    def test_jour_semaine_court(self):
        """Vérifie l'abréviation du jour."""
        jour = JourCalendrier(date_jour=date(2024, 1, 15))
        assert jour.jour_semaine_court == "Lun"
        
    def test_est_aujourdhui_vrai(self):
        """Vérifie est_aujourdhui pour aujourd'hui."""
        jour = JourCalendrier(date_jour=date.today())
        assert jour.est_aujourdhui is True
        
    def test_est_aujourdhui_faux(self):
        """Vérifie est_aujourdhui pour autre jour."""
        jour = JourCalendrier(date_jour=date(2020, 1, 1))
        assert jour.est_aujourdhui is False
        
    def test_repas_midi_property(self, jour_avec_evenements):
        """Récupère le repas du midi."""
        assert jour_avec_evenements.repas_midi is not None
        assert jour_avec_evenements.repas_midi.titre == "Pâtes"
        
    def test_repas_soir_property(self, jour_avec_evenements):
        """Récupère le repas du soir."""
        assert jour_avec_evenements.repas_soir is not None
        assert jour_avec_evenements.repas_soir.titre == "Salade"
        
    def test_gouter_property(self, jour_avec_evenements):
        """Récupère le goûter."""
        assert jour_avec_evenements.gouter is not None
        assert jour_avec_evenements.gouter.titre == "Gâteau"
        
    def test_batch_cooking_property(self, jour_avec_evenements):
        """Récupère la session batch."""
        assert jour_avec_evenements.batch_cooking is not None
        
    def test_courses_property(self, jour_avec_evenements):
        """Récupère les courses."""
        courses = jour_avec_evenements.courses
        assert len(courses) == 1
        assert courses[0].titre == "Courses Carrefour"
        
    def test_activites_property(self, jour_avec_evenements):
        """Récupère les activités."""
        assert len(jour_avec_evenements.activites) == 1
        
    def test_rdv_property(self, jour_avec_evenements):
        """Récupère les RDV (médicaux et autres)."""
        rdv = jour_avec_evenements.rdv
        assert len(rdv) == 2
        
    def test_taches_menage_property(self, jour_avec_evenements):
        """Récupère les tâches ménage (menage + entretien)."""
        taches = jour_avec_evenements.taches_menage
        assert len(taches) == 2  # menage + entretien
        
    def test_taches_jardin_property(self, jour_avec_evenements):
        """Récupère les tâches jardin."""
        jardin = jour_avec_evenements.taches_jardin
        assert len(jardin) == 1
        
    def test_autres_evenements_property(self, jour_avec_evenements):
        """Récupère les autres événements."""
        autres = jour_avec_evenements.autres_evenements
        # Seul EVENEMENT n'est pas dans les types principaux
        assert len(autres) == 1
        assert autres[0].type == TypeEvenement.EVENEMENT
        
    def test_nb_evenements(self, jour_avec_evenements):
        """Compte les événements."""
        assert jour_avec_evenements.nb_evenements == 12
        
    def test_est_vide_faux(self, jour_avec_evenements):
        """Jour avec événements n'est pas vide."""
        assert jour_avec_evenements.est_vide is False
        
    def test_est_vide_vrai(self):
        """Jour sans événements est vide."""
        jour = JourCalendrier(date_jour=date.today())
        assert jour.est_vide is True
        
    def test_a_repas_planifies_avec_midi(self):
        """Vérifie a_repas_planifies avec midi."""
        jour = JourCalendrier(
            date_jour=date.today(),
            evenements=[
                EvenementCalendrier(
                    id="r1", type=TypeEvenement.REPAS_MIDI,
                    titre="Test", date_jour=date.today()
                )
            ]
        )
        assert jour.a_repas_planifies is True
        
    def test_a_repas_planifies_avec_soir(self):
        """Vérifie a_repas_planifies avec soir."""
        jour = JourCalendrier(
            date_jour=date.today(),
            evenements=[
                EvenementCalendrier(
                    id="r1", type=TypeEvenement.REPAS_SOIR,
                    titre="Test", date_jour=date.today()
                )
            ]
        )
        assert jour.a_repas_planifies is True
        
    def test_a_repas_planifies_sans_repas(self):
        """Vérifie a_repas_planifies sans repas."""
        jour = JourCalendrier(date_jour=date.today())
        assert jour.a_repas_planifies is False
        
    def test_repas_midi_none_si_absent(self):
        """Retourne None si pas de repas midi."""
        jour = JourCalendrier(date_jour=date.today())
        assert jour.repas_midi is None
        
    def test_gouter_none_si_absent(self):
        """Retourne None si pas de goûter."""
        jour = JourCalendrier(date_jour=date.today())
        assert jour.gouter is None
        
    def test_batch_cooking_none_si_absent(self):
        """Retourne None si pas de batch."""
        jour = JourCalendrier(date_jour=date.today())
        assert jour.batch_cooking is None


# ═══════════════════════════════════════════════════════════
# TESTS SEMAINE CALENDRIER DATACLASS
# ═══════════════════════════════════════════════════════════


class TestSemaineCalendrier:
    """Tests pour la dataclass SemaineCalendrier."""
    
    @pytest.fixture
    def semaine_complete(self):
        """Crée une semaine avec des jours et événements."""
        jours = []
        lundi = date(2024, 1, 15)
        
        for i in range(7):
            jour_date = lundi + timedelta(days=i)
            evts = []
            
            # Ajouter repas midi chaque jour
            evts.append(EvenementCalendrier(
                id=f"midi_{i}", type=TypeEvenement.REPAS_MIDI,
                titre=f"Midi {i}", date_jour=jour_date
            ))
            
            # Repas soir jours pairs
            if i % 2 == 0:
                evts.append(EvenementCalendrier(
                    id=f"soir_{i}", type=TypeEvenement.REPAS_SOIR,
                    titre=f"Soir {i}", date_jour=jour_date
                ))
                
            # Batch cooking le dimanche
            if i == 6:
                evts.append(EvenementCalendrier(
                    id="batch_dim", type=TypeEvenement.BATCH_COOKING,
                    titre="Batch dimanche", date_jour=jour_date
                ))
                
            # Courses mercredi et samedi
            if i in [2, 5]:
                evts.append(EvenementCalendrier(
                    id=f"courses_{i}", type=TypeEvenement.COURSES,
                    titre=f"Courses {i}", date_jour=jour_date
                ))
                
            # Activité le week-end
            if i >= 5:
                evts.append(EvenementCalendrier(
                    id=f"act_{i}", type=TypeEvenement.ACTIVITE,
                    titre=f"Activité {i}", date_jour=jour_date
                ))
                
            jours.append(JourCalendrier(date_jour=jour_date, evenements=evts))
            
        return SemaineCalendrier(date_debut=lundi, jours=jours)
    
    def test_date_fin(self, semaine_complete):
        """Vérifie la date de fin (dimanche)."""
        assert semaine_complete.date_fin == date(2024, 1, 21)
        
    def test_titre(self, semaine_complete):
        """Vérifie le titre de la semaine."""
        assert "15/01" in semaine_complete.titre
        assert "21/01/2024" in semaine_complete.titre
        
    def test_nb_repas_planifies(self, semaine_complete):
        """Compte les repas planifiés."""
        # 7 midis + 4 soirs (jours pairs: 0,2,4,6)
        assert semaine_complete.nb_repas_planifies == 11
        
    def test_nb_sessions_batch(self, semaine_complete):
        """Compte les sessions batch."""
        assert semaine_complete.nb_sessions_batch == 1
        
    def test_nb_courses(self, semaine_complete):
        """Compte les courses."""
        assert semaine_complete.nb_courses == 2
        
    def test_nb_activites(self, semaine_complete):
        """Compte les activités."""
        assert semaine_complete.nb_activites == 2


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS DATE
# ═══════════════════════════════════════════════════════════


class TestFonctionsDate:
    """Tests pour les fonctions utilitaires de date."""
    
    def test_get_debut_semaine_lundi(self):
        """Début de semaine depuis un lundi reste lundi."""
        lundi = date(2024, 1, 15)
        assert get_debut_semaine(lundi) == lundi
        
    def test_get_debut_semaine_vendredi(self):
        """Début de semaine depuis vendredi."""
        vendredi = date(2024, 1, 19)
        assert get_debut_semaine(vendredi) == date(2024, 1, 15)
        
    def test_get_debut_semaine_dimanche(self):
        """Début de semaine depuis dimanche."""
        dimanche = date(2024, 1, 21)
        assert get_debut_semaine(dimanche) == date(2024, 1, 15)
        
    def test_get_fin_semaine(self):
        """Fin de semaine retourne dimanche."""
        lundi = date(2024, 1, 15)
        assert get_fin_semaine(lundi) == date(2024, 1, 21)
        
    def test_get_fin_semaine_depuis_dimanche(self):
        """Fin de semaine depuis dimanche reste dimanche."""
        dimanche = date(2024, 1, 21)
        assert get_fin_semaine(dimanche) == dimanche
        
    def test_get_jours_semaine(self):
        """Génère les 7 jours de la semaine."""
        jours = get_jours_semaine(date(2024, 1, 17))  # Mercredi
        assert len(jours) == 7
        assert jours[0] == date(2024, 1, 15)  # Lundi
        assert jours[6] == date(2024, 1, 21)  # Dimanche
        
    def test_get_semaine_precedente(self):
        """Semaine précédente retourne lundi -7j."""
        assert get_semaine_precedente(date(2024, 1, 15)) == date(2024, 1, 8)
        
    def test_get_semaine_suivante(self):
        """Semaine suivante retourne lundi +7j."""
        assert get_semaine_suivante(date(2024, 1, 15)) == date(2024, 1, 22)


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION REPAS
# ═══════════════════════════════════════════════════════════


class TestConvertirRepas:
    """Tests pour convertir_repas_en_evenement."""
    
    def test_repas_none(self):
        """Retourne None si repas None."""
        assert convertir_repas_en_evenement(None) is None
        
    def test_repas_diner(self):
        """Convertit un dîner."""
        repas = MagicMock()
        repas.id = 1
        repas.type_repas = "dîner"
        repas.date_repas = date(2024, 1, 15)
        repas.recette = MagicMock()
        repas.recette.nom = "Gratin"
        repas.recette.id = 10
        repas.recette.instructions_bebe = "Mixer le gratin"
        repas.prepare = True
        repas.notes = "Extra fromage"
        
        evt = convertir_repas_en_evenement(repas)
        
        assert evt is not None
        assert evt.type == TypeEvenement.REPAS_SOIR
        assert evt.titre == "Gratin"
        assert evt.recette_id == 10
        assert evt.version_jules == "Mixer le gratin"
        assert evt.terminé is True
        assert evt.notes == "Extra fromage"
        
    def test_repas_dejeuner(self):
        """Convertit un déjeuner (non dîner)."""
        repas = MagicMock()
        repas.id = 2
        repas.type_repas = "déjeuner"
        repas.date_repas = date(2024, 1, 15)
        repas.recette = None
        
        evt = convertir_repas_en_evenement(repas)
        
        assert evt is not None
        assert evt.type == TypeEvenement.REPAS_MIDI
        assert evt.titre == "Repas non défini"
        
    def test_repas_sans_recette(self):
        """Repas sans recette associée."""
        repas = MagicMock()
        repas.id = 3
        repas.type_repas = "déjeuner"
        repas.date_repas = date.today()
        repas.recette = None
        
        evt = convertir_repas_en_evenement(repas)
        
        assert evt.titre == "Repas non défini"
        assert evt.recette_id is None
        
    def test_repas_avec_erreur(self):
        """Erreur lors de la conversion retourne None."""
        repas = MagicMock()
        # Forcer une exception en rendant id non accessible
        type(repas).id = property(lambda x: (_ for _ in ()).throw(Exception("Test error")))
        
        result = convertir_repas_en_evenement(repas)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION SESSION BATCH
# ═══════════════════════════════════════════════════════════


class TestConvertirSessionBatch:
    """Tests pour convertir_session_batch_en_evenement."""
    
    def test_session_none(self):
        """Retourne None si session None."""
        assert convertir_session_batch_en_evenement(None) is None
        
    def test_session_complete(self):
        """Convertit une session batch complète."""
        session = MagicMock()
        session.id = 5
        session.date_session = date(2024, 1, 21)
        session.heure_debut = time(14, 0)
        session.recettes_planifiees = ["Recette 1", "Recette 2", "Recette 3"]
        session.avec_jules = True
        session.statut = "terminee"
        session.notes = "Bien prévoir les contenants"
        
        evt = convertir_session_batch_en_evenement(session)
        
        assert evt is not None
        assert evt.type == TypeEvenement.BATCH_COOKING
        assert "3 plats" in evt.titre
        assert evt.heure_debut == time(14, 0)
        assert evt.pour_jules is True
        assert evt.terminé is True
        assert evt.session_id == 5
        
    def test_session_sans_recettes(self):
        """Session sans recettes planifiées."""
        session = MagicMock()
        session.id = 6
        session.date_session = date.today()
        session.recettes_planifiees = None
        session.statut = "planifiee"
        del session.heure_debut  # Pas d'heure définie
        del session.avec_jules
        del session.notes
        
        # Redéfinir hasattr behavior
        evt = convertir_session_batch_en_evenement(session)
        
        assert evt is not None
        assert evt.titre == "Session Batch Cooking"
        
    def test_session_avec_erreur(self):
        """Erreur lors de la conversion retourne None."""
        session = MagicMock()
        type(session).id = property(lambda x: (_ for _ in ()).throw(Exception("Test")))
        
        result = convertir_session_batch_en_evenement(session)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION ACTIVITÉ
# ═══════════════════════════════════════════════════════════


class TestConvertirActivite:
    """Tests pour convertir_activite_en_evenement."""
    
    def test_activite_none(self):
        """Retourne None si activité None."""
        assert convertir_activite_en_evenement(None) is None
        
    def test_activite_standard(self):
        """Convertit une activité standard."""
        activite = MagicMock()
        activite.id = 10
        activite.type_activite = "loisir"
        activite.titre = "Parc avec Jules"
        activite.date_prevue = date(2024, 1, 20)
        activite.heure_debut = time(15, 0)
        activite.lieu = "Parc Monceau"
        activite.pour_jules = True
        activite.cout_estime = 0.0
        activite.statut = "planifie"
        activite.notes = "Prendre goûter"
        
        evt = convertir_activite_en_evenement(activite)
        
        assert evt is not None
        assert evt.type == TypeEvenement.ACTIVITE
        assert evt.titre == "Parc avec Jules"
        assert evt.lieu == "Parc Monceau"
        assert evt.pour_jules is True
        
    def test_activite_rdv_medical(self):
        """Activité médicale convertie en RDV_MEDICAL."""
        activite = MagicMock()
        activite.id = 11
        activite.type_activite = "médical"
        activite.titre = "Vaccin"
        activite.date_prevue = date(2024, 2, 1)
        activite.heure_debut = time(10, 0)
        activite.lieu = "Cabinet"
        activite.pour_jules = True
        activite.statut = "terminé"
        
        evt = convertir_activite_en_evenement(activite)
        
        assert evt.type == TypeEvenement.RDV_MEDICAL
        assert evt.terminé is True
        
    def test_activite_rdv_medical_variantes(self):
        """Teste différentes variantes de type médical."""
        for type_med in ["medical", "santé", "rdv_medical"]:
            activite = MagicMock()
            activite.id = 12
            activite.type_activite = type_med
            activite.titre = "Test"
            activite.date_prevue = date.today()
            
            evt = convertir_activite_en_evenement(activite)
            assert evt.type == TypeEvenement.RDV_MEDICAL
            
    def test_activite_avec_erreur(self):
        """Erreur lors de la conversion retourne None."""
        activite = MagicMock()
        type(activite).id = property(lambda x: (_ for _ in ()).throw(Exception("Test")))
        
        result = convertir_activite_en_evenement(activite)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION EVENT CALENDRIER
# ═══════════════════════════════════════════════════════════


class TestConvertirEventCalendrier:
    """Tests pour convertir_event_calendrier_en_evenement."""
    
    def test_event_none(self):
        """Retourne None si event None."""
        assert convertir_event_calendrier_en_evenement(None) is None
        
    def test_event_standard(self):
        """Convertit un événement standard."""
        event = MagicMock()
        event.id = 20
        event.type_event = "standard"
        event.titre = "Réunion famille"
        event.date_debut = datetime(2024, 1, 20, 16, 0)
        event.lieu = "Maison"
        event.description = "Anniversaire"
        event.termine = False
        
        evt = convertir_event_calendrier_en_evenement(event)
        
        assert evt is not None
        assert evt.type == TypeEvenement.EVENEMENT
        assert evt.titre == "Réunion famille"
        assert evt.heure_debut == time(16, 0)
        assert evt.date_jour == date(2024, 1, 20)
        
    def test_event_medical(self):
        """Événement médical."""
        event = MagicMock()
        event.id = 21
        event.type_event = "médical"
        event.titre = "RDV dentiste"
        event.date_debut = datetime(2024, 1, 25, 9, 0)
        
        evt = convertir_event_calendrier_en_evenement(event)
        
        assert evt.type == TypeEvenement.RDV_MEDICAL
        
    def test_event_courses(self):
        """Événement courses/shopping."""
        for type_c in ["courses", "shopping"]:
            event = MagicMock()
            event.id = 22
            event.type_event = type_c
            event.titre = "Supermarché"
            event.date_debut = date(2024, 1, 27)
            
            evt = convertir_event_calendrier_en_evenement(event)
            
            assert evt.type == TypeEvenement.COURSES
            
    def test_event_avec_date_simple(self):
        """Événement avec date (pas datetime)."""
        event = MagicMock()
        event.id = 23
        event.type_event = "standard"
        event.titre = "Journée"
        event.date_debut = date(2024, 2, 1)
        
        evt = convertir_event_calendrier_en_evenement(event)
        
        assert evt.date_jour == date(2024, 2, 1)
        assert evt.heure_debut is None
        
    def test_event_avec_erreur(self):
        """Erreur lors de la conversion retourne None."""
        event = MagicMock()
        type(event).id = property(lambda x: (_ for _ in ()).throw(Exception("Test")))
        
        result = convertir_event_calendrier_en_evenement(event)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION TACHE MENAGE
# ═══════════════════════════════════════════════════════════


class TestConvertirTacheMenage:
    """Tests pour convertir_tache_menage_en_evenement."""
    
    def test_tache_none(self):
        """Retourne None si tâche None."""
        assert convertir_tache_menage_en_evenement(None) is None
        
    def test_tache_menage(self):
        """Convertit une tâche ménage."""
        tache = MagicMock()
        tache.id = 30
        tache.categorie = "menage"
        tache.nom = "Aspirateur salon"
        tache.prochaine_fois = date(2024, 1, 16)
        tache.responsable = "Maman"
        tache.duree_minutes = 30
        tache.description = "Salon et couloir"
        tache.fait = False
        tache.notes = None
        
        evt = convertir_tache_menage_en_evenement(tache)
        
        assert evt is not None
        assert evt.type == TypeEvenement.MENAGE
        assert "Aspirateur salon" in evt.titre
        assert "(Maman)" in evt.titre
        assert "30min" in evt.description
        
    def test_tache_jardin(self):
        """Tâche catégorie jardin."""
        for cat in ["jardin", "exterieur", "pelouse"]:
            tache = MagicMock()
            tache.id = 31
            tache.categorie = cat
            tache.nom = "Tondre"
            tache.prochaine_fois = date.today()
            tache.fait = False
            
            evt = convertir_tache_menage_en_evenement(tache)
            
            assert evt.type == TypeEvenement.JARDIN
            
    def test_tache_entretien(self):
        """Tâche catégorie entretien."""
        tache = MagicMock()
        tache.id = 32
        tache.categorie = "autre"
        tache.nom = "Chaudière"
        tache.prochaine_fois = date.today()
        
        evt = convertir_tache_menage_en_evenement(tache)
        
        assert evt.type == TypeEvenement.ENTRETIEN
        
    def test_tache_en_retard(self):
        """Tâche en retard marque la note."""
        tache = MagicMock()
        tache.id = 33
        tache.categorie = "menage"
        tache.nom = "Nettoyage"
        tache.prochaine_fois = date.today() - timedelta(days=5)
        tache.fait = False
        
        evt = convertir_tache_menage_en_evenement(tache)
        
        assert "EN RETARD" in evt.notes
        
    def test_tache_sans_prochaine_fois(self):
        """Tâche sans date utilise aujourd'hui."""
        tache = MagicMock()
        tache.id = 34
        tache.categorie = "menage"
        tache.nom = "Test"
        tache.prochaine_fois = None
        
        evt = convertir_tache_menage_en_evenement(tache)
        
        assert evt.date_jour == date.today()
        
    def test_tache_avec_erreur(self):
        """Erreur lors de la conversion retourne None."""
        tache = MagicMock()
        type(tache).id = property(lambda x: (_ for _ in ()).throw(Exception("Test")))
        
        result = convertir_tache_menage_en_evenement(tache)
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS GENERER TACHES MENAGE SEMAINE
# ═══════════════════════════════════════════════════════════


class TestGenererTachesMenageSemaine:
    """Tests pour generer_taches_menage_semaine."""
    
    def test_liste_vide(self):
        """Liste vide retourne dict vide."""
        result = generer_taches_menage_semaine(
            [], date(2024, 1, 15), date(2024, 1, 21)
        )
        assert result == {}
        
    def test_tache_non_integree(self):
        """Tâche non intégrée au planning ignorée."""
        tache = MagicMock()
        tache.integrer_planning = False
        
        result = generer_taches_menage_semaine(
            [tache], date(2024, 1, 15), date(2024, 1, 21)
        )
        assert result == {}
        
    def test_tache_dans_semaine(self):
        """Tâche avec prochaine_fois dans la semaine."""
        tache = MagicMock()
        tache.id = 40
        tache.integrer_planning = True
        tache.prochaine_fois = date(2024, 1, 17)
        tache.frequence_jours = None
        tache.categorie = "menage"
        tache.nom = "Aspirateur"
        
        result = generer_taches_menage_semaine(
            [tache], date(2024, 1, 15), date(2024, 1, 21)
        )
        
        assert date(2024, 1, 17) in result
        assert len(result[date(2024, 1, 17)]) == 1
        
    def test_tache_recurrente_sans_prochaine(self):
        """Tâche récurrente sans prochaine_fois distribuée sur la semaine."""
        tache = MagicMock()
        tache.id = 3  # id % 7 = 3 → Jeudi
        tache.integrer_planning = True
        tache.prochaine_fois = None
        tache.frequence_jours = 7  # Hebdomadaire
        tache.categorie = "menage"
        tache.nom = "Ménage hebdo"
        
        result = generer_taches_menage_semaine(
            [tache], date(2024, 1, 15), date(2024, 1, 21)
        )
        
        # id=3, donc jour offset = 3 → Jeudi 18 janvier
        assert date(2024, 1, 18) in result
        
    def test_tache_frequente(self):
        """Tâche très fréquente (≤7j) est incluse."""
        tache = MagicMock()
        tache.id = 1
        tache.integrer_planning = True
        tache.prochaine_fois = None
        tache.frequence_jours = 3  # Tous les 3 jours
        tache.categorie = "menage"
        tache.nom = "Fréquent"
        
        result = generer_taches_menage_semaine(
            [tache], date(2024, 1, 15), date(2024, 1, 21)
        )
        
        # Devrait avoir au moins une entrée
        assert len(result) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS CREER EVENEMENT COURSES
# ═══════════════════════════════════════════════════════════


class TestCreerEvenementCourses:
    """Tests pour creer_evenement_courses."""
    
    def test_creation_basique(self):
        """Crée un événement courses basique."""
        evt = creer_evenement_courses(
            date_jour=date(2024, 1, 20),
            magasin="Carrefour"
        )
        
        assert evt.type == TypeEvenement.COURSES
        assert evt.titre == "Courses Carrefour"
        assert evt.date_jour == date(2024, 1, 20)
        assert evt.magasin == "Carrefour"
        
    def test_avec_heure(self):
        """Crée un événement courses avec heure."""
        evt = creer_evenement_courses(
            date_jour=date(2024, 1, 20),
            magasin="Leclerc",
            heure=time(10, 30)
        )
        
        assert evt.heure_debut == time(10, 30)
        
    def test_avec_id_source(self):
        """Crée avec ID source explicite."""
        evt = creer_evenement_courses(
            date_jour=date(2024, 1, 20),
            magasin="Lidl",
            id_source=100
        )
        
        assert evt.id == "courses_100"


# ═══════════════════════════════════════════════════════════
# TESTS AGREGER EVENEMENTS JOUR
# ═══════════════════════════════════════════════════════════


class TestAgregerEvenementsJour:
    """Tests pour agreger_evenements_jour."""
    
    def test_jour_vide(self):
        """Agrège un jour sans événements."""
        jour = agreger_evenements_jour(date(2024, 1, 15))
        
        assert jour.date_jour == date(2024, 1, 15)
        assert len(jour.evenements) == 0
        
    def test_avec_repas(self):
        """Agrège avec des repas."""
        repas = MagicMock()
        repas.id = 1
        repas.date_repas = date(2024, 1, 15)
        repas.type_repas = "déjeuner"
        repas.recette = None
        
        jour = agreger_evenements_jour(
            date_jour=date(2024, 1, 15),
            repas=[repas]
        )
        
        assert len(jour.evenements) == 1
        assert jour.repas_midi is not None
        
    def test_avec_session_batch(self):
        """Agrège avec session batch."""
        session = MagicMock()
        session.id = 5
        session.date_session = date(2024, 1, 15)
        session.recettes_planifiees = ["A", "B"]
        session.statut = "planifiee"
        
        jour = agreger_evenements_jour(
            date_jour=date(2024, 1, 15),
            sessions_batch=[session]
        )
        
        assert jour.batch_cooking is not None
        
    def test_avec_activites(self):
        """Agrège avec activités."""
        activite = MagicMock()
        activite.id = 10
        activite.date_prevue = date(2024, 1, 15)
        activite.titre = "Parc"
        activite.type_activite = "loisir"
        
        jour = agreger_evenements_jour(
            date_jour=date(2024, 1, 15),
            activites=[activite]
        )
        
        assert len(jour.activites) == 1
        
    def test_avec_events(self):
        """Agrège avec events calendrier."""
        event = MagicMock()
        event.id = 20
        event.date_debut = date(2024, 1, 15)
        event.type_event = "standard"
        event.titre = "Événement"
        
        jour = agreger_evenements_jour(
            date_jour=date(2024, 1, 15),
            events=[event]
        )
        
        assert len(jour.autres_evenements) == 1
        
    def test_avec_courses_planifiees(self):
        """Agrège avec courses planifiées."""
        courses = [
            {"date": date(2024, 1, 15), "magasin": "Carrefour", "heure": time(10, 0)}
        ]
        
        jour = agreger_evenements_jour(
            date_jour=date(2024, 1, 15),
            courses_planifiees=courses
        )
        
        assert len(jour.courses) == 1
        
    def test_avec_taches_menage_pretraitees(self):
        """Agrège avec tâches ménage déjà converties."""
        tache_evt = EvenementCalendrier(
            id="menage_1", type=TypeEvenement.MENAGE,
            titre="Aspirateur", date_jour=date(2024, 1, 15)
        )
        
        jour = agreger_evenements_jour(
            date_jour=date(2024, 1, 15),
            taches_menage=[tache_evt]
        )
        
        assert len(jour.taches_menage) == 1
        
    def test_tri_par_heure(self):
        """Vérifie que les événements sont triés par heure."""
        evt1 = EvenementCalendrier(
            id="e1", type=TypeEvenement.ACTIVITE,
            titre="Tard", date_jour=date(2024, 1, 15),
            heure_debut=time(18, 0)
        )
        evt2 = EvenementCalendrier(
            id="e2", type=TypeEvenement.ACTIVITE,
            titre="Tôt", date_jour=date(2024, 1, 15),
            heure_debut=time(9, 0)
        )
        
        jour = agreger_evenements_jour(
            date_jour=date(2024, 1, 15),
            taches_menage=[evt1, evt2]
        )
        
        # Le premier devrait être celui à 9h
        assert jour.evenements[0].heure_debut == time(9, 0)


# ═══════════════════════════════════════════════════════════
# TESTS CONSTRUIRE SEMAINE CALENDRIER
# ═══════════════════════════════════════════════════════════


class TestConstruireSemaineCalendrier:
    """Tests pour construire_semaine_calendrier."""
    
    def test_semaine_vide(self):
        """Construit une semaine vide."""
        semaine = construire_semaine_calendrier(date(2024, 1, 17))  # Mercredi
        
        # Devrait aligner sur lundi
        assert semaine.date_debut == date(2024, 1, 15)
        assert len(semaine.jours) == 7
        
    def test_avec_repas_semaine(self):
        """Construit avec repas sur la semaine."""
        repas1 = MagicMock()
        repas1.id = 1
        repas1.date_repas = date(2024, 1, 15)
        repas1.type_repas = "déjeuner"
        repas1.recette = None
        
        repas2 = MagicMock()
        repas2.id = 2
        repas2.date_repas = date(2024, 1, 17)
        repas2.type_repas = "dîner"
        repas2.recette = None
        
        semaine = construire_semaine_calendrier(
            date_debut=date(2024, 1, 15),
            repas=[repas1, repas2]
        )
        
        assert semaine.nb_repas_planifies == 2
        
    def test_avec_taches_menage(self):
        """Construit avec tâches ménage à distribuer."""
        tache = MagicMock()
        tache.id = 0  # id % 7 = 0 → Lundi
        tache.integrer_planning = True
        tache.prochaine_fois = date(2024, 1, 15)
        tache.frequence_jours = 7
        tache.categorie = "menage"
        tache.nom = "Ménage"
        
        semaine = construire_semaine_calendrier(
            date_debut=date(2024, 1, 15),
            taches_menage=[tache]
        )
        
        # Vérifier qu'il y a au moins une tâche ménage sur la semaine
        total_menage = sum(len(j.taches_menage) for j in semaine.jours)
        assert total_menage >= 1


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT TEXTE
# ═══════════════════════════════════════════════════════════


class TestGenererTexteSemaine:
    """Tests pour generer_texte_semaine_pour_impression."""
    
    @pytest.fixture
    def semaine_test(self):
        """Crée une semaine pour les tests d'export."""
        lundi = date(2024, 1, 15)
        jours = []
        
        for i in range(7):
            jour_date = lundi + timedelta(days=i)
            evts = []
            
            if i == 0:  # Lundi: repas midi avec version Jules
                evt_midi = EvenementCalendrier(
                    id="midi_0", type=TypeEvenement.REPAS_MIDI,
                    titre="Pâtes bolognaise", date_jour=jour_date,
                    version_jules="Mixer finement la sauce avec des pâtes étoiles"
                )
                evts.append(evt_midi)
                
            if i == 0:  # Lundi: repas soir avec version Jules
                evt_soir = EvenementCalendrier(
                    id="soir_0", type=TypeEvenement.REPAS_SOIR,
                    titre="Gratin", date_jour=jour_date,
                    version_jules="Écraser le gratin"
                )
                evts.append(evt_soir)
                
            if i == 0:  # Lundi: goûter
                evt_gouter = EvenementCalendrier(
                    id="gouter_0", type=TypeEvenement.GOUTER,
                    titre="Compote maison", date_jour=jour_date
                )
                evts.append(evt_gouter)
                
            if i == 6:  # Dimanche: batch cooking
                evt_batch = EvenementCalendrier(
                    id="batch_6", type=TypeEvenement.BATCH_COOKING,
                    titre="Batch", date_jour=jour_date,
                    heure_debut=time(14, 0)
                )
                evts.append(evt_batch)
                
            if i == 2:  # Mercredi: courses
                evt_courses = EvenementCalendrier(
                    id="courses_2", type=TypeEvenement.COURSES,
                    titre="Courses Carrefour", date_jour=jour_date,
                    heure_debut=time(10, 30),
                    magasin="Carrefour"
                )
                evts.append(evt_courses)
                
            if i == 5:  # Samedi: activité
                evt_act = EvenementCalendrier(
                    id="act_5", type=TypeEvenement.ACTIVITE,
                    titre="Parc Jules", date_jour=jour_date,
                    heure_debut=time(15, 0)
                )
                evts.append(evt_act)
                
            if i == 3:  # Jeudi: RDV médical
                evt_rdv = EvenementCalendrier(
                    id="rdv_3", type=TypeEvenement.RDV_MEDICAL,
                    titre="Vaccin Jules", date_jour=jour_date,
                    heure_debut=time(9, 30)
                )
                evts.append(evt_rdv)
                
            if i == 4:  # Vendredi: RDV autre
                evt_rdv2 = EvenementCalendrier(
                    id="rdv_4", type=TypeEvenement.RDV_AUTRE,
                    titre="Réunion école", date_jour=jour_date,
                    heure_debut=time(18, 0)
                )
                evts.append(evt_rdv2)
                
            jours.append(JourCalendrier(date_jour=jour_date, evenements=evts))
            
        return SemaineCalendrier(date_debut=lundi, jours=jours)
    
    def test_genere_texte_avec_titre(self, semaine_test):
        """Vérifie que le titre de semaine est présent."""
        texte = generer_texte_semaine_pour_impression(semaine_test)
        
        assert "SEMAINE DU" in texte
        assert "15/01" in texte
        
    def test_genere_texte_avec_repas_midi(self, semaine_test):
        """Vérifie repas midi dans le texte."""
        texte = generer_texte_semaine_pour_impression(semaine_test)
        
        assert "🌞 Midi:" in texte
        assert "Pâtes bolognaise" in texte
        
    def test_genere_texte_avec_repas_soir(self, semaine_test):
        """Vérifie repas soir dans le texte."""
        texte = generer_texte_semaine_pour_impression(semaine_test)
        
        assert "🌙 Soir:" in texte
        assert "Gratin" in texte
        
    def test_genere_texte_avec_version_jules(self, semaine_test):
        """Vérifie version Jules dans le texte."""
        texte = generer_texte_semaine_pour_impression(semaine_test)
        
        assert "👶 Jules:" in texte
        
    def test_genere_texte_avec_gouter(self, semaine_test):
        """Vérifie goûter dans le texte."""
        texte = generer_texte_semaine_pour_impression(semaine_test)
        
        assert "🍰 Goûter:" in texte
        
    def test_genere_texte_avec_batch(self, semaine_test):
        """Vérifie batch cooking dans le texte."""
        texte = generer_texte_semaine_pour_impression(semaine_test)
        
        assert "🍳 BATCH COOKING" in texte
        
    def test_genere_texte_avec_courses(self, semaine_test):
        """Vérifie courses dans le texte."""
        texte = generer_texte_semaine_pour_impression(semaine_test)
        
        assert "🛒 Courses:" in texte
        
    def test_genere_texte_avec_activite(self, semaine_test):
        """Vérifie activité dans le texte."""
        texte = generer_texte_semaine_pour_impression(semaine_test)
        
        assert "🎨" in texte
        assert "Parc Jules" in texte
        
    def test_genere_texte_avec_rdv_medical(self, semaine_test):
        """Vérifie RDV médical dans le texte."""
        texte = generer_texte_semaine_pour_impression(semaine_test)
        
        assert "🏥" in texte
        assert "Vaccin Jules" in texte
        
    def test_genere_texte_avec_rdv_autre(self, semaine_test):
        """Vérifie RDV autre dans le texte."""
        texte = generer_texte_semaine_pour_impression(semaine_test)
        
        assert "📅" in texte
        assert "Réunion école" in texte
        
    def test_genere_texte_jour_vide(self):
        """Vérifie affichage jour vide."""
        semaine = SemaineCalendrier(
            date_debut=date(2024, 1, 15),
            jours=[JourCalendrier(date_jour=date(2024, 1, 15), evenements=[])]
            + [JourCalendrier(date_jour=date(2024, 1, 15) + timedelta(days=i)) 
               for i in range(1, 7)]
        )
        
        texte = generer_texte_semaine_pour_impression(semaine)
        
        assert "(rien de planifié)" in texte
        
    def test_genere_texte_statistiques(self, semaine_test):
        """Vérifie les statistiques en fin de texte."""
        texte = generer_texte_semaine_pour_impression(semaine_test)
        
        assert "repas" in texte.lower()
        assert "batch" in texte.lower()
        assert "courses" in texte.lower()


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT HTML
# ═══════════════════════════════════════════════════════════


class TestGenererHtmlSemaine:
    """Tests pour generer_html_semaine_pour_impression."""
    
    @pytest.fixture
    def semaine_html_test(self):
        """Crée une semaine pour tests HTML."""
        lundi = date(2024, 1, 15)
        jours = []
        
        for i in range(7):
            jour_date = lundi + timedelta(days=i)
            evts = []
            
            if i == 0:
                evts.append(EvenementCalendrier(
                    id="midi_0", type=TypeEvenement.REPAS_MIDI,
                    titre="Quiche lorraine", date_jour=jour_date,
                    version_jules="Couper en petits morceaux pour Jules qui mange seul maintenant"
                ))
                evts.append(EvenementCalendrier(
                    id="soir_0", type=TypeEvenement.REPAS_SOIR,
                    titre="Soupe", date_jour=jour_date,
                    version_jules="Adapter texture"
                ))
                
            if i == 6:
                evts.append(EvenementCalendrier(
                    id="batch_6", type=TypeEvenement.BATCH_COOKING,
                    titre="Batch", date_jour=jour_date,
                    heure_debut=time(14, 0)
                ))
                
            if i == 2:
                evts.append(EvenementCalendrier(
                    id="courses_2", type=TypeEvenement.COURSES,
                    titre="Courses", date_jour=jour_date,
                    heure_debut=time(10, 0),
                    magasin="Leclerc"
                ))
                
            if i == 3:
                evts.append(EvenementCalendrier(
                    id="rdv_3", type=TypeEvenement.RDV_MEDICAL,
                    titre="Pédiatre", date_jour=jour_date,
                    heure_debut=time(11, 0)
                ))
                
            jours.append(JourCalendrier(date_jour=jour_date, evenements=evts))
            
        return SemaineCalendrier(date_debut=lundi, jours=jours)
    
    def test_genere_html_structure(self, semaine_html_test):
        """Vérifie structure HTML basique."""
        html = generer_html_semaine_pour_impression(semaine_html_test)
        
        assert "<html>" in html
        assert "</html>" in html
        assert "<body>" in html
        assert "</body>" in html
        assert "<style>" in html
        
    def test_genere_html_titre(self, semaine_html_test):
        """Vérifie titre dans HTML."""
        html = generer_html_semaine_pour_impression(semaine_html_test)
        
        assert "📅 SEMAINE DU" in html
        
    def test_genere_html_repas_midi(self, semaine_html_test):
        """Vérifie repas midi dans HTML."""
        html = generer_html_semaine_pour_impression(semaine_html_test)
        
        assert "🌞 Midi:" in html
        assert "Quiche lorraine" in html
        
    def test_genere_html_repas_soir(self, semaine_html_test):
        """Vérifie repas soir dans HTML."""
        html = generer_html_semaine_pour_impression(semaine_html_test)
        
        assert "🌙 Soir:" in html
        assert "Soupe" in html
        
    def test_genere_html_version_jules_tronquee(self, semaine_html_test):
        """Vérifie version Jules tronquée à 60 chars."""
        html = generer_html_semaine_pour_impression(semaine_html_test)
        
        # La version originale fait >60 chars, devrait être tronquée
        assert "👶" in html
        assert "..." in html  # Indique troncature
        
    def test_genere_html_batch_cooking(self, semaine_html_test):
        """Vérifie batch cooking dans HTML."""
        html = generer_html_semaine_pour_impression(semaine_html_test)
        
        assert "🍳 Batch Cooking" in html
        
    def test_genere_html_courses(self, semaine_html_test):
        """Vérifie courses dans HTML."""
        html = generer_html_semaine_pour_impression(semaine_html_test)
        
        assert "🛒" in html
        
    def test_genere_html_rdv_medical(self, semaine_html_test):
        """Vérifie RDV médical dans HTML."""
        html = generer_html_semaine_pour_impression(semaine_html_test)
        
        assert "🏥" in html
        assert "Pédiatre" in html


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes du module."""
    
    def test_jours_semaine_complets(self):
        """Vérifie les 7 jours complets."""
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"
        assert JOURS_SEMAINE[6] == "Dimanche"
        
    def test_jours_semaine_courts(self):
        """Vérifie les abréviations."""
        assert len(JOURS_SEMAINE_COURT) == 7
        assert JOURS_SEMAINE_COURT[0] == "Lun"
        assert JOURS_SEMAINE_COURT[6] == "Dim"
        
    def test_emoji_type_complet(self):
        """Vérifie tous les types ont un emoji."""
        for type_evt in TypeEvenement:
            assert type_evt in EMOJI_TYPE
            
    def test_couleur_type_complet(self):
        """Vérifie tous les types ont une couleur."""
        for type_evt in TypeEvenement:
            assert type_evt in COULEUR_TYPE
            assert COULEUR_TYPE[type_evt].startswith("#")
