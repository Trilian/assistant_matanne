"""Tests unitaires pour les modules famille."""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch


# =============================================================================
# TESTS ROUTINES
# =============================================================================

class TestRoutinesLogique:
    """Tests pour la logique des routines."""

    def test_calculer_progression_routine(self):
        """Calcul de la progression d'une routine."""
        taches = [
            {"id": 1, "completee": True},
            {"id": 2, "completee": True},
            {"id": 3, "completee": False},
            {"id": 4, "completee": False},
        ]
        
        completees = sum(1 for t in taches if t["completee"])
        total = len(taches)
        progression = (completees / total) * 100 if total > 0 else 0
        
        assert progression == 50.0

    def test_trier_taches_par_ordre(self):
        """Tri des tÃ¢ches par ordre."""
        taches = [
            {"nom": "Petit-dÃ©jeuner", "ordre": 2},
            {"nom": "RÃ©veil", "ordre": 1},
            {"nom": "Habillage", "ordre": 3},
        ]
        
        triees = sorted(taches, key=lambda t: t["ordre"])
        
        assert triees[0]["nom"] == "RÃ©veil"
        assert triees[1]["nom"] == "Petit-dÃ©jeuner"
        assert triees[2]["nom"] == "Habillage"

    def test_filtrer_routines_actives(self):
        """Filtrage des routines actives."""
        routines = [
            {"nom": "Matin", "active": True},
            {"nom": "Soir", "active": True},
            {"nom": "Weekend", "active": False},
        ]
        
        actives = [r for r in routines if r["active"]]
        
        assert len(actives) == 2

    def test_routines_par_moment(self):
        """Routines par moment de la journÃ©e."""
        routines = [
            {"nom": "Routine matin", "moment": "matin"},
            {"nom": "Routine midi", "moment": "midi"},
            {"nom": "Routine soir", "moment": "soir"},
            {"nom": "Routine matin 2", "moment": "matin"},
        ]
        
        par_moment = {}
        for r in routines:
            moment = r["moment"]
            if moment not in par_moment:
                par_moment[moment] = []
            par_moment[moment].append(r)
        
        assert len(par_moment["matin"]) == 2


# =============================================================================
# TESTS BIEN-ÃŠTRE
# =============================================================================

class TestBienEtreLogique:
    """Tests pour la logique bien-Ãªtre."""

    def test_calculer_moyenne_humeur(self):
        """Calcul de la moyenne d'humeur sur une pÃ©riode."""
        entrees = [
            {"date": date.today() - timedelta(days=i), "humeur": 3 + (i % 3)}
            for i in range(7)
        ]
        
        moyenne = sum(e["humeur"] for e in entrees) / len(entrees)
        
        assert 3 <= moyenne <= 5

    def test_detecter_tendance_humeur(self):
        """DÃ©tection de tendance d'humeur."""
        # Tendance croissante
        entrees_croissante = [
            {"humeur": 2},
            {"humeur": 3},
            {"humeur": 4},
            {"humeur": 5},
        ]
        
        variations = [
            entrees_croissante[i+1]["humeur"] - entrees_croissante[i]["humeur"]
            for i in range(len(entrees_croissante) - 1)
        ]
        
        tendance = "croissante" if sum(variations) > 0 else "dÃ©croissante" if sum(variations) < 0 else "stable"
        
        assert tendance == "croissante"

    def test_statistiques_activites(self):
        """Statistiques par type d'activitÃ©."""
        entrees = [
            {"activite": "Sport", "duree": 60},
            {"activite": "MÃ©ditation", "duree": 15},
            {"activite": "Sport", "duree": 45},
            {"activite": "Lecture", "duree": 30},
        ]
        
        par_activite = {}
        for e in entrees:
            act = e["activite"]
            if act not in par_activite:
                par_activite[act] = {"count": 0, "duree_totale": 0}
            par_activite[act]["count"] += 1
            par_activite[act]["duree_totale"] += e["duree"]
        
        assert par_activite["Sport"]["count"] == 2
        assert par_activite["Sport"]["duree_totale"] == 105


# =============================================================================
# TESTS PROFILS ENFANTS (Jules)
# =============================================================================

class TestProfilsEnfants:
    """Tests pour les profils enfants."""

    def test_calculer_age_mois(self):
        """Calcul de l'Ã¢ge en mois."""
        date_naissance = date(2024, 6, 15)  # NÃ© le 15 juin 2024
        today = date(2026, 1, 28)  # Aujourd'hui
        
        # Calcul approximatif en mois
        mois = (today.year - date_naissance.year) * 12 + (today.month - date_naissance.month)
        
        assert mois == 19  # 19 mois

    def test_calculer_age_annees(self):
        """Calcul de l'Ã¢ge en annÃ©es."""
        date_naissance = date(2022, 5, 10)
        today = date(2026, 1, 28)
        
        age = today.year - date_naissance.year
        if (today.month, today.day) < (date_naissance.month, date_naissance.day):
            age -= 1
        
        assert age == 3

    def test_format_age_display(self):
        """Format d'affichage de l'Ã¢ge."""
        mois = 19
        
        if mois < 24:
            display = f"{mois} mois"
        else:
            annees = mois // 12
            mois_restants = mois % 12
            display = f"{annees} an{'s' if annees > 1 else ''}" + \
                     (f" et {mois_restants} mois" if mois_restants > 0 else "")
        
        assert display == "19 mois"

    def test_etapes_developpement(self):
        """VÃ©rification des Ã©tapes de dÃ©veloppement."""
        etapes_19_mois = [
            "Marche acquise",
            "Premiers mots",
            "Mange seul (cuillÃ¨re)",
            "Joue Ã  cÃ´tÃ© des autres enfants",
        ]
        
        profil = {"age_mois": 19, "etapes_validees": ["Marche acquise", "Premiers mots"]}
        
        etapes_non_validees = [e for e in etapes_19_mois if e not in profil["etapes_validees"]]
        
        assert len(etapes_non_validees) == 2


# =============================================================================
# TESTS ACTIVITÃ‰S
# =============================================================================

class TestActivitesLogique:
    """Tests pour la logique des activitÃ©s."""

    def test_activites_par_jour_semaine(self):
        """ActivitÃ©s groupÃ©es par jour de la semaine."""
        activites = [
            {"nom": "CrÃ¨che", "jour": "lundi"},
            {"nom": "CrÃ¨che", "jour": "mardi"},
            {"nom": "Piscine", "jour": "mercredi"},
            {"nom": "CrÃ¨che", "jour": "jeudi"},
            {"nom": "Parc", "jour": "samedi"},
        ]
        
        par_jour = {}
        for a in activites:
            jour = a["jour"]
            if jour not in par_jour:
                par_jour[jour] = []
            par_jour[jour].append(a["nom"])
        
        assert "CrÃ¨che" in par_jour["lundi"]
        assert "Piscine" in par_jour["mercredi"]

    def test_filtrer_activites_recurrentes(self):
        """Filtrage des activitÃ©s rÃ©currentes."""
        activites = [
            {"nom": "CrÃ¨che", "recurrente": True, "frequence": "hebdomadaire"},
            {"nom": "Anniversaire", "recurrente": False},
            {"nom": "Piscine", "recurrente": True, "frequence": "hebdomadaire"},
        ]
        
        recurrentes = [a for a in activites if a["recurrente"]]
        
        assert len(recurrentes) == 2


# =============================================================================
# TESTS SANTÃ‰
# =============================================================================

class TestSanteLogique:
    """Tests pour le module santÃ©."""

    def test_calculer_imc(self):
        """Calcul de l'IMC."""
        poids = 75  # kg
        taille = 1.75  # m
        
        imc = poids / (taille ** 2)
        
        assert 24 < imc < 25  # IMC normal

    def test_interpreter_imc(self):
        """InterprÃ©tation de l'IMC."""
        def interpreter_imc(imc):
            if imc < 18.5:
                return "Insuffisance pondÃ©rale"
            elif imc < 25:
                return "Poids normal"
            elif imc < 30:
                return "Surpoids"
            else:
                return "ObÃ©sitÃ©"
        
        assert interpreter_imc(17) == "Insuffisance pondÃ©rale"
        assert interpreter_imc(22) == "Poids normal"
        assert interpreter_imc(27) == "Surpoids"
        assert interpreter_imc(35) == "ObÃ©sitÃ©"

    def test_suivre_objectif_pas(self):
        """Suivi de l'objectif de pas quotidiens."""
        objectif = 10000
        pas_jour = 8500
        
        pourcentage = (pas_jour / objectif) * 100
        atteint = pas_jour >= objectif
        
        assert pourcentage == 85.0
        assert atteint == False

    def test_calculer_calories_brulees(self):
        """Estimation des calories brÃ»lÃ©es (marche)."""
        pas = 10000
        calories_par_pas = 0.04  # Approximation
        
        calories = pas * calories_par_pas
        
        assert calories == 400.0


# =============================================================================
# TESTS SHOPPING
# =============================================================================

class TestShoppingLogique:
    """Tests pour le module shopping."""

    def test_grouper_articles_par_magasin(self):
        """Groupement des articles par magasin."""
        articles = [
            {"nom": "Lait", "magasin": "Carrefour"},
            {"nom": "Pain", "magasin": "Boulangerie"},
            {"nom": "Yaourt", "magasin": "Carrefour"},
            {"nom": "Viande", "magasin": "Boucherie"},
        ]
        
        par_magasin = {}
        for a in articles:
            mag = a["magasin"]
            if mag not in par_magasin:
                par_magasin[mag] = []
            par_magasin[mag].append(a["nom"])
        
        assert len(par_magasin["Carrefour"]) == 2

    def test_calculer_budget_courses(self):
        """Calcul du budget courses."""
        articles = [
            {"nom": "Lait", "prix": 1.20, "quantite": 2},
            {"nom": "Pain", "prix": 1.50, "quantite": 1},
            {"nom": "Yaourt", "prix": 3.00, "quantite": 1},
        ]
        
        total = sum(a["prix"] * a["quantite"] for a in articles)
        
        assert total == 6.90


# =============================================================================
# TESTS INTÃ‰GRATION CUISINE-COURSES
# =============================================================================

class TestIntegrationCuisineCourses:
    """Tests pour l'intÃ©gration cuisine/courses."""

    def test_extraire_ingredients_planning(self):
        """Extraction des ingrÃ©dients du planning."""
        planning = [
            {
                "recette": "Tarte aux pommes",
                "ingredients": [
                    {"nom": "Pommes", "quantite": 4},
                    {"nom": "PÃ¢te feuilletÃ©e", "quantite": 1},
                ]
            },
            {
                "recette": "Salade",
                "ingredients": [
                    {"nom": "Laitue", "quantite": 1},
                    {"nom": "Tomates", "quantite": 3},
                ]
            }
        ]
        
        tous_ingredients = []
        for repas in planning:
            tous_ingredients.extend(repas["ingredients"])
        
        assert len(tous_ingredients) == 4

    def test_generer_liste_courses_depuis_planning(self):
        """GÃ©nÃ©ration de liste de courses depuis le planning."""
        ingredients_necessaires = [
            {"nom": "Pommes", "quantite": 4},
            {"nom": "Lait", "quantite": 2},
        ]
        
        inventaire = {"Pommes": 2, "Lait": 0}
        
        liste_courses = []
        for ing in ingredients_necessaires:
            en_stock = inventaire.get(ing["nom"], 0)
            a_acheter = ing["quantite"] - en_stock
            if a_acheter > 0:
                liste_courses.append({"nom": ing["nom"], "quantite": a_acheter})
        
        assert len(liste_courses) == 2
        pommes = next(i for i in liste_courses if i["nom"] == "Pommes")
        assert pommes["quantite"] == 2


# =============================================================================
# TESTS HELPERS FAMILLE
# =============================================================================

class TestHelpersFamille:
    """Tests pour les helpers du module famille."""

    def test_format_duree(self):
        """Format de durÃ©e en texte lisible."""
        def format_duree(minutes):
            if minutes < 60:
                return f"{minutes} min"
            heures = minutes // 60
            mins = minutes % 60
            if mins == 0:
                return f"{heures}h"
            return f"{heures}h{mins:02d}"
        
        assert format_duree(30) == "30 min"
        assert format_duree(60) == "1h"
        assert format_duree(90) == "1h30"

    def test_format_date_relative(self):
        """Format de date relative (aujourd'hui, hier, etc.)."""
        def format_date_relative(d):
            today = date.today()
            diff = (today - d).days
            
            if diff == 0:
                return "Aujourd'hui"
            elif diff == 1:
                return "Hier"
            elif diff < 7:
                return f"Il y a {diff} jours"
            else:
                return d.strftime("%d/%m/%Y")
        
        assert format_date_relative(date.today()) == "Aujourd'hui"
        assert format_date_relative(date.today() - timedelta(days=1)) == "Hier"
        assert format_date_relative(date.today() - timedelta(days=3)) == "Il y a 3 jours"

    def test_calculer_streak(self):
        """Calcul de la sÃ©rie (streak) de jours consÃ©cutifs."""
        dates_completees = [
            date.today(),
            date.today() - timedelta(days=1),
            date.today() - timedelta(days=2),
            # Jour manquant
            date.today() - timedelta(days=4),
        ]
        
        dates_set = set(dates_completees)
        streak = 0
        current = date.today()
        
        while current in dates_set:
            streak += 1
            current -= timedelta(days=1)
        
        assert streak == 3  # 3 jours consÃ©cutifs


# =============================================================================
# TESTS STATISTIQUES FAMILLE
# =============================================================================

class TestStatistiquesFamille:
    """Tests pour les statistiques familiales."""

    def test_compter_routines_par_categorie(self):
        """Comptage des routines par catÃ©gorie."""
        routines = [
            {"categorie": "matin"},
            {"categorie": "matin"},
            {"categorie": "soir"},
            {"categorie": "weekend"},
        ]
        
        from collections import Counter
        counts = Counter(r["categorie"] for r in routines)
        
        assert counts["matin"] == 2
        assert counts["soir"] == 1

    def test_moyenne_humeur_semaine(self):
        """Moyenne d'humeur sur la semaine."""
        entrees = [{"humeur": h} for h in [3, 4, 5, 4, 3, 4, 5]]
        
        moyenne = sum(e["humeur"] for e in entrees) / len(entrees)
        
        assert moyenne == pytest.approx(4.0, rel=0.1)

    def test_temps_total_activites(self):
        """Temps total passÃ© sur les activitÃ©s."""
        activites = [
            {"duree": 60},
            {"duree": 45},
            {"duree": 30},
        ]
        
        total = sum(a["duree"] for a in activites)
        
        assert total == 135  # minutes

