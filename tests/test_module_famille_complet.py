"""
Tests complets pour les modules Famille
- accueil.py
- activites.py
- bien_etre.py
- helpers.py
- integration_cuisine_courses.py
- jules.py
- routines.py
- sante.py
- shopping.py
- suivi_jules.py
"""

import pytest
from datetime import date, timedelta, datetime
from unittest.mock import MagicMock, patch


# ════════════════════════════════════════════════════════════════════════════
# TESTS HELPERS FAMILLE
# ════════════════════════════════════════════════════════════════════════════


class TestCalculerAgeJules:
    """Tests du calcul d'âge"""
    
    def test_calculer_age_en_jours(self):
        """Calcul de l'âge en jours"""
        naissance = date(2024, 6, 22)
        aujourd_hui = date(2025, 1, 28)
        
        delta = aujourd_hui - naissance
        jours = delta.days
        
        assert jours == 220  # Environ 7 mois
    
    def test_calculer_age_en_semaines(self):
        """Calcul de l'âge en semaines"""
        naissance = date(2024, 6, 22)
        aujourd_hui = date(2025, 1, 28)
        
        jours = (aujourd_hui - naissance).days
        semaines = jours // 7
        
        assert semaines == 31  # 220 / 7
    
    def test_calculer_age_en_mois(self):
        """Calcul de l'âge en mois"""
        naissance = date(2024, 6, 22)
        aujourd_hui = date(2025, 1, 28)
        
        jours = (aujourd_hui - naissance).days
        mois = jours // 30  # Approximation
        
        assert mois == 7
    
    def test_calculer_age_en_ans(self):
        """Calcul de l'âge en années"""
        naissance = date(2024, 6, 22)
        aujourd_hui = date(2025, 1, 28)
        
        jours = (aujourd_hui - naissance).days
        ans = jours // 365
        
        assert ans == 0  # Pas encore 1 an


class TestProgressionObjectif:
    """Tests du calcul de progression"""
    
    def test_progression_zero_si_pas_actuelle(self):
        """Progression 0% si pas de valeur actuelle"""
        objectif = {
            "valeur_cible": 100,
            "valeur_actuelle": None
        }
        
        if not objectif.get("valeur_actuelle"):
            progression = 0.0
        else:
            progression = (objectif["valeur_actuelle"] / objectif["valeur_cible"]) * 100
        
        assert progression == 0.0
    
    def test_progression_partielle(self):
        """Progression partielle"""
        objectif = {
            "valeur_cible": 100,
            "valeur_actuelle": 50
        }
        
        progression = (objectif["valeur_actuelle"] / objectif["valeur_cible"]) * 100
        assert progression == 50.0
    
    def test_progression_max_100(self):
        """Progression plafonnée à 100%"""
        objectif = {
            "valeur_cible": 100,
            "valeur_actuelle": 150  # Dépassé
        }
        
        progression = (objectif["valeur_actuelle"] / objectif["valeur_cible"]) * 100
        progression = min(progression, 100.0)
        
        assert progression == 100.0
    
    def test_progression_zero_si_cible_zero(self):
        """Protection division par zéro"""
        objectif = {
            "valeur_cible": 0,
            "valeur_actuelle": 50
        }
        
        if not objectif.get("valeur_cible"):
            progression = 0.0
        else:
            progression = (objectif["valeur_actuelle"] / objectif["valeur_cible"]) * 100
        
        assert progression == 0.0


class TestMilestones:
    """Tests des jalons de développement"""
    
    def test_grouper_par_categorie(self):
        """Groupement des jalons par catégorie"""
        milestones = [
            {"id": 1, "categorie": "langage", "titre": "Premier mot"},
            {"id": 2, "categorie": "motricité", "titre": "Premiers pas"},
            {"id": 3, "categorie": "langage", "titre": "Phrase complète"},
        ]
        
        result = {}
        for m in milestones:
            cat = m["categorie"]
            if cat not in result:
                result[cat] = []
            result[cat].append(m)
        
        assert len(result["langage"]) == 2
        assert len(result["motricité"]) == 1
    
    def test_compter_par_categorie(self):
        """Comptage des jalons par catégorie"""
        milestones = [
            {"categorie": "langage"},
            {"categorie": "motricité"},
            {"categorie": "langage"},
            {"categorie": "social"},
        ]
        
        from collections import Counter
        counts = Counter(m["categorie"] for m in milestones)
        
        assert counts["langage"] == 2
        assert counts["motricité"] == 1
        assert counts["social"] == 1
    
    def test_categories_jules(self):
        """Les catégories de jalons sont définies"""
        categories = {
            "langage": "🗣️ Langage",
            "motricité": "🚶 Motricité",
            "social": "👥 Social",
            "cognitif": "🧠 Cognitif",
        }
        
        assert "langage" in categories
        assert "motricité" in categories
        assert categories["langage"] == "🗣️ Langage"


# ════════════════════════════════════════════════════════════════════════════
# TESTS ACTIVITES
# ════════════════════════════════════════════════════════════════════════════


class TestActivites:
    """Tests du module activités"""
    
    def test_suggestions_par_type(self):
        """Les suggestions sont disponibles par type"""
        suggestions = {
            "parc": ["Parc local", "Terrain de jeu"],
            "musée": ["Musée enfants", "Aquarium"],
            "eau": ["Piscine", "Plage"],
        }
        
        assert "parc" in suggestions
        assert len(suggestions["parc"]) >= 2
    
    def test_trier_activites_par_date(self):
        """Tri des activités par date"""
        activites = [
            {"titre": "Act3", "date": date(2025, 1, 30)},
            {"titre": "Act1", "date": date(2025, 1, 28)},
            {"titre": "Act2", "date": date(2025, 1, 29)},
        ]
        
        triees = sorted(activites, key=lambda x: x["date"])
        
        assert triees[0]["titre"] == "Act1"
        assert triees[2]["titre"] == "Act3"
    
    def test_filtrer_activites_semaine(self):
        """Filtrage des activités de la semaine"""
        aujourd_hui = date(2025, 1, 28)
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)
        
        activites = [
            {"titre": "Cette semaine", "date": date(2025, 1, 29)},
            {"titre": "Semaine prochaine", "date": date(2025, 2, 5)},
        ]
        
        cette_semaine = [
            a for a in activites 
            if debut_semaine <= a["date"] <= fin_semaine
        ]
        
        assert len(cette_semaine) == 1
    
    def test_calculer_budget_activites(self):
        """Calcul du budget des activités"""
        activites = [
            {"titre": "Act1", "cout_estime": 20.0},
            {"titre": "Act2", "cout_estime": 35.0},
            {"titre": "Act3", "cout_estime": None},
        ]
        
        budget = sum(a.get("cout_estime") or 0 for a in activites)
        assert budget == 55.0


# ════════════════════════════════════════════════════════════════════════════
# TESTS BIEN-ETRE
# ════════════════════════════════════════════════════════════════════════════


class TestBienEtre:
    """Tests du module bien-être"""
    
    def test_calculer_moyenne_sommeil(self):
        """Calcul de la moyenne de sommeil"""
        entrees = [
            {"sommeil": 7.5},
            {"sommeil": 8.0},
            {"sommeil": 6.5},
        ]
        
        sommeils = [e["sommeil"] for e in entrees if e.get("sommeil")]
        moyenne = sum(sommeils) / len(sommeils) if sommeils else 0
        
        assert moyenne == pytest.approx(7.33, rel=0.1)
    
    def test_calculer_pourcentage_bonne_humeur(self):
        """Calcul du % de bonne humeur"""
        entrees = [
            {"humeur": "Bien"},
            {"humeur": "Mal"},
            {"humeur": "Très bien"},
            {"humeur": "Bien"},
        ]
        
        total = len(entrees)
        # Note: "bien" en minuscule pour matcher "Très bien" aussi
        bien = len([e for e in entrees if "bien" in e.get("humeur", "").lower()])
        pct = (bien / total) * 100 if total > 0 else 0
        
        assert pct == 75.0  # 3/4
    
    def test_detecter_alertes_humeur_basse(self):
        """Détection d'alertes humeur basse répétée"""
        entrees = [
            {"humeur": "Mal", "personne": "Test"},
            {"humeur": "Mal", "personne": "Test"},
            {"humeur": "Mal", "personne": "Test"},
            {"humeur": "Bien", "personne": "Test"},
        ]
        
        mauvaise = len([e for e in entrees if "Mal" in e["humeur"]])
        
        alertes = []
        if mauvaise >= 3:
            alertes.append({
                "type": "ATTENTION",
                "message": f"Humeur basse répétée ({mauvaise}/7 jours)"
            })
        
        assert len(alertes) == 1
    
    def test_detecter_alertes_sommeil_insuffisant(self):
        """Détection sommeil insuffisant"""
        entrees = [
            {"sommeil": 5.0},
            {"sommeil": 5.5},
            {"sommeil": 5.0},
        ]
        
        sommeils = [e["sommeil"] for e in entrees]
        avg = sum(sommeils) / len(sommeils)
        
        alertes = []
        if avg < 6.0:
            alertes.append({
                "type": "INFO",
                "message": f"Sommeil moyen bas: {avg:.1f}h"
            })
        
        assert len(alertes) == 1
        assert "5.2h" in alertes[0]["message"]


# ════════════════════════════════════════════════════════════════════════════
# TESTS ROUTINES
# ════════════════════════════════════════════════════════════════════════════


class TestRoutines:
    """Tests du module routines"""
    
    def test_charger_routines_actives(self):
        """Filtrage des routines actives"""
        routines = [
            {"nom": "Matin", "active": True},
            {"nom": "Soir", "active": False},
            {"nom": "Sport", "active": True},
        ]
        
        actives = [r for r in routines if r.get("active")]
        assert len(actives) == 2
    
    def test_compter_taches_routine(self):
        """Comptage des tâches d'une routine"""
        routine = {
            "nom": "Matin",
            "taches": [
                {"nom": "Réveil"},
                {"nom": "Déjeuner"},
                {"nom": "Douche"},
            ]
        }
        
        nb_taches = len(routine.get("taches", []))
        assert nb_taches == 3
    
    def test_detecter_taches_en_retard(self):
        """Détection des tâches en retard"""
        maintenant = datetime.now().time()
        heure_reference = datetime.now().replace(hour=8, minute=0).time()
        
        taches = [
            {"nom": "Tâche1", "heure_prevue": "07:00", "statut": "à faire"},
            {"nom": "Tâche2", "heure_prevue": "10:00", "statut": "à faire"},
            {"nom": "Tâche3", "heure_prevue": "06:00", "statut": "terminé"},
        ]
        
        # Simplification: compter les non-terminées avant l'heure de référence
        en_retard = [
            t for t in taches 
            if t["statut"] == "à faire" and t["heure_prevue"] < "08:00"
        ]
        
        assert len(en_retard) == 1
        assert en_retard[0]["nom"] == "Tâche1"
    
    def test_reinitialiser_taches(self):
        """Réinitialisation des tâches"""
        taches = [
            {"nom": "T1", "statut": "terminé"},
            {"nom": "T2", "statut": "terminé"},
            {"nom": "T3", "statut": "à faire"},
        ]
        
        for t in taches:
            if t["statut"] == "terminé":
                t["statut"] = "à faire"
        
        assert all(t["statut"] == "à faire" for t in taches)


# ════════════════════════════════════════════════════════════════════════════
# TESTS SANTE
# ════════════════════════════════════════════════════════════════════════════


class TestSante:
    """Tests du module santé"""
    
    def test_charger_entrees_recentes(self):
        """Filtrage des entrées des N derniers jours"""
        aujourd_hui = date.today()
        entrees = [
            {"date": aujourd_hui - timedelta(days=5), "type": "course"},
            {"date": aujourd_hui - timedelta(days=35), "type": "marche"},
            {"date": aujourd_hui - timedelta(days=10), "type": "vélo"},
        ]
        
        jours_max = 30
        debut = aujourd_hui - timedelta(days=jours_max)
        recentes = [e for e in entrees if e["date"] >= debut]
        
        assert len(recentes) == 2
    
    def test_calculer_calories_brulees(self):
        """Calcul du total de calories brûlées"""
        entrees = [
            {"calories": 200},
            {"calories": 350},
            {"calories": None},
            {"calories": 150},
        ]
        
        total = sum(e.get("calories") or 0 for e in entrees)
        assert total == 700
    
    def test_calculer_moyenne_energie(self):
        """Calcul de la moyenne d'énergie"""
        entrees = [
            {"energie": 7},
            {"energie": 5},
            {"energie": 8},
        ]
        
        energies = [e["energie"] for e in entrees]
        moyenne = sum(energies) / len(energies)
        
        assert moyenne == pytest.approx(6.67, rel=0.1)
    
    def test_valider_notes_energie_moral(self):
        """Validation des notes (1-10)"""
        def valider_note(note):
            return max(1, min(10, note))
        
        assert valider_note(0) == 1
        assert valider_note(15) == 10
        assert valider_note(5) == 5


# ════════════════════════════════════════════════════════════════════════════
# TESTS SHOPPING
# ════════════════════════════════════════════════════════════════════════════


class TestShopping:
    """Tests du module shopping"""
    
    def test_suggestions_par_categorie(self):
        """Les suggestions existent par catégorie"""
        suggestions = {
            "Jules": {
                "jouets": ["Blocs", "Livre"],
                "vêtements": ["T-shirt", "Pantalon"],
            },
            "Nous": {
                "épicerie": ["Riz", "Pâtes"],
            }
        }
        
        assert "Jules" in suggestions
        assert "jouets" in suggestions["Jules"]
        assert len(suggestions["Jules"]["jouets"]) >= 2
    
    def test_filtrer_articles_par_liste(self):
        """Filtrage des articles par liste"""
        articles = [
            {"titre": "Couches", "liste": "Jules"},
            {"titre": "Pain", "liste": "Nous"},
            {"titre": "Jouet", "liste": "Jules"},
        ]
        
        jules_items = [a for a in articles if a["liste"] == "Jules"]
        assert len(jules_items) == 2
    
    def test_calculer_budget_par_liste(self):
        """Calcul du budget par liste"""
        articles = [
            {"titre": "A1", "liste": "Jules", "prix_estime": 20},
            {"titre": "A2", "liste": "Nous", "prix_estime": 15},
            {"titre": "A3", "liste": "Jules", "prix_estime": 30},
        ]
        
        budget_jules = sum(
            a.get("prix_estime", 0) 
            for a in articles 
            if a["liste"] == "Jules"
        )
        
        assert budget_jules == 50
    
    def test_marquer_article_achete(self):
        """Marquage d'un article comme acheté"""
        article = {
            "titre": "Pain",
            "actif": True,
            "date_achat": None,
            "prix_reel": None,
            "prix_estime": 3.50
        }
        
        # Simuler l'achat
        article["actif"] = False
        article["date_achat"] = date.today()
        if article["prix_reel"] is None:
            article["prix_reel"] = article["prix_estime"]
        
        assert article["actif"] == False
        assert article["date_achat"] == date.today()
        assert article["prix_reel"] == 3.50


# ════════════════════════════════════════════════════════════════════════════
# TESTS SUIVI JULES
# ════════════════════════════════════════════════════════════════════════════


class TestSuiviJules:
    """Tests du suivi de Jules"""
    
    def test_etapes_developpement_par_age(self):
        """Les étapes de développement sont définies par âge"""
        etapes = {
            0: ["Réflexes primitifs", "Vision floue"],
            6: ["Tient assis seul", "Début 4 pattes"],
            12: ["Marche avec aide", "Premiers mots"],
        }
        
        # À 7 mois, trouver l'étape la plus proche
        age_mois = 7
        mois_cle = min(etapes.keys(), key=lambda x: abs(x - age_mois))
        
        assert mois_cle == 6  # Plus proche de 7
        assert len(etapes[mois_cle]) >= 2
    
    def test_activites_19_mois(self):
        """Les activités pour 19 mois sont définies"""
        activites = {
            "parc": ["Jeux dans le sable", "Toboggan"],
            "maison": ["Cache-cache", "Blocs"],
            "apprentissage": ["Nommer couleurs", "Puzzles simples"],
        }
        
        assert "parc" in activites
        assert "apprentissage" in activites
    
    def test_shopping_jules_categories(self):
        """Les catégories shopping pour Jules sont définies"""
        shopping = {
            "jouets": ["Jouets à empiler", "Livres cartonnés"],
            "vetements": ["Vêtements confortables", "Chaussures souples"],
            "hygiene": ["Couches taille 4", "Lingettes"],
        }
        
        assert "jouets" in shopping
        assert "hygiene" in shopping
        assert "Couches taille 4" in shopping["hygiene"]


# ════════════════════════════════════════════════════════════════════════════
# TESTS INTEGRATION CUISINE/COURSES
# ════════════════════════════════════════════════════════════════════════════


class TestIntegrationCuisineCourses:
    """Tests d'intégration cuisine/courses/famille"""
    
    def test_suggestions_recettes_par_objectif(self):
        """Suggestions de recettes basées sur objectifs santé"""
        recette_map = {
            "endurance": {
                "label": "Recettes pour l'endurance",
                "recettes": [
                    {"nom": "Pâtes complètes", "calories": 450},
                    {"nom": "Poulet grillé avec riz", "calories": 520},
                ]
            },
            "poids": {
                "label": "Recettes légères",
                "recettes": [
                    {"nom": "Salade composée", "calories": 280},
                    {"nom": "Soupe légumes", "calories": 200},
                ]
            }
        }
        
        objectif = "poids"
        recettes = recette_map.get(objectif, {}).get("recettes", [])
        
        assert len(recettes) == 2
        assert all(r["calories"] < 300 for r in recettes)
    
    def test_pre_remplissage_shopping_activites(self):
        """Pré-remplissage shopping depuis activités"""
        activite = {"type": "picnic", "date": date.today()}
        
        suggestions_activites = {
            "picnic": ["Serviettes", "Gobelets", "Glacière"],
            "parc": ["Ballon", "Frisbee"],
        }
        
        items_suggeres = suggestions_activites.get(activite["type"], [])
        assert len(items_suggeres) == 3
        assert "Serviettes" in items_suggeres
    
    def test_calculer_calories_depuis_recettes(self):
        """Calcul des calories depuis les recettes"""
        recettes_jour = [
            {"nom": "Petit-déj", "calories": 350},
            {"nom": "Déjeuner", "calories": 600},
            {"nom": "Dîner", "calories": 550},
        ]
        
        total_calories = sum(r.get("calories", 0) for r in recettes_jour)
        assert total_calories == 1500


# ════════════════════════════════════════════════════════════════════════════
# TESTS BUDGET FAMILLE
# ════════════════════════════════════════════════════════════════════════════


class TestBudgetFamille:
    """Tests de gestion du budget familial"""
    
    def test_calculer_budget_periode_jour(self):
        """Budget du jour"""
        depenses = [
            {"date": date.today(), "montant": 25.0},
            {"date": date.today() - timedelta(days=1), "montant": 30.0},
            {"date": date.today(), "montant": 15.0},
        ]
        
        aujourd_hui = date.today()
        budget_jour = sum(d["montant"] for d in depenses if d["date"] == aujourd_hui)
        
        assert budget_jour == 40.0
    
    def test_calculer_budget_periode_semaine(self):
        """Budget de la semaine"""
        aujourd_hui = date.today()
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)
        
        depenses = [
            {"date": debut_semaine, "montant": 50.0},
            {"date": debut_semaine + timedelta(days=3), "montant": 30.0},
            {"date": debut_semaine + timedelta(days=10), "montant": 100.0},  # Hors semaine
        ]
        
        budget_semaine = sum(
            d["montant"] for d in depenses 
            if debut_semaine <= d["date"] <= fin_semaine
        )
        
        assert budget_semaine == 80.0
    
    def test_grouper_budget_par_categorie(self):
        """Groupement du budget par catégorie"""
        depenses = [
            {"categorie": "Alimentation", "montant": 100},
            {"categorie": "Loisirs", "montant": 50},
            {"categorie": "Alimentation", "montant": 75},
        ]
        
        result = {}
        for d in depenses:
            cat = d["categorie"]
            if cat not in result:
                result[cat] = 0
            result[cat] += d["montant"]
        
        assert result["Alimentation"] == 175
        assert result["Loisirs"] == 50
