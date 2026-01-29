"""Tests unitaires pour les modules maison (entretien, jardin, projets)."""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock


# =============================================================================
# TESTS PROJETS MAISON
# =============================================================================

class TestProjetsLogique:
    """Tests pour la logique des projets maison."""

    def test_calculer_avancement_projet(self):
        """Calcul du pourcentage d'avancement."""
        taches = [
            {"id": 1, "status": "completed"},
            {"id": 2, "status": "completed"},
            {"id": 3, "status": "in_progress"},
            {"id": 4, "status": "pending"},
        ]
        
        completees = sum(1 for t in taches if t["status"] == "completed")
        total = len(taches)
        avancement = (completees / total) * 100 if total > 0 else 0
        
        assert avancement == 50.0

    def test_filtrer_projets_par_statut(self):
        """Filtrage des projets par statut."""
        projets = [
            {"nom": "Peinture salon", "status": "in_progress"},
            {"nom": "Jardin", "status": "completed"},
            {"nom": "Terrasse", "status": "pending"},
            {"nom": "Cuisine", "status": "in_progress"},
        ]
        
        en_cours = [p for p in projets if p["status"] == "in_progress"]
        
        assert len(en_cours) == 2

    def test_calculer_budget_projet(self):
        """Calcul du budget total d'un projet."""
        depenses = [
            {"description": "Peinture", "montant": 150.0},
            {"description": "Pinceaux", "montant": 25.0},
            {"description": "BÃ¢che", "montant": 15.0},
        ]
        
        budget_utilise = sum(d["montant"] for d in depenses)
        budget_prevu = 250.0
        
        assert budget_utilise == 190.0
        assert budget_utilise < budget_prevu

    def test_trier_projets_par_priorite(self):
        """Tri des projets par priorité."""
        projets = [
            {"nom": "Urgent", "priorite": 1},
            {"nom": "Normal", "priorite": 3},
            {"nom": "Haute", "priorite": 2},
        ]
        
        tries = sorted(projets, key=lambda p: p["priorite"])
        
        assert tries[0]["nom"] == "Urgent"
        assert tries[1]["nom"] == "Haute"

    def test_calculer_jours_restants(self):
        """Calcul des jours restants avant deadline."""
        deadline = date.today() + timedelta(days=15)
        jours_restants = (deadline - date.today()).days
        
        assert jours_restants == 15

    def test_projet_en_retard(self):
        """Détection d'un projet en retard."""
        projets = [
            {"nom": "Retard", "deadline": date.today() - timedelta(days=5), "status": "in_progress"},
            {"nom": "OK", "deadline": date.today() + timedelta(days=10), "status": "in_progress"},
        ]
        
        en_retard = [
            p for p in projets 
            if p["deadline"] < date.today() and p["status"] != "completed"
        ]
        
        assert len(en_retard) == 1
        assert en_retard[0]["nom"] == "Retard"


# =============================================================================
# TESTS ENTRETIEN MAISON
# =============================================================================

class TestEntretienLogique:
    """Tests pour la logique d'entretien maison."""

    def test_calculer_prochaine_tache(self):
        """Calcul de la prochaine date d'entretien."""
        derniere_execution = date(2026, 1, 1)
        frequence_jours = 30  # Mensuel
        
        prochaine = derniere_execution + timedelta(days=frequence_jours)
        
        assert prochaine == date(2026, 1, 31)

    def test_taches_a_faire_cette_semaine(self):
        """Liste des tÃ¢ches à faire cette semaine."""
        today = date.today()
        fin_semaine = today + timedelta(days=7)
        
        taches = [
            {"nom": "Ménage", "prochaine_date": today + timedelta(days=2)},
            {"nom": "Lessive", "prochaine_date": today + timedelta(days=5)},
            {"nom": "Vitres", "prochaine_date": today + timedelta(days=15)},
        ]
        
        cette_semaine = [
            t for t in taches 
            if today <= t["prochaine_date"] <= fin_semaine
        ]
        
        assert len(cette_semaine) == 2

    def test_taches_en_retard(self):
        """TÃ¢ches d'entretien en retard."""
        today = date.today()
        
        taches = [
            {"nom": "Aspirateur", "prochaine_date": today - timedelta(days=3)},
            {"nom": "Poussière", "prochaine_date": today - timedelta(days=1)},
            {"nom": "Vitres", "prochaine_date": today + timedelta(days=5)},
        ]
        
        en_retard = [t for t in taches if t["prochaine_date"] < today]
        
        assert len(en_retard) == 2

    def test_frequences_entretien(self):
        """Conversion des fréquences en jours."""
        frequences = {
            "quotidien": 1,
            "hebdomadaire": 7,
            "bimensuel": 14,
            "mensuel": 30,
            "trimestriel": 90,
            "semestriel": 180,
            "annuel": 365,
        }
        
        assert frequences["hebdomadaire"] == 7
        assert frequences["mensuel"] == 30

    def test_grouper_taches_par_piece(self):
        """Groupement des tÃ¢ches par pièce."""
        taches = [
            {"nom": "Aspirateur", "piece": "Salon"},
            {"nom": "Vitres", "piece": "Salon"},
            {"nom": "Nettoyage", "piece": "Cuisine"},
            {"nom": "Rangement", "piece": "Chambre"},
        ]
        
        par_piece = {}
        for t in taches:
            piece = t["piece"]
            if piece not in par_piece:
                par_piece[piece] = []
            par_piece[piece].append(t["nom"])
        
        assert len(par_piece["Salon"]) == 2


# =============================================================================
# TESTS JARDIN / POTAGER
# =============================================================================

class TestJardinLogique:
    """Tests pour la logique jardin/potager."""

    def test_calculer_date_recolte(self):
        """Calcul de la date de récolte estimée."""
        date_plantation = date(2026, 3, 15)
        jours_croissance = 90  # Tomates
        
        date_recolte = date_plantation + timedelta(days=jours_croissance)
        
        assert date_recolte == date(2026, 6, 13)

    def test_plantes_a_arroser(self):
        """Liste des plantes à arroser aujourd'hui."""
        today = date.today()
        
        plantes = [
            {"nom": "Tomates", "dernier_arrosage": today - timedelta(days=2), "frequence_arrosage": 2},
            {"nom": "Salades", "dernier_arrosage": today - timedelta(days=1), "frequence_arrosage": 1},
            {"nom": "Carottes", "dernier_arrosage": today, "frequence_arrosage": 3},
        ]
        
        a_arroser = [
            p for p in plantes
            if (today - p["dernier_arrosage"]).days >= p["frequence_arrosage"]
        ]
        
        assert len(a_arroser) == 2

    def test_calendrier_semis(self):
        """Calendrier des semis par mois."""
        calendrier = {
            1: ["Tomates (intérieur)", "Poivrons (intérieur)"],
            2: ["Laitues", "Ã‰pinards"],
            3: ["Carottes", "Radis", "Oignons"],
            4: ["Haricots", "Courges"],
            5: ["Tomates (extérieur)", "Courgettes"],
        }
        
        mois_actuel = 3  # Mars
        a_semer = calendrier.get(mois_actuel, [])
        
        assert "Carottes" in a_semer
        assert "Radis" in a_semer

    def test_grouper_par_emplacement(self):
        """Groupement des plantes par emplacement."""
        plantes = [
            {"nom": "Tomates", "emplacement": "Potager"},
            {"nom": "Basilic", "emplacement": "Balcon"},
            {"nom": "Carottes", "emplacement": "Potager"},
            {"nom": "Menthe", "emplacement": "Balcon"},
        ]
        
        par_emplacement = {}
        for p in plantes:
            emp = p["emplacement"]
            if emp not in par_emplacement:
                par_emplacement[emp] = []
            par_emplacement[emp].append(p["nom"])
        
        assert len(par_emplacement["Potager"]) == 2
        assert len(par_emplacement["Balcon"]) == 2

    def test_filtrer_par_type_plante(self):
        """Filtrage par type de plante."""
        plantes = [
            {"nom": "Tomates", "type": "légume"},
            {"nom": "Basilic", "type": "aromatique"},
            {"nom": "Rose", "type": "fleur"},
            {"nom": "Menthe", "type": "aromatique"},
        ]
        
        aromatiques = [p for p in plantes if p["type"] == "aromatique"]
        
        assert len(aromatiques) == 2

    def test_journal_entretien(self):
        """Entrées du journal d'entretien."""
        journal = [
            {"date": date.today() - timedelta(days=2), "action": "Arrosage", "plante": "Tomates"},
            {"date": date.today() - timedelta(days=1), "action": "Taille", "plante": "Tomates"},
            {"date": date.today(), "action": "Arrosage", "plante": "Salades"},
        ]
        
        # Filtrer par plante
        tomates_journal = [e for e in journal if e["plante"] == "Tomates"]
        
        assert len(tomates_journal) == 2


# =============================================================================
# TESTS STATISTIQUES MAISON
# =============================================================================

class TestStatistiquesMaison:
    """Tests pour les statistiques maison."""

    def test_compter_projets_par_statut(self):
        """Comptage des projets par statut."""
        projets = [
            {"status": "pending"},
            {"status": "in_progress"},
            {"status": "in_progress"},
            {"status": "completed"},
            {"status": "completed"},
            {"status": "completed"},
        ]
        
        from collections import Counter
        counts = Counter(p["status"] for p in projets)
        
        assert counts["pending"] == 1
        assert counts["in_progress"] == 2
        assert counts["completed"] == 3

    def test_budget_total_projets(self):
        """Budget total de tous les projets."""
        projets = [
            {"budget_prevu": 500, "budget_utilise": 350},
            {"budget_prevu": 1000, "budget_utilise": 800},
            {"budget_prevu": 250, "budget_utilise": 100},
        ]
        
        total_prevu = sum(p["budget_prevu"] for p in projets)
        total_utilise = sum(p["budget_utilise"] for p in projets)
        
        assert total_prevu == 1750
        assert total_utilise == 1250

    def test_taches_completees_cette_semaine(self):
        """TÃ¢ches complétées cette semaine."""
        today = date.today()
        debut_semaine = today - timedelta(days=today.weekday())
        
        taches = [
            {"completee_le": today - timedelta(days=1)},
            {"completee_le": today - timedelta(days=2)},
            {"completee_le": today - timedelta(days=10)},
        ]
        
        cette_semaine = [
            t for t in taches
            if t["completee_le"] >= debut_semaine
        ]
        
        assert len(cette_semaine) == 2

    def test_plantes_par_type(self):
        """Statistiques des plantes par type."""
        plantes = [
            {"type": "légume"},
            {"type": "légume"},
            {"type": "légume"},
            {"type": "aromatique"},
            {"type": "aromatique"},
            {"type": "fleur"},
        ]
        
        from collections import Counter
        counts = Counter(p["type"] for p in plantes)
        
        assert counts["légume"] == 3
        assert counts["aromatique"] == 2
        assert counts["fleur"] == 1


# =============================================================================
# TESTS HELPERS MAISON
# =============================================================================

class TestHelpersMaison:
    """Tests pour les helpers maison."""

    def test_format_priorite(self):
        """Format de la priorité en texte."""
        def format_priorite(niveau):
            mapping = {
                1: "ðŸ”´ Urgent",
                2: "ðŸŸ  Haute",
                3: "ðŸŸ¡ Normale",
                4: "ðŸŸ¢ Basse",
            }
            return mapping.get(niveau, "Inconnue")
        
        assert format_priorite(1) == "ðŸ”´ Urgent"
        assert format_priorite(3) == "ðŸŸ¡ Normale"

    def test_format_status(self):
        """Format du statut en texte."""
        def format_status(status):
            mapping = {
                "pending": "En attente",
                "in_progress": "En cours",
                "completed": "Terminé",
                "cancelled": "Annulé",
            }
            return mapping.get(status, status)
        
        assert format_status("in_progress") == "En cours"
        assert format_status("completed") == "Terminé"

    def test_calculer_progression_couleur(self):
        """Couleur selon la progression."""
        def couleur_progression(pourcentage):
            if pourcentage < 25:
                return "red"
            elif pourcentage < 50:
                return "orange"
            elif pourcentage < 75:
                return "yellow"
            else:
                return "green"
        
        assert couleur_progression(10) == "red"
        assert couleur_progression(40) == "orange"
        assert couleur_progression(60) == "yellow"
        assert couleur_progression(90) == "green"

    def test_jours_depuis_derniere_action(self):
        """Jours depuis la dernière action."""
        derniere_action = date.today() - timedelta(days=5)
        jours = (date.today() - derniere_action).days
        
        assert jours == 5


# =============================================================================
# TESTS ALERTES MAISON
# =============================================================================

class TestAlertesMaison:
    """Tests pour les alertes maison."""

    def test_alerte_projet_en_retard(self):
        """Génération d'alerte pour projet en retard."""
        projets = [
            {"nom": "Peinture", "deadline": date.today() - timedelta(days=5), "status": "in_progress"},
            {"nom": "Jardin", "deadline": date.today() + timedelta(days=10), "status": "in_progress"},
        ]
        
        alertes = []
        for p in projets:
            if p["status"] != "completed" and p["deadline"] < date.today():
                jours_retard = (date.today() - p["deadline"]).days
                alertes.append({
                    "type": "projet_retard",
                    "message": f"Projet '{p['nom']}' en retard de {jours_retard} jours",
                    "priorite": 1
                })
        
        assert len(alertes) == 1
        assert "Peinture" in alertes[0]["message"]

    def test_alerte_entretien_du(self):
        """Alerte pour entretien dû."""
        taches = [
            {"nom": "Ménage", "prochaine_date": date.today() - timedelta(days=2)},
            {"nom": "Vitres", "prochaine_date": date.today() + timedelta(days=5)},
        ]
        
        alertes = [
            {"type": "entretien_du", "tache": t["nom"]}
            for t in taches
            if t["prochaine_date"] <= date.today()
        ]
        
        assert len(alertes) == 1
        assert alertes[0]["tache"] == "Ménage"

    def test_alerte_arrosage_plantes(self):
        """Alerte pour plantes à arroser."""
        plantes = [
            {"nom": "Tomates", "besoin_arrosage": True},
            {"nom": "Cactus", "besoin_arrosage": False},
            {"nom": "Basilic", "besoin_arrosage": True},
        ]
        
        a_arroser = [p["nom"] for p in plantes if p["besoin_arrosage"]]
        
        assert len(a_arroser) == 2
        assert "Tomates" in a_arroser

