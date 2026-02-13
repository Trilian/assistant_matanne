"""Tests pour src/services/recettes/utils.py"""

import pytest

from src.services.recettes.utils import (
    # Constantes
    DIFFICULTES,
    ROBOTS_COMPATIBLES,
    SAISONS,
    TYPES_REPAS,
    ajuster_ingredients,
    # Portions
    ajuster_quantite_ingredient,
    calculer_score_recette,
    # Stats
    calculer_stats_recettes,
    # Temps
    calculer_temps_total,
    estimer_temps_robot,
    etape_to_dict,
    # Export CSV
    export_recettes_to_csv,
    # Export JSON
    export_recettes_to_json,
    filtrer_recettes_par_difficulte,
    filtrer_recettes_par_saison,
    # Filtres
    filtrer_recettes_par_temps,
    filtrer_recettes_par_type,
    formater_temps,
    ingredient_to_dict,
    parse_csv_to_recettes,
    parse_json_to_recettes,
    # Conversion
    recette_to_dict,
    rechercher_par_ingredient,
    rechercher_par_nom,
    # Validation
    valider_difficulte,
    valider_portions,
    valider_temps,
    valider_type_repas,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def sample_recettes():
    """Liste de recettes pour tests."""
    return [
        {
            "nom": "Poulet rôti",
            "description": "Poulet au four",
            "temps_preparation": 15,
            "temps_cuisson": 60,
            "portions": 4,
            "difficulte": "facile",
            "type_repas": "diner",
            "saison": "toute_année",
            "ingredients": [
                {"nom": "poulet", "quantite": 1.5, "unite": "kg"},
                {"nom": "herbes", "quantite": 10, "unite": "g"},
            ],
        },
        {
            "nom": "Salade César",
            "description": "Salade classique",
            "temps_preparation": 20,
            "temps_cuisson": 0,
            "portions": 2,
            "difficulte": "facile",
            "type_repas": "dejeuner",
            "saison": "ete",
            "ingredients": [
                {"nom": "salade", "quantite": 1, "unite": "pcs"},
                {"nom": "poulet", "quantite": 200, "unite": "g"},
            ],
        },
        {
            "nom": "Boeuf bourguignon",
            "description": "Plat mijoté traditionnel",
            "temps_preparation": 30,
            "temps_cuisson": 180,
            "portions": 6,
            "difficulte": "difficile",
            "type_repas": "diner",
            "saison": "hiver",
            "ingredients": [
                {"nom": "boeuf", "quantite": 1, "unite": "kg"},
                {"nom": "vin rouge", "quantite": 500, "unite": "ml"},
            ],
        },
    ]


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes."""

    def test_difficultes_defined(self):
        """Test que DIFFICULTES est défini correctement."""
        assert "facile" in DIFFICULTES
        assert "moyen" in DIFFICULTES
        assert "difficile" in DIFFICULTES
        assert len(DIFFICULTES) == 3

    def test_types_repas_defined(self):
        """Test que TYPES_REPAS est défini correctement."""
        assert "petit_dejeuner" in TYPES_REPAS
        assert "dejeuner" in TYPES_REPAS
        assert "diner" in TYPES_REPAS
        assert "gouter" in TYPES_REPAS
        assert "apero" in TYPES_REPAS

    def test_saisons_defined(self):
        """Test que SAISONS est défini correctement."""
        assert "printemps" in SAISONS
        assert "ete" in SAISONS
        assert "automne" in SAISONS
        assert "hiver" in SAISONS
        assert "toute_année" in SAISONS

    def test_robots_compatibles_defined(self):
        """Test que ROBOTS_COMPATIBLES est défini."""
        assert "cookeo" in ROBOTS_COMPATIBLES
        assert "monsieur_cuisine" in ROBOTS_COMPATIBLES
        assert "airfryer" in ROBOTS_COMPATIBLES
        assert ROBOTS_COMPATIBLES["cookeo"]["temps_reduction"] < 1.0


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT CSV
# ═══════════════════════════════════════════════════════════


class TestExportCSV:
    """Tests pour les fonctions CSV."""

    def test_export_recettes_to_csv_empty(self):
        """Test export liste vide."""
        result = export_recettes_to_csv([])
        assert result == ""

    def test_export_recettes_to_csv_basic(self, sample_recettes):
        """Test export basique."""
        result = export_recettes_to_csv(sample_recettes)
        assert "nom" in result
        assert "Poulet rôti" in result
        assert "Salade César" in result

    def test_export_recettes_to_csv_custom_separator(self, sample_recettes):
        """Test avec séparateur personnalisé."""
        result = export_recettes_to_csv(sample_recettes, separator=";")
        assert ";" in result

    def test_export_recettes_to_csv_custom_fieldnames(self, sample_recettes):
        """Test avec champs personnalisés."""
        result = export_recettes_to_csv(sample_recettes, fieldnames=["nom", "difficulte"])
        assert "nom" in result
        assert "difficulte" in result
        # Ne doit pas contenir temps_preparation
        lines = result.strip().split("\n")
        assert "temps_preparation" not in lines[0]

    def test_parse_csv_to_recettes_empty(self):
        """Test parse CSV vide."""
        result = parse_csv_to_recettes("")
        assert result == []

    def test_parse_csv_to_recettes_basic(self):
        """Test parse CSV basique."""
        csv_content = """nom,temps_preparation,temps_cuisson,portions
Poulet,15,60,4
Salade,10,0,2"""
        result = parse_csv_to_recettes(csv_content)
        assert len(result) == 2
        assert result[0]["nom"] == "Poulet"
        assert result[0]["temps_preparation"] == 15
        assert result[1]["temps_cuisson"] == 0

    def test_parse_csv_to_recettes_invalid_numbers(self):
        """Test parse avec nombres invalides."""
        csv_content = """nom,temps_preparation,temps_cuisson
Test,invalid,30"""
        result = parse_csv_to_recettes(csv_content)
        assert result[0]["temps_preparation"] == 0
        assert result[0]["temps_cuisson"] == 30

    def test_parse_csv_roundtrip(self, sample_recettes):
        """Test export puis re-import."""
        csv = export_recettes_to_csv(sample_recettes)
        parsed = parse_csv_to_recettes(csv)
        assert len(parsed) == len(sample_recettes)
        assert parsed[0]["nom"] == sample_recettes[0]["nom"]


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT JSON
# ═══════════════════════════════════════════════════════════


class TestExportJSON:
    """Tests pour les fonctions JSON."""

    def test_export_recettes_to_json_basic(self, sample_recettes):
        """Test export JSON basique."""
        result = export_recettes_to_json(sample_recettes)
        assert "Poulet rôti" in result
        import json

        parsed = json.loads(result)
        assert len(parsed) == 3

    def test_export_recettes_to_json_indent(self, sample_recettes):
        """Test export avec indentation."""
        result = export_recettes_to_json(sample_recettes, indent=4)
        assert "\n" in result

    def test_parse_json_to_recettes_empty(self):
        """Test parse JSON vide."""
        result = parse_json_to_recettes("")
        assert result == []

    def test_parse_json_to_recettes_list(self):
        """Test parse JSON liste."""
        json_content = '[{"nom": "Test1"}, {"nom": "Test2"}]'
        result = parse_json_to_recettes(json_content)
        assert len(result) == 2
        assert result[0]["nom"] == "Test1"

    def test_parse_json_to_recettes_single_object(self):
        """Test parse JSON objet unique."""
        json_content = '{"nom": "Recette unique"}'
        result = parse_json_to_recettes(json_content)
        assert len(result) == 1
        assert result[0]["nom"] == "Recette unique"

    def test_parse_json_roundtrip(self, sample_recettes):
        """Test export puis re-import."""
        json_str = export_recettes_to_json(sample_recettes)
        parsed = parse_json_to_recettes(json_str)
        assert len(parsed) == len(sample_recettes)


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION
# ═══════════════════════════════════════════════════════════


class TestConversion:
    """Tests pour les fonctions de conversion."""

    def test_recette_to_dict_minimal(self):
        """Test conversion minimale."""
        result = recette_to_dict("Ma recette")
        assert result["nom"] == "Ma recette"
        assert result["portions"] == 4
        assert result["difficulte"] == "moyen"
        assert result["ingredients"] == []

    def test_recette_to_dict_complete(self):
        """Test conversion complète."""
        result = recette_to_dict(
            nom="Tarte aux pommes",
            description="Dessert classique",
            temps_preparation=30,
            temps_cuisson=45,
            portions=8,
            difficulte="facile",
            type_repas="gouter",
            saison="automne",
            ingredients=[{"nom": "pommes"}],
            etapes=[{"description": "Couper les pommes"}],
        )
        assert result["nom"] == "Tarte aux pommes"
        assert result["temps_cuisson"] == 45
        assert result["portions"] == 8
        assert len(result["ingredients"]) == 1

    def test_ingredient_to_dict_default(self):
        """Test ingrédient avec valeurs par défaut."""
        result = ingredient_to_dict("farine")
        assert result["nom"] == "farine"
        assert result["quantite"] == 1.0
        assert result["unite"] == "pcs"

    def test_ingredient_to_dict_complete(self):
        """Test ingrédient complet."""
        result = ingredient_to_dict("sucre", quantite=200, unite="g")
        assert result["nom"] == "sucre"
        assert result["quantite"] == 200
        assert result["unite"] == "g"

    def test_etape_to_dict_minimal(self):
        """Test étape minimale."""
        result = etape_to_dict("Mélanger les ingrédients")
        assert result["description"] == "Mélanger les ingrédients"
        assert result["ordre"] == 1
        assert "duree" not in result

    def test_etape_to_dict_with_duree(self):
        """Test étape avec durée."""
        result = etape_to_dict("Cuire au four", ordre=3, duree=30)
        assert result["ordre"] == 3
        assert result["duree"] == 30


# ═══════════════════════════════════════════════════════════
# TESTS TEMPS
# ═══════════════════════════════════════════════════════════


class TestTemps:
    """Tests pour les fonctions de temps."""

    def test_calculer_temps_total(self):
        """Test calcul temps total."""
        assert calculer_temps_total(15, 60) == 75
        assert calculer_temps_total(0, 0) == 0
        assert calculer_temps_total(30, 0) == 30

    def test_estimer_temps_robot_cookeo(self):
        """Test estimation temps Cookeo."""
        # Cookeo a reduction de 0.7
        result = estimer_temps_robot(60, "cookeo")
        assert result == 42  # 60 * 0.7

    def test_estimer_temps_robot_airfryer(self):
        """Test estimation temps Airfryer."""
        result = estimer_temps_robot(60, "airfryer")
        assert result == 45  # 60 * 0.75

    def test_estimer_temps_robot_unknown(self):
        """Test robot inconnu (pas de réduction)."""
        result = estimer_temps_robot(60, "robot_inconnu")
        assert result == 60

    def test_formater_temps_minutes(self):
        """Test formatage minutes seules."""
        assert formater_temps(30) == "30min"
        assert formater_temps(59) == "59min"

    def test_formater_temps_heures(self):
        """Test formatage heures entières."""
        assert formater_temps(60) == "1h"
        assert formater_temps(120) == "2h"

    def test_formater_temps_heures_minutes(self):
        """Test formatage heures et minutes."""
        assert formater_temps(90) == "1h 30min"
        assert formater_temps(150) == "2h 30min"


# ═══════════════════════════════════════════════════════════
# TESTS PORTIONS
# ═══════════════════════════════════════════════════════════


class TestPortions:
    """Tests pour les fonctions de portions."""

    def test_ajuster_quantite_ingredient_double(self):
        """Test doublement des portions."""
        result = ajuster_quantite_ingredient(100, 4, 8)
        assert result == 200

    def test_ajuster_quantite_ingredient_half(self):
        """Test réduction de moitié."""
        result = ajuster_quantite_ingredient(100, 4, 2)
        assert result == 50

    def test_ajuster_quantite_ingredient_same(self):
        """Test même portions."""
        result = ajuster_quantite_ingredient(100, 4, 4)
        assert result == 100

    def test_ajuster_quantite_ingredient_zero_base(self):
        """Test avec portions base à 0."""
        result = ajuster_quantite_ingredient(100, 0, 4)
        assert result == 100

    def test_ajuster_ingredients_list(self):
        """Test ajustement liste d'ingrédients."""
        ingredients = [
            {"nom": "farine", "quantite": 200},
            {"nom": "sucre", "quantite": 100},
        ]
        result = ajuster_ingredients(ingredients, 4, 8)
        assert result[0]["quantite"] == 400
        assert result[1]["quantite"] == 200

    def test_ajuster_ingredients_same_portions(self):
        """Test sans changement de portions."""
        ingredients = [{"nom": "farine", "quantite": 200}]
        result = ajuster_ingredients(ingredients, 4, 4)
        assert result == ingredients

    def test_ajuster_ingredients_no_quantity(self):
        """Test ingrédient sans quantité."""
        ingredients = [{"nom": "sel"}]
        result = ajuster_ingredients(ingredients, 4, 8)
        assert "quantite" not in result[0]


# ═══════════════════════════════════════════════════════════
# TESTS FILTRES
# ═══════════════════════════════════════════════════════════


class TestFiltres:
    """Tests pour les fonctions de filtrage."""

    def test_filtrer_recettes_par_temps(self, sample_recettes):
        """Test filtre par temps total."""
        # Poulet: 75min, Salade: 20min, Boeuf: 210min
        result = filtrer_recettes_par_temps(sample_recettes, 100)
        assert len(result) == 2
        assert result[0]["nom"] == "Poulet rôti"
        assert result[1]["nom"] == "Salade César"

    def test_filtrer_recettes_par_temps_all(self, sample_recettes):
        """Test filtre incluant toutes les recettes."""
        result = filtrer_recettes_par_temps(sample_recettes, 300)
        assert len(result) == 3

    def test_filtrer_recettes_par_temps_none(self, sample_recettes):
        """Test filtre excluant tout."""
        result = filtrer_recettes_par_temps(sample_recettes, 10)
        assert len(result) == 0

    def test_filtrer_recettes_par_difficulte(self, sample_recettes):
        """Test filtre par difficulté."""
        result = filtrer_recettes_par_difficulte(sample_recettes, "facile")
        assert len(result) == 2
        assert all(r["difficulte"] == "facile" for r in result)

    def test_filtrer_recettes_par_type(self, sample_recettes):
        """Test filtre par type de repas."""
        result = filtrer_recettes_par_type(sample_recettes, "diner")
        assert len(result) == 2

    def test_filtrer_recettes_par_saison(self, sample_recettes):
        """Test filtre par saison."""
        result = filtrer_recettes_par_saison(sample_recettes, "hiver")
        # Boeuf (hiver) + Poulet (toute_année)
        assert len(result) == 2

    def test_filtrer_recettes_par_saison_ete(self, sample_recettes):
        """Test filtre saison été."""
        result = filtrer_recettes_par_saison(sample_recettes, "ete")
        # Salade (ete) + Poulet (toute_année)
        assert len(result) == 2

    def test_rechercher_par_nom(self, sample_recettes):
        """Test recherche par nom."""
        result = rechercher_par_nom(sample_recettes, "poulet")
        assert len(result) == 1
        assert result[0]["nom"] == "Poulet rôti"

    def test_rechercher_par_nom_case_insensitive(self, sample_recettes):
        """Test recherche insensible à la casse."""
        result = rechercher_par_nom(sample_recettes, "SALADE")
        assert len(result) == 1

    def test_rechercher_par_nom_partial(self, sample_recettes):
        """Test recherche partielle."""
        result = rechercher_par_nom(sample_recettes, "boeuf")
        assert len(result) == 1
        assert result[0]["nom"] == "Boeuf bourguignon"

    def test_rechercher_par_ingredient(self, sample_recettes):
        """Test recherche par ingrédient."""
        result = rechercher_par_ingredient(sample_recettes, "poulet")
        assert len(result) == 2  # Poulet rôti et Salade César

    def test_rechercher_par_ingredient_unique(self, sample_recettes):
        """Test recherche ingrédient unique."""
        result = rechercher_par_ingredient(sample_recettes, "vin")
        assert len(result) == 1
        assert result[0]["nom"] == "Boeuf bourguignon"


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestStatistiques:
    """Tests pour les fonctions de statistiques."""

    def test_calculer_stats_recettes_empty(self):
        """Test stats liste vide."""
        result = calculer_stats_recettes([])
        assert result["total"] == 0
        assert result["temps_moyen_preparation"] == 0

    def test_calculer_stats_recettes_basic(self, sample_recettes):
        """Test stats basiques."""
        result = calculer_stats_recettes(sample_recettes)
        assert result["total"] == 3
        assert result["temps_moyen_preparation"] > 0
        assert "par_difficulte" in result
        assert result["par_difficulte"]["facile"] == 2
        assert result["par_difficulte"]["difficile"] == 1

    def test_calculer_stats_recettes_par_type(self, sample_recettes):
        """Test stats par type."""
        result = calculer_stats_recettes(sample_recettes)
        assert result["par_type"]["diner"] == 2
        assert result["par_type"]["dejeuner"] == 1

    def test_calculer_score_recette_base(self):
        """Test score de base sans critères."""
        recette = {"nom": "Test", "temps_preparation": 30, "temps_cuisson": 30}
        result = calculer_score_recette(recette)
        assert result == 50.0

    def test_calculer_score_recette_with_temps(self):
        """Test score avec critère temps."""
        recette = {"nom": "Test", "temps_preparation": 15, "temps_cuisson": 15}
        result = calculer_score_recette(recette, {"temps_max": 60})
        assert result == 70.0  # 50 + 20

    def test_calculer_score_recette_with_difficulte(self):
        """Test score avec critère difficulté."""
        recette = {"nom": "Test", "difficulte": "facile"}
        result = calculer_score_recette(recette, {"difficulte_preferee": "facile"})
        assert result == 65.0  # 50 + 15

    def test_calculer_score_recette_with_type(self):
        """Test score avec critère type."""
        recette = {"nom": "Test", "type_repas": "diner"}
        result = calculer_score_recette(recette, {"type_repas": "diner"})
        assert result == 60.0  # 50 + 10

    def test_calculer_score_recette_with_saison(self):
        """Test score avec critère saison."""
        recette = {"nom": "Test", "saison": "toute_année"}
        result = calculer_score_recette(recette, {"saison": "hiver"})
        assert result == 55.0  # 50 + 5

    def test_calculer_score_recette_max_100(self):
        """Test score plafonné à 100."""
        recette = {
            "nom": "Test",
            "temps_preparation": 10,
            "temps_cuisson": 10,
            "difficulte": "facile",
            "type_repas": "diner",
            "saison": "hiver",
        }
        criteres = {
            "temps_max": 60,
            "difficulte_preferee": "facile",
            "type_repas": "diner",
            "saison": "hiver",
        }
        result = calculer_score_recette(recette, criteres)
        assert result == 100.0


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValidation:
    """Tests pour les fonctions de validation."""

    def test_valider_difficulte_valid(self):
        """Test difficulté valide."""
        assert valider_difficulte("facile") == "facile"
        assert valider_difficulte("MOYEN") == "moyen"
        assert valider_difficulte("Difficile") == "difficile"

    def test_valider_difficulte_invalid(self):
        """Test difficulté invalide."""
        with pytest.raises(ValueError) as exc_info:
            valider_difficulte("très_facile")
        assert "Difficulté invalide" in str(exc_info.value)

    def test_valider_type_repas_valid(self):
        """Test type repas valide."""
        assert valider_type_repas("diner") == "diner"
        assert valider_type_repas("PETIT_DEJEUNER") == "petit_dejeuner"

    def test_valider_type_repas_invalid(self):
        """Test type repas invalide."""
        with pytest.raises(ValueError) as exc_info:
            valider_type_repas("brunch")
        assert "Type de repas invalide" in str(exc_info.value)

    def test_valider_temps_valid(self):
        """Test temps valide."""
        assert valider_temps(30) == 30
        assert valider_temps(480) == 480

    def test_valider_temps_none(self):
        """Test temps None."""
        assert valider_temps(None) == 0
        assert valider_temps(None, defaut=30) == 30

    def test_valider_temps_negative(self):
        """Test temps négatif."""
        assert valider_temps(-10) == 0

    def test_valider_temps_too_large(self):
        """Test temps trop grand (plafonné à 480)."""
        assert valider_temps(1000) == 480

    def test_valider_portions_valid(self):
        """Test portions valides."""
        assert valider_portions(4) == 4
        assert valider_portions(1) == 1
        assert valider_portions(100) == 100

    def test_valider_portions_none(self):
        """Test portions None."""
        assert valider_portions(None) == 4
        assert valider_portions(None, defaut=6) == 6

    def test_valider_portions_zero(self):
        """Test portions 0."""
        assert valider_portions(0) == 4

    def test_valider_portions_too_large(self):
        """Test portions trop grandes (plafonné à 100)."""
        assert valider_portions(200) == 100
