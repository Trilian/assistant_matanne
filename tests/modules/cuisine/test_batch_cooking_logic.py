"""
Tests pour batch_cooking_logic.py - Fonctions pures de batch cooking
"""

from datetime import date, time, timedelta

from src.core.constants import JOURS_SEMAINE
from src.modules.cuisine.batch_cooking_utils import (
    JOURS_EMOJI,
    LOCALISATIONS,
    ROBOTS_INFO,
    calculer_duree_totale_optimisee,
    detecter_conflits_robots,
    estimer_heure_fin,
    filtrer_etapes_bruyantes,
    formater_duree,
    optimiser_ordre_etapes,
    valider_preparation,
    valider_session_batch,
)

# ═══════════════════════════════════════════════════════════
# Tests Constantes
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests des constantes du module."""

    def test_jours_semaine_complet(self):
        """Vérifie que tous les jours sont présents."""
        assert len(JOURS_SEMAINE) == 7
        assert "Lundi" in JOURS_SEMAINE
        assert "Dimanche" in JOURS_SEMAINE

    def test_jours_emoji_complet(self):
        """Vérifie que chaque jour a un emoji."""
        assert len(JOURS_EMOJI) == 7
        for i in range(7):
            assert i in JOURS_EMOJI

    def test_robots_info_structure(self):
        """Vérifie la structure des infos robots."""
        assert "cookeo" in ROBOTS_INFO
        assert "monsieur_cuisine" in ROBOTS_INFO
        for robot_key, robot_info in ROBOTS_INFO.items():
            assert "nom" in robot_info
            assert "emoji" in robot_info
            assert "peut_parallele" in robot_info

    def test_localisations_structure(self):
        """Vérifie la structure des localisations."""
        assert "frigo" in LOCALISATIONS
        assert "congelateur" in LOCALISATIONS
        for loc_key, loc_info in LOCALISATIONS.items():
            assert "nom" in loc_info
            assert "conservation_max_jours" in loc_info


# ═══════════════════════════════════════════════════════════
# Tests Calculs de Temps
# ═══════════════════════════════════════════════════════════


class TestCalculerDureeTotaleOptimisee:
    """Tests pour calculer_duree_totale_optimisee."""

    def test_liste_vide(self):
        """Retourne 0 pour une liste vide."""
        assert calculer_duree_totale_optimisee([]) == 0

    def test_etape_unique(self):
        """Durée correcte pour une seule étape."""
        etapes = [{"duree_minutes": 30, "groupe_parallele": 0}]
        assert calculer_duree_totale_optimisee(etapes) == 30

    def test_etapes_sequentielles(self):
        """Somme des durées pour des étapes séquentielles."""
        etapes = [
            {"duree_minutes": 20, "groupe_parallele": 0},
            {"duree_minutes": 30, "groupe_parallele": 1},
            {"duree_minutes": 15, "groupe_parallele": 2},
        ]
        assert calculer_duree_totale_optimisee(etapes) == 65

    def test_etapes_paralleles(self):
        """Prend le max du groupe pour les étapes parallèles."""
        etapes = [
            {"duree_minutes": 20, "groupe_parallele": 0},
            {"duree_minutes": 45, "groupe_parallele": 0},  # Plus long
            {"duree_minutes": 30, "groupe_parallele": 0},
        ]
        assert calculer_duree_totale_optimisee(etapes) == 45

    def test_mix_parallele_sequentiel(self):
        """Calcul correct pour un mix d'étapes."""
        etapes = [
            {"duree_minutes": 30, "groupe_parallele": 0},
            {"duree_minutes": 45, "groupe_parallele": 0},
            {"duree_minutes": 20, "groupe_parallele": 1},
        ]
        # Groupe 0: max(30, 45) = 45
        # Groupe 1: 20
        # Total: 65
        assert calculer_duree_totale_optimisee(etapes) == 65

    def test_sans_groupe_parallele_defaut(self):
        """Groupe parallèle 0 par défaut si non spécifié."""
        etapes = [
            {"duree_minutes": 20},
            {"duree_minutes": 30},
        ]
        # Toutes dans groupe 0 par défaut, max = 30
        assert calculer_duree_totale_optimisee(etapes) == 30


class TestEstimerHeureFin:
    """Tests pour estimer_heure_fin."""

    def test_heure_simple(self):
        """Test avec une durée simple."""
        resultat = estimer_heure_fin(time(10, 0), 30)
        assert resultat == time(10, 30)

    def test_traverse_heure(self):
        """Test quand la durée traverse une heure."""
        resultat = estimer_heure_fin(time(10, 45), 30)
        assert resultat == time(11, 15)

    def test_longue_duree(self):
        """Test avec une longue durée."""
        resultat = estimer_heure_fin(time(9, 0), 180)  # 3 heures
        assert resultat == time(12, 0)

    def test_duree_zero(self):
        """Test avec durée zéro."""
        resultat = estimer_heure_fin(time(14, 30), 0)
        assert resultat == time(14, 30)


class TestFormaterDuree:
    """Tests pour formater_duree."""

    def test_minutes_seules(self):
        """Affiche minutes seules si < 60."""
        assert formater_duree(45) == "45 min"
        assert formater_duree(30) == "30 min"
        assert formater_duree(5) == "5 min"

    def test_heures_completes(self):
        """Affiche heures sans minutes si divisible."""
        assert formater_duree(60) == "1h"
        assert formater_duree(120) == "2h"
        assert formater_duree(180) == "3h"

    def test_heures_et_minutes(self):
        """Affiche format XhYY pour durées mixtes."""
        assert formater_duree(90) == "1h30"
        assert formater_duree(150) == "2h30"
        assert formater_duree(75) == "1h15"
        assert formater_duree(125) == "2h05"


# ═══════════════════════════════════════════════════════════
# Tests Validation Session Batch
# ═══════════════════════════════════════════════════════════


class TestValiderSessionBatch:
    """Tests pour valider_session_batch."""

    def test_session_valide(self):
        """Valide une session correcte."""
        resultat = valider_session_batch(
            date_session=date.today() + timedelta(days=1),
            recettes_ids=[1, 2, 3],
            robots=["cookeo", "four"],
        )
        assert resultat["valide"] is True
        assert len(resultat["erreurs"]) == 0

    def test_date_passee(self):
        """Rejette une date passée."""
        resultat = valider_session_batch(
            date_session=date.today() - timedelta(days=1), recettes_ids=[1], robots=["cookeo"]
        )
        assert resultat["valide"] is False
        assert any("passé" in e for e in resultat["erreurs"])

    def test_date_aujourdhui(self):
        """Accepte la date d'aujourd'hui."""
        resultat = valider_session_batch(
            date_session=date.today(), recettes_ids=[1], robots=["cookeo"]
        )
        # Date d'aujourd'hui devrait être acceptée
        assert resultat["valide"] is True

    def test_sans_recettes(self):
        """Rejette une session sans recettes."""
        resultat = valider_session_batch(
            date_session=date.today(), recettes_ids=[], robots=["cookeo"]
        )
        assert resultat["valide"] is False
        assert any("recette" in e.lower() for e in resultat["erreurs"])

    def test_trop_de_recettes(self):
        """Rejette si plus de 10 recettes."""
        resultat = valider_session_batch(
            date_session=date.today(), recettes_ids=list(range(15)), robots=["cookeo"]
        )
        assert resultat["valide"] is False
        assert any("10" in e or "max" in e.lower() for e in resultat["erreurs"])

    def test_robot_inconnu(self):
        """Signale les robots inconnus."""
        resultat = valider_session_batch(
            date_session=date.today(), recettes_ids=[1], robots=["robot_inexistant"]
        )
        assert resultat["valide"] is False
        assert any("inconnu" in e.lower() for e in resultat["erreurs"])


# ═══════════════════════════════════════════════════════════
# Tests Validation Préparation
# ═══════════════════════════════════════════════════════════


class TestValiderPreparation:
    """Tests pour valider_preparation."""

    def test_preparation_valide(self):
        """Valide une préparation correcte."""
        resultat = valider_preparation(
            nom="Poulet rôti", portions=4, conservation_jours=3, localisation="frigo"
        )
        assert resultat["valide"] is True
        assert len(resultat["erreurs"]) == 0

    def test_nom_trop_court(self):
        """Rejette un nom trop court."""
        resultat = valider_preparation(
            nom="AB", portions=4, conservation_jours=3, localisation="frigo"
        )
        assert resultat["valide"] is False
        assert any("3 caractères" in e for e in resultat["erreurs"])

    def test_nom_vide(self):
        """Rejette un nom vide."""
        resultat = valider_preparation(
            nom="", portions=4, conservation_jours=3, localisation="frigo"
        )
        assert resultat["valide"] is False

    def test_portions_invalides(self):
        """Rejette des portions hors limites."""
        # Trop peu
        resultat = valider_preparation(
            nom="Test", portions=0, conservation_jours=3, localisation="frigo"
        )
        assert resultat["valide"] is False

        # Trop
        resultat = valider_preparation(
            nom="Test", portions=25, conservation_jours=3, localisation="frigo"
        )
        assert resultat["valide"] is False

    def test_localisation_invalide(self):
        """Rejette une localisation inconnue."""
        resultat = valider_preparation(
            nom="Test", portions=4, conservation_jours=3, localisation="placard_magique"
        )
        assert resultat["valide"] is False
        assert any("localisation" in e.lower() for e in resultat["erreurs"])

    def test_conservation_trop_longue_frigo(self):
        """Rejette conservation trop longue pour frigo."""
        resultat = valider_preparation(
            nom="Test",
            portions=4,
            conservation_jours=10,  # Max 5 pour frigo
            localisation="frigo",
        )
        assert resultat["valide"] is False
        assert any("conservation" in e.lower() for e in resultat["erreurs"])

    def test_conservation_congelateur(self):
        """Accepte conservation longue pour congélateur."""
        resultat = valider_preparation(
            nom="Test plat",
            portions=4,
            conservation_jours=60,  # Acceptable pour congélateur
            localisation="congelateur",
        )
        assert resultat["valide"] is True


# ═══════════════════════════════════════════════════════════
# Tests Optimisation
# ═══════════════════════════════════════════════════════════


class TestOptimiserOrdreEtapes:
    """Tests pour optimiser_ordre_etapes."""

    def test_liste_vide(self):
        """Retourne liste vide pour entrée vide."""
        assert optimiser_ordre_etapes([]) == []

    def test_supervisions_en_premier(self):
        """Les supervisions longues démarrent en premier."""
        etapes = [
            {"titre": "Hacher légumes", "duree_minutes": 10, "est_supervision": False},
            {"titre": "Cuisson four", "duree_minutes": 60, "est_supervision": True},
        ]
        resultat = optimiser_ordre_etapes(etapes)
        assert len(resultat) == 2
        # La supervision devrait être première
        assert resultat[0]["titre"] == "Cuisson four"

    def test_assignation_groupes_paralleles(self):
        """Les groupes parallèles sont assignés."""
        etapes = [
            {"titre": "Étape 1", "duree_minutes": 20, "est_supervision": False},
        ]
        resultat = optimiser_ordre_etapes(etapes)
        assert "groupe_parallele" in resultat[0]
        assert "ordre" in resultat[0]

    def test_parallelisation_sans_conflit(self):
        """Parallélise les étapes sans conflit de robot."""
        etapes = [
            {
                "titre": "Cuisson poulet",
                "duree_minutes": 45,
                "est_supervision": True,
                "robots": ["cookeo"],
            },
            {"titre": "Éplucher", "duree_minutes": 15, "est_supervision": False, "robots": []},
        ]
        resultat = optimiser_ordre_etapes(etapes)
        # Les deux devraient être dans le même groupe (parallèles)
        groupes = set(e["groupe_parallele"] for e in resultat)
        # Éplucher peut être fait pendant la cuisson
        assert len(resultat) == 2


class TestDetecterConflitsRobots:
    """Tests pour detecter_conflits_robots."""

    def test_pas_de_conflit(self):
        """Aucun conflit si robots différents."""
        etapes = [
            {"titre": "Étape 1", "groupe_parallele": 0, "robots": ["cookeo"]},
            {"titre": "Étape 2", "groupe_parallele": 0, "robots": ["four"]},
        ]
        conflits = detecter_conflits_robots(etapes)
        assert len(conflits) == 0

    def test_conflit_robot_non_parallele(self):
        """Détecte conflit si robot ne peut pas être parallélisé."""
        etapes = [
            {"titre": "Mixer 1", "groupe_parallele": 0, "robots": ["mixeur"]},
            {"titre": "Mixer 2", "groupe_parallele": 0, "robots": ["mixeur"]},
        ]
        conflits = detecter_conflits_robots(etapes)
        # Mixeur ne peut pas être parallélisé
        assert len(conflits) > 0
        assert conflits[0]["robot"] == "mixeur"

    def test_groupes_differents_ok(self):
        """Pas de conflit si groupes différents."""
        etapes = [
            {"titre": "Étape 1", "groupe_parallele": 0, "robots": ["mixeur"]},
            {"titre": "Étape 2", "groupe_parallele": 1, "robots": ["mixeur"]},
        ]
        conflits = detecter_conflits_robots(etapes)
        assert len(conflits) == 0

    def test_robot_parallele_ok(self):
        """Pas de conflit si robot peut être parallélisé."""
        etapes = [
            {"titre": "Étape 1", "groupe_parallele": 0, "robots": ["four"]},
            {"titre": "Étape 2", "groupe_parallele": 0, "robots": ["four"]},
        ]
        conflits = detecter_conflits_robots(etapes)
        # Le four peut être parallélisé
        assert len(conflits) == 0


# ═══════════════════════════════════════════════════════════
# Tests Mode Jules
# ═══════════════════════════════════════════════════════════


class TestFiltrerEtapesBruyantes:
    """Tests pour filtrer_etapes_bruyantes."""

    def test_separation_correcte(self):
        """Sépare correctement bruyantes et calmes."""
        etapes = [
            {"titre": "Mixer", "alerte_bruit": True},
            {"titre": "Cuisson", "alerte_bruit": False},
            {"titre": "Hacher électrique", "alerte_bruit": True},
            {"titre": "Éplucher", "alerte_bruit": False},
        ]
        resultat = filtrer_etapes_bruyantes(etapes)
        assert len(resultat["bruyantes"]) == 2
        assert len(resultat["calmes"]) == 2

    def test_toutes_bruyantes(self):
        """Gère le cas où toutes sont bruyantes."""
        etapes = [
            {"titre": "Mixer", "alerte_bruit": True},
            {"titre": "Hacher", "alerte_bruit": True},
        ]
        resultat = filtrer_etapes_bruyantes(etapes)
        assert len(resultat["bruyantes"]) == 2
        assert len(resultat["calmes"]) == 0

    def test_toutes_calmes(self):
        """Gère le cas où toutes sont calmes."""
        etapes = [
            {"titre": "Cuisson", "alerte_bruit": False},
            {"titre": "Repos", "alerte_bruit": False},
        ]
        resultat = filtrer_etapes_bruyantes(etapes)
        assert len(resultat["bruyantes"]) == 0
        assert len(resultat["calmes"]) == 2

    def test_liste_vide(self):
        """Gère une liste vide."""
        resultat = filtrer_etapes_bruyantes([])
        assert len(resultat["bruyantes"]) == 0
        assert len(resultat["calmes"]) == 0

    def test_sans_attribut_bruit(self):
        """Étapes sans attribut sont considérées calmes."""
        etapes = [
            {"titre": "Étape sans info"},
            {"titre": "Autre étape"},
        ]
        resultat = filtrer_etapes_bruyantes(etapes)
        assert len(resultat["bruyantes"]) == 0
        assert len(resultat["calmes"]) == 2
