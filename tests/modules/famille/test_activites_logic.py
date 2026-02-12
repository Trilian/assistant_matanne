"""
Tests pour activites_logic.py et routines_logic.py - Module Famille
Couverture cible: 80%+
"""
import pytest
from datetime import date, time, timedelta

from src.domains.famille.logic.activites_logic import (
    # Constantes
    TYPES_ACTIVITE,
    LIEUX,
    CATEGORIES_AGE,
    # Filtrage
    filtrer_par_type,
    filtrer_par_lieu,
    filtrer_par_date,
    get_activites_a_venir,
    get_activites_passees,
    # Statistiques
    calculer_statistiques_activites,
    calculer_frequence_hebdomadaire,
    detecter_desequilibre_types,
    # Recommandations
    suggerer_activites_age,
    # Validation
    valider_activite,
    # Formatage
    formater_activite_resume,
    grouper_par_mois,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def activites_sample():
    """Liste d'activités de test."""
    today = date.today()
    return [
        {
            "id": 1,
            "type": "Sport",
            "lieu": "Parc",
            "date": today + timedelta(days=1),
            "titre": "Football",
            "cout": 0.0,
            "duree": 60,
        },
        {
            "id": 2,
            "type": "Culture",
            "lieu": "Bibliothèque",
            "date": today + timedelta(days=3),
            "titre": "Lecture",
            "cout": 0.0,
            "duree": 45,
        },
        {
            "id": 3,
            "type": "Sport",
            "lieu": "Piscine",
            "date": today - timedelta(days=2),
            "titre": "Natation",
            "cout": 5.0,
            "duree": 90,
        },
        {
            "id": 4,
            "type": "Sortie",
            "lieu": "Centre culturel",
            "date": today + timedelta(days=10),
            "titre": "Spectacle",
            "cout": 15.0,
            "duree": 120,
        },
    ]


@pytest.fixture
def activites_vides():
    """Liste vide."""
    return []


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantesActivites:
    """Tests des constantes."""

    def test_types_activite_non_vide(self):
        """Types d'activité définis."""
        assert len(TYPES_ACTIVITE) > 0
        assert "Sport" in TYPES_ACTIVITE
        assert "Culture" in TYPES_ACTIVITE

    def test_lieux_non_vide(self):
        """Lieux définis."""
        assert len(LIEUX) > 0
        assert "Maison" in LIEUX
        assert "Parc" in LIEUX

    def test_categories_age_non_vide(self):
        """Catégories d'âge définies."""
        assert len(CATEGORIES_AGE) > 0
        assert "1-2 ans" in CATEGORIES_AGE


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE
# ═══════════════════════════════════════════════════════════


class TestFiltrageActivites:
    """Tests des fonctions de filtrage."""

    def test_filtrer_par_type(self, activites_sample):
        """Filtre par type d'activité."""
        result = filtrer_par_type(activites_sample, "Sport")
        assert len(result) == 2
        assert all(a["type"] == "Sport" for a in result)

    def test_filtrer_par_type_inexistant(self, activites_sample):
        """Type inexistant retourne liste vide."""
        result = filtrer_par_type(activites_sample, "Inexistant")
        assert len(result) == 0

    def test_filtrer_par_lieu(self, activites_sample):
        """Filtre par lieu."""
        result = filtrer_par_lieu(activites_sample, "Parc")
        assert len(result) == 1
        assert result[0]["lieu"] == "Parc"

    def test_filtrer_par_date(self, activites_sample):
        """Filtre par période."""
        today = date.today()
        result = filtrer_par_date(
            activites_sample,
            today,
            today + timedelta(days=5)
        )
        # Devrait inclure les activités des 5 prochains jours
        assert len(result) >= 2

    def test_filtrer_par_date_string(self):
        """Filtre avec dates en string."""
        today = date.today()
        activites = [
            {"date": (today + timedelta(days=1)).isoformat()},
        ]
        result = filtrer_par_date(activites, today, today + timedelta(days=2))
        assert len(result) == 1

    def test_get_activites_a_venir(self, activites_sample):
        """Activités des 7 prochains jours."""
        result = get_activites_a_venir(activites_sample, jours=7)
        # Vérifie que toutes les activités sont dans le futur
        today = date.today()
        for act in result:
            act_date = act["date"]
            if isinstance(act_date, str):
                from datetime import datetime
                act_date = datetime.fromisoformat(act_date).date()
            assert act_date >= today

    def test_get_activites_passees(self, activites_sample):
        """Activités des 30 derniers jours."""
        result = get_activites_passees(activites_sample, jours=30)
        # Devrait inclure la natation (passée)
        assert len(result) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestStatistiquesActivites:
    """Tests des fonctions de statistiques."""

    def test_calculer_statistiques_activites(self, activites_sample):
        """Statistiques complètes."""
        result = calculer_statistiques_activites(activites_sample)
        
        assert result["total"] == 4
        assert "par_type" in result
        assert "par_lieu" in result
        assert result["par_type"]["Sport"] == 2
        assert result["cout_total"] == 20.0  # 0 + 0 + 5 + 15

    def test_calculer_statistiques_cout_moyen(self, activites_sample):
        """Coût moyen calculé."""
        result = calculer_statistiques_activites(activites_sample)
        assert result["cout_moyen"] == 5.0  # 20 / 4

    def test_calculer_statistiques_duree_moyenne(self, activites_sample):
        """Durée moyenne calculée."""
        result = calculer_statistiques_activites(activites_sample)
        # (60 + 45 + 90 + 120) / 4 = 78.75
        assert result["duree_moyenne"] == 78.75

    def test_calculer_statistiques_liste_vide(self, activites_vides):
        """Statistiques liste vide."""
        result = calculer_statistiques_activites(activites_vides)
        assert result["total"] == 0
        assert result["cout_total"] == 0.0
        assert result["duree_moyenne"] == 0.0

    def test_calculer_frequence_hebdomadaire(self, activites_sample):
        """Fréquence hebdomadaire."""
        result = calculer_frequence_hebdomadaire(activites_sample, semaines=2)
        assert result == 2.0  # 4 activités / 2 semaines

    def test_calculer_frequence_zero_semaines(self, activites_sample):
        """Fréquence avec 0 semaines = 0."""
        result = calculer_frequence_hebdomadaire(activites_sample, semaines=0)
        assert result == 0.0

    def test_calculer_frequence_liste_vide(self, activites_vides):
        """Fréquence liste vide = 0."""
        result = calculer_frequence_hebdomadaire(activites_vides, semaines=4)
        assert result == 0.0


# ═══════════════════════════════════════════════════════════
# TESTS RECOMMANDATIONS
# ═══════════════════════════════════════════════════════════


class TestRecommandationsActivites:
    """Tests des suggestions d'activités."""

    def test_suggerer_activites_bebe(self):
        """Suggestions pour bébé < 12 mois."""
        suggestions = suggerer_activites_age(8)
        assert len(suggestions) > 0
        # Vérifier que c'est adapté aux bébés
        titres = [s["titre"] for s in suggestions]
        assert "Jeux d'éveil" in titres

    def test_suggerer_activites_1_2_ans(self):
        """Suggestions pour enfant 12-24 mois."""
        suggestions = suggerer_activites_age(18)
        assert len(suggestions) > 0
        titres = [s["titre"] for s in suggestions]
        assert "Jeux de manipulation" in titres

    def test_suggerer_activites_2_3_ans(self):
        """Suggestions pour enfant 24-36 mois."""
        suggestions = suggerer_activites_age(30)
        assert len(suggestions) > 0
        titres = [s["titre"] for s in suggestions]
        assert "Jeux symboliques" in titres

    def test_suggerer_activites_plus_3_ans(self):
        """Suggestions pour enfant > 36 mois."""
        suggestions = suggerer_activites_age(48)
        assert len(suggestions) > 0
        titres = [s["titre"] for s in suggestions]
        assert "Activités créatives" in titres

    def test_suggerer_activites_structure(self):
        """Structure des suggestions."""
        suggestions = suggerer_activites_age(19)
        for s in suggestions:
            assert "type" in s
            assert "titre" in s
            assert "description" in s

class TestDesequilibres:
    """Tests pour la détection des déséquilibres."""

    def test_equilibre_activites_variees(self):
        """Activités bien équilibrées."""
        activites = [
            {"type": "Sport", "duree": 60, "cout": 0},
            {"type": "Sport", "duree": 60, "cout": 0},
            {"type": "Culture", "duree": 60, "cout": 0},
            {"type": "Culture", "duree": 60, "cout": 0},
            {"type": "Sortie", "duree": 60, "cout": 0},
            {"type": "Sortie", "duree": 60, "cout": 0},
        ]
        result = detecter_desequilibre_types(activites)
        # Chaque type = 33%, donc équilibré
        assert result["equilibre"] is True
        assert len(result["recommandations"]) == 0

    def test_desequilibre_manque_sport(self):
        """Détecte le manque de sport."""
        activites = [
            {"type": "Culture", "duree": 60, "cout": 0},
            {"type": "Culture", "duree": 60, "cout": 0},
            {"type": "Culture", "duree": 60, "cout": 0},
            {"type": "Culture", "duree": 60, "cout": 0},
            {"type": "Culture", "duree": 60, "cout": 0},
            {"type": "Culture", "duree": 60, "cout": 0},
            {"type": "Culture", "duree": 60, "cout": 0},
        ]
        result = detecter_desequilibre_types(activites)
        assert result["equilibre"] is False
        assert any("Sport" in r for r in result["recommandations"])

    def test_desequilibre_liste_vide(self):
        """Liste vide = équilibré (pas de données)."""
        result = detecter_desequilibre_types([])
        assert result["equilibre"] is True


class TestValidation:
    """Tests pour la validation des activités."""

    def test_activite_valide(self):
        """Activité complète et valide."""
        data = {
            "titre": "Football",
            "type": "Sport",
            "date": date.today(),
            "duree": 60,
            "cout": 0
        }
        valide, erreurs = valider_activite(data)
        assert valide is True
        assert len(erreurs) == 0

    def test_activite_titre_manquant(self):
        """Titre obligatoire."""
        data = {"type": "Sport", "date": date.today()}
        valide, erreurs = valider_activite(data)
        assert valide is False
        assert any("titre" in e.lower() for e in erreurs)

    def test_activite_date_manquante(self):
        """Date obligatoire."""
        data = {"titre": "Test", "type": "Sport"}
        valide, erreurs = valider_activite(data)
        assert valide is False
        assert any("date" in e.lower() for e in erreurs)

    def test_activite_type_invalide(self):
        """Type invalide détecté."""
        data = {
            "titre": "Test",
            "type": "TypeInexistant",
            "date": date.today()
        }
        valide, erreurs = valider_activite(data)
        assert valide is False
        assert any("type" in e.lower() for e in erreurs)

    def test_activite_duree_negative(self):
        """Durée négative invalide."""
        data = {
            "titre": "Test",
            "date": date.today(),
            "duree": -30
        }
        valide, erreurs = valider_activite(data)
        assert valide is False
        assert any("durée" in e.lower() for e in erreurs)

    def test_activite_cout_negatif(self):
        """Coût négatif invalide."""
        data = {
            "titre": "Test",
            "date": date.today(),
            "cout": -10
        }
        valide, erreurs = valider_activite(data)
        assert valide is False
        assert any("coût" in e.lower() for e in erreurs)


class TestFormatage:
    """Tests pour les fonctions de formatage."""

    def test_formater_resume_complet(self):
        """Résumé avec tous les champs."""
        activite = {
            "titre": "Football",
            "type": "Sport",
            "lieu": "Parc"
        }
        resume = formater_activite_resume(activite)
        assert "Football" in resume
        assert "Sport" in resume
        assert "Parc" in resume

    def test_formater_resume_minimal(self):
        """Résumé avec titre seul."""
        activite = {"titre": "Test"}
        resume = formater_activite_resume(activite)
        assert "Test" in resume

    def test_formater_resume_sans_titre(self):
        """Résumé par défaut si pas de titre."""
        activite = {}
        resume = formater_activite_resume(activite)
        assert "Activité" in resume


class TestGroupement:
    """Tests pour le groupement par mois."""

    def test_grouper_par_mois_basic(self):
        """Groupe correctement par mois."""
        activites = [
            {"titre": "A", "date": date(2025, 1, 15)},
            {"titre": "B", "date": date(2025, 1, 20)},
            {"titre": "C", "date": date(2025, 2, 10)},
        ]
        groupes = grouper_par_mois(activites)
        assert "2025-01" in groupes
        assert "2025-02" in groupes
        assert len(groupes["2025-01"]) == 2
        assert len(groupes["2025-02"]) == 1

    def test_grouper_par_mois_date_string(self):
        """Supporte les dates en format string."""
        activites = [
            {"titre": "A", "date": "2025-03-15"},
        ]
        groupes = grouper_par_mois(activites)
        assert "2025-03" in groupes

    def test_grouper_par_mois_vide(self):
        """Liste vide = dict vide."""
        groupes = grouper_par_mois([])
        assert len(groupes) == 0