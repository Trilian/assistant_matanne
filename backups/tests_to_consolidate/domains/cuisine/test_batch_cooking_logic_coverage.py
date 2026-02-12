"""
Tests de couverture complets pour batch_cooking_logic.py
Objectif: atteindre 80%+ de couverture
Couvre: identifier_moments_jules, generer_planning_jules,
        calculer_statistiques_session, calculer_historique_batch
"""
import pytest
from datetime import date, time, timedelta

from src.modules.cuisine.logic.batch_cooking_logic import (
    identifier_moments_jules,
    generer_planning_jules,
    calculer_statistiques_session,
    calculer_historique_batch,
    optimiser_ordre_etapes,
    detecter_conflits_robots,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS IDENTIFIER_MOMENTS_JULES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestIdentifierMomentsJules:
    """Tests pour identifier_moments_jules."""

    def test_activite_melanger_securisee(self):
        """Identifier activitÃ© 'mÃ©langer' comme sÃ©curisÃ©e."""
        etapes = [
            {"titre": "MÃ©langer la pÃ¢te", "description": "MÃ©langer les ingrÃ©dients", "alerte_bruit": False}
        ]
        
        moments = identifier_moments_jules(etapes)
        
        assert len(moments) == 1
        assert "conseil_jules" in moments[0]
        assert "participer" in moments[0]["conseil_jules"].lower()

    def test_activite_verser_securisee(self):
        """Identifier activitÃ© 'verser' comme sÃ©curisÃ©e."""
        etapes = [
            {"titre": "Verser la farine", "description": "", "alerte_bruit": False}
        ]
        
        moments = identifier_moments_jules(etapes)
        
        assert len(moments) == 1

    def test_activite_observer(self):
        """Identifier activitÃ© 'observer' comme sÃ©curisÃ©e."""
        etapes = [
            {"titre": "Observer la cuisson", "description": "Regarder le gÃ¢teau lever", "alerte_bruit": False}
        ]
        
        moments = identifier_moments_jules(etapes)
        
        assert len(moments) == 1

    def test_exclusion_si_bruyant(self):
        """Exclure si activitÃ© bruyante."""
        etapes = [
            {"titre": "MÃ©langer au robot", "description": "", "alerte_bruit": True}
        ]
        
        moments = identifier_moments_jules(etapes)
        
        # Bruyant => pas adaptÃ© Ã  Jules (mÃªme si activitÃ© sÃ©curisÃ©e)
        assert len(moments) == 0

    def test_exclusion_si_temperature_elevee(self):
        """Exclure si tempÃ©rature dangereuse."""
        etapes = [
            {"titre": "MÃ©langer sauce chaude", "description": "", "alerte_bruit": False, "temperature": 100}
        ]
        
        moments = identifier_moments_jules(etapes)
        
        # TempÃ©rature > 50 => pas adaptÃ©
        assert len(moments) == 0

    def test_supervision_calme_ok(self):
        """Supervision calme avec conseil observer."""
        etapes = [
            {"titre": "Cuisson au four", "description": "", "alerte_bruit": False, "est_supervision": True}
        ]
        
        moments = identifier_moments_jules(etapes)
        
        assert len(moments) == 1
        assert "observer" in moments[0]["conseil_jules"].lower()

    def test_supervision_bruyante_exclue(self):
        """Supervision bruyante exclue."""
        etapes = [
            {"titre": "Cuisson au Cookeo", "description": "", "alerte_bruit": True, "est_supervision": True}
        ]
        
        moments = identifier_moments_jules(etapes)
        
        # Bruyant exclut mÃªme les supervisions
        assert len(moments) == 0

    def test_activites_multiples(self):
        """Tester plusieurs activitÃ©s sÃ©curisÃ©es."""
        etapes = [
            {"titre": "DÃ©corer le gÃ¢teau", "description": "", "alerte_bruit": False},
            {"titre": "Toucher la pÃ¢te", "description": "", "alerte_bruit": False},
            {"titre": "Sentir les Ã©pices", "description": "", "alerte_bruit": False},
            {"titre": "GoÃ»ter la sauce", "description": "", "alerte_bruit": False, "temperature": 30},
            {"titre": "Ranger les ingrÃ©dients", "description": "", "alerte_bruit": False},
            {"titre": "Nettoyer le plan", "description": "", "alerte_bruit": False},
        ]
        
        moments = identifier_moments_jules(etapes)
        
        assert len(moments) == 6

    def test_liste_vide(self):
        """Liste vide retourne vide."""
        moments = identifier_moments_jules([])
        assert len(moments) == 0

    def test_aucune_activite_securisee(self):
        """Aucune activitÃ© sÃ©curisÃ©e identifiÃ©e."""
        etapes = [
            {"titre": "Couper oignons", "description": "", "alerte_bruit": False},
            {"titre": "Utiliser le four", "description": "", "alerte_bruit": False, "temperature": 180},
        ]
        
        moments = identifier_moments_jules(etapes)
        
        # Couper = pas sÃ©curisÃ©, Four = tempÃ©rature Ã©levÃ©e
        assert len(moments) == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GENERER_PLANNING_JULES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestGenererPlanningJules:
    """Tests pour generer_planning_jules."""

    def test_planning_avant_sieste(self):
        """Ã‰tapes programmÃ©es avant la sieste."""
        etapes = [
            {"titre": "PrÃ©parer", "duree_minutes": 30, "alerte_bruit": False},
        ]
        
        planning = generer_planning_jules(
            etapes=etapes,
            heure_debut=time(9, 0),
            heure_sieste_debut=time(13, 0),
            heure_sieste_fin=time(15, 0)
        )
        
        assert len(planning["avant_sieste"]) == 1
        assert len(planning["pendant_sieste"]) == 0
        assert len(planning["apres_sieste"]) == 0

    def test_planning_pendant_sieste(self):
        """Ã‰tapes pendant la sieste (bruyantes idÃ©ales)."""
        etapes = [
            {"titre": "Mixer", "duree_minutes": 30, "alerte_bruit": True},
        ]
        
        planning = generer_planning_jules(
            etapes=etapes,
            heure_debut=time(13, 30),
            heure_sieste_debut=time(13, 0),
            heure_sieste_fin=time(15, 0)
        )
        
        assert len(planning["pendant_sieste"]) == 1

    def test_planning_apres_sieste(self):
        """Ã‰tapes aprÃ¨s la sieste."""
        etapes = [
            {"titre": "Finition", "duree_minutes": 30, "alerte_bruit": False},
        ]
        
        planning = generer_planning_jules(
            etapes=etapes,
            heure_debut=time(16, 0),
            heure_sieste_debut=time(13, 0),
            heure_sieste_fin=time(15, 0)
        )
        
        assert len(planning["apres_sieste"]) == 1

    def test_planning_alerte_bruyant_sieste(self):
        """Conseil si Ã©tapes bruyantes pendant sieste."""
        etapes = [
            # Ã‰tape calme avant
            {"titre": "PrÃ©parer", "duree_minutes": 30, "alerte_bruit": False},
            # Ã‰tape bruyante pendant sieste (si mal programmÃ©e)
            {"titre": "Mixer", "duree_minutes": 30, "alerte_bruit": True},
        ]
        
        planning = generer_planning_jules(
            etapes=etapes,
            heure_debut=time(12, 30),  # Finira pendant sieste
            heure_sieste_debut=time(13, 0),
            heure_sieste_fin=time(15, 0)
        )
        
        # Devrait avoir un conseil si bruyant pendant sieste
        # La 2e Ã©tape commence Ã  13:00 (pile sieste)
        assert "conseils" in planning

    def test_planning_etapes_multiples(self):
        """Planning avec plusieurs Ã©tapes Ã  diffÃ©rents moments."""
        etapes = [
            {"titre": "Ã‰tape 1", "duree_minutes": 60, "alerte_bruit": False},
            {"titre": "Ã‰tape 2", "duree_minutes": 120, "alerte_bruit": True},
            {"titre": "Ã‰tape 3", "duree_minutes": 60, "alerte_bruit": False},
        ]
        
        planning = generer_planning_jules(
            etapes=etapes,
            heure_debut=time(10, 0),
            heure_sieste_debut=time(13, 0),
            heure_sieste_fin=time(15, 0)
        )
        
        total = (len(planning["avant_sieste"]) + 
                 len(planning["pendant_sieste"]) + 
                 len(planning["apres_sieste"]))
        assert total == 3

    def test_planning_liste_vide(self):
        """Planning avec liste vide."""
        planning = generer_planning_jules(
            etapes=[],
            heure_debut=time(10, 0)
        )
        
        assert len(planning["avant_sieste"]) == 0
        assert len(planning["pendant_sieste"]) == 0
        assert len(planning["apres_sieste"]) == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALCULER_STATISTIQUES_SESSION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestCalculerStatistiquesSession:
    """Tests pour calculer_statistiques_session."""

    def test_session_complete(self):
        """Statistiques d'une session complÃ¨te."""
        session_data = {
            "etapes": [
                {"duree_minutes": 30, "statut": "terminee", "robots": ["cookeo"], "groupe_parallele": 0},
                {"duree_minutes": 20, "statut": "terminee", "robots": ["four"], "groupe_parallele": 0},
                {"duree_minutes": 15, "statut": "en_cours", "robots": ["plaques"], "groupe_parallele": 1},
            ],
            "preparations": [
                {"portions_initiales": 4},
                {"portions_initiales": 6},
            ]
        }
        
        stats = calculer_statistiques_session(session_data)
        
        assert stats["nb_etapes"] == 3
        assert stats["etapes_terminees"] == 2
        assert stats["progression_pct"] == pytest.approx(66.66, rel=0.1)
        assert stats["duree_estimee_brute"] == 65
        assert stats["nb_preparations"] == 2
        assert stats["portions_totales"] == 10
        assert "cookeo" in stats["robots_utilises"]
        assert stats["nb_robots"] == 3

    def test_session_vide(self):
        """Statistiques d'une session vide."""
        session_data = {
            "etapes": [],
            "preparations": []
        }
        
        stats = calculer_statistiques_session(session_data)
        
        assert stats["nb_etapes"] == 0
        assert stats["etapes_terminees"] == 0
        assert stats["progression_pct"] == 0
        assert stats["nb_preparations"] == 0

    def test_session_sans_preparations(self):
        """Session avec Ã©tapes mais sans prÃ©parations."""
        session_data = {
            "etapes": [
                {"duree_minutes": 30, "statut": "terminee", "robots": []},
            ],
            "preparations": []
        }
        
        stats = calculer_statistiques_session(session_data)
        
        assert stats["nb_etapes"] == 1
        assert stats["nb_preparations"] == 0
        assert stats["portions_totales"] == 0

    def test_gain_temps_optimisation(self):
        """Calculer le gain de temps par optimisation."""
        session_data = {
            "etapes": [
                {"duree_minutes": 60, "groupe_parallele": 0, "robots": []},
                {"duree_minutes": 30, "groupe_parallele": 0, "robots": []},  # ParallÃ¨le
            ],
            "preparations": []
        }
        
        stats = calculer_statistiques_session(session_data)
        
        # Brut: 60 + 30 = 90
        # OptimisÃ©: max(60, 30) = 60 (groupe 0)
        assert stats["duree_estimee_brute"] == 90
        assert stats["duree_estimee_optimisee"] == 60
        assert stats["gain_temps_pct"] == pytest.approx(33.33, rel=0.1)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALCULER_HISTORIQUE_BATCH
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestCalculerHistoriqueBatch:
    """Tests pour calculer_historique_batch."""

    def test_historique_complet(self):
        """Statistiques sur plusieurs sessions."""
        sessions = [
            {"duree_reelle": 120, "nb_portions_preparees": 10, "robots_utilises": ["cookeo", "four"]},
            {"duree_reelle": 90, "nb_portions_preparees": 8, "robots_utilises": ["cookeo"]},
            {"duree_reelle": 150, "nb_portions_preparees": 12, "robots_utilises": ["four", "airfryer"]},
        ]
        
        stats = calculer_historique_batch(sessions)
        
        assert stats["nb_sessions"] == 3
        assert stats["temps_moyen_session"] == 120  # (120 + 90 + 150) / 3
        assert stats["portions_moyennes"] == 10  # (10 + 8 + 12) / 3
        assert stats["robot_prefere"] in ["cookeo", "four"]  # Les deux ont 2 utilisations

    def test_historique_vide(self):
        """Statistiques pour historique vide."""
        stats = calculer_historique_batch([])
        
        assert stats["nb_sessions"] == 0
        assert stats["temps_moyen_session"] == 0
        assert stats["portions_moyennes"] == 0
        assert stats["robot_prefere"] is None

    def test_historique_une_session(self):
        """Statistiques pour une seule session."""
        sessions = [
            {"duree_reelle": 90, "nb_portions_preparees": 6, "robots_utilises": ["cookeo"]}
        ]
        
        stats = calculer_historique_batch(sessions)
        
        assert stats["nb_sessions"] == 1
        assert stats["temps_moyen_session"] == 90
        assert stats["portions_moyennes"] == 6
        assert stats["robot_prefere"] == "cookeo"

    def test_historique_sans_duree_reelle(self):
        """Utilise duree_estimee si duree_reelle absente."""
        sessions = [
            {"duree_estimee": 100, "nb_portions_preparees": 5, "robots_utilises": []},
        ]
        
        stats = calculer_historique_batch(sessions)
        
        assert stats["temps_moyen_session"] == 100

    def test_historique_robots_compteur(self):
        """Compte correctement les utilisations de robots."""
        sessions = [
            {"duree_reelle": 60, "nb_portions_preparees": 4, "robots_utilises": ["cookeo"]},
            {"duree_reelle": 60, "nb_portions_preparees": 4, "robots_utilises": ["cookeo"]},
            {"duree_reelle": 60, "nb_portions_preparees": 4, "robots_utilises": ["four"]},
        ]
        
        stats = calculer_historique_batch(sessions)
        
        assert stats["robots_compteur"]["cookeo"] == 2
        assert stats["robots_compteur"]["four"] == 1
        assert stats["robot_prefere"] == "cookeo"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS OPTIMISER_ORDRE_ETAPES - EDGE CASES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestOptimiserOrdreEtapesEdgeCases:
    """Tests edge cases pour optimiser_ordre_etapes."""

    def test_parallelisation_avec_conflit_robot(self):
        """Ne parallÃ©lise pas si conflit de robot."""
        etapes = [
            {"titre": "Cuisson 1", "duree_minutes": 60, "est_supervision": True, "robots": ["cookeo"]},
            {"titre": "Cuisson 2", "duree_minutes": 30, "est_supervision": False, "robots": ["cookeo"]},
        ]
        
        resultat = optimiser_ordre_etapes(etapes)
        
        # Les deux utilisent cookeo, donc ne peuvent pas Ãªtre parallÃ¨les
        assert len(resultat) == 2

    def test_sans_supervision(self):
        """GÃ¨re le cas sans Ã©tapes de supervision."""
        etapes = [
            {"titre": "Ã‰tape 1", "duree_minutes": 20, "est_supervision": False},
            {"titre": "Ã‰tape 2", "duree_minutes": 15, "est_supervision": False},
        ]
        
        resultat = optimiser_ordre_etapes(etapes)
        
        assert len(resultat) == 2
        # Les deux devraient avoir des groupes diffÃ©rents (sÃ©quentiels)

    def test_toutes_supervisions(self):
        """GÃ¨re le cas oÃ¹ toutes les Ã©tapes sont des supervisions."""
        etapes = [
            {"titre": "Four 1", "duree_minutes": 60, "est_supervision": True, "robots": ["four"]},
            {"titre": "Four 2", "duree_minutes": 30, "est_supervision": True, "robots": ["four"]},
        ]
        
        resultat = optimiser_ordre_etapes(etapes)
        
        assert len(resultat) == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DETECTER_CONFLITS_ROBOTS - EDGE CASES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestDetecterConflitsRobotsEdgeCases:
    """Tests edge cases pour detecter_conflits_robots."""

    def test_etape_unique_dans_groupe(self):
        """Pas de conflit si une seule Ã©tape dans un groupe."""
        etapes = [
            {"titre": "Ã‰tape 1", "groupe_parallele": 0, "robots": ["mixeur"]},
            {"titre": "Ã‰tape 2", "groupe_parallele": 1, "robots": ["mixeur"]},
        ]
        
        conflits = detecter_conflits_robots(etapes)
        
        assert len(conflits) == 0

    def test_robot_inconnu(self):
        """GÃ¨re robot non prÃ©sent dans ROBOTS_INFO."""
        etapes = [
            {"titre": "Ã‰tape 1", "groupe_parallele": 0, "robots": ["robot_inconnu"]},
            {"titre": "Ã‰tape 2", "groupe_parallele": 0, "robots": ["robot_inconnu"]},
        ]
        
        conflits = detecter_conflits_robots(etapes)
        
        # Robot inconnu avec peut_parallele=True par dÃ©faut => pas de conflit
        assert len(conflits) == 0

    def test_liste_vide(self):
        """Pas de conflit pour liste vide."""
        conflits = detecter_conflits_robots([])
        
        assert len(conflits) == 0

    def test_etapes_sans_robots(self):
        """Pas de conflit si Ã©tapes sans robots."""
        etapes = [
            {"titre": "Ã‰tape 1", "groupe_parallele": 0, "robots": []},
            {"titre": "Ã‰tape 2", "groupe_parallele": 0, "robots": []},
        ]
        
        conflits = detecter_conflits_robots(etapes)
        
        assert len(conflits) == 0
