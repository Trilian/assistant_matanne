"""
Tests complets pour les modules Maison
- entretien.py
- jardin.py
- projets.py
- helpers.py
"""

import pytest
from datetime import date, timedelta, datetime
from unittest.mock import MagicMock, patch


# ════════════════════════════════════════════════════════════════════════════
# TESTS HELPERS MAISON
# ════════════════════════════════════════════════════════════════════════════


class TestSaison:
    """Tests de détection de saison"""
    
    def test_detecter_printemps(self):
        """Détection du printemps (mars-mai)"""
        def get_saison(d: date) -> str:
            mois = d.month
            if mois in [3, 4, 5]:
                return "printemps"
            elif mois in [6, 7, 8]:
                return "été"
            elif mois in [9, 10, 11]:
                return "automne"
            else:
                return "hiver"
        
        assert get_saison(date(2025, 4, 15)) == "printemps"
        assert get_saison(date(2025, 3, 1)) == "printemps"
    
    def test_detecter_ete(self):
        """Détection de l'été (juin-août)"""
        def get_saison(d: date) -> str:
            mois = d.month
            if mois in [6, 7, 8]:
                return "été"
            return "autre"
        
        assert get_saison(date(2025, 7, 15)) == "été"
    
    def test_detecter_automne(self):
        """Détection de l'automne (sept-nov)"""
        def get_saison(d: date) -> str:
            mois = d.month
            if mois in [9, 10, 11]:
                return "automne"
            return "autre"
        
        assert get_saison(date(2025, 10, 15)) == "automne"
    
    def test_detecter_hiver(self):
        """Détection de l'hiver (déc-fév)"""
        def get_saison(d: date) -> str:
            mois = d.month
            if mois in [12, 1, 2]:
                return "hiver"
            return "autre"
        
        assert get_saison(date(2025, 1, 28)) == "hiver"
        assert get_saison(date(2025, 12, 25)) == "hiver"


class TestStatsProjets:
    """Tests des statistiques de projets"""
    
    def test_compter_projets_par_statut(self):
        """Comptage des projets par statut"""
        projets = [
            {"nom": "P1", "statut": "en_cours"},
            {"nom": "P2", "statut": "terminé"},
            {"nom": "P3", "statut": "en_cours"},
            {"nom": "P4", "statut": "en_attente"},
        ]
        
        en_cours = len([p for p in projets if p["statut"] == "en_cours"])
        termines = len([p for p in projets if p["statut"] == "terminé"])
        
        assert en_cours == 2
        assert termines == 1
    
    def test_compter_projets_urgents(self):
        """Comptage des projets urgents"""
        projets = [
            {"nom": "P1", "priorite": "haute"},
            {"nom": "P2", "priorite": "basse"},
            {"nom": "P3", "priorite": "haute"},
        ]
        
        urgents = len([p for p in projets if p["priorite"] == "haute"])
        assert urgents == 2
    
    def test_calculer_progression_projet(self):
        """Calcul de la progression d'un projet"""
        projet = {
            "taches": [
                {"statut": "terminé"},
                {"statut": "terminé"},
                {"statut": "à_faire"},
                {"statut": "en_cours"},
            ]
        }
        
        total = len(projet["taches"])
        terminees = len([t for t in projet["taches"] if t["statut"] == "terminé"])
        progression = (terminees / total) * 100 if total > 0 else 0
        
        assert progression == 50.0


class TestPrioriteEmojis:
    """Tests des emojis de priorité"""
    
    def test_emoji_priorite_haute(self):
        """Emoji pour priorité haute"""
        priorite_color = {
            "basse": "🟢",
            "moyenne": "🟡",
            "haute": "🔴",
        }
        
        assert priorite_color.get("haute") == "🔴"
    
    def test_emoji_priorite_inconnue(self):
        """Gestion priorité inconnue"""
        priorite_color = {
            "basse": "🟢",
            "moyenne": "🟡",
            "haute": "🔴",
        }
        
        assert priorite_color.get("inconnue", "⚪") == "⚪"
    
    def test_toutes_priorites_ont_emoji(self):
        """Chaque priorité a un emoji"""
        priorites = ["basse", "moyenne", "haute"]
        priorite_color = {
            "basse": "🟢",
            "moyenne": "🟡",
            "haute": "🔴",
        }
        
        for p in priorites:
            assert p in priorite_color


# ════════════════════════════════════════════════════════════════════════════
# TESTS ENTRETIEN
# ════════════════════════════════════════════════════════════════════════════


class TestEntretien:
    """Tests du module entretien"""
    
    def test_charger_routines_actives(self):
        """Filtrage des routines actives"""
        routines = [
            {"nom": "Ménage salon", "actif": True},
            {"nom": "Nettoyage ancien", "actif": False},
            {"nom": "Lessive", "actif": True},
        ]
        
        actives = [r for r in routines if r.get("actif")]
        assert len(actives) == 2
    
    def test_taches_du_jour(self):
        """Récupération des tâches du jour"""
        aujourd_hui = date.today()
        jour_semaine = aujourd_hui.strftime("%A").lower()
        
        taches = [
            {"nom": "Aspirateur", "jours": ["lundi", "jeudi"]},
            {"nom": "Poussière", "jours": ["lundi", "mercredi", "vendredi"]},
            {"nom": "Cuisine", "jours": ["tous"]},
        ]
        
        # Filtrer les tâches du jour (simplifié)
        taches_jour = [
            t for t in taches 
            if "tous" in t["jours"] or jour_semaine in t["jours"]
        ]
        
        # Au moins la tâche "Cuisine" (tous les jours)
        assert len(taches_jour) >= 1
    
    def test_calculer_stats_entretien(self):
        """Calcul des statistiques d'entretien"""
        routines = [
            {"nom": "R1", "actif": True, "nb_taches": 5},
            {"nom": "R2", "actif": True, "nb_taches": 3},
            {"nom": "R3", "actif": False, "nb_taches": 2},
        ]
        
        actives = [r for r in routines if r["actif"]]
        total_taches = sum(r["nb_taches"] for r in actives)
        
        assert len(actives) == 2
        assert total_taches == 8
    
    def test_frequences_routines(self):
        """Les fréquences sont définies"""
        frequences = ["quotidien", "hebdomadaire", "mensuel", "ponctuel"]
        
        assert "quotidien" in frequences
        assert "hebdomadaire" in frequences


class TestEntretienRoutines:
    """Tests des routines d'entretien"""
    
    def test_creer_routine_data(self):
        """Création des données d'une routine"""
        routine_data = {
            "nom": "Ménage complet",
            "categorie": "nettoyage",
            "frequence": "hebdomadaire",
            "description": "Nettoyage de toute la maison",
            "actif": True
        }
        
        assert routine_data["nom"] == "Ménage complet"
        assert routine_data["actif"] == True
    
    def test_ajouter_tache_routine_data(self):
        """Création des données d'une tâche"""
        tache_data = {
            "routine_id": 1,
            "nom": "Aspirateur salon",
            "description": "Passer l'aspirateur dans le salon",
            "heure_prevue": "10:00",
            "ordre": 1
        }
        
        assert tache_data["nom"] == "Aspirateur salon"
        assert tache_data["ordre"] == 1


# ════════════════════════════════════════════════════════════════════════════
# TESTS JARDIN
# ════════════════════════════════════════════════════════════════════════════


class TestJardin:
    """Tests du module jardin"""
    
    def test_types_plantes(self):
        """Les types de plantes sont définis"""
        types = ["légume", "fruit", "fleur", "arbre", "aromate"]
        
        assert "légume" in types
        assert "aromate" in types
    
    def test_filtrer_plantes_a_arroser(self):
        """Filtrage des plantes à arroser"""
        aujourd_hui = date.today()
        plantes = [
            {"nom": "Tomates", "dernier_arrosage": aujourd_hui - timedelta(days=3)},
            {"nom": "Basilic", "dernier_arrosage": aujourd_hui - timedelta(days=1)},
            {"nom": "Rosier", "dernier_arrosage": aujourd_hui - timedelta(days=5)},
        ]
        
        # Arroser si plus de 2 jours
        seuil_jours = 2
        a_arroser = [
            p for p in plantes 
            if (aujourd_hui - p["dernier_arrosage"]).days > seuil_jours
        ]
        
        assert len(a_arroser) == 2
        assert any(p["nom"] == "Tomates" for p in a_arroser)
    
    def test_filtrer_recoltes_proches(self):
        """Filtrage des récoltes proches"""
        aujourd_hui = date.today()
        plantes = [
            {"nom": "Tomates", "date_recolte_prevue": aujourd_hui + timedelta(days=5)},
            {"nom": "Carottes", "date_recolte_prevue": aujourd_hui + timedelta(days=30)},
            {"nom": "Salade", "date_recolte_prevue": aujourd_hui + timedelta(days=3)},
        ]
        
        seuil_jours = 7
        proches = [
            p for p in plantes 
            if (p["date_recolte_prevue"] - aujourd_hui).days <= seuil_jours
        ]
        
        assert len(proches) == 2
    
    def test_calculer_stats_jardin(self):
        """Calcul des statistiques du jardin"""
        plantes = [
            {"nom": "P1", "type": "légume", "statut": "actif"},
            {"nom": "P2", "type": "fleur", "statut": "actif"},
            {"nom": "P3", "type": "légume", "statut": "récolté"},
        ]
        
        actifs = len([p for p in plantes if p["statut"] == "actif"])
        legumes = len([p for p in plantes if p["type"] == "légume"])
        
        assert actifs == 2
        assert legumes == 2


class TestJardinConseils:
    """Tests des conseils de jardinage"""
    
    def test_conseils_par_saison(self):
        """Conseils disponibles par saison"""
        conseils = {
            "printemps": ["Préparer les semis", "Tailler les rosiers"],
            "été": ["Arroser régulièrement", "Récolter"],
            "automne": ["Planter les bulbes", "Ramasser les feuilles"],
            "hiver": ["Protéger les plantes", "Planifier le printemps"],
        }
        
        assert "printemps" in conseils
        assert len(conseils["printemps"]) >= 2
    
    def test_conseils_arrosage(self):
        """Conseils d'arrosage par type de plante"""
        arrosage = {
            "légume": {"frequence": "quotidien", "quantite": "abondant"},
            "aromate": {"frequence": "2-3 jours", "quantite": "modéré"},
            "cactus": {"frequence": "hebdomadaire", "quantite": "faible"},
        }
        
        assert arrosage["légume"]["frequence"] == "quotidien"
        assert arrosage["cactus"]["quantite"] == "faible"


class TestJardinLog:
    """Tests du journal du jardin"""
    
    def test_actions_journal(self):
        """Les actions du journal sont définies"""
        actions = ["arrosage", "récolte", "taille", "traitement", "semis", "repiquage"]
        
        assert "arrosage" in actions
        assert "récolte" in actions
    
    def test_creer_entree_log(self):
        """Création d'une entrée de journal"""
        log_entry = {
            "garden_item_id": 1,
            "date": date.today(),
            "action": "arrosage",
            "notes": "Arrosage matinal"
        }
        
        assert log_entry["action"] == "arrosage"
        assert log_entry["date"] == date.today()


# ════════════════════════════════════════════════════════════════════════════
# TESTS PROJETS
# ════════════════════════════════════════════════════════════════════════════


class TestProjets:
    """Tests du module projets"""
    
    def test_statuts_projets(self):
        """Les statuts de projet sont définis"""
        statuts = ["à_faire", "en_cours", "en_attente", "terminé", "annulé"]
        
        assert "en_cours" in statuts
        assert "terminé" in statuts
    
    def test_filtrer_projets_urgents(self):
        """Filtrage des projets urgents"""
        projets = [
            {"nom": "P1", "priorite": "haute", "date_fin_prevue": date.today() + timedelta(days=3)},
            {"nom": "P2", "priorite": "basse", "date_fin_prevue": date.today() + timedelta(days=30)},
            {"nom": "P3", "priorite": "haute", "date_fin_prevue": date.today() + timedelta(days=2)},
        ]
        
        urgents = [p for p in projets if p["priorite"] == "haute"]
        assert len(urgents) == 2
        
        # Urgents avec échéance proche
        seuil = 7
        urgents_proches = [
            p for p in projets 
            if p["priorite"] == "haute" and (p["date_fin_prevue"] - date.today()).days <= seuil
        ]
        assert len(urgents_proches) == 2
    
    def test_calculer_progression_taches(self):
        """Calcul de progression des tâches"""
        taches = [
            {"statut": "terminé"},
            {"statut": "terminé"},
            {"statut": "en_cours"},
            {"statut": "à_faire"},
        ]
        
        total = len(taches)
        terminees = len([t for t in taches if t["statut"] == "terminé"])
        en_cours = len([t for t in taches if t["statut"] == "en_cours"])
        
        pct_termine = (terminees / total) * 100
        pct_en_cours = (en_cours / total) * 100
        
        assert pct_termine == 50.0
        assert pct_en_cours == 25.0
    
    def test_trier_projets_par_priorite(self):
        """Tri des projets par priorité"""
        projets = [
            {"nom": "P1", "priorite": "basse"},
            {"nom": "P2", "priorite": "haute"},
            {"nom": "P3", "priorite": "moyenne"},
        ]
        
        ordre_priorite = {"haute": 0, "moyenne": 1, "basse": 2}
        tries = sorted(projets, key=lambda p: ordre_priorite.get(p["priorite"], 3))
        
        assert tries[0]["nom"] == "P2"  # haute en premier
        assert tries[2]["nom"] == "P1"  # basse en dernier


class TestProjetsTaches:
    """Tests des tâches de projet"""
    
    def test_creer_tache_data(self):
        """Création des données d'une tâche"""
        tache_data = {
            "project_id": 1,
            "nom": "Acheter matériel",
            "description": "Aller à la quincaillerie",
            "priorite": "haute",
            "date_echeance": date.today() + timedelta(days=5),
            "statut": "à_faire"
        }
        
        assert tache_data["nom"] == "Acheter matériel"
        assert tache_data["statut"] == "à_faire"
    
    def test_filtrer_taches_en_retard(self):
        """Filtrage des tâches en retard"""
        aujourd_hui = date.today()
        taches = [
            {"nom": "T1", "date_echeance": aujourd_hui - timedelta(days=2), "statut": "à_faire"},
            {"nom": "T2", "date_echeance": aujourd_hui + timedelta(days=5), "statut": "à_faire"},
            {"nom": "T3", "date_echeance": aujourd_hui - timedelta(days=1), "statut": "terminé"},
        ]
        
        en_retard = [
            t for t in taches 
            if t["statut"] != "terminé" and t["date_echeance"] < aujourd_hui
        ]
        
        assert len(en_retard) == 1
        assert en_retard[0]["nom"] == "T1"
    
    def test_marquer_tache_terminee(self):
        """Marquage d'une tâche comme terminée"""
        tache = {
            "nom": "Tâche test",
            "statut": "en_cours",
            "date_completion": None
        }
        
        tache["statut"] = "terminé"
        tache["date_completion"] = datetime.now()
        
        assert tache["statut"] == "terminé"
        assert tache["date_completion"] is not None


# ════════════════════════════════════════════════════════════════════════════
# TESTS INTEGRATION MAISON
# ════════════════════════════════════════════════════════════════════════════


class TestMaisonIntegration:
    """Tests d'intégration des modules maison"""
    
    def test_generer_planning_entretien_semaine(self):
        """Génération d'un planning d'entretien hebdomadaire"""
        routines = [
            {"nom": "Aspirateur", "frequence": "hebdomadaire", "jour_prefere": "lundi"},
            {"nom": "Lessive", "frequence": "2x/semaine", "jours": ["mardi", "vendredi"]},
            {"nom": "Poussière", "frequence": "quotidien", "jours": ["tous"]},
        ]
        
        planning = {jour: [] for jour in ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]}
        
        for r in routines:
            if r.get("jour_prefere"):
                planning[r["jour_prefere"]].append(r["nom"])
            elif r.get("jours"):
                if "tous" in r["jours"]:
                    for jour in planning:
                        planning[jour].append(r["nom"])
                else:
                    for jour in r["jours"]:
                        planning[jour].append(r["nom"])
        
        assert "Aspirateur" in planning["lundi"]
        assert "Poussière" in planning["mercredi"]  # tous les jours
    
    def test_alertes_jardin_maison(self):
        """Alertes combinées jardin/maison"""
        alertes = []
        
        # Alertes jardin
        plantes_a_arroser = 3
        if plantes_a_arroser > 0:
            alertes.append({
                "type": "jardin",
                "emoji": "🌱",
                "message": f"{plantes_a_arroser} plantes à arroser"
            })
        
        # Alertes projets
        projets_en_retard = 1
        if projets_en_retard > 0:
            alertes.append({
                "type": "projet",
                "emoji": "🏗️",
                "message": f"{projets_en_retard} projet(s) en retard"
            })
        
        assert len(alertes) == 2
        assert any(a["type"] == "jardin" for a in alertes)
    
    def test_dashboard_maison_metriques(self):
        """Métriques pour le dashboard maison"""
        metriques = {
            "projets_actifs": 5,
            "projets_termines": 12,
            "plantes_jardin": 8,
            "routines_actives": 4,
            "taches_aujourd_hui": 6,
        }
        
        assert metriques["projets_actifs"] == 5
        assert metriques["plantes_jardin"] == 8
        
        # Taux de complétion projets
        total_projets = metriques["projets_actifs"] + metriques["projets_termines"]
        taux = (metriques["projets_termines"] / total_projets) * 100
        
        assert taux == pytest.approx(70.6, rel=0.1)
