"""
Tests pour courses_logic.py - Module Cuisine
Couverture cible: 80%+
"""
import pytest
from datetime import datetime, timedelta

from src.modules.cuisine.courses.utils import (
    # Constantes
    PRIORITY_EMOJIS,
    PRIORITY_ORDER,
    RAYONS_DEFAULT,
    # Filtrage
    filtrer_par_priorite,
    filtrer_par_rayon,
    filtrer_par_recherche,
    filtrer_articles,
    # Tri
    trier_par_priorite,
    trier_par_rayon,
    trier_par_nom,
    # Groupement
    grouper_par_rayon,
    grouper_par_priorite,
    # Statistiques
    calculer_statistiques,
    calculer_statistiques_par_rayon,
    # Validation
    valider_article,
    valider_nouvel_article,
    # Formatage
    formater_article_label,
    formater_liste_impression,
    # Suggestions
    generer_suggestions_depuis_stock_bas,
    generer_suggestions_depuis_recettes,
    deduper_suggestions,
    # Historique
    analyser_historique,
    generer_modele_depuis_historique,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def articles_sample():
    """Liste d'articles de test."""
    return [
        {
            "id": 1,
            "ingredient_nom": "Tomates",
            "priorite": "haute",
            "rayon_magasin": "Fruits & Légumes",
            "notes": "Bio de préférence",
            "suggere_par_ia": False,
        },
        {
            "id": 2,
            "ingredient_nom": "Lait",
            "priorite": "moyenne",
            "rayon_magasin": "Laitier",
            "notes": "",
            "suggere_par_ia": True,
        },
        {
            "id": 3,
            "ingredient_nom": "Pain",
            "priorite": "basse",
            "rayon_magasin": "Boulangerie",
            "notes": "Complet",
            "suggere_par_ia": False,
        },
        {
            "id": 4,
            "ingredient_nom": "Carottes",
            "priorite": "haute",
            "rayon_magasin": "Fruits & Légumes",
            "notes": "",
            "suggere_par_ia": True,
        },
        {
            "id": 5,
            "ingredient_nom": "Yaourt",
            "priorite": "moyenne",
            "rayon_magasin": "Laitier",
            "notes": "Pour Jules",
            "suggere_par_ia": False,
        },
    ]


@pytest.fixture
def articles_vides():
    """Liste vide."""
    return []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestConstantes:
    """Tests des constantes du module."""

    def test_priority_emojis_structure(self):
        """Vérifie que PRIORITY_EMOJIS a les bonnes clés."""
        assert "haute" in PRIORITY_EMOJIS
        assert "moyenne" in PRIORITY_EMOJIS
        assert "basse" in PRIORITY_EMOJIS

    def test_priority_order_values(self):
        """Vérifie l'ordre des priorités (haute = 0, basse = 2)."""
        assert PRIORITY_ORDER["haute"] < PRIORITY_ORDER["moyenne"]
        assert PRIORITY_ORDER["moyenne"] < PRIORITY_ORDER["basse"]

    def test_rayons_default_non_vide(self):
        """Vérifie que RAYONS_DEFAULT n'est pas vide."""
        assert len(RAYONS_DEFAULT) > 0
        assert "Fruits & Légumes" in RAYONS_DEFAULT
        assert "Laitier" in RAYONS_DEFAULT


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FILTRAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFiltrage:
    """Tests des fonctions de filtrage."""

    def test_filtrer_par_priorite_haute(self, articles_sample):
        """Filtre par priorité haute."""
        result = filtrer_par_priorite(articles_sample, "haute")
        assert len(result) == 2
        assert all(a["priorite"] == "haute" for a in result)

    def test_filtrer_par_priorite_moyenne(self, articles_sample):
        """Filtre par priorité moyenne."""
        result = filtrer_par_priorite(articles_sample, "moyenne")
        assert len(result) == 2
        assert all(a["priorite"] == "moyenne" for a in result)

    def test_filtrer_par_priorite_toutes(self, articles_sample):
        """'toutes' retourne tous les articles."""
        result = filtrer_par_priorite(articles_sample, "toutes")
        assert len(result) == len(articles_sample)

    def test_filtrer_par_priorite_none(self, articles_sample):
        """None retourne tous les articles."""
        result = filtrer_par_priorite(articles_sample, None)
        assert len(result) == len(articles_sample)

    def test_filtrer_par_priorite_liste_vide(self, articles_vides):
        """Liste vide retourne liste vide."""
        result = filtrer_par_priorite(articles_vides, "haute")
        assert result == []

    def test_filtrer_par_rayon(self, articles_sample):
        """Filtre par rayon."""
        result = filtrer_par_rayon(articles_sample, "Laitier")
        assert len(result) == 2
        assert all(a["rayon_magasin"] == "Laitier" for a in result)

    def test_filtrer_par_rayon_tous(self, articles_sample):
        """'tous les rayons' retourne tous les articles."""
        result = filtrer_par_rayon(articles_sample, "tous les rayons")
        assert len(result) == len(articles_sample)

    def test_filtrer_par_rayon_none(self, articles_sample):
        """None retourne tous les articles."""
        result = filtrer_par_rayon(articles_sample, None)
        assert len(result) == len(articles_sample)

    def test_filtrer_par_recherche_nom(self, articles_sample):
        """Recherche par nom d'ingrédient."""
        result = filtrer_par_recherche(articles_sample, "tomate")
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Tomates"

    def test_filtrer_par_recherche_notes(self, articles_sample):
        """Recherche dans les notes."""
        result = filtrer_par_recherche(articles_sample, "jules")
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Yaourt"

    def test_filtrer_par_recherche_case_insensitive(self, articles_sample):
        """Recherche insensible Ã  la casse."""
        result = filtrer_par_recherche(articles_sample, "PAIN")
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Pain"

    def test_filtrer_par_recherche_vide(self, articles_sample):
        """Recherche vide retourne tous les articles."""
        result = filtrer_par_recherche(articles_sample, "")
        assert len(result) == len(articles_sample)

    def test_filtrer_articles_combinaison(self, articles_sample):
        """Combinaison de plusieurs filtres."""
        result = filtrer_articles(
            articles_sample,
            priorite="haute",
            rayon="Fruits & Légumes"
        )
        assert len(result) == 2
        assert all(a["priorite"] == "haute" for a in result)
        assert all(a["rayon_magasin"] == "Fruits & Légumes" for a in result)

    def test_filtrer_articles_avec_recherche(self, articles_sample):
        """Filtres avec recherche."""
        result = filtrer_articles(
            articles_sample,
            recherche="carotte"
        )
        assert len(result) == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS TRI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestTri:
    """Tests des fonctions de tri."""

    def test_trier_par_priorite_ordre(self, articles_sample):
        """Tri par priorité (haute en premier)."""
        result = trier_par_priorite(articles_sample)
        # Les premiers doivent être de priorité haute
        assert result[0]["priorite"] == "haute"
        assert result[-1]["priorite"] == "basse"

    def test_trier_par_priorite_reverse(self, articles_sample):
        """Tri par priorité inversé (basse en premier)."""
        result = trier_par_priorite(articles_sample, reverse=True)
        assert result[0]["priorite"] == "basse"
        assert result[-1]["priorite"] == "haute"

    def test_trier_par_rayon(self, articles_sample):
        """Tri par rayon alphabétique."""
        result = trier_par_rayon(articles_sample)
        rayons = [a["rayon_magasin"] for a in result]
        assert rayons == sorted(rayons)

    def test_trier_par_nom(self, articles_sample):
        """Tri par nom alphabétique."""
        result = trier_par_nom(articles_sample)
        noms = [a["ingredient_nom"].lower() for a in result]
        assert noms == sorted(noms)

    def test_trier_liste_vide(self, articles_vides):
        """Tri d'une liste vide."""
        assert trier_par_priorite(articles_vides) == []
        assert trier_par_rayon(articles_vides) == []
        assert trier_par_nom(articles_vides) == []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GROUPEMENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGroupement:
    """Tests des fonctions de groupement."""

    def test_grouper_par_rayon(self, articles_sample):
        """Groupement par rayon."""
        result = grouper_par_rayon(articles_sample)
        assert "Fruits & Légumes" in result
        assert "Laitier" in result
        assert "Boulangerie" in result
        assert len(result["Fruits & Légumes"]) == 2
        assert len(result["Laitier"]) == 2
        assert len(result["Boulangerie"]) == 1

    def test_grouper_par_rayon_autre(self):
        """Articles sans rayon vont dans 'Autre'."""
        articles = [{"ingredient_nom": "Mystère"}]
        result = grouper_par_rayon(articles)
        assert "Autre" in result
        assert len(result["Autre"]) == 1

    def test_grouper_par_priorite(self, articles_sample):
        """Groupement par priorité."""
        result = grouper_par_priorite(articles_sample)
        assert len(result["haute"]) == 2
        assert len(result["moyenne"]) == 2
        assert len(result["basse"]) == 1

    def test_grouper_par_priorite_inconnue(self):
        """Priorité inconnue va dans 'moyenne'."""
        articles = [{"ingredient_nom": "Test", "priorite": "inconnue"}]
        result = grouper_par_priorite(articles)
        assert len(result["moyenne"]) == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS STATISTIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestStatistiques:
    """Tests des fonctions de statistiques."""

    def test_calculer_statistiques(self, articles_sample):
        """Statistiques complètes."""
        result = calculer_statistiques(articles_sample)
        
        assert result["total_a_acheter"] == 5
        assert result["total_achetes"] == 0
        assert result["haute_priorite"] == 2
        assert result["moyenne_priorite"] == 2
        assert result["basse_priorite"] == 1
        assert result["suggestions_ia"] == 2
        assert result["rayons_uniques"] == 3

    def test_calculer_statistiques_avec_achetes(self, articles_sample):
        """Statistiques avec articles achetés."""
        achetes = [{"id": 1}]
        result = calculer_statistiques(articles_sample, achetes)
        
        assert result["total_achetes"] == 1
        assert result["taux_completion"] > 0

    def test_calculer_statistiques_liste_vide(self, articles_vides):
        """Statistiques liste vide."""
        result = calculer_statistiques(articles_vides)
        assert result["total_a_acheter"] == 0
        assert result["taux_completion"] == 0

    def test_calculer_statistiques_par_rayon(self, articles_sample):
        """Statistiques par rayon."""
        result = calculer_statistiques_par_rayon(articles_sample)
        
        assert "Fruits & Légumes" in result
        assert result["Fruits & Légumes"]["count"] == 2
        assert result["Laitier"]["count"] == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestValidation:
    """Tests de validation d'articles."""

    def test_valider_article_valide(self):
        """Article valide."""
        article = {
            "ingredient_nom": "Tomates",
            "quantite_necessaire": 4,
            "priorite": "haute"
        }
        valide, erreurs = valider_article(article)
        assert valide is True
        assert len(erreurs) == 0

    def test_valider_article_nom_manquant(self):
        """Nom manquant."""
        article = {"quantite": 4}
        valide, erreurs = valider_article(article)
        assert valide is False
        assert len(erreurs) > 0
        assert any("nom" in e.lower() for e in erreurs)

    def test_valider_article_nom_trop_court(self):
        """Nom trop court."""
        article = {"ingredient_nom": "A"}
        valide, erreurs = valider_article(article)
        assert valide is False
        assert any("2 caractères" in e for e in erreurs)
    def test_valider_article_priorite_invalide(self):
        """Priorité invalide."""
        article = {
            "ingredient_nom": "Tomates",
            "quantite_necessaire": 4,
            "priorite": "invalide"
        }
        valide, erreurs = valider_article(article)
        assert valide is False
        assert any("Priorité invalide" in e for e in erreurs)

    def test_valider_article_quantite_zero(self):
        """Quantité zéro invalide."""
        article = {
            "ingredient_nom": "Tomates",
            "quantite_necessaire": 0
        }
        valide, erreurs = valider_article(article)
        assert valide is False
        assert any("quantité" in e.lower() for e in erreurs)


class TestValiderNouvelArticle:
    """Tests pour valider_nouvel_article."""

    def test_nouvel_article_valide(self):
        """Création d'un nouvel article valide."""
        valide, result = valider_nouvel_article(
            nom="Tomates",
            quantite=4,
            unite="kg",
            priorite="haute",
            rayon="Fruits & Légumes"
        )
        assert valide is True
        assert isinstance(result, dict)
        assert result["ingredient_nom"] == "Tomates"
        assert result["quantite_necessaire"] == 4
        assert result["achete"] is False

    def test_nouvel_article_invalide(self):
        """Article avec nom invalide."""
        valide, erreurs = valider_nouvel_article(
            nom="",
            quantite=4,
            unite="kg"
        )
        assert valide is False
        assert isinstance(erreurs, list)
        assert len(erreurs) > 0


class TestFormatage:
    """Tests pour les fonctions de formatage."""

    def test_formater_article_label_simple(self):
        """Label simple."""
        article = {
            "ingredient_nom": "Tomates",
            "quantite_necessaire": 4,
            "unite": "kg",
            "priorite": "haute"
        }
        label = formater_article_label(article)
        assert "ðŸ”´" in label
        assert "Tomates" in label
        assert "4" in label
        assert "kg" in label

    def test_formater_article_label_avec_notes(self):
        """Label avec notes."""
        article = {
            "ingredient_nom": "Tomates",
            "quantite_necessaire": 4,
            "unite": "kg",
            "priorite": "moyenne",
            "notes": "Bio préféré"
        }
        label = formater_article_label(article)
        assert "Bio préféré" in label

    def test_formater_article_label_suggestion_ia(self):
        """Label avec suggestion IA."""
        article = {
            "ingredient_nom": "Tomates",
            "quantite_necessaire": 4,
            "unite": "kg",
            "priorite": "basse",
            "suggere_par_ia": True
        }
        label = formater_article_label(article)
        assert "ðŸŸ¢" in label
        assert "SPARKLE" in label

    def test_formater_liste_impression(self, articles_sample):
        """Test du formatage pour impression."""
        texte = formater_liste_impression(articles_sample)
        assert "LISTE DE COURSES" in texte
        assert "Total:" in texte
        assert "Date:" in texte
        # Vérifie que les rayons sont présents
        assert "FRUITS & LÃ‰GUMES" in texte


class TestSuggestions:
    """Tests pour les fonctions de suggestions."""

    def test_suggestions_depuis_stock_critique(self):
        """Suggestions depuis alertes critiques."""
        alertes = {
            "critique": [
                {
                    "ingredient_nom": "Lait",
                    "quantite": 0,
                    "seuil_alerte": 2,
                    "unite": "L",
                    "rayon": "Laitier"
                }
            ],
            "stock_bas": []
        }
        suggestions = generer_suggestions_depuis_stock_bas(alertes)
        assert len(suggestions) == 1
        assert suggestions[0]["priorite"] == "haute"
        assert suggestions[0]["quantite_necessaire"] == 2

    def test_suggestions_depuis_stock_bas(self):
        """Suggestions depuis stock bas."""
        alertes = {
            "critique": [],
            "stock_bas": [
                {
                    "ingredient_nom": "Beurre",
                    "quantite": 1,
                    "seuil_alerte": 3,
                    "unite": "pièces",
                    "rayon": "Laitier"
                }
            ]
        }
        suggestions = generer_suggestions_depuis_stock_bas(alertes)
        assert len(suggestions) == 1
        assert suggestions[0]["priorite"] == "moyenne"
        assert suggestions[0]["quantite_necessaire"] == 2

    def test_suggestions_depuis_recettes(self):
        """Suggestions depuis recettes sélectionnées."""
        recettes = [
            {
                "nom": "Tarte aux pommes",
                "ingredients": [
                    {"nom": "Pommes", "quantite": 5, "unite": "pièces", "categorie": "Fruits & Légumes"},
                    {"nom": "Farine", "quantite": 200, "unite": "g", "categorie": "Ã‰picerie"}
                ]
            }
        ]
        inventaire = [
            {"ingredient_nom": "pommes", "quantite": 2}
        ]
        suggestions = generer_suggestions_depuis_recettes(recettes, inventaire)
        assert len(suggestions) == 2
        # Pommes: 5 requis - 2 en stock = 3 manquant
        pommes_suggestion = next((s for s in suggestions if s["ingredient_nom"] == "Pommes"), None)
        assert pommes_suggestion is not None
        assert pommes_suggestion["quantite_necessaire"] == 3
        assert pommes_suggestion["suggere_par_ia"] is True

    def test_deduper_suggestions_cumul_quantites(self):
        """Déduplique et cumule les quantités."""
        suggestions = [
            {"ingredient_nom": "Tomates", "quantite_necessaire": 2, "priorite": "moyenne"},
            {"ingredient_nom": "Tomates", "quantite_necessaire": 3, "priorite": "basse"},
        ]
        result = deduper_suggestions(suggestions)
        assert len(result) == 1
        assert result[0]["quantite_necessaire"] == 5

    def test_deduper_suggestions_garde_haute_priorite(self):
        """Garde la plus haute priorité."""
        suggestions = [
            {"ingredient_nom": "Lait", "quantite_necessaire": 1, "priorite": "basse"},
            {"ingredient_nom": "Lait", "quantite_necessaire": 1, "priorite": "haute"},
        ]
        result = deduper_suggestions(suggestions)
        assert len(result) == 1
        assert result[0]["priorite"] == "haute"


class TestHistorique:
    """Tests pour les fonctions d'historique."""

    def test_analyser_historique_basic(self):
        """Analyse basique d'historique."""
        now = datetime.now()
        historique = [
            {"ingredient_nom": "Tomates", "achete_le": now - timedelta(days=5), "quantite_necessaire": 4},
            {"ingredient_nom": "Tomates", "achete_le": now - timedelta(days=10), "quantite_necessaire": 3},
            {"ingredient_nom": "Tomates", "achete_le": now - timedelta(days=15), "quantite_necessaire": 5},
            {"ingredient_nom": "Lait", "achete_le": now - timedelta(days=7), "quantite_necessaire": 2},
        ]
        analyse = analyser_historique(historique, jours=30)
        assert analyse["total_achats"] == 4
        assert analyse["articles_uniques"] == 2
        assert len(analyse["recurrents"]) == 1  # Tomates avec 3 achats
        assert analyse["recurrents"][0]["ingredient_nom"] == "tomates"
        assert analyse["recurrents"][0]["frequence"] == 3

    def test_analyser_historique_filtre_date(self):
        """Filtre par date limite."""
        now = datetime.now()
        historique = [
            {"ingredient_nom": "Tomates", "achete_le": now - timedelta(days=5), "quantite_necessaire": 4},
            {"ingredient_nom": "Vieux", "achete_le": now - timedelta(days=60), "quantite_necessaire": 1},
        ]
        analyse = analyser_historique(historique, jours=30)
        assert analyse["total_achats"] == 1
        assert analyse["articles_uniques"] == 1

    def test_generer_modele_depuis_historique(self):
        """Génère modèle depuis analyse."""
        analyse = {
            "recurrents": [
                {"ingredient_nom": "Tomates", "frequence": 5, "quantite_moyenne": 4.5, "rayon": "Fruits & Légumes"},
                {"ingredient_nom": "Lait", "frequence": 2, "quantite_moyenne": 2.0, "rayon": "Laitier"},
            ]
        }
        modele = generer_modele_depuis_historique(analyse, seuil_frequence=3)
        assert len(modele) == 1  # Seulement Tomates (freq 5 >= 3)
        assert modele[0]["ingredient_nom"] == "Tomates"
        assert modele[0]["quantite_necessaire"] == 4  # arrondi de 4.5
        assert modele[0]["source"] == "modele_historique"