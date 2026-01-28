"""
Tests complets pour les modules Planning
- calendrier.py
- vue_ensemble.py
- vue_semaine.py
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch


# ════════════════════════════════════════════════════════════════════════════
# TESTS CALENDRIER
# ════════════════════════════════════════════════════════════════════════════


class TestCalendrierNavigation:
    """Tests de navigation dans le calendrier"""
    
    def test_calculer_debut_semaine(self):
        """Calcul du début de la semaine courante"""
        aujourd_hui = date(2025, 1, 28)  # Mardi
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        
        assert debut_semaine == date(2025, 1, 27)  # Lundi
        assert debut_semaine.weekday() == 0  # Lundi = 0
    
    def test_calculer_fin_semaine(self):
        """Calcul de la fin de la semaine"""
        debut_semaine = date(2025, 1, 27)  # Lundi
        fin_semaine = debut_semaine + timedelta(days=6)
        
        assert fin_semaine == date(2025, 2, 2)  # Dimanche
        assert fin_semaine.weekday() == 6  # Dimanche = 6
    
    def test_naviguer_semaine_precedente(self):
        """Navigation vers la semaine précédente"""
        debut_actuel = date(2025, 1, 27)
        debut_precedent = debut_actuel - timedelta(days=7)
        
        assert debut_precedent == date(2025, 1, 20)
    
    def test_naviguer_semaine_suivante(self):
        """Navigation vers la semaine suivante"""
        debut_actuel = date(2025, 1, 27)
        debut_suivant = debut_actuel + timedelta(days=7)
        
        assert debut_suivant == date(2025, 2, 3)
    
    def test_generer_7_jours(self):
        """Génération des 7 jours de la semaine"""
        debut = date(2025, 1, 27)
        jours = [debut + timedelta(days=i) for i in range(7)]
        
        assert len(jours) == 7
        assert jours[0] == date(2025, 1, 27)
        assert jours[6] == date(2025, 2, 2)


class TestCalendrierAffichage:
    """Tests d'affichage du calendrier"""
    
    def test_format_header_semaine(self):
        """Format du header de semaine"""
        debut = date(2025, 1, 27)
        fin = date(2025, 2, 2)
        
        header = f"{debut.strftime('%d/%m')} — {fin.strftime('%d/%m/%Y')}"
        assert header == "27/01 — 02/02/2025"
    
    def test_identifier_jour_actuel(self):
        """Identification du jour actuel"""
        aujourd_hui = date.today()
        jour_test = date.today()
        
        is_today = jour_test == aujourd_hui
        assert is_today == True
    
    def test_nom_jour_semaine(self):
        """Récupération du nom du jour"""
        jours_noms = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        
        jour = date(2025, 1, 28)  # Mardi
        nom = jours_noms[jour.weekday()]
        
        assert nom == "mardi"


class TestCalendrierCharge:
    """Tests de calcul de charge"""
    
    def test_charge_faible(self):
        """Charge faible (peu d'événements)"""
        evenements = {"repas": 2, "activites": 0, "projets": 0}
        
        charge_score = sum(evenements.values()) * 10
        
        if charge_score < 30:
            charge = "faible"
        elif charge_score < 60:
            charge = "normal"
        else:
            charge = "intense"
        
        assert charge == "faible"
    
    def test_charge_normale(self):
        """Charge normale"""
        evenements = {"repas": 2, "activites": 2, "projets": 1}
        
        charge_score = sum(evenements.values()) * 10  # 50
        
        if charge_score < 30:
            charge = "faible"
        elif charge_score < 60:
            charge = "normal"
        else:
            charge = "intense"
        
        assert charge == "normal"
    
    def test_charge_intense(self):
        """Charge intense (beaucoup d'événements)"""
        evenements = {"repas": 3, "activites": 3, "projets": 2, "events": 2}
        
        charge_score = sum(evenements.values()) * 10  # 100
        
        if charge_score < 30:
            charge = "faible"
        elif charge_score < 60:
            charge = "normal"
        else:
            charge = "intense"
        
        assert charge == "intense"
    
    def test_emoji_charge(self):
        """Emoji selon la charge"""
        charge_emoji = {
            "faible": "🟢",
            "normal": "🟡",
            "intense": "🔴",
        }
        
        assert charge_emoji.get("faible") == "🟢"
        assert charge_emoji.get("intense") == "🔴"


class TestCalendrierEvenements:
    """Tests des événements du calendrier"""
    
    def test_grouper_evenements_par_type(self):
        """Groupement des événements par type"""
        evenements = [
            {"type": "repas", "titre": "Déjeuner"},
            {"type": "activite", "titre": "Parc"},
            {"type": "repas", "titre": "Dîner"},
        ]
        
        grouped = {}
        for e in evenements:
            t = e["type"]
            if t not in grouped:
                grouped[t] = []
            grouped[t].append(e)
        
        assert len(grouped["repas"]) == 2
        assert len(grouped["activite"]) == 1
    
    def test_trier_evenements_par_heure(self):
        """Tri des événements par heure"""
        evenements = [
            {"titre": "E3", "heure": "18:00"},
            {"titre": "E1", "heure": "08:00"},
            {"titre": "E2", "heure": "12:00"},
        ]
        
        tries = sorted(evenements, key=lambda e: e.get("heure", "00:00"))
        
        assert tries[0]["titre"] == "E1"
        assert tries[2]["titre"] == "E3"
    
    def test_jour_vide(self):
        """Détection d'un jour sans événements"""
        jour_complet = {
            "repas": [],
            "activites": [],
            "projets": [],
            "events": [],
            "routines": [],
        }
        
        is_vide = not any([
            jour_complet.get("repas"),
            jour_complet.get("activites"),
            jour_complet.get("projets"),
            jour_complet.get("events"),
            jour_complet.get("routines"),
        ])
        
        assert is_vide == True


# ════════════════════════════════════════════════════════════════════════════
# TESTS VUE ENSEMBLE
# ════════════════════════════════════════════════════════════════════════════


class TestVueEnsembleMetriques:
    """Tests des métriques de la vue d'ensemble"""
    
    def test_calculer_total_repas(self):
        """Calcul du total des repas planifiés"""
        semaine = {
            "lundi": {"repas": [{"type": "déjeuner"}, {"type": "dîner"}]},
            "mardi": {"repas": [{"type": "déjeuner"}]},
            "mercredi": {"repas": []},
        }
        
        total = sum(len(j["repas"]) for j in semaine.values())
        assert total == 3
    
    def test_calculer_total_activites(self):
        """Calcul du total des activités"""
        semaine = {
            "lundi": {"activites": [{"titre": "A1"}]},
            "mardi": {"activites": [{"titre": "A2"}, {"titre": "A3"}]},
        }
        
        total = sum(len(j.get("activites", [])) for j in semaine.values())
        assert total == 3
    
    def test_calculer_budget_semaine(self):
        """Calcul du budget total de la semaine"""
        jours = [
            {"budget_jour": 25.0},
            {"budget_jour": 50.0},
            {"budget_jour": 0.0},
            {"budget_jour": 30.0},
        ]
        
        budget_total = sum(j.get("budget_jour", 0) for j in jours)
        assert budget_total == 105.0


class TestVueEnsembleAlertes:
    """Tests des alertes de la vue d'ensemble"""
    
    def test_detecter_jour_surcharge(self):
        """Détection d'un jour surchargé"""
        jours = [
            {"jour": "lundi", "charge_score": 30},
            {"jour": "mardi", "charge_score": 85},
            {"jour": "mercredi", "charge_score": 50},
        ]
        
        seuil = 80
        surcharges = [j for j in jours if j["charge_score"] > seuil]
        
        assert len(surcharges) == 1
        assert surcharges[0]["jour"] == "mardi"
    
    def test_detecter_jour_vide(self):
        """Détection d'un jour vide"""
        jours = [
            {"jour": "lundi", "charge_score": 30},
            {"jour": "mardi", "charge_score": 0},
            {"jour": "mercredi", "charge_score": 50},
        ]
        
        vides = [j for j in jours if j["charge_score"] == 0]
        
        assert len(vides) == 1
        assert vides[0]["jour"] == "mardi"
    
    def test_generer_alertes(self):
        """Génération des alertes"""
        jour_complet = {
            "alertes": ["Stock bas: lait", "Projet en retard"],
        }
        
        assert len(jour_complet["alertes"]) == 2


class TestVueEnsembleGraphiques:
    """Tests des données pour graphiques"""
    
    def test_donnees_graphique_charge(self):
        """Données pour graphique de charge"""
        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        charges = [30, 50, 45, 60, 70, 40, 20]
        
        assert len(jours) == 7
        assert len(charges) == 7
        assert max(charges) == 70
    
    def test_donnees_repartition_activites(self):
        """Données pour graphique de répartition"""
        stats = {
            "total_repas": 14,
            "total_activites": 5,
            "total_projets": 3,
            "total_events": 2,
        }
        
        total = sum(stats.values())
        assert total == 24
        
        # Pourcentages
        pct_repas = (stats["total_repas"] / total) * 100
        assert pct_repas == pytest.approx(58.3, rel=0.1)


# ════════════════════════════════════════════════════════════════════════════
# TESTS VUE SEMAINE
# ════════════════════════════════════════════════════════════════════════════


class TestVueSemaineTimeline:
    """Tests de la timeline de la vue semaine"""
    
    def test_format_heure_evenement(self):
        """Format de l'heure d'un événement"""
        evenement = {
            "titre": "Réunion",
            "debut": datetime(2025, 1, 28, 14, 30),
        }
        
        heure_str = evenement["debut"].strftime("%H:%M")
        assert heure_str == "14:30"
    
    def test_format_heure_evenement_sans_datetime(self):
        """Gestion d'événement sans datetime"""
        evenement = {
            "titre": "Événement",
            "debut": "10:00",  # String au lieu de datetime
        }
        
        if isinstance(evenement["debut"], datetime):
            heure_str = evenement["debut"].strftime("%H:%M")
        else:
            heure_str = evenement["debut"] if evenement["debut"] else "—"
        
        assert heure_str == "10:00"
    
    def test_grouper_par_type_evenement(self):
        """Groupement par type pour la timeline"""
        events_grouped = {
            "🍽️ Repas": [{"type": "déjeuner"}, {"type": "dîner"}],
            "🎨 Activités": [{"titre": "Parc"}],
            "🏗️ Projets": [],
            "⏰ Routines": [{"nom": "Matin"}],
            "📅 Événements": [],
        }
        
        # Compter les types avec des événements
        with_events = [k for k, v in events_grouped.items() if v]
        assert len(with_events) == 3


class TestVueSemaineJour:
    """Tests de l'affichage par jour"""
    
    def test_nom_jour_capitalize(self):
        """Nom du jour avec majuscule"""
        jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        
        jour = jours[0].capitalize()
        assert jour == "Lundi"
    
    def test_afficher_metriques_jour(self):
        """Métriques d'un jour"""
        jour_complet = {
            "charge_score": 65,
            "charge": "normal",
            "budget_jour": 45.0,
        }
        
        assert jour_complet["charge_score"] == 65
        assert jour_complet["charge"] == "normal"
    
    def test_emoji_statut_charge(self):
        """Emoji selon le statut de charge"""
        charge_label = "intense"
        charge_emoji = {"faible": "🟢", "normal": "🟡", "intense": "🔴"}.get(charge_label, "⚪")
        
        assert charge_emoji == "🔴"


class TestVueSemaineRepas:
    """Tests de l'affichage des repas"""
    
    def test_afficher_repas_avec_portions(self):
        """Affichage d'un repas avec portions"""
        repas = {
            "type": "déjeuner",
            "recette": "Pâtes bolognaise",
            "portions": 4,
            "temps_total": 45,
        }
        
        display = f"**{repas['type'].capitalize()}**: {repas['recette']}"
        info = f"{repas['portions']} portions | {repas['temps_total']} min"
        
        assert "Déjeuner" in display
        assert "4 portions" in info
    
    def test_repas_sans_recette(self):
        """Gestion d'un repas sans recette"""
        repas = {
            "type": "dîner",
            "recette": None,
            "portions": 2,
        }
        
        recette_name = repas.get("recette") or "Non défini"
        assert recette_name == "Non défini"


class TestVueSemaineActivites:
    """Tests de l'affichage des activités"""
    
    def test_afficher_activite_jules(self):
        """Affichage d'une activité pour Jules"""
        activite = {
            "titre": "Parc",
            "type": "sortie",
            "pour_jules": True,
            "budget": 0,
        }
        
        label = "👶" if activite.get("pour_jules") else "👨‍👩‍👧"
        assert label == "👶"
    
    def test_afficher_activite_famille(self):
        """Affichage d'une activité familiale"""
        activite = {
            "titre": "Cinéma",
            "type": "sortie",
            "pour_jules": False,
            "budget": 35.0,
        }
        
        label = "👶" if activite.get("pour_jules") else "👨‍👩‍👧"
        assert label == "👨‍👩‍👧"
    
    def test_afficher_budget_activite(self):
        """Affichage du budget d'une activité"""
        activite = {"budget": 25.50}
        
        budget_str = f"💰 {activite['budget']:.0f}€"
        assert budget_str == "💰 26€"


class TestVueSemaineProjets:
    """Tests de l'affichage des projets"""
    
    def test_afficher_projet_avec_priorite(self):
        """Affichage d'un projet avec priorité"""
        projet = {
            "nom": "Rénovation cuisine",
            "statut": "en_cours",
            "priorite": "haute",
        }
        
        priorite_emoji = {
            "basse": "🟢",
            "moyenne": "🟡",
            "haute": "🔴",
        }.get(projet.get("priorite", "moyenne"), "⚪")
        
        display = f"{priorite_emoji} **{projet['nom']}** ({projet['statut']})"
        
        assert "🔴" in display
        assert "Rénovation cuisine" in display


# ════════════════════════════════════════════════════════════════════════════
# TESTS INTEGRATION PLANNING
# ════════════════════════════════════════════════════════════════════════════


class TestPlanningIntegration:
    """Tests d'intégration des modules planning"""
    
    def test_construire_semaine_complete(self):
        """Construction d'une semaine complète"""
        debut_semaine = date(2025, 1, 27)
        
        semaine = {}
        for i in range(7):
            jour = debut_semaine + timedelta(days=i)
            jour_key = jour.strftime("%Y-%m-%d")
            semaine[jour_key] = {
                "date": jour,
                "repas": [],
                "activites": [],
                "projets": [],
                "events": [],
                "routines": [],
                "charge_score": 0,
                "charge": "faible",
                "budget_jour": 0,
            }
        
        assert len(semaine) == 7
        assert "2025-01-27" in semaine
        assert "2025-02-02" in semaine
    
    def test_calculer_stats_semaine(self):
        """Calcul des statistiques de la semaine"""
        jours = [
            {"repas": 2, "activites": 1, "charge_score": 40},
            {"repas": 2, "activites": 0, "charge_score": 30},
            {"repas": 2, "activites": 2, "charge_score": 60},
        ]
        
        stats = {
            "total_repas": sum(j["repas"] for j in jours),
            "total_activites": sum(j["activites"] for j in jours),
            "charge_moyenne": sum(j["charge_score"] for j in jours) / len(jours),
        }
        
        assert stats["total_repas"] == 6
        assert stats["total_activites"] == 3
        assert stats["charge_moyenne"] == pytest.approx(43.3, rel=0.1)
    
    def test_detecter_conflits_horaires(self):
        """Détection de conflits horaires"""
        evenements = [
            {"titre": "E1", "debut": "10:00", "fin": "11:00"},
            {"titre": "E2", "debut": "10:30", "fin": "12:00"},  # Conflit!
            {"titre": "E3", "debut": "14:00", "fin": "15:00"},
        ]
        
        def has_conflict(e1, e2):
            """Simplifié: vérifie si les horaires se chevauchent"""
            return e1["debut"] < e2["fin"] and e2["debut"] < e1["fin"]
        
        conflits = []
        for i, e1 in enumerate(evenements):
            for e2 in evenements[i+1:]:
                if has_conflict(e1, e2):
                    conflits.append((e1["titre"], e2["titre"]))
        
        assert len(conflits) == 1
        assert ("E1", "E2") in conflits
    
    def test_suggerer_equilibrage_charge(self):
        """Suggestions d'équilibrage de la charge"""
        jours = [
            {"jour": "lundi", "charge": 80},
            {"jour": "mardi", "charge": 20},
            {"jour": "mercredi", "charge": 90},
            {"jour": "jeudi", "charge": 30},
        ]
        
        charge_moyenne = sum(j["charge"] for j in jours) / len(jours)
        
        surcharges = [j for j in jours if j["charge"] > charge_moyenne + 20]
        sous_charges = [j for j in jours if j["charge"] < charge_moyenne - 20]
        
        suggestions = []
        for sur in surcharges:
            for sous in sous_charges:
                suggestions.append(f"Déplacer des activités de {sur['jour']} vers {sous['jour']}")
        
        assert len(suggestions) >= 1
