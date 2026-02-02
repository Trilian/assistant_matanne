"""
Tests E2E pour les workflows complets des domains.
Teste les flux utilisateur de bout en bout sans mock de la logique métier.
"""
import pytest
from datetime import date, time, timedelta
from unittest.mock import patch, MagicMock


# ═══════════════════════════════════════════════════════════
# E2E: WORKFLOW CUISINE COMPLET
# ═══════════════════════════════════════════════════════════


@pytest.mark.e2e
class TestWorkflowCuisineE2E:
    """Tests E2E du workflow Cuisine."""

    def test_workflow_creation_liste_courses(self):
        """
        Workflow complet: Création d'une liste de courses
        1. Définir les préférences utilisateur
        2. Filtrer les articles existants
        3. Ajouter de nouveaux articles
        4. Grouper par rayon
        5. Trier par priorité
        """
        from src.domains.cuisine.logic.courses_logic import (
            filtrer_articles,
            grouper_par_rayon,
            trier_par_priorite,
            calculer_statistiques,
        )

        # 1. Articles initiaux
        articles = [
            {"ingredient_nom": "Tomates", "priorite": "haute", "rayon_magasin": "Fruits & Légumes"},
            {"ingredient_nom": "Lait", "priorite": "moyenne", "rayon_magasin": "Laitier"},
            {"ingredient_nom": "Pain", "priorite": "basse", "rayon_magasin": "Boulangerie"},
            {"ingredient_nom": "Poulet", "priorite": "haute", "rayon_magasin": "Viandes"},
        ]

        # 2. Filtrer par priorité haute
        urgents = filtrer_articles(articles, priorite="haute")
        assert len(urgents) == 2

        # 3. Grouper par rayon
        par_rayon = grouper_par_rayon(articles)
        assert "Fruits & Légumes" in par_rayon
        assert "Viandes" in par_rayon

        # 4. Trier par priorité
        tries = trier_par_priorite(articles)
        assert tries[0]["priorite"] == "haute"
        assert tries[-1]["priorite"] == "basse"

        # 5. Calculer statistiques
        stats = calculer_statistiques(articles)
        assert stats["total_a_acheter"] == 4
        assert stats["haute_priorite"] == 2

    def test_workflow_preferences_repas(self):
        """
        Workflow complet: Gestion des préférences de repas
        1. Créer des préférences
        2. Sérialiser en JSON
        3. Restaurer depuis JSON
        4. Modifier les préférences
        """
        import json
        from src.domains.cuisine.logic.schemas import PreferencesUtilisateur

        # 1. Créer préférences
        prefs = PreferencesUtilisateur(
            nb_adultes=2,
            jules_present=True,
            aliments_exclus=["fruits de mer"],
            poisson_par_semaine=2,
            budget_semaine=150.0
        )

        # 2. Sérialiser
        json_str = json.dumps(prefs.to_dict())
        assert "nb_adultes" in json_str

        # 3. Restaurer
        data = json.loads(json_str)
        restored = PreferencesUtilisateur.from_dict(data)
        assert restored.nb_adultes == 2
        assert "fruits de mer" in restored.aliments_exclus

        # 4. Vérifier cohérence
        assert restored.budget_semaine == prefs.budget_semaine


# ═══════════════════════════════════════════════════════════
# E2E: WORKFLOW FAMILLE COMPLET
# ═══════════════════════════════════════════════════════════


@pytest.mark.e2e
class TestWorkflowFamilleE2E:
    """Tests E2E du workflow Famille."""

    def test_workflow_planification_activites_semaine(self):
        """
        Workflow complet: Planifier les activités de la semaine
        1. Récupérer les suggestions par âge
        2. Créer des activités
        3. Filtrer par type
        4. Calculer le budget
        """
        from src.domains.famille.logic.activites_logic import (
            suggerer_activites_age,
            filtrer_par_type,
            calculer_statistiques_activites,
            get_activites_a_venir,
        )

        # 1. Suggestions pour Jules (19 mois)
        suggestions = suggerer_activites_age(19)
        assert len(suggestions) >= 3
        assert any(s["titre"] == "Jeux de manipulation" for s in suggestions)

        # 2. Créer activités de la semaine
        today = date.today()
        activites = [
            {"type": "Sport", "date": today + timedelta(days=1), "cout": 0, "duree": 60},
            {"type": "Culture", "date": today + timedelta(days=2), "cout": 10, "duree": 90},
            {"type": "Sport", "date": today + timedelta(days=3), "cout": 5, "duree": 45},
            {"type": "Sortie", "date": today + timedelta(days=5), "cout": 20, "duree": 120},
        ]

        # 3. Filtrer par type Sport
        sports = filtrer_par_type(activites, "Sport")
        assert len(sports) == 2

        # 4. Calculer statistiques
        stats = calculer_statistiques_activites(activites)
        assert stats["total"] == 4
        assert stats["cout_total"] == 35.0
        assert stats["par_type"]["Sport"] == 2

        # 5. Activités à venir
        a_venir = get_activites_a_venir(activites, jours=7)
        assert len(a_venir) == 4

    def test_workflow_gestion_routines_jules(self):
        """
        Workflow complet: Gérer les routines de Jules
        1. Définir les routines
        2. Grouper par moment
        3. Calculer la durée totale
        4. Filtrer par jour
        """
        from src.domains.famille.logic.routines_logic import (
            grouper_par_moment,
            calculer_duree_routine,
            filtrer_par_jour,
            get_moment_journee,
            JOURS_SEMAINE,
        )

        # 1. Routines de Jules
        routines = [
            {"type": "Réveil", "moment": "Matin", "heure": time(7, 0), "duree": 20,
             "jours_actifs": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]},
            {"type": "Repas", "moment": "Midi", "duree": 30, "jours_actifs": JOURS_SEMAINE},
            {"type": "Sieste", "moment": "Après-midi", "duree": 90, "jours_actifs": JOURS_SEMAINE},
            {"type": "Bain", "moment": "Soir", "heure": time(18, 30), "duree": 20,
             "jours_actifs": JOURS_SEMAINE},
            {"type": "Coucher", "moment": "Soir", "heure": time(19, 30), "duree": 30,
             "jours_actifs": JOURS_SEMAINE},
        ]

        # 2. Grouper par moment
        par_moment = grouper_par_moment(routines)
        assert len(par_moment["Soir"]) == 2
        assert len(par_moment["Matin"]) == 1

        # 3. Durée totale
        duree = calculer_duree_routine(routines)
        assert duree == 190  # 20+30+90+20+30

        # 4. Filtrer par jour (samedi = pas de réveil)
        samedi = filtrer_par_jour(routines, "Samedi")
        assert len(samedi) == 4  # Pas le réveil

        # 5. Vérifier moment de la journée
        assert get_moment_journee(time(7, 0)) == "Matin"
        assert get_moment_journee(time(19, 0)) == "Soir"


# ═══════════════════════════════════════════════════════════
# E2E: WORKFLOW PLANNING COMPLET
# ═══════════════════════════════════════════════════════════


@pytest.mark.e2e
class TestWorkflowPlanningE2E:
    """Tests E2E du workflow Planning."""

    def test_workflow_navigation_calendrier(self):
        """
        Workflow complet: Navigation dans le calendrier
        1. Obtenir la semaine courante
        2. Naviguer vers la semaine précédente
        3. Naviguer vers la semaine suivante
        4. Vérifier les bornes
        """
        from src.domains.planning.logic.calendrier_unifie_logic import (
            get_debut_semaine,
            get_fin_semaine,
            get_jours_semaine,
            get_semaine_precedente,
            get_semaine_suivante,
        )

        # 1. Semaine courante
        today = date.today()
        lundi = get_debut_semaine(today)
        dimanche = get_fin_semaine(today)

        assert lundi.weekday() == 0  # Lundi
        assert dimanche.weekday() == 6  # Dimanche
        assert (dimanche - lundi).days == 6

        # 2. Jours de la semaine
        jours = get_jours_semaine(today)
        assert len(jours) == 7
        assert jours[0] == lundi
        assert jours[6] == dimanche

        # 3. Navigation avant/arrière
        semaine_prec = get_semaine_precedente(lundi)
        semaine_suiv = get_semaine_suivante(lundi)

        assert (lundi - semaine_prec).days == 7
        assert (semaine_suiv - lundi).days == 7

        # 4. Aller-retour
        retour = get_semaine_suivante(semaine_prec)
        assert retour == lundi

    def test_workflow_creation_evenements_semaine(self):
        """
        Workflow complet: Créer les événements d'une semaine
        1. Créer des événements variés
        2. Construire les jours
        3. Vérifier les properties
        """
        from src.domains.planning.logic.calendrier_unifie_logic import (
            TypeEvenement,
            EvenementCalendrier,
            JourCalendrier,
            SemaineCalendrier,
            get_debut_semaine,
        )

        today = date.today()
        lundi = get_debut_semaine(today)

        # 1. Créer une semaine complète
        jours = []
        for i in range(7):
            jour_date = lundi + timedelta(days=i)
            evenements = []

            # Repas midi tous les jours
            evenements.append(EvenementCalendrier(
                id=f"repas_midi_{i}",
                type=TypeEvenement.REPAS_MIDI,
                titre=f"Déjeuner jour {i+1}",
                date_jour=jour_date,
                heure_debut=time(12, 0)
            ))

            # Activité mercredi après-midi
            if i == 2:  # Mercredi
                evenements.append(EvenementCalendrier(
                    id="activite_mercredi",
                    type=TypeEvenement.ACTIVITE,
                    titre="Activité Jules",
                    date_jour=jour_date,
                    heure_debut=time(14, 0),
                    pour_jules=True
                ))

            # Courses samedi
            if i == 5:  # Samedi
                evenements.append(EvenementCalendrier(
                    id="courses_samedi",
                    type=TypeEvenement.COURSES,
                    titre="Courses Carrefour",
                    date_jour=jour_date,
                    magasin="Carrefour"
                ))

            # Batch cooking dimanche
            if i == 6:  # Dimanche
                evenements.append(EvenementCalendrier(
                    id="batch_dimanche",
                    type=TypeEvenement.BATCH_COOKING,
                    titre="Batch cooking",
                    date_jour=jour_date,
                    heure_debut=time(10, 0)
                ))

            jours.append(JourCalendrier(date_jour=jour_date, evenements=evenements))

        # 2. Construire la semaine
        semaine = SemaineCalendrier(date_debut=lundi, jours=jours)

        # 3. Vérifications
        assert semaine.nb_repas_planifies == 7  # 7 midis
        assert semaine.nb_sessions_batch == 1
        assert semaine.nb_courses == 1
        assert semaine.nb_activites == 1

        # 4. Vérifier jour spécifique
        mercredi = jours[2]
        assert len(mercredi.activites) == 1
        assert mercredi.activites[0].pour_jules is True


# ═══════════════════════════════════════════════════════════
# E2E: WORKFLOW MAISON COMPLET
# ═══════════════════════════════════════════════════════════


@pytest.mark.e2e
class TestWorkflowMaisonE2E:
    """Tests E2E du workflow Maison."""

    def test_workflow_gestion_entretien_mensuel(self):
        """
        Workflow complet: Gérer l'entretien mensuel
        1. Définir les tâches
        2. Identifier les tâches urgentes
        3. Grouper par pièce
        4. Calculer les statistiques
        """
        from src.domains.maison.logic.entretien_logic import (
            calculer_jours_avant_tache,
            get_taches_aujourd_hui,
            get_taches_semaine,
            get_taches_en_retard,
            grouper_par_piece,
            calculer_statistiques_entretien,
        )

        today = date.today()

        # 1. Tâches d'entretien
        taches = [
            # Tâche en retard
            {"titre": "Nettoyer filtres VMC", "piece": "Garage", 
             "frequence": "Mensuelle", "categorie": "Maintenance",
             "derniere_execution": today - timedelta(days=45)},
            # Tâche à faire cette semaine
            {"titre": "Aspirateur", "piece": "Salon",
             "frequence": "Hebdomadaire", "categorie": "Ménage",
             "derniere_execution": today - timedelta(days=5)},
            # Tâche à jour
            {"titre": "Nettoyage cuisine", "piece": "Cuisine",
             "frequence": "Quotidienne", "categorie": "Ménage",
             "derniere_execution": today - timedelta(days=1)},
            # Tâche annuelle OK
            {"titre": "Contrôle chaudière", "piece": "Garage",
             "frequence": "Annuelle", "categorie": "Contrôle",
             "derniere_execution": today - timedelta(days=100)},
        ]

        # 2. Identifier les urgentes
        en_retard = get_taches_en_retard(taches)
        assert len(en_retard) >= 1
        # VMC en retard de ~15 jours
        assert any("VMC" in t["titre"] for t in en_retard)

        # 3. Tâches de la semaine
        semaine = get_taches_semaine(taches)
        assert len(semaine) >= 1

        # 4. Grouper par pièce
        par_piece = grouper_par_piece(taches)
        assert "Garage" in par_piece
        assert len(par_piece["Garage"]) == 2  # VMC + chaudière

        # 5. Statistiques
        stats = calculer_statistiques_entretien(taches)
        assert stats["total_taches"] == 4
        assert stats["par_categorie"]["Ménage"] == 2
        assert stats["en_retard"] >= 1

    def test_workflow_planification_nettoyage_printemps(self):
        """
        Workflow: Planifier le grand nettoyage de printemps
        1. Lister toutes les pièces
        2. Créer les tâches par pièce
        3. Estimer le temps total
        4. Prioriser
        """
        from src.domains.maison.logic.entretien_logic import (
            PIECES,
            filtrer_par_piece,
            valider_tache,
            calculer_statistiques_entretien,
        )

        # 1. Créer tâches pour chaque pièce
        taches_printemps = []
        for piece in ["Cuisine", "Salon", "Chambre", "Salle de bain"]:
            taches_printemps.extend([
                {"titre": f"Nettoyer vitres - {piece}", "piece": piece,
                 "frequence": "Trimestrielle", "categorie": "Ménage"},
                {"titre": f"Nettoyer rideaux - {piece}", "piece": piece,
                 "frequence": "Annuelle", "categorie": "Ménage"},
            ])

        # 2. Valider les tâches
        for tache in taches_printemps:
            valide, erreurs = valider_tache(tache)
            assert valide is True, f"Tâche invalide: {tache['titre']}"

        # 3. Filtrer par pièce
        cuisine = filtrer_par_piece(taches_printemps, "Cuisine")
        assert len(cuisine) == 2

        # 4. Statistiques globales
        stats = calculer_statistiques_entretien(taches_printemps)
        assert stats["total_taches"] == 8  # 4 pièces x 2 tâches


# ═══════════════════════════════════════════════════════════
# E2E: WORKFLOW CROSS-DOMAIN
# ═══════════════════════════════════════════════════════════


@pytest.mark.e2e
class TestWorkflowCrossDomainE2E:
    """Tests E2E impliquant plusieurs domains."""

    def test_workflow_journee_type_famille(self):
        """
        Workflow complet: Une journée type de la famille
        1. Routines du matin (famille)
        2. Repas de midi (cuisine)
        3. Activités après-midi (famille)
        4. Tâches ménage (maison)
        5. Planifier le tout (planning)
        """
        from src.domains.famille.logic.routines_logic import (
            get_moment_journee,
            calculer_duree_routine,
        )
        from src.domains.cuisine.logic.courses_logic import (
            filtrer_par_priorite,
        )
        from src.domains.maison.logic.entretien_logic import (
            get_taches_aujourd_hui,
        )
        from src.domains.planning.logic.calendrier_unifie_logic import (
            TypeEvenement,
            EvenementCalendrier,
            JourCalendrier,
        )

        today = date.today()

        # 1. Routines matin
        routines_matin = [
            {"type": "Réveil", "moment": "Matin", "duree": 20},
            {"type": "Petit-déjeuner", "moment": "Matin", "duree": 30},
            {"type": "Habillage", "moment": "Matin", "duree": 15},
        ]
        duree_matin = calculer_duree_routine(routines_matin)
        assert duree_matin == 65

        # 2. Courses urgentes pour le repas
        courses = [
            {"ingredient_nom": "Pâtes", "priorite": "haute", "rayon_magasin": "Épicerie"},
            {"ingredient_nom": "Fromage", "priorite": "moyenne", "rayon_magasin": "Laitier"},
        ]
        urgentes = filtrer_par_priorite(courses, "haute")
        assert len(urgentes) == 1

        # 3. Tâches ménage du jour
        taches_menage = [
            {"titre": "Aspirateur", "frequence": "Hebdomadaire",
             "derniere_execution": today - timedelta(days=8)},
        ]
        taches_jour = get_taches_aujourd_hui(taches_menage)
        assert len(taches_jour) >= 1

        # 4. Construire le jour complet dans le calendrier
        evenements = [
            # Routines matin
            EvenementCalendrier(
                id="routine_matin",
                type=TypeEvenement.ROUTINE,
                titre="Routines matin",
                date_jour=today,
                heure_debut=time(7, 0)
            ),
            # Repas midi
            EvenementCalendrier(
                id="repas_midi",
                type=TypeEvenement.REPAS_MIDI,
                titre="Pâtes au fromage",
                date_jour=today,
                heure_debut=time(12, 0)
            ),
            # Ménage
            EvenementCalendrier(
                id="menage",
                type=TypeEvenement.MENAGE,
                titre="Aspirateur",
                date_jour=today,
                heure_debut=time(14, 0)
            ),
        ]

        jour = JourCalendrier(date_jour=today, evenements=evenements)

        # 5. Vérifications
        assert jour.nb_evenements == 3
        assert jour.repas_midi is not None
        assert len(jour.taches_menage) == 1

    def test_workflow_preparation_semaine(self):
        """
        Workflow: Préparer la semaine (batch cooking + courses)
        1. Définir les repas de la semaine (cuisine/schemas)
        2. Générer la liste de courses
        3. Planifier le batch cooking
        4. Ajouter au calendrier
        """
        from src.domains.cuisine.logic.schemas import PreferencesUtilisateur
        from src.domains.cuisine.logic.courses_logic import (
            grouper_par_rayon,
            calculer_statistiques,
        )
        from src.domains.planning.logic.calendrier_unifie_logic import (
            TypeEvenement,
            EvenementCalendrier,
            JourCalendrier,
            SemaineCalendrier,
            get_debut_semaine,
        )

        # 1. Préférences pour la semaine
        prefs = PreferencesUtilisateur(
            nb_adultes=2,
            jules_present=True,
            poisson_par_semaine=2,
            vegetarien_par_semaine=1
        )

        # 2. Liste de courses générée
        courses = [
            {"ingredient_nom": "Saumon", "priorite": "haute", "rayon_magasin": "Poissons"},
            {"ingredient_nom": "Courgettes", "priorite": "haute", "rayon_magasin": "Fruits & Légumes"},
            {"ingredient_nom": "Riz", "priorite": "moyenne", "rayon_magasin": "Épicerie"},
            {"ingredient_nom": "Lentilles", "priorite": "moyenne", "rayon_magasin": "Épicerie"},
            {"ingredient_nom": "Yaourts", "priorite": "basse", "rayon_magasin": "Laitier"},
        ]

        # Statistiques courses
        stats = calculer_statistiques(courses)
        assert stats["total_a_acheter"] == 5

        # Grouper par rayon
        par_rayon = grouper_par_rayon(courses)
        assert len(par_rayon) == 4

        # 3. Créer le calendrier de la semaine
        today = date.today()
        lundi = get_debut_semaine(today)

        jours = []
        for i in range(7):
            jour_date = lundi + timedelta(days=i)
            evenements = []

            # Samedi = courses
            if i == 5:
                evenements.append(EvenementCalendrier(
                    id="courses",
                    type=TypeEvenement.COURSES,
                    titre="Courses hebdo",
                    date_jour=jour_date,
                    description=f"{len(courses)} articles"
                ))

            # Dimanche = batch cooking
            if i == 6:
                evenements.append(EvenementCalendrier(
                    id="batch",
                    type=TypeEvenement.BATCH_COOKING,
                    titre="Batch cooking",
                    date_jour=jour_date,
                    heure_debut=time(10, 0)
                ))

            jours.append(JourCalendrier(date_jour=jour_date, evenements=evenements))

        semaine = SemaineCalendrier(date_debut=lundi, jours=jours)

        # Vérifications
        assert semaine.nb_courses == 1
        assert semaine.nb_sessions_batch == 1
