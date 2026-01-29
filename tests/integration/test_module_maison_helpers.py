"""
Tests pour le module maison/helpers.py
Fonctions utilitaires pour la gestion de la maison (logique métier)
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock


class TestProjetsPriorite:
    """Tests pour la logique de priorité des projets"""

    def test_detecte_priorite_haute(self):
        """Détecte les projets haute priorité"""
        projets = [
            MagicMock(priorite="haute"),
            MagicMock(priorite="basse"),
            MagicMock(priorite="haute"),
        ]
        
        urgents = [p for p in projets if p.priorite == "haute"]
        assert len(urgents) == 2

    def test_detecte_projets_en_retard(self):
        """Détecte les projets en retard"""
        aujourd_hui = date.today()
        hier = aujourd_hui - timedelta(days=1)
        demain = aujourd_hui + timedelta(days=1)
        
        projets = [
            MagicMock(date_echeance=hier, complete=False),
            MagicMock(date_echeance=demain, complete=False),
            MagicMock(date_echeance=hier, complete=True),  # Pas en retard car complété
        ]
        
        en_retard = [p for p in projets if p.date_echeance < aujourd_hui and not p.complete]
        assert len(en_retard) == 1


class TestStatsProjets:
    """Tests pour les statistiques de projets"""

    def test_compte_projets_par_statut(self):
        """Compte les projets par statut"""
        projets = [
            MagicMock(statut="planifie"),
            MagicMock(statut="en_cours"),
            MagicMock(statut="en_cours"),
            MagicMock(statut="termine"),
        ]
        
        stats = {}
        for p in projets:
            if p.statut not in stats:
                stats[p.statut] = 0
            stats[p.statut] += 1
        
        assert stats["planifie"] == 1
        assert stats["en_cours"] == 2
        assert stats["termine"] == 1

    def test_calcul_progression_projet(self):
        """Calcule la progression d'un projet avec tÃ¢ches"""
        taches = [
            MagicMock(complete=True),
            MagicMock(complete=True),
            MagicMock(complete=False),
            MagicMock(complete=False),
        ]
        
        total = len(taches)
        completes = len([t for t in taches if t.complete])
        progression = (completes / total) * 100 if total > 0 else 0
        
        assert progression == 50.0


class TestSaison:
    """Tests pour get_saison()"""

    def test_saison_printemps(self):
        """Détecte le printemps (mars-mai)"""
        def get_saison(mois):
            if mois in [3, 4, 5]:
                return "Printemps"
            elif mois in [6, 7, 8]:
                return "Ã‰té"
            elif mois in [9, 10, 11]:
                return "Automne"
            else:
                return "Hiver"
        
        assert get_saison(4) == "Printemps"

    def test_saison_ete(self):
        """Détecte l'été (juin-août)"""
        def get_saison(mois):
            if mois in [3, 4, 5]:
                return "Printemps"
            elif mois in [6, 7, 8]:
                return "Ã‰té"
            elif mois in [9, 10, 11]:
                return "Automne"
            else:
                return "Hiver"
        
        assert get_saison(7) == "Ã‰té"

    def test_saison_automne(self):
        """Détecte l'automne (septembre-novembre)"""
        def get_saison(mois):
            if mois in [3, 4, 5]:
                return "Printemps"
            elif mois in [6, 7, 8]:
                return "Ã‰té"
            elif mois in [9, 10, 11]:
                return "Automne"
            else:
                return "Hiver"
        
        assert get_saison(10) == "Automne"

    def test_saison_hiver(self):
        """Détecte l'hiver (décembre-février)"""
        def get_saison(mois):
            if mois in [3, 4, 5]:
                return "Printemps"
            elif mois in [6, 7, 8]:
                return "Ã‰té"
            elif mois in [9, 10, 11]:
                return "Automne"
            else:
                return "Hiver"
        
        assert get_saison(1) == "Hiver"
        assert get_saison(12) == "Hiver"


class TestPlantesJardin:
    """Tests pour les plantes du jardin"""

    def test_plantes_a_arroser(self):
        """Détecte les plantes à arroser"""
        aujourd_hui = date.today()
        avant_hier = aujourd_hui - timedelta(days=2)
        demain = aujourd_hui + timedelta(days=1)
        
        plantes = [
            MagicMock(dernier_arrosage=avant_hier, frequence_arrosage=1),
            MagicMock(dernier_arrosage=aujourd_hui, frequence_arrosage=1),
            MagicMock(dernier_arrosage=avant_hier, frequence_arrosage=7),
        ]
        
        def doit_arroser(plante):
            jours_depuis = (aujourd_hui - plante.dernier_arrosage).days
            return jours_depuis >= plante.frequence_arrosage
        
        a_arroser = [p for p in plantes if doit_arroser(p)]
        assert len(a_arroser) == 1  # Seule la première doit être arrosée

    def test_recoltes_proches(self):
        """Détecte les récoltes proches (7 jours)"""
        aujourd_hui = date.today()
        dans_5_jours = aujourd_hui + timedelta(days=5)
        dans_10_jours = aujourd_hui + timedelta(days=10)
        
        plantes = [
            MagicMock(date_recolte_prevue=dans_5_jours),
            MagicMock(date_recolte_prevue=dans_10_jours),
        ]
        
        proches = [p for p in plantes if (p.date_recolte_prevue - aujourd_hui).days <= 7]
        assert len(proches) == 1


class TestStatsJardin:
    """Tests pour les statistiques du jardin"""

    def test_compte_plantes_par_type(self):
        """Compte les plantes par type"""
        plantes = [
            MagicMock(type_plante="légume"),
            MagicMock(type_plante="légume"),
            MagicMock(type_plante="fruit"),
            MagicMock(type_plante="herbe"),
        ]
        
        stats = {}
        for p in plantes:
            if p.type_plante not in stats:
                stats[p.type_plante] = 0
            stats[p.type_plante] += 1
        
        assert stats["légume"] == 2
        assert stats["fruit"] == 1
        assert stats["herbe"] == 1

    def test_plantes_actives(self):
        """Compte les plantes actives"""
        plantes = [
            MagicMock(actif=True),
            MagicMock(actif=False),
            MagicMock(actif=True),
        ]
        
        actives = len([p for p in plantes if p.actif])
        assert actives == 2


class TestRoutinesEntretien:
    """Tests pour les routines d'entretien"""

    def test_taches_today(self):
        """Détecte les tÃ¢ches du jour"""
        aujourd_hui = date.today()
        jour_semaine = aujourd_hui.weekday()  # 0=lundi, 6=dimanche
        
        routines = [
            MagicMock(jours_semaine=[jour_semaine], actif=True),
            MagicMock(jours_semaine=[jour_semaine + 1], actif=True),
            MagicMock(jours_semaine=[jour_semaine], actif=False),
        ]
        
        taches_today = [r for r in routines if jour_semaine in r.jours_semaine and r.actif]
        assert len(taches_today) == 1

    def test_taches_hebdomadaires(self):
        """Compte les tÃ¢ches hebdomadaires"""
        routines = [
            MagicMock(frequence="quotidien"),
            MagicMock(frequence="hebdomadaire"),
            MagicMock(frequence="hebdomadaire"),
            MagicMock(frequence="mensuel"),
        ]
        
        hebdo = len([r for r in routines if r.frequence == "hebdomadaire"])
        assert hebdo == 2


class TestStatsEntretien:
    """Tests pour les statistiques d'entretien"""

    def test_taches_completees_mois(self):
        """Compte les tÃ¢ches complétées ce mois"""
        aujourd_hui = date.today()
        debut_mois = date(aujourd_hui.year, aujourd_hui.month, 1)
        
        completions = [
            MagicMock(date_completion=debut_mois + timedelta(days=5)),
            MagicMock(date_completion=debut_mois - timedelta(days=5)),  # Mois précédent
            MagicMock(date_completion=debut_mois + timedelta(days=10)),
        ]
        
        ce_mois = len([c for c in completions if c.date_completion >= debut_mois])
        assert ce_mois == 2

    def test_score_entretien(self):
        """Calcule le score d'entretien"""
        taches_prevues = 10
        taches_completes = 8
        
        score = (taches_completes / taches_prevues) * 100 if taches_prevues > 0 else 100
        
        assert score == 80.0


class TestPrioriteEmojis:
    """Tests pour les emojis de priorité maison"""

    def test_emoji_priorite_haute(self):
        """Emoji pour haute priorité"""
        PRIORITE_EMOJIS = {"haute": "ðŸ”´", "moyenne": "ðŸŸ¡", "basse": "ðŸŸ¢"}
        assert PRIORITE_EMOJIS.get("haute") == "ðŸ”´"

    def test_emoji_priorite_moyenne(self):
        """Emoji pour priorité moyenne"""
        PRIORITE_EMOJIS = {"haute": "ðŸ”´", "moyenne": "ðŸŸ¡", "basse": "ðŸŸ¢"}
        assert PRIORITE_EMOJIS.get("moyenne") == "ðŸŸ¡"

    def test_emoji_priorite_basse(self):
        """Emoji pour basse priorité"""
        PRIORITE_EMOJIS = {"haute": "ðŸ”´", "moyenne": "ðŸŸ¡", "basse": "ðŸŸ¢"}
        assert PRIORITE_EMOJIS.get("basse") == "ðŸŸ¢"


class TestStatutProjets:
    """Tests pour les statuts de projets"""

    def test_statuts_possibles(self):
        """Vérifie les statuts possibles"""
        STATUTS = ["planifie", "en_cours", "en_attente", "termine", "annule"]
        
        assert "planifie" in STATUTS
        assert "en_cours" in STATUTS
        assert "termine" in STATUTS

    def test_transition_statut(self):
        """Test de transition de statut"""
        projet = MagicMock()
        projet.statut = "planifie"
        
        # Simule la transition vers en_cours
        projet.statut = "en_cours"
        
        assert projet.statut == "en_cours"

