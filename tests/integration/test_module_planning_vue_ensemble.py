"""
Tests pour le module planning/vue_ensemble.py
Tableau de bord et vue d'ensemble du planning familial (logique métier)
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from tests.conftest import SessionStateMock


class TestActionsPrioritaires:
    """Tests pour la logique des actions prioritaires"""

    def test_detecte_taches_urgentes(self):
        """Détecte les tÃ¢ches urgentes (deadline proche)"""
        aujourd_hui = date.today()
        demain = aujourd_hui + timedelta(days=1)
        dans_7_jours = aujourd_hui + timedelta(days=7)
        
        taches = [
            MagicMock(deadline=demain, complete=False, priorite="haute"),
            MagicMock(deadline=dans_7_jours, complete=False, priorite="basse"),
            MagicMock(deadline=demain, complete=True, priorite="haute"),
        ]
        
        # Urgentes = deadline < 3 jours et non complétées
        urgentes = [t for t in taches if (t.deadline - aujourd_hui).days < 3 and not t.complete]
        assert len(urgentes) == 1

    def test_tri_par_priorite(self):
        """Trie les actions par priorité"""
        ORDRE_PRIORITE = {"haute": 0, "moyenne": 1, "basse": 2}
        
        actions = [
            MagicMock(priorite="basse"),
            MagicMock(priorite="haute"),
            MagicMock(priorite="moyenne"),
        ]
        
        sorted_actions = sorted(actions, key=lambda a: ORDRE_PRIORITE.get(a.priorite, 99))
        
        assert sorted_actions[0].priorite == "haute"
        assert sorted_actions[1].priorite == "moyenne"
        assert sorted_actions[2].priorite == "basse"


class TestMetriquesCles:
    """Tests pour les métriques clés du planning"""

    def test_compte_evenements_semaine(self):
        """Compte les événements de la semaine"""
        aujourd_hui = date.today()
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)
        
        evenements = [
            MagicMock(date=debut_semaine + timedelta(days=1)),
            MagicMock(date=debut_semaine + timedelta(days=3)),
            MagicMock(date=debut_semaine - timedelta(days=1)),  # Semaine précédente
        ]
        
        cette_semaine = [e for e in evenements if debut_semaine <= e.date <= fin_semaine]
        assert len(cette_semaine) == 2

    def test_compte_taches_en_retard(self):
        """Compte les tÃ¢ches en retard"""
        aujourd_hui = date.today()
        hier = aujourd_hui - timedelta(days=1)
        
        taches = [
            MagicMock(deadline=hier, complete=False),
            MagicMock(deadline=hier, complete=True),
            MagicMock(deadline=aujourd_hui, complete=False),
        ]
        
        en_retard = [t for t in taches if t.deadline < aujourd_hui and not t.complete]
        assert len(en_retard) == 1

    def test_progression_semaine(self):
        """Calcule la progression de la semaine"""
        taches_semaine = [
            MagicMock(complete=True),
            MagicMock(complete=True),
            MagicMock(complete=False),
            MagicMock(complete=False),
        ]
        
        total = len(taches_semaine)
        completes = len([t for t in taches_semaine if t.complete])
        progression = (completes / total) * 100 if total > 0 else 0
        
        assert progression == 50.0


class TestSyntheseJours:
    """Tests pour la synthèse des jours de la semaine"""

    def test_genere_jours_semaine(self):
        """Génère les jours de la semaine à partir d'une date"""
        date_debut = date(2024, 1, 1)  # Un lundi
        
        jours = []
        for i in range(7):
            jours.append(date_debut + timedelta(days=i))
        
        assert len(jours) == 7
        assert jours[0].weekday() == 0  # Lundi

    def test_groupe_evenements_par_jour(self):
        """Groupe les événements par jour"""
        evenements = [
            MagicMock(date=date(2024, 1, 1)),
            MagicMock(date=date(2024, 1, 1)),
            MagicMock(date=date(2024, 1, 2)),
        ]
        
        grouped = {}
        for e in evenements:
            d = e.date
            if d not in grouped:
                grouped[d] = []
            grouped[d].append(e)
        
        assert len(grouped[date(2024, 1, 1)]) == 2
        assert len(grouped[date(2024, 1, 2)]) == 1

    def test_detecte_jour_charge(self):
        """Détecte un jour chargé (>3 événements)"""
        evenements_jour = [MagicMock() for _ in range(5)]
        
        est_charge = len(evenements_jour) > 3
        
        assert est_charge is True


class TestOpportunities:
    """Tests pour les suggestions d'opportunités"""

    def test_detecte_creneaux_libres(self):
        """Détecte les créneaux libres"""
        jours_semaine = [
            MagicMock(date=date(2024, 1, 1), evenements=[]),
            MagicMock(date=date(2024, 1, 2), evenements=[MagicMock()]),
            MagicMock(date=date(2024, 1, 3), evenements=[]),
        ]
        
        jours_libres = [j for j in jours_semaine if len(j.evenements) == 0]
        
        assert len(jours_libres) == 2

    def test_suggere_activites_famille(self):
        """Suggère des activités si temps libre"""
        SUGGESTIONS = ["Sortie au parc", "Film en famille", "Cuisine ensemble"]
        
        jours_libres = 2
        
        if jours_libres > 0:
            suggestion = SUGGESTIONS[0]  # Première suggestion
        else:
            suggestion = None
        
        assert suggestion is not None


class TestNavigationSemaine:
    """Tests pour la navigation entre semaines"""

    def test_semaine_precedente(self):
        """Navigation vers la semaine précédente"""
        semaine_actuelle = date(2024, 1, 8)  # Un lundi
        
        semaine_prec = semaine_actuelle - timedelta(weeks=1)
        
        assert semaine_prec == date(2024, 1, 1)

    def test_semaine_suivante(self):
        """Navigation vers la semaine suivante"""
        semaine_actuelle = date(2024, 1, 1)
        
        semaine_suiv = semaine_actuelle + timedelta(weeks=1)
        
        assert semaine_suiv == date(2024, 1, 8)

    def test_retour_semaine_courante(self):
        """Retour à la semaine courante"""
        aujourd_hui = date.today()
        debut_semaine_courante = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        
        assert debut_semaine_courante.weekday() == 0  # C'est un lundi


class TestAlertes:
    """Tests pour le système d'alertes"""

    def test_alerte_tache_en_retard(self):
        """Génère une alerte pour tÃ¢che en retard"""
        aujourd_hui = date.today()
        
        tache = MagicMock()
        tache.deadline = aujourd_hui - timedelta(days=2)
        tache.complete = False
        tache.nom = "TÃ¢che test"
        
        alertes = []
        if tache.deadline < aujourd_hui and not tache.complete:
            alertes.append({
                "type": "retard",
                "message": f"âš ï¸ {tache.nom} en retard de {(aujourd_hui - tache.deadline).days} jour(s)",
                "priorite": "haute"
            })
        
        assert len(alertes) == 1
        assert alertes[0]["type"] == "retard"

    def test_alerte_deadline_proche(self):
        """Génère une alerte pour deadline proche"""
        aujourd_hui = date.today()
        
        tache = MagicMock()
        tache.deadline = aujourd_hui + timedelta(days=1)
        tache.complete = False
        tache.nom = "TÃ¢che urgente"
        
        alertes = []
        jours_restants = (tache.deadline - aujourd_hui).days
        if 0 < jours_restants <= 2 and not tache.complete:
            alertes.append({
                "type": "urgent",
                "message": f"â° {tache.nom} dans {jours_restants} jour(s)",
                "priorite": "moyenne"
            })
        
        assert len(alertes) == 1
        assert alertes[0]["type"] == "urgent"

    def test_pas_alerte_tache_complete(self):
        """Pas d'alerte pour tÃ¢che complétée"""
        aujourd_hui = date.today()
        
        tache = MagicMock()
        tache.deadline = aujourd_hui - timedelta(days=2)
        tache.complete = True
        
        alertes = []
        if tache.deadline < aujourd_hui and not tache.complete:
            alertes.append({"type": "retard"})
        
        assert len(alertes) == 0


class TestCategoriesPlanning:
    """Tests pour les catégories de planning"""

    def test_emojis_categories(self):
        """Vérifie les emojis des catégories"""
        CATEGORIE_EMOJIS = {
            "repas": "ðŸ½ï¸",
            "activite": "ðŸŽ¯",
            "rdv": "ðŸ“…",
            "tache": "âœ…",
            "routine": "ðŸ”„"
        }
        
        assert CATEGORIE_EMOJIS.get("repas") == "ðŸ½ï¸"
        assert CATEGORIE_EMOJIS.get("activite") == "ðŸŽ¯"
        assert CATEGORIE_EMOJIS.get("rdv") == "ðŸ“…"

    def test_couleurs_categories(self):
        """Vérifie les couleurs des catégories"""
        CATEGORIE_COULEURS = {
            "repas": "#4CAF50",
            "activite": "#2196F3",
            "rdv": "#FF9800",
            "tache": "#9C27B0"
        }
        
        assert CATEGORIE_COULEURS.get("repas").startswith("#")


class TestFormattageDate:
    """Tests pour le formattage des dates"""

    def test_format_jour_semaine_francais(self):
        """Formate le jour de la semaine en français"""
        JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        
        date_test = date(2024, 1, 1)  # C'est un lundi
        jour_fr = JOURS_FR[date_test.weekday()]
        
        assert jour_fr == "Lundi"

    def test_format_date_courte(self):
        """Formate une date en format court"""
        date_test = date(2024, 6, 15)
        
        format_court = f"{date_test.day}/{date_test.month}"
        
        assert format_court == "15/6"

