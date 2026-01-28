"""
Tests unitaires pour courses_logic.py
Module de logique métier séparé de l'UI
"""

import pytest
from datetime import datetime, date, timedelta

from src.modules.cuisine.courses_logic import (
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


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def sample_articles():
    """Retourne une liste d'articles de test"""
    return [
        {
            "ingredient_nom": "Pommes",
            "quantite_necessaire": 5,
            "unite": "kg",
            "priorite": "haute",
            "rayon_magasin": "Fruits & Légumes",
            "notes": "Bio de préférence",
            "suggere_par_ia": True,
        },
        {
            "ingredient_nom": "Lait",
            "quantite_necessaire": 2,
            "unite": "L",
            "priorite": "moyenne",
            "rayon_magasin": "Laitier",
            "notes": "",
            "suggere_par_ia": False,
        },
        {
            "ingredient_nom": "Pain",
            "quantite_necessaire": 1,
            "unite": "pièce",
            "priorite": "haute",
            "rayon_magasin": "Boulangerie",
            "notes": "",
            "suggere_par_ia": False,
        },
        {
            "ingredient_nom": "Sel",
            "quantite_necessaire": 1,
            "unite": "kg",
            "priorite": "basse",
            "rayon_magasin": "Épices",
            "notes": "",
            "suggere_par_ia": False,
        },
    ]


@pytest.fixture
def sample_articles_achetes():
    """Retourne une liste d'articles achetés"""
    return [
        {"ingredient_nom": "Beurre", "achete": True},
        {"ingredient_nom": "Oeufs", "achete": True},
    ]


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════

class TestConstantes:
    """Tests pour les constantes du module"""
    
    def test_priority_emojis_has_all_levels(self):
        """Vérifie que tous les niveaux de priorité ont un emoji"""
        assert "haute" in PRIORITY_EMOJIS
        assert "moyenne" in PRIORITY_EMOJIS
        assert "basse" in PRIORITY_EMOJIS
    
    def test_priority_order_is_correct(self):
        """Vérifie l'ordre des priorités"""
        assert PRIORITY_ORDER["haute"] < PRIORITY_ORDER["moyenne"]
        assert PRIORITY_ORDER["moyenne"] < PRIORITY_ORDER["basse"]
    
    def test_rayons_default_is_not_empty(self):
        """Vérifie que la liste des rayons n'est pas vide"""
        assert len(RAYONS_DEFAULT) > 0
        assert "Fruits & Légumes" in RAYONS_DEFAULT
        assert "Autre" in RAYONS_DEFAULT


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE
# ═══════════════════════════════════════════════════════════

class TestFiltrage:
    """Tests pour les fonctions de filtrage"""
    
    def test_filtrer_par_priorite_haute(self, sample_articles):
        """Filtre les articles haute priorité"""
        result = filtrer_par_priorite(sample_articles, "haute")
        assert len(result) == 2
        assert all(a["priorite"] == "haute" for a in result)
    
    def test_filtrer_par_priorite_moyenne(self, sample_articles):
        """Filtre les articles moyenne priorité"""
        result = filtrer_par_priorite(sample_articles, "moyenne")
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Lait"
    
    def test_filtrer_par_priorite_toutes(self, sample_articles):
        """Retourne tous les articles si priorité 'toutes'"""
        result = filtrer_par_priorite(sample_articles, "toutes")
        assert len(result) == len(sample_articles)
    
    def test_filtrer_par_priorite_none(self, sample_articles):
        """Retourne tous les articles si priorité None"""
        result = filtrer_par_priorite(sample_articles, None)
        assert len(result) == len(sample_articles)
    
    def test_filtrer_par_rayon(self, sample_articles):
        """Filtre les articles par rayon"""
        result = filtrer_par_rayon(sample_articles, "Laitier")
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Lait"
    
    def test_filtrer_par_rayon_tous(self, sample_articles):
        """Retourne tous les articles si rayon 'tous les rayons'"""
        result = filtrer_par_rayon(sample_articles, "tous les rayons")
        assert len(result) == len(sample_articles)
    
    def test_filtrer_par_recherche_nom(self, sample_articles):
        """Filtre par recherche sur le nom"""
        result = filtrer_par_recherche(sample_articles, "pom")
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Pommes"
    
    def test_filtrer_par_recherche_notes(self, sample_articles):
        """Filtre par recherche dans les notes"""
        result = filtrer_par_recherche(sample_articles, "bio")
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Pommes"
    
    def test_filtrer_par_recherche_insensible_casse(self, sample_articles):
        """Recherche insensible à la casse"""
        result = filtrer_par_recherche(sample_articles, "POMMES")
        assert len(result) == 1
    
    def test_filtrer_par_recherche_vide(self, sample_articles):
        """Retourne tout si recherche vide"""
        result = filtrer_par_recherche(sample_articles, "")
        assert len(result) == len(sample_articles)
    
    def test_filtrer_articles_combinaison(self, sample_articles):
        """Test filtrage combiné"""
        result = filtrer_articles(
            sample_articles,
            priorite="haute",
            rayon="Fruits & Légumes"
        )
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Pommes"


# ═══════════════════════════════════════════════════════════
# TESTS TRI
# ═══════════════════════════════════════════════════════════

class TestTri:
    """Tests pour les fonctions de tri"""
    
    def test_trier_par_priorite(self, sample_articles):
        """Trie par priorité (haute en premier)"""
        result = trier_par_priorite(sample_articles)
        assert result[0]["priorite"] == "haute"
        assert result[-1]["priorite"] == "basse"
    
    def test_trier_par_priorite_reverse(self, sample_articles):
        """Trie par priorité inversé"""
        result = trier_par_priorite(sample_articles, reverse=True)
        assert result[0]["priorite"] == "basse"
        assert result[-1]["priorite"] == "haute"
    
    def test_trier_par_rayon(self, sample_articles):
        """Trie par rayon alphabétique"""
        result = trier_par_rayon(sample_articles)
        rayons = [a["rayon_magasin"] for a in result]
        assert rayons == sorted(rayons)
    
    def test_trier_par_nom(self, sample_articles):
        """Trie par nom alphabétique"""
        result = trier_par_nom(sample_articles)
        noms = [a["ingredient_nom"].lower() for a in result]
        assert noms == sorted(noms)


# ═══════════════════════════════════════════════════════════
# TESTS GROUPEMENT
# ═══════════════════════════════════════════════════════════

class TestGroupement:
    """Tests pour les fonctions de groupement"""
    
    def test_grouper_par_rayon(self, sample_articles):
        """Groupe les articles par rayon"""
        result = grouper_par_rayon(sample_articles)
        assert "Fruits & Légumes" in result
        assert "Laitier" in result
        assert len(result["Fruits & Légumes"]) == 1
    
    def test_grouper_par_rayon_article_sans_rayon(self):
        """Article sans rayon va dans 'Autre'"""
        articles = [{"ingredient_nom": "Test"}]
        result = grouper_par_rayon(articles)
        assert "Autre" in result
    
    def test_grouper_par_priorite(self, sample_articles):
        """Groupe les articles par priorité"""
        result = grouper_par_priorite(sample_articles)
        assert "haute" in result
        assert "moyenne" in result
        assert "basse" in result
        assert len(result["haute"]) == 2
        assert len(result["moyenne"]) == 1
        assert len(result["basse"]) == 1
    
    def test_grouper_par_priorite_invalide(self):
        """Priorité invalide va dans 'moyenne'"""
        articles = [{"ingredient_nom": "Test", "priorite": "invalide"}]
        result = grouper_par_priorite(articles)
        assert len(result["moyenne"]) == 1


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════

class TestStatistiques:
    """Tests pour les fonctions de statistiques"""
    
    def test_calculer_statistiques(self, sample_articles, sample_articles_achetes):
        """Calcule les statistiques de base"""
        result = calculer_statistiques(sample_articles, sample_articles_achetes)
        
        assert result["total_a_acheter"] == 4
        assert result["total_achetes"] == 2
        assert result["haute_priorite"] == 2
        assert result["moyenne_priorite"] == 1
        assert result["basse_priorite"] == 1
        assert result["suggestions_ia"] == 1
        assert result["rayons_uniques"] == 4
    
    def test_calculer_statistiques_taux_completion(self, sample_articles, sample_articles_achetes):
        """Calcule le taux de complétion"""
        result = calculer_statistiques(sample_articles, sample_articles_achetes)
        expected_taux = 2 / 6 * 100  # 2 achetés sur 6 total
        assert abs(result["taux_completion"] - expected_taux) < 0.01
    
    def test_calculer_statistiques_liste_vide(self):
        """Statistiques avec liste vide"""
        result = calculer_statistiques([], [])
        assert result["total_a_acheter"] == 0
        assert result["taux_completion"] == 0
    
    def test_calculer_statistiques_par_rayon(self, sample_articles):
        """Statistiques par rayon"""
        result = calculer_statistiques_par_rayon(sample_articles)
        
        assert "Fruits & Légumes" in result
        assert result["Fruits & Légumes"]["count"] == 1
        assert result["Fruits & Légumes"]["haute_priorite"] == 1
        assert result["Fruits & Légumes"]["suggestions_ia"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════

class TestValidation:
    """Tests pour les fonctions de validation"""
    
    def test_valider_article_valide(self):
        """Article valide"""
        article = {
            "ingredient_nom": "Pommes",
            "quantite_necessaire": 5,
            "priorite": "haute"
        }
        est_valide, erreurs = valider_article(article)
        assert est_valide
        assert len(erreurs) == 0
    
    def test_valider_article_nom_manquant(self):
        """Article sans nom"""
        article = {"quantite_necessaire": 5}
        est_valide, erreurs = valider_article(article)
        assert not est_valide
        assert any("nom" in e.lower() for e in erreurs)
    
    def test_valider_article_nom_trop_court(self):
        """Nom trop court"""
        article = {"ingredient_nom": "X", "quantite_necessaire": 5}
        est_valide, erreurs = valider_article(article)
        assert not est_valide
        assert any("2 caractères" in e for e in erreurs)
    
    def test_valider_article_quantite_negative(self):
        """Quantité négative"""
        article = {"ingredient_nom": "Test", "quantite_necessaire": -1}
        est_valide, erreurs = valider_article(article)
        assert not est_valide
        assert any("quantité" in e.lower() for e in erreurs)
    
    def test_valider_article_priorite_invalide(self):
        """Priorité invalide"""
        article = {"ingredient_nom": "Test", "quantite_necessaire": 1, "priorite": "invalide"}
        est_valide, erreurs = valider_article(article)
        assert not est_valide
        assert any("priorité" in e.lower() for e in erreurs)
    
    def test_valider_nouvel_article_valide(self):
        """Création d'article valide"""
        est_valide, result = valider_nouvel_article(
            nom="Pommes",
            quantite=5,
            unite="kg",
            priorite="haute",
            rayon="Fruits & Légumes"
        )
        assert est_valide
        assert result["ingredient_nom"] == "Pommes"
        assert result["achete"] is False
        assert "date_ajout" in result
    
    def test_valider_nouvel_article_invalide(self):
        """Création d'article invalide"""
        est_valide, result = valider_nouvel_article(
            nom="",
            quantite=-1,
            unite="kg"
        )
        assert not est_valide
        assert isinstance(result, list)
        assert len(result) > 0


# ═══════════════════════════════════════════════════════════
# TESTS FORMATAGE
# ═══════════════════════════════════════════════════════════

class TestFormatage:
    """Tests pour les fonctions de formatage"""
    
    def test_formater_article_label_basique(self):
        """Label basique"""
        article = {
            "ingredient_nom": "Pommes",
            "quantite_necessaire": 5,
            "unite": "kg",
            "priorite": "haute"
        }
        label = formater_article_label(article)
        assert "🔴" in label  # emoji haute priorité
        assert "Pommes" in label
        assert "5" in label
        assert "kg" in label
    
    def test_formater_article_label_avec_notes(self):
        """Label avec notes"""
        article = {
            "ingredient_nom": "Pommes",
            "quantite_necessaire": 5,
            "unite": "kg",
            "priorite": "moyenne",
            "notes": "Bio"
        }
        label = formater_article_label(article)
        assert "📝" in label
        assert "Bio" in label
    
    def test_formater_article_label_suggestion_ia(self):
        """Label pour suggestion IA"""
        article = {
            "ingredient_nom": "Pommes",
            "quantite_necessaire": 5,
            "unite": "kg",
            "priorite": "moyenne",
            "suggere_par_ia": True
        }
        label = formater_article_label(article)
        assert "✨" in label
    
    def test_formater_liste_impression(self, sample_articles):
        """Formatage pour impression"""
        result = formater_liste_impression(sample_articles)
        
        assert "LISTE DE COURSES" in result
        assert "Total:" in result
        assert "4 articles" in result
        # Vérifie les rayons
        assert "FRUITS & LÉGUMES" in result
        assert "LAITIER" in result


# ═══════════════════════════════════════════════════════════
# TESTS SUGGESTIONS
# ═══════════════════════════════════════════════════════════

class TestSuggestions:
    """Tests pour les fonctions de suggestion"""
    
    def test_generer_suggestions_stock_bas(self):
        """Génère suggestions depuis alertes stock"""
        alertes = {
            "critique": [
                {"ingredient_nom": "Lait", "seuil_alerte": 5, "quantite": 1, "unite": "L", "rayon": "Laitier"}
            ],
            "stock_bas": [
                {"ingredient_nom": "Pain", "seuil_alerte": 3, "quantite": 2, "unite": "pièce", "rayon": "Boulangerie"}
            ]
        }
        
        suggestions = generer_suggestions_depuis_stock_bas(alertes)
        
        assert len(suggestions) == 2
        
        # Critique = haute priorité
        critique = [s for s in suggestions if s["ingredient_nom"] == "Lait"][0]
        assert critique["priorite"] == "haute"
        assert critique["quantite_necessaire"] == 4  # 5 - 1
        
        # Stock bas = moyenne priorité
        bas = [s for s in suggestions if s["ingredient_nom"] == "Pain"][0]
        assert bas["priorite"] == "moyenne"
    
    def test_generer_suggestions_recettes(self):
        """Génère suggestions depuis recettes"""
        recettes = [
            {
                "nom": "Tarte aux pommes",
                "ingredients": [
                    {"nom": "Pommes", "quantite": 5, "unite": "pièce", "categorie": "Fruits & Légumes"},
                    {"nom": "Sucre", "quantite": 100, "unite": "g", "categorie": "Épicerie"},
                ]
            }
        ]
        
        inventaire = [
            {"ingredient_nom": "Pommes", "quantite": 2},
            {"ingredient_nom": "Sucre", "quantite": 200},
        ]
        
        suggestions = generer_suggestions_depuis_recettes(recettes, inventaire)
        
        # Pommes manquantes (besoin 5, a 2)
        assert len(suggestions) == 1
        assert suggestions[0]["ingredient_nom"] == "Pommes"
        assert suggestions[0]["quantite_necessaire"] == 3
    
    def test_deduper_suggestions(self):
        """Déduplique les suggestions"""
        suggestions = [
            {"ingredient_nom": "Pommes", "quantite_necessaire": 3, "priorite": "moyenne"},
            {"ingredient_nom": "Pommes", "quantite_necessaire": 2, "priorite": "haute"},
            {"ingredient_nom": "Lait", "quantite_necessaire": 1, "priorite": "basse"},
        ]
        
        result = deduper_suggestions(suggestions)
        
        assert len(result) == 2
        
        # Pommes garde la haute priorité avec quantité cumulée
        pommes = [s for s in result if s["ingredient_nom"] == "Pommes"][0]
        assert pommes["priorite"] == "haute"
        assert pommes["quantite_necessaire"] == 5  # 3 + 2


# ═══════════════════════════════════════════════════════════
# TESTS HISTORIQUE
# ═══════════════════════════════════════════════════════════

class TestHistorique:
    """Tests pour les fonctions d'historique"""
    
    def test_analyser_historique(self):
        """Analyse l'historique d'achats"""
        maintenant = datetime.now()
        historique = [
            {"ingredient_nom": "Lait", "achete_le": maintenant - timedelta(days=5), 
             "quantite_necessaire": 2, "rayon_magasin": "Laitier"},
            {"ingredient_nom": "Lait", "achete_le": maintenant - timedelta(days=15),
             "quantite_necessaire": 2, "rayon_magasin": "Laitier"},
            {"ingredient_nom": "Lait", "achete_le": maintenant - timedelta(days=25),
             "quantite_necessaire": 1, "rayon_magasin": "Laitier"},
            {"ingredient_nom": "Pain", "achete_le": maintenant - timedelta(days=3),
             "quantite_necessaire": 1, "rayon_magasin": "Boulangerie"},
        ]
        
        analyse = analyser_historique(historique, jours=30)
        
        assert analyse["total_achats"] == 4
        assert analyse["articles_uniques"] == 2
        assert len(analyse["recurrents"]) == 1  # Lait acheté 3 fois
        assert analyse["recurrents"][0]["ingredient_nom"] == "lait"
        assert analyse["recurrents"][0]["frequence"] == 3
    
    def test_analyser_historique_filtre_date(self):
        """L'analyse filtre par date"""
        maintenant = datetime.now()
        historique = [
            {"ingredient_nom": "Vieux", "achete_le": maintenant - timedelta(days=60),
             "quantite_necessaire": 1, "rayon_magasin": "Autre"},
        ]
        
        analyse = analyser_historique(historique, jours=30)
        assert analyse["total_achats"] == 0
    
    def test_generer_modele_historique(self):
        """Génère un modèle depuis l'historique"""
        analyse = {
            "recurrents": [
                {"ingredient_nom": "Lait", "frequence": 5, "quantite_moyenne": 2, "rayon": "Laitier"},
                {"ingredient_nom": "Pain", "frequence": 2, "quantite_moyenne": 1, "rayon": "Boulangerie"},
            ]
        }
        
        modele = generer_modele_depuis_historique(analyse, seuil_frequence=3)
        
        assert len(modele) == 1  # Seul le lait passe le seuil de 3
        assert modele[0]["ingredient_nom"] == "Lait"
        assert modele[0]["quantite_necessaire"] == 2


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════

class TestEdgeCases:
    """Tests pour les cas limites"""
    
    def test_filtrer_liste_vide(self):
        """Filtrer une liste vide"""
        assert filtrer_par_priorite([], "haute") == []
        assert filtrer_par_rayon([], "Laitier") == []
        assert filtrer_par_recherche([], "test") == []
    
    def test_trier_liste_vide(self):
        """Trier une liste vide"""
        assert trier_par_priorite([]) == []
        assert trier_par_rayon([]) == []
        assert trier_par_nom([]) == []
    
    def test_grouper_liste_vide(self):
        """Grouper une liste vide"""
        assert grouper_par_rayon([]) == {}
        assert grouper_par_priorite([]) == {"haute": [], "moyenne": [], "basse": []}
    
    def test_article_champs_manquants(self):
        """Article avec champs manquants"""
        article = {"ingredient_nom": "Test"}
        
        # Le formatage ne doit pas échouer
        label = formater_article_label(article)
        assert "Test" in label
    
    def test_statistiques_sans_achetes(self, sample_articles):
        """Statistiques sans articles achetés"""
        stats = calculer_statistiques(sample_articles)
        assert stats["total_achetes"] == 0
        assert stats["taux_completion"] == 0
