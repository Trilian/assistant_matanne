"""
Tests pour les fonctions utilitaires pures des recettes.

Ces tests ne nécessitent pas de base de données.
"""

import pytest
import json

from src.services.recettes_utils import (
    # Constantes
    DIFFICULTES,
    TYPES_REPAS,
    SAISONS,
    ROBOTS_COMPATIBLES,
    # Export CSV
    export_recettes_to_csv,
    parse_csv_to_recettes,
    # Export JSON
    export_recettes_to_json,
    parse_json_to_recettes,
    # Conversion
    recette_to_dict,
    ingredient_to_dict,
    etape_to_dict,
    # Temps
    calculer_temps_total,
    estimer_temps_robot,
    formater_temps,
    # Portions
    ajuster_quantite_ingredient,
    ajuster_ingredients,
    # Filtres
    filtrer_recettes_par_temps,
    filtrer_recettes_par_difficulte,
    filtrer_recettes_par_type,
    filtrer_recettes_par_saison,
    rechercher_par_nom,
    rechercher_par_ingredient,
    # Stats
    calculer_stats_recettes,
    calculer_score_recette,
    # Validation
    valider_difficulte,
    valider_type_repas,
    valider_temps,
    valider_portions,
)


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes."""

    def test_difficultes_count(self):
        assert len(DIFFICULTES) == 3

    def test_difficultes_values(self):
        assert "facile" in DIFFICULTES
        assert "moyen" in DIFFICULTES
        assert "difficile" in DIFFICULTES

    def test_types_repas_count(self):
        assert len(TYPES_REPAS) >= 4

    def test_saisons_count(self):
        assert len(SAISONS) == 5

    def test_robots_compatibles(self):
        assert "cookeo" in ROBOTS_COMPATIBLES


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT CSV
# ═══════════════════════════════════════════════════════════


class TestExportCsv:
    """Tests pour export_recettes_to_csv."""

    def test_liste_vide(self):
        result = export_recettes_to_csv([])
        assert result == ""

    def test_une_recette(self):
        recettes = [{"nom": "Poulet rôti", "temps_preparation": 20}]
        result = export_recettes_to_csv(recettes)
        assert "nom" in result
        assert "Poulet rôti" in result

    def test_plusieurs_recettes(self):
        recettes = [
            {"nom": "Poulet rôti", "temps_preparation": 20},
            {"nom": "Gratin", "temps_preparation": 15},
        ]
        result = export_recettes_to_csv(recettes)
        assert "Poulet rôti" in result
        assert "Gratin" in result

    def test_separator_custom(self):
        recettes = [{"nom": "Test", "temps_preparation": 10}]
        result = export_recettes_to_csv(recettes, separator=";")
        assert ";" in result


class TestParseCsv:
    """Tests pour parse_csv_to_recettes."""

    def test_contenu_vide(self):
        result = parse_csv_to_recettes("")
        assert result == []

    def test_parse_simple(self):
        csv_content = "nom,temps_preparation\nPoulet,20"
        result = parse_csv_to_recettes(csv_content)
        assert len(result) == 1
        assert result[0]["nom"] == "Poulet"
        assert result[0]["temps_preparation"] == 20

    def test_parse_time_invalid(self):
        csv_content = "nom,temps_preparation\nPoulet,invalid"
        result = parse_csv_to_recettes(csv_content)
        assert result[0]["temps_preparation"] == 0


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT JSON
# ═══════════════════════════════════════════════════════════


class TestExportJson:
    """Tests pour export_recettes_to_json."""

    def test_liste_vide(self):
        result = export_recettes_to_json([])
        assert result == "[]"

    def test_une_recette(self):
        recettes = [{"nom": "Poulet rôti"}]
        result = export_recettes_to_json(recettes)
        data = json.loads(result)
        assert data[0]["nom"] == "Poulet rôti"


class TestParseJson:
    """Tests pour parse_json_to_recettes."""

    def test_contenu_vide(self):
        result = parse_json_to_recettes("")
        assert result == []

    def test_parse_liste(self):
        json_content = '[{"nom": "Poulet"}]'
        result = parse_json_to_recettes(json_content)
        assert len(result) == 1

    def test_parse_dict_unique(self):
        json_content = '{"nom": "Poulet"}'
        result = parse_json_to_recettes(json_content)
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION
# ═══════════════════════════════════════════════════════════


class TestRecetteToDict:
    """Tests pour recette_to_dict."""

    def test_minimal(self):
        result = recette_to_dict("Poulet rôti")
        assert result["nom"] == "Poulet rôti"
        assert result["portions"] == 4  # Défaut

    def test_complet(self):
        result = recette_to_dict(
            "Poulet rôti",
            description="Délicieux",
            temps_preparation=20,
            temps_cuisson=60,
            portions=6,
        )
        assert result["temps_preparation"] == 20
        assert result["portions"] == 6


class TestIngredientToDict:
    """Tests pour ingredient_to_dict."""

    def test_minimal(self):
        result = ingredient_to_dict("Poulet")
        assert result["nom"] == "Poulet"
        assert result["unite"] == "pcs"

    def test_complet(self):
        result = ingredient_to_dict("Poulet", 1.5, "kg")
        assert result["quantite"] == 1.5
        assert result["unite"] == "kg"


class TestEtapeToDict:
    """Tests pour etape_to_dict."""

    def test_minimal(self):
        result = etape_to_dict("Préchauffer le four")
        assert result["description"] == "Préchauffer le four"
        assert result["ordre"] == 1

    def test_avec_duree(self):
        result = etape_to_dict("Cuisson", 2, 30)
        assert result["ordre"] == 2
        assert result["duree"] == 30


# ═══════════════════════════════════════════════════════════
# TESTS TEMPS
# ═══════════════════════════════════════════════════════════


class TestCalculerTempsTotal:
    """Tests pour calculer_temps_total."""

    def test_simple(self):
        assert calculer_temps_total(20, 60) == 80

    def test_zero(self):
        assert calculer_temps_total(0, 0) == 0


class TestEstimerTempsRobot:
    """Tests pour estimer_temps_robot."""

    def test_cookeo(self):
        # Cookeo réduit de 30%
        result = estimer_temps_robot(100, "cookeo")
        assert result == 70

    def test_robot_inconnu(self):
        # Robot inconnu = pas de réduction
        result = estimer_temps_robot(100, "robot_inconnu")
        assert result == 100


class TestFormaterTemps:
    """Tests pour formater_temps."""

    def test_minutes_seules(self):
        assert formater_temps(45) == "45min"

    def test_une_heure(self):
        assert formater_temps(60) == "1h"

    def test_heures_et_minutes(self):
        assert formater_temps(90) == "1h 30min"


# ═══════════════════════════════════════════════════════════
# TESTS PORTIONS
# ═══════════════════════════════════════════════════════════


class TestAjusterQuantiteIngredient:
    """Tests pour ajuster_quantite_ingredient."""

    def test_doubler(self):
        result = ajuster_quantite_ingredient(100, 4, 8)
        assert result == 200.0

    def test_diviser(self):
        result = ajuster_quantite_ingredient(100, 4, 2)
        assert result == 50.0

    def test_portions_base_zero(self):
        result = ajuster_quantite_ingredient(100, 0, 4)
        assert result == 100  # Pas de changement


class TestAjusterIngredients:
    """Tests pour ajuster_ingredients."""

    def test_memes_portions(self):
        ingredients = [{"nom": "Farine", "quantite": 200}]
        result = ajuster_ingredients(ingredients, 4, 4)
        assert result[0]["quantite"] == 200

    def test_doubler_portions(self):
        ingredients = [
            {"nom": "Farine", "quantite": 200},
            {"nom": "Sucre", "quantite": 100},
        ]
        result = ajuster_ingredients(ingredients, 4, 8)
        assert result[0]["quantite"] == 400
        assert result[1]["quantite"] == 200


# ═══════════════════════════════════════════════════════════
# TESTS FILTRES
# ═══════════════════════════════════════════════════════════


class TestFiltrerRecettesParTemps:
    """Tests pour filtrer_recettes_par_temps."""

    def test_filtre_temps(self):
        recettes = [
            {"nom": "Rapide", "temps_preparation": 10, "temps_cuisson": 10},
            {"nom": "Long", "temps_preparation": 30, "temps_cuisson": 60},
        ]
        result = filtrer_recettes_par_temps(recettes, 30)
        assert len(result) == 1
        assert result[0]["nom"] == "Rapide"


class TestFiltrerRecettesParDifficulte:
    """Tests pour filtrer_recettes_par_difficulte."""

    def test_filtre(self):
        recettes = [
            {"nom": "Facile", "difficulte": "facile"},
            {"nom": "Moyen", "difficulte": "moyen"},
        ]
        result = filtrer_recettes_par_difficulte(recettes, "facile")
        assert len(result) == 1


class TestFiltrerRecettesParType:
    """Tests pour filtrer_recettes_par_type."""

    def test_filtre(self):
        recettes = [
            {"nom": "Dîner", "type_repas": "diner"},
            {"nom": "Déjeuner", "type_repas": "dejeuner"},
        ]
        result = filtrer_recettes_par_type(recettes, "diner")
        assert len(result) == 1


class TestFiltrerRecettesParSaison:
    """Tests pour filtrer_recettes_par_saison."""

    def test_filtre_saison(self):
        recettes = [
            {"nom": "Été", "saison": "ete"},
            {"nom": "Toute année", "saison": "toute_année"},
            {"nom": "Hiver", "saison": "hiver"},
        ]
        result = filtrer_recettes_par_saison(recettes, "ete")
        assert len(result) == 2  # Été + toute_année


class TestRechercherParNom:
    """Tests pour rechercher_par_nom."""

    def test_recherche_simple(self):
        recettes = [
            {"nom": "Poulet rôti"},
            {"nom": "Gratin de pâtes"},
        ]
        result = rechercher_par_nom(recettes, "poulet")
        assert len(result) == 1

    def test_recherche_insensible_casse(self):
        recettes = [{"nom": "Poulet rôti"}]
        result = rechercher_par_nom(recettes, "POULET")
        assert len(result) == 1


class TestRechercherParIngredient:
    """Tests pour rechercher_par_ingredient."""

    def test_recherche_ingredient(self):
        recettes = [
            {"nom": "Poulet", "ingredients": [{"nom": "poulet"}]},
            {"nom": "Boeuf", "ingredients": [{"nom": "boeuf"}]},
        ]
        result = rechercher_par_ingredient(recettes, "poulet")
        assert len(result) == 1

    def test_sans_ingredients(self):
        recettes = [{"nom": "Test"}]
        result = rechercher_par_ingredient(recettes, "poulet")
        assert len(result) == 0


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestCalculerStatsRecettes:
    """Tests pour calculer_stats_recettes."""

    def test_liste_vide(self):
        result = calculer_stats_recettes([])
        assert result["total"] == 0

    def test_stats_basiques(self):
        recettes = [
            {"nom": "A", "temps_preparation": 10, "temps_cuisson": 20, "difficulte": "facile", "type_repas": "diner", "saison": "ete"},
            {"nom": "B", "temps_preparation": 20, "temps_cuisson": 40, "difficulte": "facile", "type_repas": "diner", "saison": "hiver"},
        ]
        result = calculer_stats_recettes(recettes)
        assert result["total"] == 2
        assert result["temps_moyen_preparation"] == 15
        assert result["par_difficulte"]["facile"] == 2


class TestCalculerScoreRecette:
    """Tests pour calculer_score_recette."""

    def test_sans_criteres(self):
        recette = {"nom": "Test"}
        result = calculer_score_recette(recette)
        assert result == 50.0  # Score de base

    def test_avec_criteres(self):
        recette = {
            "nom": "Test",
            "temps_preparation": 10,
            "temps_cuisson": 10,
            "difficulte": "facile",
        }
        result = calculer_score_recette(recette, {
            "temps_max": 30,
            "difficulte_preferee": "facile",
        })
        assert result > 50.0  # Bonus appliqués


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValiderDifficulte:
    """Tests pour valider_difficulte."""

    def test_valide(self):
        assert valider_difficulte("facile") == "facile"

    def test_normalise_casse(self):
        assert valider_difficulte("FACILE") == "facile"

    def test_invalide(self):
        with pytest.raises(ValueError):
            valider_difficulte("super_facile")


class TestValiderTypeRepas:
    """Tests pour valider_type_repas."""

    def test_valide(self):
        assert valider_type_repas("diner") == "diner"

    def test_invalide(self):
        with pytest.raises(ValueError):
            valider_type_repas("petit_cafe")


class TestValiderTemps:
    """Tests pour valider_temps."""

    def test_valide(self):
        assert valider_temps(60) == 60

    def test_none(self):
        assert valider_temps(None) == 0

    def test_negatif(self):
        assert valider_temps(-10) == 0

    def test_trop_long(self):
        assert valider_temps(600) == 480


class TestValiderPortions:
    """Tests pour valider_portions."""

    def test_valide(self):
        assert valider_portions(6) == 6

    def test_none(self):
        assert valider_portions(None) == 4

    def test_zero(self):
        assert valider_portions(0) == 4

    def test_trop(self):
        assert valider_portions(200) == 100
