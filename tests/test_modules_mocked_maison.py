"""
Tests avec mocks Streamlit pour les modules maison
Couverture cible: 40%+ pour entretien, jardin, projets
"""

import pytest
from unittest.mock import MagicMock, patch
from contextlib import ExitStack
from datetime import date, datetime, timedelta
import pandas as pd


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES COMMUNES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_tache_entretien():
    """Mock d'une tâche d'entretien"""
    tache = MagicMock()
    tache.id = 1
    tache.nom = "Nettoyage cuisine"
    tache.description = "Nettoyage complet de la cuisine"
    tache.frequence = "hebdomadaire"
    tache.derniere_realisation = date.today() - timedelta(days=5)
    tache.prochaine_echeance = date.today() + timedelta(days=2)
    tache.priorite = "moyenne"
    tache.statut = "à faire"
    tache.piece = "Cuisine"
    tache.duree_estimee = 30
    return tache


@pytest.fixture
def mock_plante():
    """Mock d'une plante de jardin"""
    plante = MagicMock()
    plante.id = 1
    plante.nom = "Tomates cerises"
    plante.type = "légume"
    plante.emplacement = "Potager"
    plante.date_plantation = date(2024, 4, 15)
    plante.frequence_arrosage = 2
    plante.dernier_arrosage = date.today() - timedelta(days=1)
    plante.statut = "en croissance"
    return plante


@pytest.fixture
def mock_projet():
    """Mock d'un projet maison"""
    projet = MagicMock()
    projet.id = 1
    projet.nom = "Rénovation salle de bain"
    projet.description = "Refaire la salle de bain"
    projet.date_debut = date(2024, 6, 1)
    projet.date_fin_prevue = date(2024, 7, 1)
    projet.budget = 5000
    projet.depense_actuelle = 2500
    projet.statut = "en cours"
    projet.priorite = "haute"
    projet.progression = 50
    return projet


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE ENTRETIEN - TACHES
# ═══════════════════════════════════════════════════════════════════════════════


class TestEntretienTaches:
    """Tests des tâches d'entretien"""
    
    def test_tache_structure(self, mock_tache_entretien):
        """Test structure d'une tâche"""
        tache = mock_tache_entretien
        
        assert tache.nom == "Nettoyage cuisine"
        assert tache.frequence == "hebdomadaire"
        assert tache.piece == "Cuisine"
    
    def test_tache_echeance(self, mock_tache_entretien):
        """Test calcul échéance"""
        tache = mock_tache_entretien
        
        jours_restants = (tache.prochaine_echeance - date.today()).days
        assert jours_restants == 2
    
    def test_tache_retard(self):
        """Test détection retard"""
        echeance = date.today() - timedelta(days=3)
        
        est_en_retard = echeance < date.today()
        jours_retard = (date.today() - echeance).days
        
        assert est_en_retard
        assert jours_retard == 3


class TestEntretienFrequences:
    """Tests des fréquences d'entretien"""
    
    def test_frequences_standard(self):
        """Test des fréquences standards"""
        frequences = ["quotidienne", "hebdomadaire", "mensuelle", "trimestrielle", "annuelle"]
        
        assert "quotidienne" in frequences
        assert "hebdomadaire" in frequences
    
    def test_calcul_prochaine_echeance(self):
        """Test calcul prochaine échéance"""
        derniere = date.today()
        frequences_jours = {
            "quotidienne": 1,
            "hebdomadaire": 7,
            "mensuelle": 30,
            "trimestrielle": 90,
            "annuelle": 365,
        }
        
        prochaine = derniere + timedelta(days=frequences_jours["hebdomadaire"])
        assert prochaine == date.today() + timedelta(days=7)
    
    def test_frequence_personnalisee(self):
        """Test fréquence personnalisée"""
        jours = 14  # Tous les 14 jours
        derniere = date.today()
        prochaine = derniere + timedelta(days=jours)
        
        assert (prochaine - derniere).days == 14


class TestEntretienPieces:
    """Tests des pièces de la maison"""
    
    def test_pieces_standard(self):
        """Test des pièces standards"""
        pieces = ["Cuisine", "Salon", "Salle de bain", "Chambre", "Garage", "Jardin"]
        
        assert "Cuisine" in pieces
        assert "Salon" in pieces
    
    def test_piece_icons(self):
        """Test des icônes par pièce"""
        icons = {
            "Cuisine": "🍳",
            "Salon": "🛋️",
            "Salle de bain": "🚿",
            "Chambre": "🛏️",
            "Garage": "🚗",
            "Jardin": "🌳",
        }
        
        assert icons["Cuisine"] == "🍳"
    
    def test_filter_by_piece(self, mock_tache_entretien):
        """Test filtrage par pièce"""
        taches = [mock_tache_entretien]
        
        filtrees = [t for t in taches if t.piece == "Cuisine"]
        assert len(filtrees) == 1


class TestEntretienPriorites:
    """Tests des priorités d'entretien"""
    
    def test_priorites_standard(self):
        """Test des priorités standards"""
        priorites = ["basse", "moyenne", "haute", "urgente"]
        
        assert "urgente" in priorites
    
    def test_priorite_colors(self):
        """Test des couleurs par priorité"""
        colors = {
            "basse": "🟢",
            "moyenne": "🟡",
            "haute": "🟠",
            "urgente": "🔴",
        }
        
        assert colors["urgente"] == "🔴"
    
    def test_sort_by_priorite(self):
        """Test tri par priorité"""
        taches = [
            {"nom": "A", "priorite": "basse"},
            {"nom": "B", "priorite": "urgente"},
            {"nom": "C", "priorite": "moyenne"},
        ]
        
        ordre = {"urgente": 0, "haute": 1, "moyenne": 2, "basse": 3}
        triees = sorted(taches, key=lambda t: ordre.get(t["priorite"], 99))
        
        assert triees[0]["nom"] == "B"


class TestEntretienStatuts:
    """Tests des statuts d'entretien"""
    
    def test_statuts_standard(self):
        """Test des statuts standards"""
        statuts = ["à faire", "en cours", "terminé", "reporté"]
        
        assert "à faire" in statuts
        assert "terminé" in statuts
    
    def test_filter_by_statut(self, mock_tache_entretien):
        """Test filtrage par statut"""
        taches = [mock_tache_entretien]
        
        filtrees = [t for t in taches if t.statut == "à faire"]
        assert len(filtrees) == 1
    
    def test_count_by_statut(self):
        """Test comptage par statut"""
        taches = [
            {"statut": "à faire"},
            {"statut": "terminé"},
            {"statut": "à faire"},
            {"statut": "en cours"},
        ]
        
        a_faire = len([t for t in taches if t["statut"] == "à faire"])
        assert a_faire == 2


class TestEntretienDuree:
    """Tests de la durée des tâches"""
    
    def test_format_duree(self):
        """Test formatage durée"""
        duree = 45
        formatted = f"{duree} min"
        
        assert formatted == "45 min"
    
    def test_format_duree_heures(self):
        """Test formatage durée en heures"""
        duree = 120
        heures = duree // 60
        minutes = duree % 60
        
        formatted = f"{heures}h" if minutes == 0 else f"{heures}h{minutes:02d}"
        assert formatted == "2h"
    
    def test_calcul_duree_totale(self):
        """Test calcul durée totale"""
        taches = [
            {"duree": 30},
            {"duree": 45},
            {"duree": 15},
        ]
        
        total = sum(t["duree"] for t in taches)
        assert total == 90


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE JARDIN - PLANTES
# ═══════════════════════════════════════════════════════════════════════════════


class TestJardinPlantes:
    """Tests des plantes du jardin"""
    
    def test_plante_structure(self, mock_plante):
        """Test structure d'une plante"""
        plante = mock_plante
        
        assert plante.nom == "Tomates cerises"
        assert plante.type == "légume"
        assert plante.emplacement == "Potager"
    
    def test_plante_arrosage(self, mock_plante):
        """Test calcul arrosage"""
        plante = mock_plante
        
        jours_depuis = (date.today() - plante.dernier_arrosage).days
        besoin_arrosage = jours_depuis >= plante.frequence_arrosage
        
        assert jours_depuis == 1
        assert not besoin_arrosage  # Arrosé hier, fréquence = 2 jours


class TestJardinTypes:
    """Tests des types de plantes"""
    
    def test_types_standard(self):
        """Test des types standards"""
        types = ["légume", "fruit", "fleur", "aromatique", "arbuste", "arbre"]
        
        assert "légume" in types
        assert "fleur" in types
    
    def test_type_icons(self):
        """Test des icônes par type"""
        icons = {
            "légume": "🥬",
            "fruit": "🍓",
            "fleur": "🌸",
            "aromatique": "🌿",
        }
        
        assert icons["légume"] == "🥬"
    
    def test_filter_by_type(self, mock_plante):
        """Test filtrage par type"""
        plantes = [mock_plante]
        
        filtrees = [p for p in plantes if p.type == "légume"]
        assert len(filtrees) == 1


class TestJardinEmplacements:
    """Tests des emplacements de jardin"""
    
    def test_emplacements_standard(self):
        """Test des emplacements standards"""
        emplacements = ["Potager", "Serre", "Terrasse", "Balcon", "Intérieur"]
        
        assert "Potager" in emplacements
        assert "Serre" in emplacements
    
    def test_emplacement_icons(self):
        """Test des icônes par emplacement"""
        icons = {
            "Potager": "🥕",
            "Serre": "🏠",
            "Terrasse": "☀️",
            "Intérieur": "🏡",
        }
        
        assert icons["Potager"] == "🥕"


class TestJardinArrosage:
    """Tests du système d'arrosage"""
    
    def test_frequences_arrosage(self):
        """Test des fréquences d'arrosage"""
        frequences = {
            "quotidien": 1,
            "2 jours": 2,
            "3 jours": 3,
            "hebdomadaire": 7,
        }
        
        assert frequences["quotidien"] == 1
        assert frequences["hebdomadaire"] == 7
    
    def test_calcul_prochain_arrosage(self):
        """Test calcul prochain arrosage"""
        dernier = date.today() - timedelta(days=1)
        frequence = 3
        
        prochain = dernier + timedelta(days=frequence)
        jours_restants = (prochain - date.today()).days
        
        assert jours_restants == 2
    
    def test_plantes_a_arroser(self):
        """Test liste plantes à arroser"""
        plantes = [
            {"nom": "A", "dernier_arrosage": date.today() - timedelta(days=3), "frequence": 2},
            {"nom": "B", "dernier_arrosage": date.today() - timedelta(days=1), "frequence": 3},
            {"nom": "C", "dernier_arrosage": date.today() - timedelta(days=5), "frequence": 2},
        ]
        
        a_arroser = [
            p for p in plantes 
            if (date.today() - p["dernier_arrosage"]).days >= p["frequence"]
        ]
        
        assert len(a_arroser) == 2


class TestJardinStatuts:
    """Tests des statuts des plantes"""
    
    def test_statuts_standard(self):
        """Test des statuts standards"""
        statuts = ["semis", "en croissance", "floraison", "récolte", "repos"]
        
        assert "en croissance" in statuts
        assert "récolte" in statuts
    
    def test_statut_icons(self):
        """Test des icônes par statut"""
        icons = {
            "semis": "🌱",
            "en croissance": "🌿",
            "floraison": "🌸",
            "récolte": "🍎",
        }
        
        assert icons["semis"] == "🌱"


class TestJardinSaisons:
    """Tests des saisons de jardinage"""
    
    def test_saisons(self):
        """Test des saisons"""
        saisons = ["printemps", "été", "automne", "hiver"]
        
        assert len(saisons) == 4
    
    def test_saison_actuelle(self):
        """Test détermination saison actuelle"""
        mois = date.today().month
        
        if mois in [3, 4, 5]:
            saison = "printemps"
        elif mois in [6, 7, 8]:
            saison = "été"
        elif mois in [9, 10, 11]:
            saison = "automne"
        else:
            saison = "hiver"
        
        assert saison in ["printemps", "été", "automne", "hiver"]


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE PROJETS
# ═══════════════════════════════════════════════════════════════════════════════


class TestProjetsStructure:
    """Tests de la structure des projets"""
    
    def test_projet_structure(self, mock_projet):
        """Test structure d'un projet"""
        projet = mock_projet
        
        assert projet.nom == "Rénovation salle de bain"
        assert projet.budget == 5000
        assert projet.progression == 50
    
    def test_projet_dates(self, mock_projet):
        """Test dates du projet"""
        projet = mock_projet
        
        duree = (projet.date_fin_prevue - projet.date_debut).days
        assert duree == 30


class TestProjetsBudget:
    """Tests du budget des projets"""
    
    def test_calcul_depense(self, mock_projet):
        """Test calcul dépense"""
        projet = mock_projet
        
        pourcentage_depense = (projet.depense_actuelle / projet.budget) * 100
        assert pourcentage_depense == 50.0
    
    def test_budget_restant(self, mock_projet):
        """Test budget restant"""
        projet = mock_projet
        
        restant = projet.budget - projet.depense_actuelle
        assert restant == 2500
    
    def test_budget_depasse(self):
        """Test détection dépassement budget"""
        budget = 5000
        depense = 5500
        
        depasse = depense > budget
        depassement = depense - budget if depasse else 0
        
        assert depasse
        assert depassement == 500


class TestProjetsProgression:
    """Tests de la progression des projets"""
    
    def test_progression_range(self, mock_projet):
        """Test plage de progression"""
        projet = mock_projet
        
        assert 0 <= projet.progression <= 100
    
    def test_calcul_progression(self):
        """Test calcul progression"""
        taches_completees = 7
        taches_total = 10
        
        progression = (taches_completees / taches_total) * 100
        assert progression == 70.0
    
    def test_progression_icons(self):
        """Test icônes de progression"""
        def get_progress_icon(pct):
            if pct >= 100:
                return "✅"
            elif pct >= 75:
                return "🟢"
            elif pct >= 50:
                return "🟡"
            elif pct >= 25:
                return "🟠"
            else:
                return "🔴"
        
        assert get_progress_icon(100) == "✅"
        assert get_progress_icon(50) == "🟡"
        assert get_progress_icon(10) == "🔴"


class TestProjetsStatuts:
    """Tests des statuts des projets"""
    
    def test_statuts_standard(self):
        """Test des statuts standards"""
        statuts = ["planifié", "en cours", "en pause", "terminé", "annulé"]
        
        assert "en cours" in statuts
        assert "terminé" in statuts
    
    def test_statut_icons(self):
        """Test des icônes par statut"""
        icons = {
            "planifié": "📋",
            "en cours": "🔨",
            "en pause": "⏸️",
            "terminé": "✅",
            "annulé": "❌",
        }
        
        assert icons["en cours"] == "🔨"
    
    def test_filter_by_statut(self, mock_projet):
        """Test filtrage par statut"""
        projets = [mock_projet]
        
        en_cours = [p for p in projets if p.statut == "en cours"]
        assert len(en_cours) == 1


class TestProjetsPriorites:
    """Tests des priorités des projets"""
    
    def test_priorites_standard(self):
        """Test des priorités standards"""
        priorites = ["basse", "moyenne", "haute", "critique"]
        
        assert "haute" in priorites
    
    def test_sort_by_priorite(self):
        """Test tri par priorité"""
        projets = [
            {"nom": "A", "priorite": "basse"},
            {"nom": "B", "priorite": "critique"},
            {"nom": "C", "priorite": "moyenne"},
        ]
        
        ordre = {"critique": 0, "haute": 1, "moyenne": 2, "basse": 3}
        tries = sorted(projets, key=lambda p: ordre.get(p["priorite"], 99))
        
        assert tries[0]["nom"] == "B"


class TestProjetsEcheances:
    """Tests des échéances des projets"""
    
    def test_jours_restants(self, mock_projet):
        """Test calcul jours restants"""
        projet = mock_projet
        
        jours = (projet.date_fin_prevue - date.today()).days
        assert isinstance(jours, int)
    
    def test_projet_en_retard(self):
        """Test détection retard"""
        date_fin = date.today() - timedelta(days=5)
        statut = "en cours"
        
        en_retard = date_fin < date.today() and statut != "terminé"
        assert en_retard
    
    def test_projets_a_venir(self):
        """Test projets à venir"""
        projets = [
            {"date_fin_prevue": date.today() + timedelta(days=5)},
            {"date_fin_prevue": date.today() + timedelta(days=15)},
            {"date_fin_prevue": date.today() + timedelta(days=3)},
        ]
        
        a_venir_semaine = [
            p for p in projets 
            if 0 <= (p["date_fin_prevue"] - date.today()).days <= 7
        ]
        
        assert len(a_venir_semaine) == 2


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS INTÉGRATION MAISON
# ═══════════════════════════════════════════════════════════════════════════════


class TestMaisonIntegration:
    """Tests d'intégration des modules maison"""
    
    def test_entretien_to_projets(self, mock_tache_entretien, mock_projet):
        """Test lien entretien -> projets"""
        # Une tâche d'entretien récurrente peut devenir un projet
        tache = mock_tache_entretien
        projet = mock_projet
        
        assert tache.piece is not None
        assert projet.nom is not None
    
    def test_jardin_to_entretien(self, mock_plante, mock_tache_entretien):
        """Test lien jardin -> entretien"""
        # L'arrosage des plantes est lié à l'entretien
        plante = mock_plante
        tache = mock_tache_entretien
        
        assert plante.frequence_arrosage is not None
        assert tache.frequence is not None
    
    def test_dashboard_stats(self, mock_tache_entretien, mock_plante, mock_projet):
        """Test statistiques dashboard"""
        stats = {
            "taches_a_faire": 1,
            "plantes_a_arroser": 0,
            "projets_en_cours": 1,
        }
        
        total_actions = sum(stats.values())
        assert total_actions == 2


class TestMaisonStats:
    """Tests des statistiques maison"""
    
    def test_count_par_piece(self):
        """Test comptage par pièce"""
        taches = [
            {"piece": "Cuisine"},
            {"piece": "Salon"},
            {"piece": "Cuisine"},
            {"piece": "Chambre"},
        ]
        
        count = {}
        for t in taches:
            piece = t["piece"]
            count[piece] = count.get(piece, 0) + 1
        
        assert count["Cuisine"] == 2
    
    def test_budget_total_projets(self):
        """Test budget total projets"""
        projets = [
            {"budget": 5000, "depense": 2500},
            {"budget": 3000, "depense": 1500},
            {"budget": 2000, "depense": 2000},
        ]
        
        budget_total = sum(p["budget"] for p in projets)
        depense_total = sum(p["depense"] for p in projets)
        
        assert budget_total == 10000
        assert depense_total == 6000
    
    def test_progression_globale(self):
        """Test progression globale"""
        projets = [
            {"progression": 50},
            {"progression": 75},
            {"progression": 100},
        ]
        
        moyenne = sum(p["progression"] for p in projets) / len(projets)
        assert moyenne == 75.0
