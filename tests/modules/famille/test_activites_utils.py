"""
Tests pour src/modules/famille/activites_utils.py

Tests complets des fonctions utilitaires d'activités familiales.
"""

from datetime import date, timedelta

import pytest

from src.modules.famille.activites_utils import (
    LIEUX,
    TYPES_ACTIVITE,
    calculer_frequence_hebdomadaire,
    calculer_statistiques_activites,
    detecter_desequilibre_types,
    filtrer_par_date,
    filtrer_par_lieu,
    filtrer_par_type,
    formater_activite_resume,
    grouper_par_mois,
    suggerer_activites_age,
    valider_activite,
)


class TestConstantes:
    """Tests pour les constantes du module."""

    def test_types_activite_non_vide(self):
        assert len(TYPES_ACTIVITE) > 0
        assert "Sport" in TYPES_ACTIVITE
        assert "Culture" in TYPES_ACTIVITE

    def test_lieux_non_vide(self):
        assert len(LIEUX) > 0
        assert "Maison" in LIEUX
        assert "Parc" in LIEUX


class TestFiltrerParType:
    """Tests pour filtrer_par_type."""

    @pytest.fixture
    def activites_exemple(self):
        return [
            {"titre": "Football", "type": "Sport"},
            {"titre": "Musée", "type": "Culture"},
            {"titre": "Natation", "type": "Sport"},
        ]

    def test_filtre_sport(self, activites_exemple):
        resultat = filtrer_par_type(activites_exemple, "Sport")
        assert len(resultat) == 2
        assert all(a["type"] == "Sport" for a in resultat)

    def test_filtre_aucun_resultat(self, activites_exemple):
        resultat = filtrer_par_type(activites_exemple, "Jeux")
        assert len(resultat) == 0

    def test_liste_vide(self):
        assert filtrer_par_type([], "Sport") == []


class TestFiltrerParLieu:
    """Tests pour filtrer_par_lieu."""

    @pytest.fixture
    def activites_exemple(self):
        return [
            {"titre": "Jeux", "lieu": "Maison"},
            {"titre": "Pique-nique", "lieu": "Parc"},
            {"titre": "Lecture", "lieu": "Maison"},
        ]

    def test_filtre_maison(self, activites_exemple):
        resultat = filtrer_par_lieu(activites_exemple, "Maison")
        assert len(resultat) == 2

    def test_filtre_parc(self, activites_exemple):
        resultat = filtrer_par_lieu(activites_exemple, "Parc")
        assert len(resultat) == 1

    def test_liste_vide(self):
        assert filtrer_par_lieu([], "Maison") == []


class TestFiltrerParDate:
    """Tests pour filtrer_par_date."""

    def test_filtre_dans_periode(self):
        activites = [
            {"titre": "A1", "date": date(2024, 6, 1)},
            {"titre": "A2", "date": date(2024, 6, 15)},
            {"titre": "A3", "date": date(2024, 7, 1)},
        ]
        resultat = filtrer_par_date(activites, date(2024, 6, 1), date(2024, 6, 30))
        assert len(resultat) == 2

    def test_filtre_bornes_incluses(self):
        activites = [
            {"titre": "Debut", "date": date(2024, 6, 1)},
            {"titre": "Fin", "date": date(2024, 6, 30)},
        ]
        resultat = filtrer_par_date(activites, date(2024, 6, 1), date(2024, 6, 30))
        assert len(resultat) == 2

    def test_string_iso_date(self):
        activites = [{"titre": "Test", "date": "2024-06-15"}]
        resultat = filtrer_par_date(activites, date(2024, 6, 1), date(2024, 6, 30))
        assert len(resultat) == 1

    def test_liste_vide(self):
        assert filtrer_par_date([], date(2024, 1, 1), date(2024, 12, 31)) == []


class TestCalculerStatistiquesActivites:
    """Tests pour calculer_statistiques_activites."""

    def test_liste_vide(self):
        stats = calculer_statistiques_activites([])
        assert stats["total"] == 0
        assert stats["cout_total"] == 0.0
        assert stats["cout_moyen"] == 0.0

    def test_stats_completes(self):
        activites = [
            {"type": "Sport", "lieu": "Parc", "cout": 10.0, "duree": 60},
            {"type": "Sport", "lieu": "Piscine", "cout": 20.0, "duree": 90},
            {"type": "Culture", "lieu": "Musée", "cout": 15.0, "duree": 120},
        ]
        stats = calculer_statistiques_activites(activites)
        assert stats["total"] == 3
        assert stats["par_type"]["Sport"] == 2
        assert stats["par_type"]["Culture"] == 1
        assert stats["cout_total"] == 45.0
        assert stats["cout_moyen"] == 15.0
        assert stats["duree_moyenne"] == 90.0


class TestCalculerFrequenceHebdomadaire:
    """Tests pour calculer_frequence_hebdomadaire."""

    def test_frequence_normale(self):
        activites = [{"titre": f"Act {i}"} for i in range(8)]
        freq = calculer_frequence_hebdomadaire(activites, semaines=4)
        assert freq == 2.0

    def test_semaines_zero(self):
        activites = [{"titre": "Test"}]
        assert calculer_frequence_hebdomadaire(activites, semaines=0) == 0.0

    def test_aucune_activite(self):
        assert calculer_frequence_hebdomadaire([], semaines=4) == 0.0


class TestSuggererActivitesAge:
    """Tests pour suggerer_activites_age."""

    def test_bebe_moins_12_mois(self):
        suggestions = suggerer_activites_age(6)
        assert len(suggestions) > 0
        assert any("Éveil" in s["type"] for s in suggestions)

    def test_enfant_12_24_mois(self):
        suggestions = suggerer_activites_age(18)
        assert len(suggestions) > 0

    def test_enfant_24_36_mois(self):
        suggestions = suggerer_activites_age(30)
        assert len(suggestions) > 0

    def test_enfant_plus_36_mois(self):
        suggestions = suggerer_activites_age(48)
        assert len(suggestions) > 0


class TestDetecterDesequilibreTypes:
    """Tests pour detecter_desequilibre_types."""

    def test_liste_vide_equilibre(self):
        resultat = detecter_desequilibre_types([])
        assert resultat["equilibre"] is True
        assert resultat["recommandations"] == []

    def test_desequilibre_type_dominant(self):
        activites = [{"type": "Sport"} for _ in range(10)]
        resultat = detecter_desequilibre_types(activites)
        assert resultat["equilibre"] is False
        assert any("surreprésenté" in r for r in resultat["recommandations"])

    def test_type_essentiel_manquant(self):
        activites = [{"type": "Jeux"} for _ in range(5)]
        resultat = detecter_desequilibre_types(activites)
        assert resultat["equilibre"] is False
        assert any("Sport" in r for r in resultat["recommandations"])

    def test_equilibre_parfait(self):
        activites = [
            {"type": "Sport"},
            {"type": "Culture"},
            {"type": "Sortie"},
            {"type": "Jeux"},
        ]
        resultat = detecter_desequilibre_types(activites)
        assert resultat["equilibre"] is True


class TestValiderActivite:
    """Tests pour valider_activite."""

    def test_activite_valide(self):
        data = {"titre": "Football", "date": "2024-06-15", "type": "Sport"}
        valide, erreurs = valider_activite(data)
        assert valide is True
        assert erreurs == []

    def test_titre_manquant(self):
        data = {"date": "2024-06-15"}
        valide, erreurs = valider_activite(data)
        assert valide is False
        assert any("titre" in e.lower() for e in erreurs)

    def test_date_manquante(self):
        data = {"titre": "Test"}
        valide, erreurs = valider_activite(data)
        assert valide is False
        assert any("date" in e.lower() for e in erreurs)

    def test_type_invalide(self):
        data = {"titre": "Test", "date": "2024-06-15", "type": "TypeInexistant"}
        valide, erreurs = valider_activite(data)
        assert valide is False
        assert any("invalide" in e.lower() for e in erreurs)

    def test_duree_negative(self):
        data = {"titre": "Test", "date": "2024-06-15", "duree": -10}
        valide, erreurs = valider_activite(data)
        assert valide is False
        assert any("durée" in e.lower() for e in erreurs)

    def test_cout_negatif(self):
        data = {"titre": "Test", "date": "2024-06-15", "cout": -5.0}
        valide, erreurs = valider_activite(data)
        assert valide is False
        assert any("coût" in e.lower() for e in erreurs)


class TestFormaterActiviteResume:
    """Tests pour formater_activite_resume."""

    def test_titre_seul(self):
        resultat = formater_activite_resume({"titre": "Football"})
        assert resultat == "Football"

    def test_avec_type(self):
        resultat = formater_activite_resume({"titre": "Football", "type": "Sport"})
        assert "Football (Sport)" in resultat

    def test_avec_lieu(self):
        resultat = formater_activite_resume({"titre": "Football", "lieu": "Parc"})
        assert "Parc" in resultat

    def test_complet(self):
        resultat = formater_activite_resume({"titre": "Football", "type": "Sport", "lieu": "Parc"})
        assert resultat == "Football (Sport) — Parc"

    def test_sans_titre(self):
        resultat = formater_activite_resume({})
        assert "Activité" in resultat


class TestGrouperParMois:
    """Tests pour grouper_par_mois."""

    def test_groupement_basique(self):
        activites = [
            {"titre": "A1", "date": date(2024, 6, 1)},
            {"titre": "A2", "date": date(2024, 6, 15)},
            {"titre": "A3", "date": date(2024, 7, 1)},
        ]
        groupes = grouper_par_mois(activites)
        assert "2024-06" in groupes
        assert "2024-07" in groupes
        assert len(groupes["2024-06"]) == 2
        assert len(groupes["2024-07"]) == 1

    def test_liste_vide(self):
        assert grouper_par_mois([]) == {}

    def test_string_iso_date(self):
        activites = [{"titre": "Test", "date": "2024-06-15"}]
        groupes = grouper_par_mois(activites)
        assert "2024-06" in groupes
