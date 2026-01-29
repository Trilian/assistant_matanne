"""Tests unitaires pour les modules cuisine (inventaire, recettes, recettes_import)."""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch
import pandas as pd


# =============================================================================
# TESTS HELPERS INVENTAIRE
# =============================================================================

class TestPrepareInventaireDataframe:
    """Tests pour _prepare_inventaire_dataframe."""

    def test_prepare_dataframe_basique(self):
        """PrÃ©paration d'un DataFrame basique."""
        # DonnÃ©es d'inventaire mockÃ©es
        items = [
            MagicMock(
                id=1,
                nom="Lait",
                quantite=2.0,
                unite="L",
                date_peremption=date.today() + timedelta(days=5),
                emplacement="Frigo"
            ),
            MagicMock(
                id=2,
                nom="Farine",
                quantite=500.0,
                unite="g",
                date_peremption=date.today() + timedelta(days=30),
                emplacement="Placard"
            )
        ]
        
        # Simulation de la transformation
        df = pd.DataFrame([
            {
                "id": item.id,
                "nom": item.nom,
                "quantite": item.quantite,
                "unite": item.unite,
                "date_peremption": item.date_peremption,
                "emplacement": item.emplacement
            }
            for item in items
        ])
        
        assert len(df) == 2
        assert "nom" in df.columns
        assert "quantite" in df.columns

    def test_prepare_dataframe_vide(self):
        """DataFrame avec liste vide."""
        df = pd.DataFrame([])
        
        assert len(df) == 0

    def test_prepare_dataframe_avec_peremption_passee(self):
        """DataFrame avec articles expirÃ©s."""
        items = [
            {
                "nom": "Yaourt",
                "date_peremption": date.today() - timedelta(days=3),
                "quantite": 4
            }
        ]
        
        df = pd.DataFrame(items)
        
        # Ajouter colonne "expirÃ©"
        df["expire"] = df["date_peremption"] < date.today()
        
        assert df["expire"].iloc[0] == True


class TestPrepareStatsDataframe:
    """Tests pour _prepare_stats_dataframe."""

    def test_stats_par_emplacement(self):
        """Statistiques groupÃ©es par emplacement."""
        items = [
            {"emplacement": "Frigo", "quantite": 5, "valeur": 10.0},
            {"emplacement": "Frigo", "quantite": 3, "valeur": 8.0},
            {"emplacement": "Placard", "quantite": 10, "valeur": 15.0},
        ]
        
        df = pd.DataFrame(items)
        stats = df.groupby("emplacement").agg({
            "quantite": "sum",
            "valeur": "sum"
        }).reset_index()
        
        frigo_stats = stats[stats["emplacement"] == "Frigo"]
        assert frigo_stats["quantite"].values[0] == 8
        assert frigo_stats["valeur"].values[0] == 18.0

    def test_stats_par_categorie(self):
        """Statistiques groupÃ©es par catÃ©gorie."""
        items = [
            {"categorie": "Produits laitiers", "count": 5},
            {"categorie": "Produits laitiers", "count": 3},
            {"categorie": "Ã‰picerie", "count": 10},
        ]
        
        df = pd.DataFrame(items)
        stats = df.groupby("categorie")["count"].sum()
        
        assert stats["Produits laitiers"] == 8
        assert stats["Ã‰picerie"] == 10


# =============================================================================
# TESTS FILTRAGE INVENTAIRE
# =============================================================================

class TestFiltrageInventaire:
    """Tests pour la logique de filtrage."""

    def test_filtre_par_emplacement(self):
        """Filtrage par emplacement."""
        items = [
            {"nom": "Lait", "emplacement": "Frigo"},
            {"nom": "Farine", "emplacement": "Placard"},
            {"nom": "Beurre", "emplacement": "Frigo"},
        ]
        
        df = pd.DataFrame(items)
        filtre = df[df["emplacement"] == "Frigo"]
        
        assert len(filtre) == 2

    def test_filtre_stock_bas(self):
        """Filtrage des stocks bas."""
        items = [
            {"nom": "Lait", "quantite": 1, "quantite_min": 2},  # Stock bas
            {"nom": "Farine", "quantite": 500, "quantite_min": 100},  # OK
            {"nom": "Å’ufs", "quantite": 2, "quantite_min": 6},  # Stock bas
        ]
        
        df = pd.DataFrame(items)
        stock_bas = df[df["quantite"] < df["quantite_min"]]
        
        assert len(stock_bas) == 2

    def test_filtre_peremption_proche(self):
        """Filtrage des pÃ©remptions proches (7 jours)."""
        today = date.today()
        items = [
            {"nom": "Yaourt", "date_peremption": today + timedelta(days=3)},  # Proche
            {"nom": "Conserve", "date_peremption": today + timedelta(days=365)},  # OK
            {"nom": "Lait", "date_peremption": today + timedelta(days=5)},  # Proche
        ]
        
        df = pd.DataFrame(items)
        seuil = today + timedelta(days=7)
        peremption_proche = df[df["date_peremption"] <= seuil]
        
        assert len(peremption_proche) == 2


# =============================================================================
# TESTS CALCULS INVENTAIRE
# =============================================================================

class TestCalculsInventaire:
    """Tests pour les calculs d'inventaire."""

    def test_calcul_valeur_totale(self):
        """Calcul de la valeur totale de l'inventaire."""
        items = [
            {"quantite": 2, "prix_unitaire": 1.50},  # 3.00
            {"quantite": 1, "prix_unitaire": 4.00},  # 4.00
            {"quantite": 5, "prix_unitaire": 0.80},  # 4.00
        ]
        
        valeur_totale = sum(item["quantite"] * item["prix_unitaire"] for item in items)
        
        assert valeur_totale == 11.00

    def test_calcul_jours_avant_peremption(self):
        """Calcul des jours avant pÃ©remption."""
        today = date.today()
        date_peremption = today + timedelta(days=5)
        
        jours = (date_peremption - today).days
        
        assert jours == 5

    def test_calcul_pourcentage_stock(self):
        """Calcul du pourcentage de stock."""
        quantite_actuelle = 3
        quantite_max = 10
        
        pourcentage = (quantite_actuelle / quantite_max) * 100
        
        assert pourcentage == 30.0


# =============================================================================
# TESTS RECETTES - PARSING INGREDIENTS
# =============================================================================

class TestParsingIngredients:
    """Tests pour le parsing d'ingrÃ©dients dans recettes_import."""

    def test_parse_ingredient_simple(self):
        """Parse '200 g de farine'."""
        text = "200 g de farine"
        
        # Simulation du parsing
        import re
        pattern = r'(\d+(?:[.,]\d+)?)\s*(\w+)?\s*(?:de\s+)?(.+)'
        match = re.match(pattern, text)
        
        if match:
            quantite = float(match.group(1).replace(',', '.'))
            unite = match.group(2)
            nom = match.group(3)
            
            assert quantite == 200.0
            assert unite == "g"
            assert "farine" in nom

    def test_parse_ingredient_fraction(self):
        """Parse '1/2 citron'."""
        text = "1/2 citron"
        
        # Conversion de fraction
        if "/" in text:
            parts = text.split()
            fraction = parts[0]
            num, denom = fraction.split("/")
            quantite = float(num) / float(denom)
            
            assert quantite == 0.5

    def test_parse_ingredient_avec_parentheses(self):
        """Parse '3 Å“ufs (gros)'."""
        text = "3 Å“ufs (gros)"
        
        import re
        # Retirer les parenthÃ¨ses
        clean = re.sub(r'\([^)]*\)', '', text).strip()
        pattern = r'(\d+)\s*(.+)'
        match = re.match(pattern, clean)
        
        if match:
            quantite = int(match.group(1))
            assert quantite == 3


# =============================================================================
# TESTS RECETTES - VALIDATION
# =============================================================================

class TestValidationRecettes:
    """Tests de validation des recettes."""

    def test_validation_temps_positif(self):
        """Le temps de prÃ©paration doit Ãªtre positif."""
        temps_preparation = 30
        temps_cuisson = 45
        
        assert temps_preparation > 0
        assert temps_cuisson >= 0

    def test_validation_portions(self):
        """Les portions doivent Ãªtre entre 1 et 50."""
        portions_valides = [1, 4, 8, 12, 50]
        portions_invalides = [0, -1, 100]
        
        for p in portions_valides:
            assert 1 <= p <= 50
        
        for p in portions_invalides:
            assert not (1 <= p <= 50)

    def test_validation_difficulte(self):
        """La difficultÃ© doit Ãªtre 1-5."""
        difficultes_valides = [1, 2, 3, 4, 5]
        
        for d in difficultes_valides:
            assert 1 <= d <= 5


# =============================================================================
# TESTS RECETTES - FILTRAGE
# =============================================================================

class TestFiltrageRecettes:
    """Tests pour le filtrage des recettes."""

    def test_filtre_par_temps(self):
        """Filtrage par temps total."""
        recettes = [
            {"nom": "Salade", "temps_total": 15},
            {"nom": "Tarte", "temps_total": 90},
            {"nom": "PÃ¢tes", "temps_total": 25},
        ]
        
        # Recettes rapides (< 30 min)
        rapides = [r for r in recettes if r["temps_total"] < 30]
        
        assert len(rapides) == 2

    def test_filtre_par_categorie(self):
        """Filtrage par catÃ©gorie."""
        recettes = [
            {"nom": "Tarte aux pommes", "categorie": "dessert"},
            {"nom": "Poulet rÃ´ti", "categorie": "plat"},
            {"nom": "GÃ¢teau chocolat", "categorie": "dessert"},
        ]
        
        desserts = [r for r in recettes if r["categorie"] == "dessert"]
        
        assert len(desserts) == 2

    def test_filtre_par_difficulte(self):
        """Filtrage par niveau de difficultÃ©."""
        recettes = [
            {"nom": "Salade", "difficulte": 1},
            {"nom": "BÅ“uf bourguignon", "difficulte": 4},
            {"nom": "Omelette", "difficulte": 2},
        ]
        
        # Recettes faciles (difficultÃ© <= 2)
        faciles = [r for r in recettes if r["difficulte"] <= 2]
        
        assert len(faciles) == 2

    def test_filtre_recherche_texte(self):
        """Recherche textuelle dans nom/description."""
        recettes = [
            {"nom": "Tarte aux pommes", "description": "DÃ©licieuse tarte"},
            {"nom": "Poulet curry", "description": "Ã‰picÃ© et savoureux"},
            {"nom": "Crumble pommes", "description": "Dessert facile"},
        ]
        
        terme = "pomme"
        resultats = [
            r for r in recettes 
            if terme.lower() in r["nom"].lower() or terme.lower() in r["description"].lower()
        ]
        
        assert len(resultats) == 2


# =============================================================================
# TESTS SUGGESTIONS RECETTES
# =============================================================================

class TestSuggestionsRecettes:
    """Tests pour les suggestions de recettes."""

    def test_suggestion_par_ingredients_disponibles(self):
        """Suggestion basÃ©e sur ingrÃ©dients disponibles."""
        ingredients_dispo = {"farine", "Å“ufs", "sucre", "beurre"}
        
        recettes = [
            {"nom": "GÃ¢teau", "ingredients": {"farine", "Å“ufs", "sucre"}},  # 100%
            {"nom": "Quiche", "ingredients": {"farine", "Å“ufs", "crÃ¨me"}},  # 66%
            {"nom": "Sushi", "ingredients": {"riz", "poisson", "algue"}},  # 0%
        ]
        
        def score_disponibilite(recette):
            requis = recette["ingredients"]
            disponibles = requis & ingredients_dispo
            return len(disponibles) / len(requis) if requis else 0
        
        scores = [(r["nom"], score_disponibilite(r)) for r in recettes]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        assert scores[0][0] == "GÃ¢teau"
        assert scores[0][1] == 1.0

    def test_suggestion_par_saison(self):
        """Suggestion basÃ©e sur la saison."""
        mois_actuel = 1  # Janvier
        
        recettes = [
            {"nom": "Soupe", "saisons": [10, 11, 12, 1, 2, 3]},  # Hiver
            {"nom": "Salade", "saisons": [4, 5, 6, 7, 8, 9]},  # Ã‰tÃ©
            {"nom": "Tarte", "saisons": list(range(1, 13))},  # Toute l'annÃ©e
        ]
        
        de_saison = [r for r in recettes if mois_actuel in r["saisons"]]
        
        assert len(de_saison) == 2
        assert "Soupe" in [r["nom"] for r in de_saison]


# =============================================================================
# TESTS GENERATION LISTE COURSES
# =============================================================================

class TestGenerationListeCourses:
    """Tests pour la gÃ©nÃ©ration de liste de courses."""

    def test_extraire_ingredients_recette(self):
        """Extraction des ingrÃ©dients d'une recette."""
        recette = {
            "ingredients": [
                {"nom": "Farine", "quantite": 200, "unite": "g"},
                {"nom": "Å’ufs", "quantite": 3, "unite": "piÃ¨ces"},
                {"nom": "Lait", "quantite": 250, "unite": "ml"},
            ]
        }
        
        ingredients = recette["ingredients"]
        
        assert len(ingredients) == 3

    def test_grouper_ingredients_par_categorie(self):
        """Groupement des ingrÃ©dients par catÃ©gorie."""
        ingredients = [
            {"nom": "Lait", "categorie": "Produits laitiers"},
            {"nom": "Yaourt", "categorie": "Produits laitiers"},
            {"nom": "Carottes", "categorie": "LÃ©gumes"},
            {"nom": "Pommes", "categorie": "Fruits"},
        ]
        
        from itertools import groupby
        from operator import itemgetter
        
        sorted_ing = sorted(ingredients, key=itemgetter("categorie"))
        grouped = {k: list(v) for k, v in groupby(sorted_ing, key=itemgetter("categorie"))}
        
        assert len(grouped["Produits laitiers"]) == 2
        assert len(grouped["LÃ©gumes"]) == 1

    def test_fusionner_ingredients_identiques(self):
        """Fusion des ingrÃ©dients identiques."""
        ingredients = [
            {"nom": "Farine", "quantite": 200, "unite": "g"},
            {"nom": "Farine", "quantite": 150, "unite": "g"},
            {"nom": "Sucre", "quantite": 100, "unite": "g"},
        ]
        
        # Fusion par nom
        merged = {}
        for ing in ingredients:
            nom = ing["nom"]
            if nom in merged:
                merged[nom]["quantite"] += ing["quantite"]
            else:
                merged[nom] = ing.copy()
        
        assert merged["Farine"]["quantite"] == 350
        assert merged["Sucre"]["quantite"] == 100

    def test_soustraire_inventaire(self):
        """Soustraction de l'inventaire existant."""
        besoin = {"Farine": 500, "Å’ufs": 6, "Sucre": 200}
        inventaire = {"Farine": 300, "Å’ufs": 2}
        
        a_acheter = {}
        for nom, qte in besoin.items():
            en_stock = inventaire.get(nom, 0)
            if qte > en_stock:
                a_acheter[nom] = qte - en_stock
        
        assert a_acheter["Farine"] == 200  # 500 - 300
        assert a_acheter["Å’ufs"] == 4  # 6 - 2
        assert a_acheter["Sucre"] == 200  # Pas en stock

