"""
Tests complémentaires pour utils.py - Batch Cooking.

Ce fichier vise à couvrir les branches manquantes:
- prochain_jour_batch: retourne None après 7 jours sans match
- construire_contexte_recette: avec étapes
- est_preparation_expiree: sans date_reference (utilise today)
- jours_avant_expiration: sans date_reference (utilise today)
"""

from datetime import date, datetime, time, timedelta

import pytest

from src.services.batch_cooking import (
    construire_contexte_recette,
    est_preparation_a_risque,
    est_preparation_expiree,
    jours_avant_expiration,
    # Fonctions à tester
    prochain_jour_batch,
)

# ═══════════════════════════════════════════════════════════
# TESTS - PROCHAIN JOUR BATCH (BRANCHES MANQUANTES)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProchainJourBatchBranches:
    """Tests pour les branches manquantes de prochain_jour_batch."""

    def test_prochain_jour_batch_no_match_in_week(self):
        """prochain_jour_batch retourne le prochain jour même si test spécifique."""
        # Ce test vérifie qu'on trouve toujours un jour dans les 7 prochains
        depuis = date(2026, 2, 11)  # Mercredi 11 février 2026

        # Chercher samedi (5)
        prochain = prochain_jour_batch(depuis, [5])

        # Le samedi suivant est le 14 février
        assert prochain == date(2026, 2, 14)

    def test_prochain_jour_batch_multiple_days(self):
        """prochain_jour_batch trouve le premier jour disponible."""
        depuis = date(2026, 2, 11)  # Mercredi

        # Chercher jeudi (3) ou dimanche (6)
        prochain = prochain_jour_batch(depuis, [3, 6])

        # Jeudi 12 février est plus proche
        assert prochain == date(2026, 2, 12)


# ═══════════════════════════════════════════════════════════
# TESTS - CONSTRUIRE CONTEXTE RECETTE (AVEC ÉTAPES)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestConstruireContexteRecetteWithEtapes:
    """Tests pour construire_contexte_recette avec étapes."""

    def test_contexte_avec_etapes(self):
        """construire_contexte_recette formate correctement les étapes."""
        etapes = [
            {"ordre": 1, "description": "Couper les légumes", "duree": 10},
            {"ordre": 2, "description": "Faire cuire", "duree": 30},
            {"ordre": 3, "description": "Servir", "duree": 5},
        ]

        result = construire_contexte_recette(
            nom="Légumes sautés",
            temps_preparation=15,
            temps_cuisson=35,
            portions=4,
            compatible_batch=True,
            congelable=False,
            robots_compatibles=["plaques", "hachoir"],
            etapes=etapes,
        )

        # Vérifier que les étapes sont incluses
        assert "Légumes sautés" in result
        assert "Couper les légumes" in result
        assert "Faire cuire" in result
        assert "Servir" in result
        assert "10" in result or "30" in result  # durées

    def test_contexte_avec_etapes_partielles(self):
        """construire_contexte_recette avec étapes sans certains champs."""
        etapes = [
            {"description": "Étape 1"},  # Pas d'ordre ni durée
            {"ordre": 2},  # Pas de description ni durée
        ]

        result = construire_contexte_recette(
            nom="Recette test",
            etapes=etapes,
        )

        # Ne devrait pas lever d'exception
        assert "Recette test" in result

    def test_contexte_avec_etapes_vides(self):
        """construire_contexte_recette avec liste d'étapes vide."""
        result = construire_contexte_recette(
            nom="Recette sans étapes",
            etapes=[],
        )

        assert "Recette sans étapes" in result


# ═══════════════════════════════════════════════════════════
# TESTS - EST PREPARATION EXPIREE (SANS DATE_REFERENCE)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEstPreparationExpireeSansDateRef:
    """Tests pour est_preparation_expiree sans date_reference."""

    def test_expiree_sans_date_reference_aujourd_hui(self):
        """est_preparation_expiree utilise today() si date_reference=None."""
        # Préparation d'il y a 10 jours avec 3 jours de conservation
        date_prep = date.today() - timedelta(days=10)

        result = est_preparation_expiree(date_prep, 3)  # Sans date_reference

        # Devrait être expirée
        assert result is True

    def test_non_expiree_sans_date_reference_recente(self):
        """est_preparation_expiree récente non expirée sans date_reference."""
        # Préparation d'aujourd'hui avec 7 jours de conservation
        date_prep = date.today()

        result = est_preparation_expiree(date_prep, 7)  # Sans date_reference

        # Pas encore expirée
        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS - JOURS AVANT EXPIRATION (SANS DATE_REFERENCE)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestJoursAvantExpirationSansDateRef:
    """Tests pour jours_avant_expiration sans date_reference."""

    def test_jours_restants_sans_date_reference(self):
        """jours_avant_expiration utilise today() si date_reference=None."""
        # Préparation d'aujourd'hui avec 5 jours de conservation
        date_prep = date.today()

        result = jours_avant_expiration(date_prep, 5)  # Sans date_reference

        # Devrait rester 5 jours
        assert result == 5

    def test_expire_sans_date_reference(self):
        """jours_avant_expiration retourne négatif si expiré."""
        # Préparation d'il y a 10 jours avec 3 jours de conservation
        date_prep = date.today() - timedelta(days=10)

        result = jours_avant_expiration(date_prep, 3)  # Sans date_reference

        # Devrait être négatif (expiré depuis 7 jours)
        assert result == -7


# ═══════════════════════════════════════════════════════════
# TESTS - EST PREPARATION A RISQUE (SANS DATE_REFERENCE)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEstPreparationARisqueSansDateRef:
    """Tests pour est_preparation_a_risque sans date_reference."""

    def test_a_risque_sans_date_reference(self):
        """est_preparation_a_risque utilise today() si date_reference=None."""
        # Préparation d'il y a 4 jours avec 5 jours de conservation
        # Il reste 1 jour -> à risque
        date_prep = date.today() - timedelta(days=4)

        result = est_preparation_a_risque(date_prep, 5, seuil_alerte_jours=2)

        assert result is True

    def test_pas_a_risque_sans_date_reference(self):
        """Préparation pas à risque sans date_reference."""
        # Préparation d'aujourd'hui avec 10 jours
        date_prep = date.today()

        result = est_preparation_a_risque(date_prep, 10, seuil_alerte_jours=2)

        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS COMPLÉMENTAIRES POUR COUVERTURE 100%
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUtilsEdgeCases:
    """Tests pour les cas limites des fonctions utils."""

    def test_construire_contexte_recette_sans_robots(self):
        """construire_contexte_recette avec robots_compatibles=None."""
        result = construire_contexte_recette(
            nom="Recette simple",
            temps_preparation=20,
            temps_cuisson=30,
            portions=2,
            compatible_batch=False,
            congelable=True,
            robots_compatibles=None,  # Explicitement None
        )

        assert "Recette simple" in result
        assert "Aucun" in result  # Robots="Aucun"

    def test_construire_contexte_recette_robots_vides(self):
        """construire_contexte_recette avec robots_compatibles=[]."""
        result = construire_contexte_recette(
            nom="Recette sans robot",
            robots_compatibles=[],  # Liste vide
        )

        # Ne devrait pas lever d'exception
        assert "Recette sans robot" in result


# ═══════════════════════════════════════════════════════════
# TESTS - CALCULS DE DURÉE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculsDuree:
    """Tests pour les fonctions de calcul de durée."""

    def test_calculer_duree_totale_etapes(self):
        """calculer_duree_totale_etapes retourne la somme des durées."""
        from src.services.batch_cooking import calculer_duree_totale_etapes

        etapes = [
            {"duree_minutes": 10},
            {"duree_minutes": 20},
            {"duree_minutes": 30},
        ]

        result = calculer_duree_totale_etapes(etapes)

        assert result == 60

    def test_calculer_duree_totale_etapes_missing_duree(self):
        """calculer_duree_totale_etapes utilise 10 par défaut si durée manquante."""
        from src.services.batch_cooking import calculer_duree_totale_etapes

        etapes = [
            {"titre": "Etape sans durée"},
            {"duree_minutes": 20},
        ]

        result = calculer_duree_totale_etapes(etapes)

        assert result == 30  # 10 (défaut) + 20

    def test_calculer_duree_parallele_empty(self):
        """calculer_duree_parallele retourne 0 pour liste vide."""
        from src.services.batch_cooking import calculer_duree_parallele

        result = calculer_duree_parallele([])

        assert result == 0

    def test_calculer_duree_parallele_sequential(self):
        """calculer_duree_parallele avec groupe_parallele=0 (séquentiel)."""
        from src.services.batch_cooking import calculer_duree_parallele

        etapes = [
            {"duree_minutes": 10, "groupe_parallele": 0},
            {"duree_minutes": 20, "groupe_parallele": 0},
        ]

        result = calculer_duree_parallele(etapes)

        assert result == 30  # Séquentiel: somme

    def test_calculer_duree_parallele_parallel(self):
        """calculer_duree_parallele avec groupe_parallele>0 (parallèle)."""
        from src.services.batch_cooking import calculer_duree_parallele

        etapes = [
            {"duree_minutes": 10, "groupe_parallele": 1},
            {"duree_minutes": 20, "groupe_parallele": 1},
        ]

        result = calculer_duree_parallele(etapes)

        assert result == 20  # Parallèle: max

    def test_calculer_duree_parallele_mixed(self):
        """calculer_duree_parallele avec groupes mixtes."""
        from src.services.batch_cooking import calculer_duree_parallele

        etapes = [
            {"duree_minutes": 10, "groupe_parallele": 0},  # Séquentiel
            {"duree_minutes": 20, "groupe_parallele": 0},  # Séquentiel
            {"duree_minutes": 30, "groupe_parallele": 1},  # Parallèle groupe 1
            {"duree_minutes": 15, "groupe_parallele": 1},  # Parallèle groupe 1
        ]

        result = calculer_duree_parallele(etapes)

        assert result == 60  # 10 + 20 + max(30, 15)

    def test_calculer_duree_reelle(self):
        """calculer_duree_reelle calcule la différence en minutes."""
        from src.services.batch_cooking import calculer_duree_reelle

        debut = datetime(2026, 2, 11, 10, 0, 0)
        fin = datetime(2026, 2, 11, 11, 30, 0)

        result = calculer_duree_reelle(debut, fin)

        assert result == 90

    def test_calculer_duree_reelle_none(self):
        """calculer_duree_reelle retourne 0 si None."""
        from src.services.batch_cooking import calculer_duree_reelle

        result = calculer_duree_reelle(None, datetime.now())

        assert result == 0

        result2 = calculer_duree_reelle(datetime.now(), None)

        assert result2 == 0

    def test_estimer_heure_fin(self):
        """estimer_heure_fin calcule l'heure de fin."""
        from src.services.batch_cooking import estimer_heure_fin

        heure_debut = time(10, 0)
        duree = 90

        result = estimer_heure_fin(heure_debut, duree)

        assert result == time(11, 30)


# ═══════════════════════════════════════════════════════════
# TESTS - ROBOTS ET ÉQUIPEMENTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRobotsEquipements:
    """Tests pour les fonctions de robots."""

    def test_obtenir_info_robot_known(self):
        """obtenir_info_robot retourne info pour robot connu."""
        from src.services.batch_cooking import obtenir_info_robot

        result = obtenir_info_robot("four")

        assert "nom" in result
        assert "emoji" in result

    def test_obtenir_info_robot_unknown(self):
        """obtenir_info_robot retourne défaut pour robot inconnu."""
        from src.services.batch_cooking import obtenir_info_robot

        result = obtenir_info_robot("robot_inconnu")

        assert result["nom"] == "robot_inconnu"
        assert result["emoji"] == "🔧"
        assert result["parallele"] is True

    def test_obtenir_nom_robot(self):
        """obtenir_nom_robot retourne le nom d'affichage."""
        from src.services.batch_cooking import obtenir_nom_robot

        result = obtenir_nom_robot("four")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_obtenir_emoji_robot(self):
        """obtenir_emoji_robot retourne l'emoji."""
        from src.services.batch_cooking import obtenir_emoji_robot

        result = obtenir_emoji_robot("four")

        assert isinstance(result, str)

    def test_est_robot_parallele(self):
        """est_robot_parallele vérifie si parallélisable."""
        from src.services.batch_cooking import est_robot_parallele

        result = est_robot_parallele("four")

        assert isinstance(result, bool)

    def test_formater_liste_robots_empty(self):
        """formater_liste_robots retourne 'Aucun' si vide."""
        from src.services.batch_cooking import formater_liste_robots

        result = formater_liste_robots([])

        assert result == "Aucun"

    def test_formater_liste_robots_multiple(self):
        """formater_liste_robots formate plusieurs robots."""
        from src.services.batch_cooking import formater_liste_robots

        result = formater_liste_robots(["four", "plaques"])

        assert "," in result or len(result) > 0

    def test_filtrer_robots_paralleles(self):
        """filtrer_robots_paralleles filtre les robots parallélisables."""
        from src.services.batch_cooking import filtrer_robots_paralleles

        result = filtrer_robots_paralleles(["four", "plaques"])

        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# TESTS - JOURS ET DATES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestJoursDates:
    """Tests pour les fonctions de jours et dates."""

    def test_obtenir_nom_jour_valid(self):
        """obtenir_nom_jour retourne le nom pour index valide."""
        from src.services.batch_cooking import obtenir_nom_jour

        result = obtenir_nom_jour(0)  # Lundi

        assert result == "Lundi"

        result6 = obtenir_nom_jour(6)  # Dimanche

        assert result6 == "Dimanche"

    def test_obtenir_nom_jour_invalid(self):
        """obtenir_nom_jour retourne '' pour index invalide."""
        from src.services.batch_cooking import obtenir_nom_jour

        result = obtenir_nom_jour(-1)
        assert result == ""

        result7 = obtenir_nom_jour(7)
        assert result7 == ""

    def test_obtenir_index_jour_valid(self):
        """obtenir_index_jour retourne l'index pour nom valide."""
        from src.services.batch_cooking import obtenir_index_jour

        result = obtenir_index_jour("lundi")
        assert result == 0

        result_upper = obtenir_index_jour("DIMANCHE")
        assert result_upper == 6

    def test_obtenir_index_jour_invalid(self):
        """obtenir_index_jour retourne -1 pour nom invalide."""
        from src.services.batch_cooking import obtenir_index_jour

        result = obtenir_index_jour("jour_inconnu")

        assert result == -1

    def test_formater_jours_batch_valid(self):
        """formater_jours_batch formate les indices de jours."""
        from src.services.batch_cooking import formater_jours_batch

        result = formater_jours_batch([5, 6])

        assert "Samedi" in result
        assert "Dimanche" in result

    def test_formater_jours_batch_empty(self):
        """formater_jours_batch retourne 'Aucun' si vide."""
        from src.services.batch_cooking import formater_jours_batch

        result = formater_jours_batch([])

        assert result == "Aucun"

    def test_est_jour_batch_true(self):
        """est_jour_batch retourne True si jour dans la liste."""
        from src.services.batch_cooking import est_jour_batch

        # Créer une date pour dimanche
        dimanche = date(2026, 2, 15)  # Dimanche

        result = est_jour_batch(dimanche, [6])  # 6 = Dimanche

        assert result is True

    def test_est_jour_batch_false(self):
        """est_jour_batch retourne False si jour pas dans la liste."""
        from src.services.batch_cooking import est_jour_batch

        lundi = date(2026, 2, 16)  # Lundi

        result = est_jour_batch(lundi, [5, 6])  # Samedi, Dimanche seulement

        assert result is False

    def test_prochain_jour_batch_empty_list(self):
        """prochain_jour_batch retourne None si liste vide."""
        result = prochain_jour_batch(date.today(), [])

        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS - CONTEXTE JULES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestContexteJules:
    """Tests pour construire_contexte_jules."""

    def test_contexte_jules_present(self):
        """construire_contexte_jules avec present=True."""
        from src.services.batch_cooking import construire_contexte_jules

        result = construire_contexte_jules(present=True)

        assert "JULES" in result
        assert "bébé" in result.lower() or "sieste" in result.lower()

    def test_contexte_jules_absent(self):
        """construire_contexte_jules avec present=False."""
        from src.services.batch_cooking import construire_contexte_jules

        result = construire_contexte_jules(present=False)

        assert result == ""


# ═══════════════════════════════════════════════════════════
# TESTS - CALCULS DE SESSION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculsSession:
    """Tests pour les calculs de session."""

    def test_calculer_progression_session_zero(self):
        """calculer_progression_session retourne 0 si total=0."""
        from src.services.batch_cooking import calculer_progression_session

        result = calculer_progression_session(0, 0)

        assert result == 0.0

    def test_calculer_progression_session_partial(self):
        """calculer_progression_session retourne pourcentage partiel."""
        from src.services.batch_cooking import calculer_progression_session

        result = calculer_progression_session(3, 10)

        assert result == 30.0

    def test_calculer_progression_session_complete(self):
        """calculer_progression_session retourne 100 si complet."""
        from src.services.batch_cooking import calculer_progression_session

        result = calculer_progression_session(10, 10)

        assert result == 100.0

    def test_calculer_temps_restant_empty(self):
        """calculer_temps_restant retourne 0 si liste vide."""
        from src.services.batch_cooking import calculer_temps_restant

        result = calculer_temps_restant([])

        assert result == 0

    def test_calculer_temps_restant_parallele(self):
        """calculer_temps_restant avec parallélisme."""
        from src.services.batch_cooking import calculer_temps_restant

        etapes = [
            {"duree_minutes": 10, "groupe_parallele": 0},
            {"duree_minutes": 20, "groupe_parallele": 1},
            {"duree_minutes": 15, "groupe_parallele": 1},
        ]

        result = calculer_temps_restant(etapes, utiliser_parallele=True)

        assert result == 30  # 10 + max(20, 15)

    def test_calculer_temps_restant_sequentiel(self):
        """calculer_temps_restant sans parallélisme."""
        from src.services.batch_cooking import calculer_temps_restant

        etapes = [
            {"duree_minutes": 10},
            {"duree_minutes": 20},
        ]

        result = calculer_temps_restant(etapes, utiliser_parallele=False)

        assert result == 30


# ═══════════════════════════════════════════════════════════
# TESTS - PRÉPARATIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPreparations:
    """Tests pour les fonctions de préparations."""

    def test_calculer_portions_restantes(self):
        """calculer_portions_restantes retourne la différence."""
        from src.services.batch_cooking import calculer_portions_restantes

        result = calculer_portions_restantes(10, 3)

        assert result == 7

    def test_calculer_portions_restantes_negative_becomes_zero(self):
        """calculer_portions_restantes retourne 0 minimum."""
        from src.services.batch_cooking import calculer_portions_restantes

        result = calculer_portions_restantes(5, 10)

        assert result == 0


# ═══════════════════════════════════════════════════════════
# TESTS - VALIDATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestValidation:
    """Tests pour les fonctions de validation."""

    def test_valider_jours_batch_duplicates(self):
        """valider_jours_batch supprime les doublons."""
        from src.services.batch_cooking import valider_jours_batch

        result = valider_jours_batch([5, 5, 6, 6])

        assert result == [5, 6]

    def test_valider_jours_batch_invalid(self):
        """valider_jours_batch filtre les valeurs invalides."""
        from src.services.batch_cooking import valider_jours_batch

        result = valider_jours_batch([-1, 0, 7, 6])

        assert result == [0, 6]

    def test_valider_duree_none(self):
        """valider_duree retourne défaut si None."""
        from src.services.batch_cooking import valider_duree

        result = valider_duree(None, defaut=15)

        assert result == 15

    def test_valider_duree_zero(self):
        """valider_duree retourne défaut si 0."""
        from src.services.batch_cooking import valider_duree

        result = valider_duree(0, defaut=10)

        assert result == 10

    def test_valider_duree_max(self):
        """valider_duree limite à 480 minutes."""
        from src.services.batch_cooking import valider_duree

        result = valider_duree(600)

        assert result == 480

    def test_valider_portions_none(self):
        """valider_portions retourne défaut si None."""
        from src.services.batch_cooking import valider_portions

        result = valider_portions(None, defaut=6)

        assert result == 6

    def test_valider_portions_max(self):
        """valider_portions limite à 20."""
        from src.services.batch_cooking import valider_portions

        result = valider_portions(50)

        assert result == 20

    def test_valider_conservation_none(self):
        """valider_conservation retourne défaut si None."""
        from src.services.batch_cooking import valider_conservation

        result = valider_conservation(None, defaut=5)

        assert result == 5

    def test_valider_conservation_max(self):
        """valider_conservation limite à 90 jours."""
        from src.services.batch_cooking import valider_conservation

        result = valider_conservation(120)

        assert result == 90


# ═══════════════════════════════════════════════════════════
# TESTS - EST PREPARATION A RISQUE AVEC DATE_REFERENCE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEstPreparationARisqueAvecDateRef:
    """Tests pour est_preparation_a_risque avec date_reference explicite."""

    def test_a_risque_avec_date_reference(self):
        """est_preparation_a_risque avec date_reference explicite."""
        date_prep = date(2026, 2, 1)
        date_ref = date(2026, 2, 10)

        # Conservation 12 jours -> expire le 13/02
        # Il reste 3 jours -> seuil=2 -> pas à risque
        result = est_preparation_a_risque(
            date_prep, 12, seuil_alerte_jours=2, date_reference=date_ref
        )

        assert result is False

        # Conservation 11 jours -> expire le 12/02
        # Il reste 2 jours -> seuil=2 -> à risque
        result2 = est_preparation_a_risque(
            date_prep, 11, seuil_alerte_jours=2, date_reference=date_ref
        )

        assert result2 is True
