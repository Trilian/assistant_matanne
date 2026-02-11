"""
Tests pour les fonctions utilitaires pures de batch_cooking.

Ces tests ne nécessitent pas de base de données.
"""

import pytest
from datetime import date, time, datetime, timedelta

from src.services.batch_cooking import (
    # Constantes
    JOURS_SEMAINE,
    ROBOTS_DISPONIBLES,
    # Durées
    calculer_duree_totale_etapes,
    calculer_duree_parallele,
    calculer_duree_reelle,
    estimer_heure_fin,
    # Robots
    obtenir_info_robot,
    obtenir_nom_robot,
    obtenir_emoji_robot,
    est_robot_parallele,
    formater_liste_robots,
    filtrer_robots_paralleles,
    # Jours
    obtenir_nom_jour,
    obtenir_index_jour,
    formater_jours_batch,
    est_jour_batch,
    prochain_jour_batch,
    # Contexte
    construire_contexte_recette,
    construire_contexte_jules,
    # Session
    calculer_progression_session,
    calculer_temps_restant,
    # Préparations
    calculer_portions_restantes,
    est_preparation_expiree,
    jours_avant_expiration,
    est_preparation_a_risque,
    # Validation
    valider_jours_batch,
    valider_duree,
    valider_portions,
    valider_conservation,
)


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes."""

    def test_jours_semaine_count(self):
        assert len(JOURS_SEMAINE) == 7

    def test_jours_semaine_first_last(self):
        assert JOURS_SEMAINE[0] == "Lundi"
        assert JOURS_SEMAINE[6] == "Dimanche"

    def test_robots_disponibles_count(self):
        assert len(ROBOTS_DISPONIBLES) >= 5

    def test_robots_disponibles_structure(self):
        for robot_id, info in ROBOTS_DISPONIBLES.items():
            assert "nom" in info
            assert "emoji" in info
            assert "parallele" in info


# ═══════════════════════════════════════════════════════════
# TESTS CALCULS DE DURÉE
# ═══════════════════════════════════════════════════════════


class TestCalculerDureeTotaleEtapes:
    """Tests pour calculer_duree_totale_etapes."""

    def test_liste_vide(self):
        assert calculer_duree_totale_etapes([]) == 0

    def test_une_etape(self):
        etapes = [{"duree_minutes": 15}]
        assert calculer_duree_totale_etapes(etapes) == 15

    def test_plusieurs_etapes(self):
        etapes = [
            {"duree_minutes": 15},
            {"duree_minutes": 20},
            {"duree_minutes": 30},
        ]
        assert calculer_duree_totale_etapes(etapes) == 65

    def test_etape_sans_duree(self):
        etapes = [{"titre": "Test"}]  # Pas de duree_minutes
        assert calculer_duree_totale_etapes(etapes) == 10  # Défaut


class TestCalculerDureeParallele:
    """Tests pour calculer_duree_parallele."""

    def test_liste_vide(self):
        assert calculer_duree_parallele([]) == 0

    def test_etapes_sequentielles(self):
        # Groupe 0 = séquentiel
        etapes = [
            {"duree_minutes": 15, "groupe_parallele": 0},
            {"duree_minutes": 20, "groupe_parallele": 0},
        ]
        assert calculer_duree_parallele(etapes) == 35

    def test_etapes_paralleles(self):
        # Même groupe = parallèle
        etapes = [
            {"duree_minutes": 15, "groupe_parallele": 1},
            {"duree_minutes": 20, "groupe_parallele": 1},
        ]
        # Prend le max
        assert calculer_duree_parallele(etapes) == 20

    def test_etapes_mixtes(self):
        etapes = [
            {"duree_minutes": 10, "groupe_parallele": 0},  # Séquentiel
            {"duree_minutes": 15, "groupe_parallele": 1},  # Parallèle
            {"duree_minutes": 20, "groupe_parallele": 1},  # Parallèle
        ]
        # 10 (séquentiel) + 20 (max groupe 1)
        assert calculer_duree_parallele(etapes) == 30


class TestCalculerDureeReelle:
    """Tests pour calculer_duree_reelle."""

    def test_une_heure(self):
        debut = datetime(2026, 2, 8, 10, 0)
        fin = datetime(2026, 2, 8, 11, 0)
        assert calculer_duree_reelle(debut, fin) == 60

    def test_20_minutes(self):
        debut = datetime(2026, 2, 8, 10, 0)
        fin = datetime(2026, 2, 8, 10, 20)
        assert calculer_duree_reelle(debut, fin) == 20

    def test_debut_none(self):
        assert calculer_duree_reelle(None, datetime.now()) == 0

    def test_fin_none(self):
        assert calculer_duree_reelle(datetime.now(), None) == 0


class TestEstimerHeureFin:
    """Tests pour estimer_heure_fin."""

    def test_une_heure(self):
        debut = time(10, 0)
        fin = estimer_heure_fin(debut, 60)
        assert fin.hour == 11
        assert fin.minute == 0

    def test_30_minutes(self):
        debut = time(10, 30)
        fin = estimer_heure_fin(debut, 30)
        assert fin.hour == 11
        assert fin.minute == 0

    def test_2_heures(self):
        debut = time(9, 0)
        fin = estimer_heure_fin(debut, 120)
        assert fin.hour == 11
        assert fin.minute == 0


# ═══════════════════════════════════════════════════════════
# TESTS ROBOTS
# ═══════════════════════════════════════════════════════════


class TestObtenirInfoRobot:
    """Tests pour obtenir_info_robot."""

    def test_robot_existant(self):
        info = obtenir_info_robot("cookeo")
        assert info["nom"] == "Cookeo"
        assert info["emoji"] == "🍲"

    def test_robot_inexistant(self):
        info = obtenir_info_robot("robot_inconnu")
        assert info["nom"] == "robot_inconnu"
        assert info["emoji"] == "🔧"


class TestObtenirNomRobot:
    """Tests pour obtenir_nom_robot."""

    def test_cookeo(self):
        assert obtenir_nom_robot("cookeo") == "Cookeo"

    def test_four(self):
        assert obtenir_nom_robot("four") == "Four"

    def test_inconnu(self):
        assert obtenir_nom_robot("xyz") == "xyz"


class TestObtenirEmojiRobot:
    """Tests pour obtenir_emoji_robot."""

    def test_cookeo(self):
        assert obtenir_emoji_robot("cookeo") == "🍲"

    def test_airfryer(self):
        assert obtenir_emoji_robot("airfryer") == "🍟"


class TestEstRobotParallele:
    """Tests pour est_robot_parallele."""

    def test_cookeo_parallele(self):
        assert est_robot_parallele("cookeo") is True

    def test_plaques_non_parallele(self):
        assert est_robot_parallele("plaques") is False

    def test_mixeur_non_parallele(self):
        assert est_robot_parallele("mixeur") is False


class TestFormaterListeRobots:
    """Tests pour formater_liste_robots."""

    def test_liste_vide(self):
        assert formater_liste_robots([]) == "Aucun"

    def test_un_robot(self):
        assert formater_liste_robots(["cookeo"]) == "Cookeo"

    def test_plusieurs_robots(self):
        result = formater_liste_robots(["cookeo", "four"])
        assert "Cookeo" in result
        assert "Four" in result


class TestFiltrerRobotsParalleles:
    """Tests pour filtrer_robots_paralleles."""

    def test_tous_paralleles(self):
        robots = ["cookeo", "four", "airfryer"]
        result = filtrer_robots_paralleles(robots)
        assert len(result) == 3

    def test_mixte(self):
        robots = ["cookeo", "plaques", "mixeur"]
        result = filtrer_robots_paralleles(robots)
        assert "cookeo" in result
        assert "plaques" not in result
        assert "mixeur" not in result


# ═══════════════════════════════════════════════════════════
# TESTS JOURS
# ═══════════════════════════════════════════════════════════


class TestObtenirNomJour:
    """Tests pour obtenir_nom_jour."""

    def test_lundi(self):
        assert obtenir_nom_jour(0) == "Lundi"

    def test_dimanche(self):
        assert obtenir_nom_jour(6) == "Dimanche"

    def test_invalide(self):
        assert obtenir_nom_jour(7) == ""
        assert obtenir_nom_jour(-1) == ""


class TestObtenirIndexJour:
    """Tests pour obtenir_index_jour."""

    def test_lundi(self):
        assert obtenir_index_jour("Lundi") == 0

    def test_dimanche(self):
        assert obtenir_index_jour("Dimanche") == 6

    def test_insensible_casse(self):
        assert obtenir_index_jour("MARDI") == 1
        assert obtenir_index_jour("mardi") == 1

    def test_invalide(self):
        assert obtenir_index_jour("Jour Inconnu") == -1


class TestFormaterJoursBatch:
    """Tests pour formater_jours_batch."""

    def test_liste_vide(self):
        assert formater_jours_batch([]) == "Aucun"

    def test_un_jour(self):
        assert formater_jours_batch([6]) == "Dimanche"

    def test_plusieurs_jours(self):
        result = formater_jours_batch([5, 6])
        assert "Samedi" in result
        assert "Dimanche" in result

    def test_ordre_croissant(self):
        result = formater_jours_batch([6, 5])  # Dimanche, Samedi
        # Devrait être trié: Samedi, Dimanche
        assert result.index("Samedi") < result.index("Dimanche")


class TestEstJourBatch:
    """Tests pour est_jour_batch."""

    def test_est_jour_batch(self):
        # Un dimanche
        jour = date(2026, 2, 8)  # Dimanche
        assert est_jour_batch(jour, [6]) is True  # 6 = Dimanche

    def test_nest_pas_jour_batch(self):
        jour = date(2026, 2, 8)  # Dimanche
        assert est_jour_batch(jour, [5]) is False  # 5 = Samedi


class TestProchainJourBatch:
    """Tests pour prochain_jour_batch."""

    def test_prochain_dimanche(self):
        depuis = date(2026, 2, 8)  # Dimanche
        prochain = prochain_jour_batch(depuis, [6])  # Prochain dimanche
        assert prochain == date(2026, 2, 15)

    def test_prochain_samedi(self):
        depuis = date(2026, 2, 8)  # Dimanche
        prochain = prochain_jour_batch(depuis, [5])  # Prochain samedi
        assert prochain == date(2026, 2, 14)

    def test_liste_vide(self):
        depuis = date(2026, 2, 8)
        assert prochain_jour_batch(depuis, []) is None


# ═══════════════════════════════════════════════════════════
# TESTS CONTEXTE
# ═══════════════════════════════════════════════════════════


class TestConstruireContexteRecette:
    """Tests pour construire_contexte_recette."""

    def test_contexte_minimal(self):
        result = construire_contexte_recette("Poulet rôti")
        assert "Poulet rôti" in result

    def test_contexte_complet(self):
        result = construire_contexte_recette(
            nom="Poulet rôti",
            temps_preparation=20,
            temps_cuisson=60,
            portions=4,
            compatible_batch=True,
            congelable=True,
            robots_compatibles=["four", "cookeo"],
        )
        assert "Poulet rôti" in result
        assert "20" in result
        assert "60" in result
        assert "four" in result or "cookeo" in result


class TestConstruireContexteJules:
    """Tests pour construire_contexte_jules."""

    def test_jules_present(self):
        result = construire_contexte_jules(present=True)
        assert "JULES" in result
        assert "bébé" in result.lower()

    def test_jules_absent(self):
        result = construire_contexte_jules(present=False)
        assert result == ""


# ═══════════════════════════════════════════════════════════
# TESTS SESSION
# ═══════════════════════════════════════════════════════════


class TestCalculerProgressionSession:
    """Tests pour calculer_progression_session."""

    def test_progression_zero(self):
        assert calculer_progression_session(0, 10) == 0.0

    def test_progression_50(self):
        assert calculer_progression_session(5, 10) == 50.0

    def test_progression_100(self):
        assert calculer_progression_session(10, 10) == 100.0

    def test_total_zero(self):
        assert calculer_progression_session(0, 0) == 0.0


class TestCalculerTempsRestant:
    """Tests pour calculer_temps_restant."""

    def test_liste_vide(self):
        assert calculer_temps_restant([]) == 0

    def test_avec_parallele(self):
        etapes = [
            {"duree_minutes": 20, "groupe_parallele": 1},
            {"duree_minutes": 30, "groupe_parallele": 1},
        ]
        assert calculer_temps_restant(etapes, utiliser_parallele=True) == 30

    def test_sans_parallele(self):
        etapes = [
            {"duree_minutes": 20, "groupe_parallele": 1},
            {"duree_minutes": 30, "groupe_parallele": 1},
        ]
        assert calculer_temps_restant(etapes, utiliser_parallele=False) == 50


# ═══════════════════════════════════════════════════════════
# TESTS PRÉPARATIONS
# ═══════════════════════════════════════════════════════════


class TestCalculerPortionsRestantes:
    """Tests pour calculer_portions_restantes."""

    def test_portions_restantes(self):
        assert calculer_portions_restantes(10, 3) == 7

    def test_toutes_consommees(self):
        assert calculer_portions_restantes(10, 10) == 0

    def test_surconsommation(self):
        # Ne peut pas être négatif
        assert calculer_portions_restantes(5, 10) == 0


class TestEstPreparationExpiree:
    """Tests pour est_preparation_expiree."""

    def test_non_expiree(self):
        date_prep = date(2026, 2, 8)
        date_ref = date(2026, 2, 10)
        assert est_preparation_expiree(date_prep, 5, date_ref) is False

    def test_expiree(self):
        date_prep = date(2026, 2, 1)
        date_ref = date(2026, 2, 10)
        assert est_preparation_expiree(date_prep, 3, date_ref) is True

    def test_jour_expiration(self):
        date_prep = date(2026, 2, 8)
        date_ref = date(2026, 2, 11)  # 3 jours après
        assert est_preparation_expiree(date_prep, 3, date_ref) is False


class TestJoursAvantExpiration:
    """Tests pour jours_avant_expiration."""

    def test_jours_restants(self):
        date_prep = date(2026, 2, 8)
        date_ref = date(2026, 2, 10)
        result = jours_avant_expiration(date_prep, 5, date_ref)
        assert result == 3  # 8 + 5 = 13, 13 - 10 = 3

    def test_expiration_passee(self):
        date_prep = date(2026, 2, 1)
        date_ref = date(2026, 2, 10)
        result = jours_avant_expiration(date_prep, 3, date_ref)
        assert result < 0


class TestEstPreparationARisque:
    """Tests pour est_preparation_a_risque."""

    def test_a_risque(self):
        date_prep = date(2026, 2, 8)
        date_ref = date(2026, 2, 10)  # 2 jours après, conservation 3j
        assert est_preparation_a_risque(date_prep, 3, 2, date_ref) is True

    def test_pas_a_risque(self):
        date_prep = date(2026, 2, 8)
        date_ref = date(2026, 2, 9)  # 1 jour après, conservation 7j
        assert est_preparation_a_risque(date_prep, 7, 2, date_ref) is False

    def test_deja_expiree(self):
        date_prep = date(2026, 2, 1)
        date_ref = date(2026, 2, 10)  # 9 jours après, conservation 3j
        # Expiré n'est pas "à risque"
        assert est_preparation_a_risque(date_prep, 3, 2, date_ref) is False


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValiderJoursBatch:
    """Tests pour valider_jours_batch."""

    def test_valides(self):
        assert valider_jours_batch([0, 1, 6]) == [0, 1, 6]

    def test_doublons(self):
        assert valider_jours_batch([6, 6, 5]) == [5, 6]

    def test_invalides(self):
        assert valider_jours_batch([7, -1, 10]) == []

    def test_mixte(self):
        assert valider_jours_batch([6, 7, 5, -1]) == [5, 6]


class TestValiderDuree:
    """Tests pour valider_duree."""

    def test_duree_valide(self):
        assert valider_duree(30) == 30

    def test_duree_none(self):
        assert valider_duree(None) == 10  # Défaut

    def test_duree_zero(self):
        assert valider_duree(0) == 10  # Défaut

    def test_duree_trop_longue(self):
        assert valider_duree(600) == 480  # Max 8h


class TestValiderPortions:
    """Tests pour valider_portions."""

    def test_portions_valides(self):
        assert valider_portions(6) == 6

    def test_portions_none(self):
        assert valider_portions(None) == 4  # Défaut

    def test_portions_trop(self):
        assert valider_portions(50) == 20  # Max


class TestValiderConservation:
    """Tests pour valider_conservation."""

    def test_conservation_valide(self):
        assert valider_conservation(7) == 7

    def test_conservation_none(self):
        assert valider_conservation(None) == 3  # Défaut

    def test_conservation_trop_longue(self):
        assert valider_conservation(120) == 90  # Max
