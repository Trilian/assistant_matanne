"""
Tests pour src/services/recettes/utils.py

Ce module teste les fonctions utilitaires pures pour les recettes:
- Export/Import CSV et JSON
- Conversion recette/ingrédient/étape
- Calculs de temps et portions
- Filtres et recherche
- Statistiques
- Validation
"""

import pytest
import json

from src.services.recettes.utils import (
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
# FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def sample_recettes():
    """Liste de recettes pour les tests."""
    return [
        {
            "nom": "Poulet Rôti",
            "description": "Poulet rôti aux herbes",
            "temps_preparation": 15,
            "temps_cuisson": 60,
            "portions": 6,
            "difficulte": "facile",
            "type_repas": "diner",
            "saison": "toute_année",
            "ingredients": [
                {"nom": "poulet", "quantite": 1.5, "unite": "kg"},
                {"nom": "thym", "quantite": 10, "unite": "g"},
            ],
            "etapes": [
                {"ordre": 1, "description": "Préchauffer le four"},
                {"ordre": 2, "description": "Assaisonner le poulet"},
            ],
        },
        {
            "nom": "Salade César",
            "description": "Salade traditionnelle",
            "temps_preparation": 20,
            "temps_cuisson": 0,
            "portions": 4,
            "difficulte": "facile",
            "type_repas": "dejeuner",
            "saison": "ete",
            "ingredients": [
                {"nom": "salade romaine", "quantite": 1, "unite": "pcs"},
                {"nom": "parmesan", "quantite": 50, "unite": "g"},
            ],
            "etapes": [],
        },
        {
            "nom": "Boeuf Bourguignon",
            "description": "Plat mijoté traditionnel",
            "temps_preparation": 30,
            "temps_cuisson": 180,
            "portions": 8,
            "difficulte": "difficile",
            "type_repas": "diner",
            "saison": "hiver",
            "ingredients": [
                {"nom": "boeuf", "quantite": 1, "unite": "kg"},
                {"nom": "vin rouge", "quantite": 750, "unite": "ml"},
            ],
            "etapes": [],
        },
    ]


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════

class TestConstantes:
    """Tests pour les constantes."""
    
    def test_difficultes_contains_expected_values(self):
        """Vérifie que les difficultés attendues sont présentes."""
        assert "facile" in DIFFICULTES
        assert "moyen" in DIFFICULTES
        assert "difficile" in DIFFICULTES
        assert len(DIFFICULTES) == 3
    
    def test_types_repas_contains_expected_values(self):
        """Vérifie que les types de repas attendus sont présents."""
        assert "petit_dejeuner" in TYPES_REPAS
        assert "dejeuner" in TYPES_REPAS
        assert "diner" in TYPES_REPAS
        assert "gouter" in TYPES_REPAS
        assert "apero" in TYPES_REPAS
    
    def test_saisons_contains_expected_values(self):
        """Vérifie que les saisons attendues sont présentes."""
        assert "printemps" in SAISONS
        assert "ete" in SAISONS
        assert "automne" in SAISONS
        assert "hiver" in SAISONS
        assert "toute_année" in SAISONS
    
    def test_robots_compatibles_structure(self):
        """Vérifie la structure des robots compatibles."""
        assert "cookeo" in ROBOTS_COMPATIBLES
        assert "monsieur_cuisine" in ROBOTS_COMPATIBLES
        assert "airfryer" in ROBOTS_COMPATIBLES
        
        for robot_key, robot_info in ROBOTS_COMPATIBLES.items():
            assert "nom" in robot_info
            assert "temps_reduction" in robot_info
            assert 0 < robot_info["temps_reduction"] <= 1.0


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT CSV
# ═══════════════════════════════════════════════════════════

class TestExportCSV:
    """Tests pour l'export CSV."""
    
    def test_export_recettes_to_csv_with_data(self, sample_recettes):
        """Teste l'export CSV avec des données."""
        csv_output = export_recettes_to_csv(sample_recettes)
        
        assert csv_output
        lines = csv_output.strip().split('\n')
        assert len(lines) == 4  # Header + 3 recettes
        
        # Vérifier le header
        header = lines[0]
        assert "nom" in header
        assert "description" in header
        assert "temps_preparation" in header
    
    def test_export_recettes_to_csv_empty_list(self):
        """Teste l'export CSV avec une liste vide."""
        csv_output = export_recettes_to_csv([])
        assert csv_output == ""
    
    def test_export_recettes_to_csv_custom_separator(self, sample_recettes):
        """Teste l'export CSV avec séparateur personnalisé."""
        csv_output = export_recettes_to_csv(sample_recettes[:1], separator=";")
        
        assert ";" in csv_output
        lines = csv_output.strip().split('\n')
        assert len(lines[0].split(";")) > 1
    
    def test_export_recettes_to_csv_custom_fieldnames(self, sample_recettes):
        """Teste l'export CSV avec colonnes personnalisées."""
        csv_output = export_recettes_to_csv(
            sample_recettes[:1],
            fieldnames=["nom", "portions"]
        )
        
        lines = csv_output.strip().split('\n')
        header = lines[0]
        assert "nom" in header
        assert "portions" in header
        assert "description" not in header
    
    def test_parse_csv_to_recettes(self, sample_recettes):
        """Teste le parsing CSV."""
        csv_content = export_recettes_to_csv(sample_recettes)
        parsed = parse_csv_to_recettes(csv_content)
        
        assert len(parsed) == 3
        assert parsed[0]["nom"] == "Poulet Rôti"
        assert parsed[0]["temps_preparation"] == 15
        assert parsed[0]["portions"] == 6
    
    def test_parse_csv_to_recettes_empty(self):
        """Teste le parsing CSV vide."""
        parsed = parse_csv_to_recettes("")
        assert parsed == []
        
        parsed = parse_csv_to_recettes("   ")
        assert parsed == []
    
    def test_parse_csv_to_recettes_invalid_numbers(self):
        """Teste le parsing CSV avec nombres invalides."""
        csv_content = "nom,temps_preparation,portions\nTest,abc,xyz"
        parsed = parse_csv_to_recettes(csv_content)
        
        assert len(parsed) == 1
        assert parsed[0]["nom"] == "Test"
        assert parsed[0]["temps_preparation"] == 0
        assert parsed[0]["portions"] == 0


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT JSON
# ═══════════════════════════════════════════════════════════

class TestExportJSON:
    """Tests pour l'export JSON."""
    
    def test_export_recettes_to_json(self, sample_recettes):
        """Teste l'export JSON."""
        json_output = export_recettes_to_json(sample_recettes)
        
        assert json_output
        data = json.loads(json_output)
        assert len(data) == 3
        assert data[0]["nom"] == "Poulet Rôti"
    
    def test_export_recettes_to_json_empty(self):
        """Teste l'export JSON vide."""
        json_output = export_recettes_to_json([])
        data = json.loads(json_output)
        assert data == []
    
    def test_export_recettes_to_json_indentation(self, sample_recettes):
        """Teste l'export JSON avec indentation."""
        json_output_2 = export_recettes_to_json(sample_recettes[:1], indent=2)
        json_output_4 = export_recettes_to_json(sample_recettes[:1], indent=4)
        
        # Plus d'indentation = plus long
        assert len(json_output_4) > len(json_output_2)
    
    def test_parse_json_to_recettes_list(self, sample_recettes):
        """Teste le parsing JSON liste."""
        json_content = export_recettes_to_json(sample_recettes)
        parsed = parse_json_to_recettes(json_content)
        
        assert len(parsed) == 3
        assert parsed[0]["nom"] == "Poulet Rôti"
    
    def test_parse_json_to_recettes_single_object(self):
        """Teste le parsing JSON objet unique."""
        json_content = '{"nom": "Test Recipe", "portions": 4}'
        parsed = parse_json_to_recettes(json_content)
        
        assert len(parsed) == 1
        assert parsed[0]["nom"] == "Test Recipe"
    
    def test_parse_json_to_recettes_empty(self):
        """Teste le parsing JSON vide."""
        parsed = parse_json_to_recettes("")
        assert parsed == []
        
        parsed = parse_json_to_recettes("   ")
        assert parsed == []


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSION
# ═══════════════════════════════════════════════════════════

class TestConversion:
    """Tests pour les fonctions de conversion."""
    
    def test_recette_to_dict_minimal(self):
        """Teste la création d'un dict recette minimal."""
        result = recette_to_dict("Test Recipe")
        
        assert result["nom"] == "Test Recipe"
        assert result["description"] == ""
        assert result["temps_preparation"] == 0
        assert result["temps_cuisson"] == 0
        assert result["portions"] == 4
        assert result["difficulte"] == "moyen"
        assert result["type_repas"] == "diner"
        assert result["saison"] == "toute_année"
        assert result["ingredients"] == []
        assert result["etapes"] == []
    
    def test_recette_to_dict_complete(self):
        """Teste la création d'un dict recette complet."""
        ingredients = [{"nom": "Test", "quantite": 1}]
        etapes = [{"description": "Step 1"}]
        
        result = recette_to_dict(
            nom="Complete Recipe",
            description="Full description",
            temps_preparation=30,
            temps_cuisson=60,
            portions=8,
            difficulte="difficile",
            type_repas="dejeuner",
            saison="hiver",
            ingredients=ingredients,
            etapes=etapes,
        )
        
        assert result["nom"] == "Complete Recipe"
        assert result["description"] == "Full description"
        assert result["temps_preparation"] == 30
        assert result["temps_cuisson"] == 60
        assert result["portions"] == 8
        assert result["difficulte"] == "difficile"
        assert result["type_repas"] == "dejeuner"
        assert result["saison"] == "hiver"
        assert result["ingredients"] == ingredients
        assert result["etapes"] == etapes
    
    def test_ingredient_to_dict(self):
        """Teste la création d'un dict ingrédient."""
        result = ingredient_to_dict("Farine", 500, "g")
        
        assert result["nom"] == "Farine"
        assert result["quantite"] == 500
        assert result["unite"] == "g"
    
    def test_ingredient_to_dict_defaults(self):
        """Teste les valeurs par défaut de l'ingrédient."""
        result = ingredient_to_dict("Pomme")
        
        assert result["nom"] == "Pomme"
        assert result["quantite"] == 1.0
        assert result["unite"] == "pcs"
    
    def test_etape_to_dict(self):
        """Teste la création d'un dict étape."""
        result = etape_to_dict("Mélanger les ingrédients", ordre=2, duree=5)
        
        assert result["description"] == "Mélanger les ingrédients"
        assert result["ordre"] == 2
        assert result["duree"] == 5
    
    def test_etape_to_dict_defaults(self):
        """Teste les valeurs par défaut de l'étape."""
        result = etape_to_dict("Step description")
        
        assert result["description"] == "Step description"
        assert result["ordre"] == 1
        assert "duree" not in result


# ═══════════════════════════════════════════════════════════
# TESTS TEMPS
# ═══════════════════════════════════════════════════════════

class TestTemps:
    """Tests pour les fonctions de temps."""
    
    def test_calculer_temps_total(self):
        """Teste le calcul du temps total."""
        assert calculer_temps_total(15, 30) == 45
        assert calculer_temps_total(0, 60) == 60
        assert calculer_temps_total(30, 0) == 30
        assert calculer_temps_total(0, 0) == 0
    
    def test_estimer_temps_robot_cookeo(self):
        """Teste l'estimation temps pour Cookeo."""
        temps_original = 100
        temps_robot = estimer_temps_robot(temps_original, "cookeo")
        
        # Cookeo réduit de 30% (0.7)
        assert temps_robot == 70
    
    def test_estimer_temps_robot_airfryer(self):
        """Teste l'estimation temps pour Airfryer."""
        temps_original = 100
        temps_robot = estimer_temps_robot(temps_original, "airfryer")
        
        # Airfryer réduit de 25% (0.75)
        assert temps_robot == 75
    
    def test_estimer_temps_robot_unknown(self):
        """Teste l'estimation temps pour robot inconnu."""
        temps_original = 100
        temps_robot = estimer_temps_robot(temps_original, "unknown_robot")
        
        # Pas de réduction
        assert temps_robot == 100
    
    def test_formater_temps_minutes(self):
        """Teste le formatage en minutes."""
        assert formater_temps(30) == "30min"
        assert formater_temps(59) == "59min"
        assert formater_temps(1) == "1min"
    
    def test_formater_temps_heures(self):
        """Teste le formatage en heures."""
        assert formater_temps(60) == "1h"
        assert formater_temps(120) == "2h"
    
    def test_formater_temps_heures_minutes(self):
        """Teste le formatage mixte heures/minutes."""
        assert formater_temps(90) == "1h 30min"
        assert formater_temps(145) == "2h 25min"


# ═══════════════════════════════════════════════════════════
# TESTS PORTIONS
# ═══════════════════════════════════════════════════════════

class TestPortions:
    """Tests pour l'ajustement des portions."""
    
    def test_ajuster_quantite_ingredient(self):
        """Teste l'ajustement simple de quantité."""
        # Double les portions
        result = ajuster_quantite_ingredient(100, 4, 8)
        assert result == 200.0
        
        # Divise par 2
        result = ajuster_quantite_ingredient(100, 4, 2)
        assert result == 50.0
    
    def test_ajuster_quantite_ingredient_same_portions(self):
        """Teste avec le même nombre de portions."""
        result = ajuster_quantite_ingredient(100, 4, 4)
        assert result == 100.0
    
    def test_ajuster_quantite_ingredient_zero_base(self):
        """Teste avec portions base à 0."""
        result = ajuster_quantite_ingredient(100, 0, 4)
        assert result == 100  # Retourne la quantité originale
    
    def test_ajuster_ingredients(self):
        """Teste l'ajustement de liste d'ingrédients."""
        ingredients = [
            {"nom": "Farine", "quantite": 500},
            {"nom": "Sucre", "quantite": 100},
        ]
        
        result = ajuster_ingredients(ingredients, 4, 8)
        
        assert len(result) == 2
        assert result[0]["quantite"] == 1000.0
        assert result[1]["quantite"] == 200.0
        assert result[0]["nom"] == "Farine"
    
    def test_ajuster_ingredients_same_portions(self):
        """Teste sans changement de portions."""
        ingredients = [{"nom": "Test", "quantite": 100}]
        
        result = ajuster_ingredients(ingredients, 4, 4)
        
        # Doit retourner la liste originale
        assert result == ingredients


# ═══════════════════════════════════════════════════════════
# TESTS FILTRES
# ═══════════════════════════════════════════════════════════

class TestFiltres:
    """Tests pour les fonctions de filtrage."""
    
    def test_filtrer_recettes_par_temps(self, sample_recettes):
        """Teste le filtrage par temps total."""
        result = filtrer_recettes_par_temps(sample_recettes, temps_max=60)
        
        # Poulet: 15+60=75 > 60 => exclu
        # Salade: 20+0=20 <= 60 => inclus
        # Boeuf: 30+180=210 > 60 => exclu
        assert len(result) == 1
        assert result[0]["nom"] == "Salade César"
    
    def test_filtrer_recettes_par_temps_all_included(self, sample_recettes):
        """Teste le filtrage avec temps très élevé."""
        result = filtrer_recettes_par_temps(sample_recettes, temps_max=300)
        assert len(result) == 3
    
    def test_filtrer_recettes_par_difficulte(self, sample_recettes):
        """Teste le filtrage par difficulté."""
        result = filtrer_recettes_par_difficulte(sample_recettes, "facile")
        assert len(result) == 2
        
        result = filtrer_recettes_par_difficulte(sample_recettes, "difficile")
        assert len(result) == 1
        assert result[0]["nom"] == "Boeuf Bourguignon"
    
    def test_filtrer_recettes_par_type(self, sample_recettes):
        """Teste le filtrage par type de repas."""
        result = filtrer_recettes_par_type(sample_recettes, "diner")
        assert len(result) == 2
        
        result = filtrer_recettes_par_type(sample_recettes, "dejeuner")
        assert len(result) == 1
        assert result[0]["nom"] == "Salade César"
    
    def test_filtrer_recettes_par_saison(self, sample_recettes):
        """Teste le filtrage par saison."""
        # Été: Salade (ete) + Poulet (toute_année)
        result = filtrer_recettes_par_saison(sample_recettes, "ete")
        assert len(result) == 2
        
        # Hiver: Boeuf (hiver) + Poulet (toute_année)
        result = filtrer_recettes_par_saison(sample_recettes, "hiver")
        assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# TESTS RECHERCHE
# ═══════════════════════════════════════════════════════════

class TestRecherche:
    """Tests pour les fonctions de recherche."""
    
    def test_rechercher_par_nom(self, sample_recettes):
        """Teste la recherche par nom."""
        result = rechercher_par_nom(sample_recettes, "poulet")
        assert len(result) == 1
        assert result[0]["nom"] == "Poulet Rôti"
    
    def test_rechercher_par_nom_case_insensitive(self, sample_recettes):
        """Teste la recherche insensible à la casse."""
        result = rechercher_par_nom(sample_recettes, "POULET")
        assert len(result) == 1
    
    def test_rechercher_par_nom_partial(self, sample_recettes):
        """Teste la recherche partielle."""
        result = rechercher_par_nom(sample_recettes, "sal")
        assert len(result) == 1
        assert result[0]["nom"] == "Salade César"
    
    def test_rechercher_par_nom_no_match(self, sample_recettes):
        """Teste la recherche sans résultat."""
        result = rechercher_par_nom(sample_recettes, "pizza")
        assert len(result) == 0
    
    def test_rechercher_par_ingredient(self, sample_recettes):
        """Teste la recherche par ingrédient."""
        result = rechercher_par_ingredient(sample_recettes, "poulet")
        assert len(result) == 1
        assert result[0]["nom"] == "Poulet Rôti"
    
    def test_rechercher_par_ingredient_case_insensitive(self, sample_recettes):
        """Teste la recherche ingrédient insensible à la casse."""
        result = rechercher_par_ingredient(sample_recettes, "VIN")
        assert len(result) == 1
        assert result[0]["nom"] == "Boeuf Bourguignon"
    
    def test_rechercher_par_ingredient_no_match(self, sample_recettes):
        """Teste la recherche ingrédient sans résultat."""
        result = rechercher_par_ingredient(sample_recettes, "chocolat")
        assert len(result) == 0


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════

class TestStatistiques:
    """Tests pour les fonctions de statistiques."""
    
    def test_calculer_stats_recettes(self, sample_recettes):
        """Teste le calcul de statistiques."""
        stats = calculer_stats_recettes(sample_recettes)
        
        assert stats["total"] == 3
        assert stats["temps_moyen_preparation"] > 0
        assert stats["temps_moyen_cuisson"] > 0
        assert stats["temps_moyen_total"] > 0
        assert "par_difficulte" in stats
        assert "par_type" in stats
        assert "par_saison" in stats
        
        # Vérifier les comptages
        assert stats["par_difficulte"]["facile"] == 2
        assert stats["par_difficulte"]["difficile"] == 1
    
    def test_calculer_stats_recettes_empty(self):
        """Teste les stats avec liste vide."""
        stats = calculer_stats_recettes([])
        
        assert stats["total"] == 0
        assert stats["temps_moyen_preparation"] == 0
        assert stats["temps_moyen_cuisson"] == 0
        assert stats["par_difficulte"] == {}
    
    def test_calculer_score_recette_no_criteres(self, sample_recettes):
        """Teste le score sans critères."""
        score = calculer_score_recette(sample_recettes[0])
        assert score == 50.0  # Score de base
    
    def test_calculer_score_recette_temps_max(self, sample_recettes):
        """Teste le score avec critère temps_max."""
        recette = sample_recettes[1]  # Salade: 20min total
        
        score = calculer_score_recette(recette, {"temps_max": 30})
        assert score > 50  # Bonus car temps < max
    
    def test_calculer_score_recette_multiple_criteres(self, sample_recettes):
        """Teste le score avec plusieurs critères."""
        recette = sample_recettes[0]  # Poulet
        
        score = calculer_score_recette(recette, {
            "temps_max": 100,
            "difficulte_preferee": "facile",
            "type_repas": "diner",
            "saison": "automne",  # toute_année match aussi
        })
        
        # Devrait avoir plusieurs bonus
        assert score > 70


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════

class TestValidation:
    """Tests pour les fonctions de validation."""
    
    def test_valider_difficulte_valid(self):
        """Teste la validation de difficulté valide."""
        assert valider_difficulte("facile") == "facile"
        assert valider_difficulte("MOYEN") == "moyen"
        assert valider_difficulte("Difficile") == "difficile"
    
    def test_valider_difficulte_invalid(self):
        """Teste la validation de difficulté invalide."""
        with pytest.raises(ValueError) as excinfo:
            valider_difficulte("extreme")
        assert "invalide" in str(excinfo.value).lower()
    
    def test_valider_type_repas_valid(self):
        """Teste la validation de type de repas valide."""
        assert valider_type_repas("diner") == "diner"
        assert valider_type_repas("DEJEUNER") == "dejeuner"
    
    def test_valider_type_repas_invalid(self):
        """Teste la validation de type de repas invalide."""
        with pytest.raises(ValueError) as excinfo:
            valider_type_repas("brunch")
        assert "invalide" in str(excinfo.value).lower()
    
    def test_valider_temps_valid(self):
        """Teste la validation de temps valide."""
        assert valider_temps(30) == 30
        assert valider_temps(0) == 0
        assert valider_temps(480) == 480
    
    def test_valider_temps_too_high(self):
        """Teste la validation de temps trop élevé."""
        result = valider_temps(1000)
        assert result == 480  # Max 8 heures
    
    def test_valider_temps_negative(self):
        """Teste la validation de temps négatif."""
        result = valider_temps(-10)
        assert result == 0  # Défaut
    
    def test_valider_temps_none(self):
        """Teste la validation de temps None."""
        result = valider_temps(None, defaut=30)
        assert result == 30
    
    def test_valider_portions_valid(self):
        """Teste la validation de portions valide."""
        assert valider_portions(4) == 4
        assert valider_portions(1) == 1
        assert valider_portions(100) == 100
    
    def test_valider_portions_too_high(self):
        """Teste la validation de portions trop élevées."""
        result = valider_portions(200)
        assert result == 100  # Max
    
    def test_valider_portions_zero_or_negative(self):
        """Teste la validation de portions <= 0."""
        result = valider_portions(0, defaut=4)
        assert result == 4
        
        result = valider_portions(-5, defaut=6)
        assert result == 6
    
    def test_valider_portions_none(self):
        """Teste la validation de portions None."""
        result = valider_portions(None, defaut=8)
        assert result == 8
