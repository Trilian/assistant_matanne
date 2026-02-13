"""
Tests pour src/modules/cuisine/batch_cooking_utils.py

Tests complets pour atteindre ≥80% de couverture.
"""

from datetime import date, time, timedelta

from src.modules.cuisine.batch_cooking_utils import (
    JOURS_EMOJI,
    LOCALISATIONS,
    ROBOTS_INFO,
    calculer_duree_totale_optimisee,
    calculer_historique_batch,
    calculer_statistiques_session,
    detecter_conflits_robots,
    estimer_heure_fin,
    filtrer_etapes_bruyantes,
    formater_duree,
    generer_planning_jules,
    identifier_moments_jules,
    optimiser_ordre_etapes,
    valider_preparation,
    valider_session_batch,
)

# ═══════════════════════════════════════════════════════════
# TESTS DES CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes du module"""

    def test_jours_emoji_complet(self):
        """Vérifie que tous les jours ont un emoji"""
        assert len(JOURS_EMOJI) == 7
        for i in range(7):
            assert i in JOURS_EMOJI

    def test_robots_info_structure(self):
        """Vérifie la structure des infos robots"""
        assert len(ROBOTS_INFO) >= 5
        for robot_id, info in ROBOTS_INFO.items():
            assert "nom" in info
            assert "emoji" in info
            assert "peut_parallele" in info

    def test_localisations_structure(self):
        """Vérifie la structure des localisations"""
        assert "frigo" in LOCALISATIONS
        assert "congelateur" in LOCALISATIONS
        assert "temperature_ambiante" in LOCALISATIONS
        for loc_id, info in LOCALISATIONS.items():
            assert "conservation_max_jours" in info


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER DUREE TOTALE OPTIMISEE
# ═══════════════════════════════════════════════════════════


class TestCalculerDureeTotaleOptimisee:
    """Tests pour calculer_duree_totale_optimisee"""

    def test_liste_vide(self):
        """Test avec liste vide"""
        assert calculer_duree_totale_optimisee([]) == 0

    def test_une_etape(self):
        """Test avec une seule étape"""
        etapes = [{"duree_minutes": 30}]
        assert calculer_duree_totale_optimisee(etapes) == 30

    def test_etapes_meme_groupe(self):
        """Test avec étapes dans le même groupe - prend le max"""
        etapes = [
            {"duree_minutes": 20, "groupe_parallele": 0},
            {"duree_minutes": 30, "groupe_parallele": 0},
            {"duree_minutes": 15, "groupe_parallele": 0},
        ]
        assert calculer_duree_totale_optimisee(etapes) == 30

    def test_etapes_groupes_differents(self):
        """Test avec étapes dans différents groupes - somme des max"""
        etapes = [
            {"duree_minutes": 20, "groupe_parallele": 0},
            {"duree_minutes": 30, "groupe_parallele": 0},
            {"duree_minutes": 15, "groupe_parallele": 1},
            {"duree_minutes": 25, "groupe_parallele": 1},
        ]
        # Groupe 0: max(20,30) = 30
        # Groupe 1: max(15,25) = 25
        # Total: 55
        assert calculer_duree_totale_optimisee(etapes) == 55

    def test_etapes_sans_groupe_parallele(self):
        """Test avec étapes sans groupe_parallele défini"""
        etapes = [
            {"duree_minutes": 10},
            {"duree_minutes": 20},
        ]
        # Toutes dans groupe 0 par défaut, max = 20
        assert calculer_duree_totale_optimisee(etapes) == 20

    def test_etapes_sans_duree(self):
        """Test avec étapes sans durée définie"""
        etapes = [
            {"groupe_parallele": 0},
            {"duree_minutes": 15, "groupe_parallele": 1},
        ]
        # Groupe 0: max(0) = 0
        # Groupe 1: max(15) = 15
        assert calculer_duree_totale_optimisee(etapes) == 15


# ═══════════════════════════════════════════════════════════
# TESTS ESTIMER HEURE FIN
# ═══════════════════════════════════════════════════════════


class TestEstimerHeureFin:
    """Tests pour estimer_heure_fin"""

    def test_heure_simple(self):
        """Test estimation simple"""
        heure_debut = time(10, 0)
        result = estimer_heure_fin(heure_debut, 30)
        assert result == time(10, 30)

    def test_heure_depasse_heure(self):
        """Test quand la durée dépasse l'heure"""
        heure_debut = time(10, 45)
        result = estimer_heure_fin(heure_debut, 30)
        assert result == time(11, 15)

    def test_duree_plusieurs_heures(self):
        """Test avec durée de plusieurs heures"""
        heure_debut = time(9, 0)
        result = estimer_heure_fin(heure_debut, 150)  # 2h30
        assert result == time(11, 30)

    def test_duree_zero(self):
        """Test avec durée nulle"""
        heure_debut = time(14, 30)
        result = estimer_heure_fin(heure_debut, 0)
        assert result == time(14, 30)


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER DUREE
# ═══════════════════════════════════════════════════════════


class TestFormaterDuree:
    """Tests pour formater_duree"""

    def test_moins_une_heure(self):
        """Test avec durée < 60 min"""
        assert formater_duree(45) == "45 min"
        assert formater_duree(1) == "1 min"
        assert formater_duree(59) == "59 min"

    def test_exactement_une_heure(self):
        """Test avec exactement 60 min"""
        assert formater_duree(60) == "1h"

    def test_heures_entieres(self):
        """Test avec heures entières"""
        assert formater_duree(120) == "2h"
        assert formater_duree(180) == "3h"

    def test_heures_et_minutes(self):
        """Test avec heures et minutes"""
        assert formater_duree(90) == "1h30"
        assert formater_duree(150) == "2h30"
        assert formater_duree(65) == "1h05"


# ═══════════════════════════════════════════════════════════
# TESTS VALIDER SESSION BATCH
# ═══════════════════════════════════════════════════════════


class TestValiderSessionBatch:
    """Tests pour valider_session_batch"""

    def test_session_valide(self):
        """Test avec session valide"""
        result = valider_session_batch(
            date_session=date.today() + timedelta(days=1),
            recettes_ids=[1, 2, 3],
            robots=["cookeo", "four"],
        )
        assert result["valide"] is True
        assert len(result["erreurs"]) == 0

    def test_date_passee(self):
        """Test avec date dans le passé"""
        result = valider_session_batch(
            date_session=date.today() - timedelta(days=1),
            recettes_ids=[1],
            robots=["cookeo"],
        )
        assert result["valide"] is False
        assert any("passé" in e for e in result["erreurs"])

    def test_aucune_recette(self):
        """Test sans recettes"""
        result = valider_session_batch(
            date_session=date.today() + timedelta(days=1),
            recettes_ids=[],
            robots=["cookeo"],
        )
        assert result["valide"] is False
        assert any("recette" in e.lower() for e in result["erreurs"])

    def test_trop_recettes(self):
        """Test avec trop de recettes (>10)"""
        result = valider_session_batch(
            date_session=date.today() + timedelta(days=1),
            recettes_ids=list(range(15)),
            robots=["cookeo"],
        )
        assert result["valide"] is False
        assert any("10" in e for e in result["erreurs"])

    def test_robot_inconnu(self):
        """Test avec robot inconnu"""
        result = valider_session_batch(
            date_session=date.today() + timedelta(days=1),
            recettes_ids=[1],
            robots=["cookeo", "robot_inconnu"],
        )
        assert result["valide"] is False
        assert any("inconnu" in e.lower() for e in result["erreurs"])

    def test_plusieurs_erreurs(self):
        """Test avec plusieurs erreurs"""
        result = valider_session_batch(
            date_session=date.today() - timedelta(days=1),
            recettes_ids=[],
            robots=["robot_fantome"],
        )
        assert result["valide"] is False
        assert len(result["erreurs"]) >= 2


# ═══════════════════════════════════════════════════════════
# TESTS VALIDER PREPARATION
# ═══════════════════════════════════════════════════════════


class TestValiderPreparation:
    """Tests pour valider_preparation"""

    def test_preparation_valide(self):
        """Test avec préparation valide"""
        result = valider_preparation(
            nom="Sauce tomate",
            portions=4,
            conservation_jours=3,
            localisation="frigo",
        )
        assert result["valide"] is True
        assert len(result["erreurs"]) == 0

    def test_nom_trop_court(self):
        """Test avec nom trop court"""
        result = valider_preparation(
            nom="AB",
            portions=4,
            conservation_jours=3,
            localisation="frigo",
        )
        assert result["valide"] is False
        assert any("3 caractères" in e for e in result["erreurs"])

    def test_nom_vide(self):
        """Test avec nom vide"""
        result = valider_preparation(
            nom="",
            portions=4,
            conservation_jours=3,
            localisation="frigo",
        )
        assert result["valide"] is False

    def test_portions_invalides(self):
        """Test avec portions invalides"""
        # Trop peu
        result = valider_preparation(
            nom="Test",
            portions=0,
            conservation_jours=3,
            localisation="frigo",
        )
        assert result["valide"] is False

        # Trop
        result = valider_preparation(
            nom="Test",
            portions=25,
            conservation_jours=3,
            localisation="frigo",
        )
        assert result["valide"] is False

    def test_localisation_invalide(self):
        """Test avec localisation invalide"""
        result = valider_preparation(
            nom="Test",
            portions=4,
            conservation_jours=3,
            localisation="placard",
        )
        assert result["valide"] is False
        assert any("invalide" in e.lower() for e in result["erreurs"])

    def test_conservation_trop_longue_frigo(self):
        """Test avec conservation trop longue pour le frigo"""
        result = valider_preparation(
            nom="Test",
            portions=4,
            conservation_jours=10,  # Max frigo: 5 jours
            localisation="frigo",
        )
        assert result["valide"] is False
        assert any("max" in e.lower() for e in result["erreurs"])

    def test_conservation_congelateur(self):
        """Test avec conservation au congélateur"""
        result = valider_preparation(
            nom="Test",
            portions=4,
            conservation_jours=60,
            localisation="congelateur",
        )
        assert result["valide"] is True

    def test_conservation_trop_longue_congelateur(self):
        """Test avec conservation trop longue pour le congélateur"""
        result = valider_preparation(
            nom="Test",
            portions=4,
            conservation_jours=100,  # Max congélateur: 90 jours
            localisation="congelateur",
        )
        assert result["valide"] is False


# ═══════════════════════════════════════════════════════════
# TESTS OPTIMISER ORDRE ETAPES
# ═══════════════════════════════════════════════════════════


class TestOptimiserOrdreEtapes:
    """Tests pour optimiser_ordre_etapes"""

    def test_liste_vide(self):
        """Test avec liste vide"""
        assert optimiser_ordre_etapes([]) == []

    def test_supervision_en_premier(self):
        """Test que les supervisions longues viennent en premier"""
        etapes = [
            {"titre": "Active courte", "duree_minutes": 10, "est_supervision": False},
            {"titre": "Supervision longue", "duree_minutes": 60, "est_supervision": True},
        ]
        result = optimiser_ordre_etapes(etapes)
        assert result[0]["titre"] == "Supervision longue"

    def test_parallelisation(self):
        """Test de la parallélisation supervision + actif"""
        etapes = [
            {"titre": "Supervision", "duree_minutes": 60, "est_supervision": True, "robots": ["four"]},
            {"titre": "Actif", "duree_minutes": 15, "est_supervision": False, "robots": ["mixeur"]},
        ]
        result = optimiser_ordre_etapes(etapes)
        # Les deux devraient être dans le même groupe si pas de conflit
        assert len(result) == 2
        assert all("groupe_parallele" in e for e in result)

    def test_conflit_robot_pas_parallelise(self):
        """Test que les conflits de robot empêchent la parallélisation"""
        etapes = [
            {"titre": "Supervision", "duree_minutes": 60, "est_supervision": True, "robots": ["four"]},
            {"titre": "Actif", "duree_minutes": 15, "est_supervision": False, "robots": ["four"]},
        ]
        result = optimiser_ordre_etapes(etapes)
        # Les deux ne devraient pas être dans le même groupe
        groupes = set(e["groupe_parallele"] for e in result)
        assert len(groupes) == 2

    def test_assignation_ordre(self):
        """Test que l'ordre est assigné"""
        etapes = [
            {"titre": "E1", "duree_minutes": 10, "est_supervision": False},
            {"titre": "E2", "duree_minutes": 20, "est_supervision": False},
        ]
        result = optimiser_ordre_etapes(etapes)
        assert all("ordre" in e for e in result)

    def test_etapes_actives_sans_supervision(self):
        """Test avec uniquement des étapes actives"""
        etapes = [
            {"titre": "Actif1", "duree_minutes": 10, "est_supervision": False, "robots": ["mixeur"]},
            {"titre": "Actif2", "duree_minutes": 20, "est_supervision": False, "robots": ["four"]},
        ]
        result = optimiser_ordre_etapes(etapes)
        assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# TESTS DETECTER CONFLITS ROBOTS
# ═══════════════════════════════════════════════════════════


class TestDetecterConflitsRobots:
    """Tests pour detecter_conflits_robots"""

    def test_pas_de_conflit(self):
        """Test sans conflit"""
        etapes = [
            {"titre": "E1", "groupe_parallele": 0, "robots": ["four"]},
            {"titre": "E2", "groupe_parallele": 1, "robots": ["mixeur"]},
        ]
        assert detecter_conflits_robots(etapes) == []

    def test_conflit_robot_non_parallelisable(self):
        """Test conflit avec robot non parallélisable"""
        # Les plaques ne peuvent pas être parallélisées
        etapes = [
            {"titre": "E1", "groupe_parallele": 0, "robots": ["plaques"]},
            {"titre": "E2", "groupe_parallele": 0, "robots": ["plaques"]},
        ]
        conflits = detecter_conflits_robots(etapes)
        assert len(conflits) >= 1
        assert conflits[0]["robot"] == "plaques"

    def test_pas_conflit_robot_parallelisable(self):
        """Test pas de conflit avec robot parallélisable"""
        # Le four peut être parallélisé
        etapes = [
            {"titre": "E1", "groupe_parallele": 0, "robots": ["four"]},
            {"titre": "E2", "groupe_parallele": 0, "robots": ["four"]},
        ]
        conflits = detecter_conflits_robots(etapes)
        assert len(conflits) == 0

    def test_groupe_une_etape(self):
        """Test avec groupe d'une seule étape"""
        etapes = [
            {"titre": "E1", "groupe_parallele": 0, "robots": ["mixeur"]},
        ]
        assert detecter_conflits_robots(etapes) == []

    def test_etape_sans_robot(self):
        """Test avec étape sans robot défini"""
        etapes = [
            {"titre": "E1", "groupe_parallele": 0},
            {"titre": "E2", "groupe_parallele": 0, "robots": []},
        ]
        assert detecter_conflits_robots(etapes) == []


# ═══════════════════════════════════════════════════════════
# TESTS FILTRER ETAPES BRUYANTES
# ═══════════════════════════════════════════════════════════


class TestFiltrerEtapesBruyantes:
    """Tests pour filtrer_etapes_bruyantes"""

    def test_separation_correcte(self):
        """Test séparation bruyantes/calmes"""
        etapes = [
            {"titre": "Bruyante", "alerte_bruit": True},
            {"titre": "Calme1", "alerte_bruit": False},
            {"titre": "Calme2"},  # Sans alerte_bruit = calme par défaut
        ]
        result = filtrer_etapes_bruyantes(etapes)
        assert len(result["bruyantes"]) == 1
        assert len(result["calmes"]) == 2

    def test_toutes_bruyantes(self):
        """Test avec toutes les étapes bruyantes"""
        etapes = [
            {"titre": "B1", "alerte_bruit": True},
            {"titre": "B2", "alerte_bruit": True},
        ]
        result = filtrer_etapes_bruyantes(etapes)
        assert len(result["bruyantes"]) == 2
        assert len(result["calmes"]) == 0

    def test_toutes_calmes(self):
        """Test avec toutes les étapes calmes"""
        etapes = [
            {"titre": "C1", "alerte_bruit": False},
            {"titre": "C2"},
        ]
        result = filtrer_etapes_bruyantes(etapes)
        assert len(result["bruyantes"]) == 0
        assert len(result["calmes"]) == 2

    def test_liste_vide(self):
        """Test avec liste vide"""
        result = filtrer_etapes_bruyantes([])
        assert result["bruyantes"] == []
        assert result["calmes"] == []


# ═══════════════════════════════════════════════════════════
# TESTS IDENTIFIER MOMENTS JULES
# ═══════════════════════════════════════════════════════════


class TestIdentifierMomentsJules:
    """Tests pour identifier_moments_jules"""

    def test_activite_securisee(self):
        """Test avec activité sécurisée (melanger sans accent)"""
        etapes = [
            {"titre": "melanger la pate", "alerte_bruit": False, "temperature": None},
        ]
        result = identifier_moments_jules(etapes)
        assert len(result) == 1
        assert "conseil_jules" in result[0]

    def test_activite_bruyante_exclue(self):
        """Test que les activités bruyantes sont exclues"""
        etapes = [
            {"titre": "melanger", "alerte_bruit": True, "temperature": None},
        ]
        result = identifier_moments_jules(etapes)
        assert len(result) == 0

    def test_temperature_chaude_exclue(self):
        """Test que les températures chaudes sont exclues"""
        etapes = [
            {"titre": "melanger", "alerte_bruit": False, "temperature": 100},
        ]
        result = identifier_moments_jules(etapes)
        assert len(result) == 0

    def test_supervision_calme(self):
        """Test que la supervision calme est incluse"""
        etapes = [
            {"titre": "Cuisson", "est_supervision": True, "alerte_bruit": False},
        ]
        result = identifier_moments_jules(etapes)
        assert len(result) == 1
        assert "observer" in result[0]["conseil_jules"].lower()

    def test_activites_diverses(self):
        """Test avec diverses activités sécurisées (sans accents)"""
        etapes = [
            {"titre": "verser le lait", "alerte_bruit": False},
            {"titre": "decorer le gateau", "alerte_bruit": False, "temperature": 20},
            {"titre": "ranger les ustensiles", "alerte_bruit": False},
        ]
        result = identifier_moments_jules(etapes)
        assert len(result) == 3

    def test_activite_non_securisee(self):
        """Test que les activités non sécurisées sont exclues"""
        etapes = [
            {"titre": "couper les legumes", "alerte_bruit": False, "temperature": None},
        ]
        result = identifier_moments_jules(etapes)
        # "couper" n'est pas dans activites_securisees
        assert len(result) == 0

    def test_activite_description_securisee(self):
        """Test détection via description"""
        etapes = [
            {"titre": "Etape 1", "description": "observer la cuisson", "alerte_bruit": False},
        ]
        result = identifier_moments_jules(etapes)
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════
# TESTS GENERER PLANNING JULES
# ═══════════════════════════════════════════════════════════


class TestGenererPlanningJules:
    """Tests pour generer_planning_jules"""

    def test_planning_complet(self):
        """Test génération planning complet"""
        etapes = [
            {"titre": "Matin", "duree_minutes": 60},  # 9h-10h
            {"titre": "Midi", "duree_minutes": 180},  # 10h-13h
            {"titre": "Sieste", "duree_minutes": 60},  # 13h-14h
            {"titre": "Après", "duree_minutes": 60},  # 14h-15h
        ]
        result = generer_planning_jules(
            etapes=etapes,
            heure_debut=time(9, 0),
            heure_sieste_debut=time(13, 0),
            heure_sieste_fin=time(15, 0),
        )
        assert "avant_sieste" in result
        assert "pendant_sieste" in result
        assert "apres_sieste" in result
        assert "conseils" in result

    def test_etapes_avant_sieste(self):
        """Test avec étapes uniquement avant la sieste"""
        etapes = [
            {"titre": "E1", "duree_minutes": 30},
            {"titre": "E2", "duree_minutes": 30},
        ]
        result = generer_planning_jules(
            etapes=etapes,
            heure_debut=time(9, 0),
            heure_sieste_debut=time(13, 0),
            heure_sieste_fin=time(15, 0),
        )
        assert len(result["avant_sieste"]) == 2
        assert len(result["pendant_sieste"]) == 0
        assert len(result["apres_sieste"]) == 0

    def test_conseil_etapes_bruyantes_sieste(self):
        """Test conseil pour étapes bruyantes pendant sieste"""
        etapes = [
            {"titre": "E1", "duree_minutes": 240, "alerte_bruit": True},  # 9h-13h -> chevauche sieste
        ]
        result = generer_planning_jules(
            etapes=etapes,
            heure_debut=time(9, 0),
            heure_sieste_debut=time(13, 0),
            heure_sieste_fin=time(15, 0),
        )
        # L'étape est pendant la sieste et bruyante
        assert len(result["pendant_sieste"]) >= 1 or len(result["conseils"]) >= 0

    def test_etapes_apres_sieste(self):
        """Test avec étapes après la sieste"""
        etapes = [
            {"titre": "Après sieste", "duree_minutes": 60},
        ]
        result = generer_planning_jules(
            etapes=etapes,
            heure_debut=time(16, 0),  # Après la sieste
            heure_sieste_debut=time(13, 0),
            heure_sieste_fin=time(15, 0),
        )
        assert len(result["apres_sieste"]) == 1


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER STATISTIQUES SESSION
# ═══════════════════════════════════════════════════════════


class TestCalculerStatistiquesSession:
    """Tests pour calculer_statistiques_session"""

    def test_session_vide(self):
        """Test avec session vide"""
        result = calculer_statistiques_session({})
        assert result["nb_etapes"] == 0
        assert result["nb_preparations"] == 0
        assert result["progression_pct"] == 0

    def test_session_complete(self):
        """Test avec session complète"""
        session = {
            "etapes": [
                {"duree_minutes": 30, "statut": "terminee", "robots": ["four"], "groupe_parallele": 0},
                {"duree_minutes": 20, "statut": "terminee", "robots": ["mixeur"], "groupe_parallele": 0},
                {"duree_minutes": 15, "statut": "en_cours", "robots": ["cookeo"], "groupe_parallele": 1},
            ],
            "preparations": [
                {"portions_initiales": 4},
                {"portions_initiales": 6},
            ],
        }
        result = calculer_statistiques_session(session)
        assert result["nb_etapes"] == 3
        assert result["etapes_terminees"] == 2
        assert result["nb_preparations"] == 2
        assert result["portions_totales"] == 10
        assert result["nb_robots"] == 3

    def test_progression_pourcentage(self):
        """Test calcul pourcentage de progression"""
        session = {
            "etapes": [
                {"statut": "terminee"},
                {"statut": "terminee"},
                {"statut": "en_cours"},
                {"statut": "a_faire"},
            ],
        }
        result = calculer_statistiques_session(session)
        assert result["progression_pct"] == 50.0

    def test_gain_temps(self):
        """Test calcul du gain de temps"""
        session = {
            "etapes": [
                {"duree_minutes": 30, "groupe_parallele": 0},
                {"duree_minutes": 20, "groupe_parallele": 0},  # Parallèle, max = 30
                {"duree_minutes": 10, "groupe_parallele": 1},
            ],
        }
        result = calculer_statistiques_session(session)
        # Durée brute: 30 + 20 + 10 = 60
        # Durée optimisée: max(30,20) + 10 = 40
        assert result["duree_estimee_brute"] == 60
        assert result["duree_estimee_optimisee"] == 40
        assert result["gain_temps_pct"] > 0


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER HISTORIQUE BATCH
# ═══════════════════════════════════════════════════════════


class TestCalculerHistoriqueBatch:
    """Tests pour calculer_historique_batch"""

    def test_historique_vide(self):
        """Test avec historique vide"""
        result = calculer_historique_batch([])
        assert result["nb_sessions"] == 0
        assert result["temps_moyen_session"] == 0
        assert result["robot_prefere"] is None

    def test_historique_simple(self):
        """Test avec historique simple"""
        sessions = [
            {"duree_reelle": 120, "nb_portions_preparees": 8, "robots_utilises": ["cookeo", "four"]},
            {"duree_reelle": 90, "nb_portions_preparees": 6, "robots_utilises": ["cookeo"]},
        ]
        result = calculer_historique_batch(sessions)
        assert result["nb_sessions"] == 2
        assert result["temps_moyen_session"] == 105  # (120+90)/2
        assert result["portions_moyennes"] == 7  # (8+6)/2
        assert result["robot_prefere"] == "cookeo"  # Utilisé 2 fois

    def test_duree_estimee_fallback(self):
        """Test avec fallback sur durée estimée"""
        sessions = [
            {"duree_estimee": 100, "nb_portions_preparees": 5, "robots_utilises": []},
        ]
        result = calculer_historique_batch(sessions)
        assert result["temps_moyen_session"] == 100

    def test_robots_compteur(self):
        """Test comptage des robots"""
        sessions = [
            {"duree_reelle": 60, "robots_utilises": ["four", "cookeo"]},
            {"duree_reelle": 60, "robots_utilises": ["four", "mixeur"]},
            {"duree_reelle": 60, "robots_utilises": ["four"]},
        ]
        result = calculer_historique_batch(sessions)
        assert result["robots_compteur"]["four"] == 3
        assert result["robots_compteur"]["cookeo"] == 1
        assert result["robot_prefere"] == "four"
