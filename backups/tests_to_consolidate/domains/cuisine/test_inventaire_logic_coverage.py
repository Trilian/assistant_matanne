"""
Tests de couverture complets pour inventaire_logic.py
Objectif: atteindre 80%+ de couverture
Couvre les lignes non testées
"""
import pytest
from datetime import date, datetime, timedelta

from src.domains.cuisine.logic.inventaire_logic import (
    calculer_status_stock,
    calculer_status_peremption,
    calculer_status_global,
    filtrer_par_status,
    valider_article_inventaire,
    valider_nouvel_article_inventaire,
    formater_article_label,
    formater_inventaire_rapport,
    calculer_jours_avant_peremption,
    grouper_par_emplacement,
    grouper_par_categorie,
    trier_par_peremption,
    trier_par_urgence,
    formater_article_inventaire,
    calculer_alertes,
    alertes_critiques_existent,
    EMPLACEMENTS,
    CATEGORIES,
)


# ═══════════════════════════════════════════════════════════
# TESTS FILTRER_PAR_STATUS
# ═══════════════════════════════════════════════════════════

class TestFiltrerParStatus:
    """Tests pour filtrer_par_status."""

    def test_filtrer_articles_critique(self):
        """Filtre les articles avec statut critique."""
        articles = [
            {"ingredient_nom": "Sel", "quantite": 1, "seuil_alerte": 5, "seuil_critique": 2},
            {"ingredient_nom": "Sucre", "quantite": 10, "seuil_alerte": 5, "seuil_critique": 2},
        ]
        
        result = filtrer_par_status(articles, "critique")
        
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Sel"

    def test_filtrer_articles_stock_bas(self):
        """Filtre les articles avec statut stock_bas."""
        articles = [
            {"ingredient_nom": "Sel", "quantite": 3, "seuil_alerte": 5, "seuil_critique": 2},
            {"ingredient_nom": "Sucre", "quantite": 10, "seuil_alerte": 5, "seuil_critique": 2},
        ]
        
        result = filtrer_par_status(articles, "stock_bas")
        
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Sel"

    def test_filtrer_par_status_tous(self):
        """Status 'tous' retourne tous les articles."""
        articles = [
            {"ingredient_nom": "Sel", "quantite": 1, "seuil_alerte": 5, "seuil_critique": 2},
            {"ingredient_nom": "Sucre", "quantite": 10, "seuil_alerte": 5, "seuil_critique": 2},
        ]
        
        result = filtrer_par_status(articles, "tous")
        
        assert len(result) == 2

    def test_filtrer_par_status_perime(self):
        """Filtre les articles périmés."""
        hier = date.today() - timedelta(days=1)
        articles = [
            {"ingredient_nom": "Lait", "quantite": 1, "seuil_alerte": 5, "seuil_critique": 2, "date_peremption": hier},
            {"ingredient_nom": "Sucre", "quantite": 10, "seuil_alerte": 5, "seuil_critique": 2},
        ]
        
        result = filtrer_par_status(articles, "perime")
        
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Lait"


# ═══════════════════════════════════════════════════════════
# TESTS VALIDER_ARTICLE_INVENTAIRE
# ═══════════════════════════════════════════════════════════

class TestValiderArticleInventaire:
    """Tests pour valider_article_inventaire."""

    def test_article_valide(self):
        """Article valide."""
        article = {
            "ingredient_nom": "Sel",
            "quantite": 5,
            "seuil_alerte": 5,
            "seuil_critique": 2,
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is True
        assert len(erreurs) == 0

    def test_article_sans_nom(self):
        """Article sans nom invalide."""
        article = {
            "quantite": 5,
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is False
        assert any("nom" in e.lower() for e in erreurs)

    def test_article_nom_court(self):
        """Nom trop court invalide."""
        article = {
            "ingredient_nom": "A",
            "quantite": 5,
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is False
        assert any("2 caractères" in e for e in erreurs)

    def test_article_quantite_negative(self):
        """Quantité négative invalide."""
        article = {
            "ingredient_nom": "Sel",
            "quantite": -5,
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is False
        assert any("négative" in e.lower() for e in erreurs)

    def test_seuil_critique_superieur_alerte(self):
        """Seuil critique > seuil alerte invalide."""
        article = {
            "ingredient_nom": "Sel",
            "quantite": 5,
            "seuil_alerte": 3,
            "seuil_critique": 5,
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is False
        assert any("critique" in e.lower() for e in erreurs)

    def test_emplacement_non_standard(self):
        """Emplacement non standard génère warning (mais valide)."""
        article = {
            "ingredient_nom": "Sel",
            "quantite": 5,
            "emplacement": "Garage",
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        # Reste valide mais warning logged
        assert valide is True

    def test_categorie_non_standard(self):
        """Catégorie non standard génère warning (mais valide)."""
        article = {
            "ingredient_nom": "Sel",
            "quantite": 5,
            "categorie": "Nouveauté",
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is True

    def test_date_peremption_format_invalide(self):
        """Date de péremption au format invalide."""
        article = {
            "ingredient_nom": "Sel",
            "quantite": 5,
            "date_peremption": "pas-une-date",
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is False
        assert any("date" in e.lower() for e in erreurs)

    def test_date_peremption_string_valide(self):
        """Date de péremption string valide."""
        demain = (date.today() + timedelta(days=1)).isoformat()
        article = {
            "ingredient_nom": "Sel",
            "quantite": 5,
            "date_peremption": demain,
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is True

    def test_date_peremption_datetime(self):
        """Date de péremption comme datetime."""
        article = {
            "ingredient_nom": "Sel",
            "quantite": 5,
            "date_peremption": datetime.now() + timedelta(days=7),
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is True


# ═══════════════════════════════════════════════════════════
# TESTS VALIDER_NOUVEL_ARTICLE_INVENTAIRE
# ═══════════════════════════════════════════════════════════

class TestValiderNouvelArticleInventaire:
    """Tests pour valider_nouvel_article_inventaire."""

    def test_nouvel_article_valide(self):
        """Création d'un nouvel article valide."""
        valide, result = valider_nouvel_article_inventaire(
            nom="Farine",
            quantite=1.5,
            unite="kg",
            emplacement="Garde-manger",
            categorie="Épicerie"
        )
        
        assert valide is True
        assert isinstance(result, dict)
        assert result["ingredient_nom"] == "Farine"
        assert result["quantite"] == 1.5
        assert "date_ajout" in result

    def test_nouvel_article_invalide(self):
        """Création article invalide retourne erreurs."""
        valide, result = valider_nouvel_article_inventaire(
            nom="",  # Nom vide invalide
            quantite=5,
            unite="kg"
        )
        
        assert valide is False
        assert isinstance(result, list)
        assert len(result) > 0

    def test_nouvel_article_avec_date_peremption(self):
        """Création avec date de péremption."""
        valide, result = valider_nouvel_article_inventaire(
            nom="Lait",
            quantite=1,
            unite="L",
            date_peremption=date.today() + timedelta(days=5)
        )
        
        assert valide is True
        assert result["date_peremption"] == date.today() + timedelta(days=5)

    def test_nouvel_article_seuils_personnalises(self):
        """Création avec seuils personnalisés."""
        valide, result = valider_nouvel_article_inventaire(
            nom="Épice rare",
            quantite=3,
            unite="g",
            seuil_alerte=10,
            seuil_critique=5
        )
        
        assert valide is True
        assert result["seuil_alerte"] == 10
        assert result["seuil_critique"] == 5


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER_ARTICLE_LABEL
# ═══════════════════════════════════════════════════════════

class TestFormaterArticleLabel:
    """Tests pour formater_article_label."""

    def test_label_article_ok(self):
        """Label pour article OK."""
        article = {
            "ingredient_nom": "Sucre",
            "quantite": 10,
            "unite": "kg",
            "seuil_alerte": 5,
            "seuil_critique": 2,
        }
        
        label = formater_article_label(article)
        
        assert "Sucre" in label
        assert "10" in label
        assert "kg" in label
        assert "💡" in label

    def test_label_article_critique(self):
        """Label pour article critique."""
        article = {
            "ingredient_nom": "Sel",
            "quantite": 1,
            "unite": "kg",
            "seuil_alerte": 5,
            "seuil_critique": 2,
        }
        
        label = formater_article_label(article)
        
        assert "❌" in label

    def test_label_article_bientot_perime(self):
        """Label avec date de péremption proche."""
        article = {
            "ingredient_nom": "Lait",
            "quantite": 1,
            "unite": "L",
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "date_peremption": date.today() + timedelta(days=3),
        }
        
        label = formater_article_label(article)
        
        assert "📅" in label

    def test_label_article_perime(self):
        """Label pour article périmé."""
        article = {
            "ingredient_nom": "Yaourt",
            "quantite": 4,
            "unite": "pcs",
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "date_peremption": date.today() - timedelta(days=1),
        }
        
        label = formater_article_label(article)
        
        assert "📅" in label  # Date affichée
        assert "⚫" in label  # Emoji périmé

    def test_label_article_perime_datetime(self):
        """Label pour article périmé avec datetime."""
        article = {
            "ingredient_nom": "Yaourt",
            "quantite": 4,
            "unite": "pcs",
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "date_peremption": datetime.now() - timedelta(days=1),
        }
        
        label = formater_article_label(article)
        
        assert "📅" in label


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER_INVENTAIRE_RAPPORT
# ═══════════════════════════════════════════════════════════

class TestFormaterInventaireRapport:
    """Tests pour formater_inventaire_rapport."""

    def test_rapport_inventaire_complet(self):
        """Génère un rapport complet."""
        articles = [
            {"ingredient_nom": "Sucre", "quantite": 10, "prix_unitaire": 1.5, "seuil_alerte": 5, "seuil_critique": 2, "emplacement": "Garde-manger", "categorie": "Épicerie"},
            {"ingredient_nom": "Sel", "quantite": 1, "prix_unitaire": 0.5, "seuil_alerte": 5, "seuil_critique": 2, "emplacement": "Garde-manger", "categorie": "Épicerie"},
        ]
        
        rapport = formater_inventaire_rapport(articles)
        
        assert "RAPPORT D'INVENTAIRE" in rapport
        assert "Total articles: 2" in rapport
        assert "Garde-manger" in rapport

    def test_rapport_avec_alertes_critiques(self):
        """Rapport avec alertes critiques."""
        hier = date.today() - timedelta(days=1)
        articles = [
            {"ingredient_nom": "Sel critique", "quantite": 1, "prix_unitaire": 0.5, "seuil_alerte": 5, "seuil_critique": 2, "emplacement": "Cuisine"},
            {"ingredient_nom": "Lait périmé", "quantite": 1, "prix_unitaire": 1.0, "seuil_alerte": 5, "seuil_critique": 2, "date_peremption": hier, "emplacement": "Frigo"},
        ]
        
        rapport = formater_inventaire_rapport(articles)
        
        assert "ALERTES CRITIQUES" in rapport
        assert "Stock critique" in rapport or "PÉRIMÉ" in rapport

    def test_rapport_inventaire_minimum(self):
        """Rapport pour inventaire avec un seul article."""
        articles = [
            {"ingredient_nom": "Sucre", "quantite": 10, "seuil_alerte": 5, "seuil_critique": 2, "emplacement": "Garde-manger"},
        ]
        
        rapport = formater_inventaire_rapport(articles)
        
        assert "Total articles: 1" in rapport


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER_JOURS_AVANT_PEREMPTION
# ═══════════════════════════════════════════════════════════

class TestCalculerJoursAvantPeremption:
    """Tests pour calculer_jours_avant_peremption."""

    def test_date_future(self):
        """Calcul jours pour date future."""
        article = {"date_peremption": date.today() + timedelta(days=10)}
        
        result = calculer_jours_avant_peremption(article)
        
        assert result == 10

    def test_date_passee(self):
        """Calcul jours pour date passée (négatif)."""
        article = {"date_peremption": date.today() - timedelta(days=3)}
        
        result = calculer_jours_avant_peremption(article)
        
        assert result == -3

    def test_sans_date(self):
        """Retourne None si pas de date."""
        article = {"ingredient_nom": "Sel"}
        
        result = calculer_jours_avant_peremption(article)
        
        assert result is None

    def test_date_string_valide(self):
        """Gère les dates en string."""
        date_str = (date.today() + timedelta(days=5)).isoformat()
        article = {"date_peremption": date_str}
        
        result = calculer_jours_avant_peremption(article)
        
        assert result == 5

    def test_date_string_invalide(self):
        """Retourne None pour date string invalide."""
        article = {"date_peremption": "not-a-date"}
        
        result = calculer_jours_avant_peremption(article)
        
        assert result is None

    def test_date_datetime(self):
        """Gère les datetime."""
        article = {"date_peremption": datetime.now() + timedelta(days=7)}
        
        result = calculer_jours_avant_peremption(article)
        
        assert result == 7


# ═══════════════════════════════════════════════════════════
# TESTS GROUPER_PAR_EMPLACEMENT ET CATEGORIE
# ═══════════════════════════════════════════════════════════

class TestGrouperParEmplacement:
    """Tests pour grouper_par_emplacement."""

    def test_grouper_par_emplacement(self):
        """Groupe correctement par emplacement."""
        articles = [
            {"ingredient_nom": "Lait", "emplacement": "Réfrigérateur"},
            {"ingredient_nom": "Sucre", "emplacement": "Garde-manger"},
            {"ingredient_nom": "Beurre", "emplacement": "Réfrigérateur"},
        ]
        
        groupes = grouper_par_emplacement(articles)
        
        assert len(groupes["Réfrigérateur"]) == 2
        assert len(groupes["Garde-manger"]) == 1

    def test_grouper_sans_emplacement(self):
        """Articles sans emplacement vont dans 'Autre'."""
        articles = [
            {"ingredient_nom": "Inconnu"},
        ]
        
        groupes = grouper_par_emplacement(articles)
        
        assert "Autre" in groupes
        assert len(groupes["Autre"]) == 1


class TestGrouperParCategorie:
    """Tests pour grouper_par_categorie."""

    def test_grouper_par_categorie(self):
        """Groupe correctement par catégorie."""
        articles = [
            {"ingredient_nom": "Pomme", "categorie": "Fruits & Légumes"},
            {"ingredient_nom": "Boeuf", "categorie": "Viandes & Poissons"},
            {"ingredient_nom": "Carotte", "categorie": "Fruits & Légumes"},
        ]
        
        groupes = grouper_par_categorie(articles)
        
        assert len(groupes["Fruits & Légumes"]) == 2
        assert len(groupes["Viandes & Poissons"]) == 1

    def test_grouper_sans_categorie(self):
        """Articles sans catégorie vont dans 'Autre'."""
        articles = [
            {"ingredient_nom": "Inconnu"},
        ]
        
        groupes = grouper_par_categorie(articles)
        
        assert "Autre" in groupes


# ═══════════════════════════════════════════════════════════
# TESTS TRI
# ═══════════════════════════════════════════════════════════

class TestTrierParPeremption:
    """Tests pour trier_par_peremption."""

    def test_trier_par_peremption(self):
        """Trie correctement par date de péremption."""
        articles = [
            {"ingredient_nom": "Lait", "date_peremption": date.today() + timedelta(days=10)},
            {"ingredient_nom": "Yaourt", "date_peremption": date.today() + timedelta(days=3)},
            {"ingredient_nom": "Fromage", "date_peremption": date.today() + timedelta(days=7)},
        ]
        
        result = trier_par_peremption(articles)
        
        assert result[0]["ingredient_nom"] == "Yaourt"  # Plus proche
        assert result[2]["ingredient_nom"] == "Lait"  # Plus lointain

    def test_trier_avec_sans_date(self):
        """Articles sans date à la fin."""
        articles = [
            {"ingredient_nom": "Sel"},  # Pas de date
            {"ingredient_nom": "Lait", "date_peremption": date.today() + timedelta(days=5)},
        ]
        
        result = trier_par_peremption(articles)
        
        assert result[0]["ingredient_nom"] == "Lait"  # Avec date en premier
        assert result[1]["ingredient_nom"] == "Sel"  # Sans date à la fin


class TestTrierParUrgence:
    """Tests pour trier_par_urgence."""

    def test_trier_par_urgence(self):
        """Trie correctement par urgence."""
        hier = date.today() - timedelta(days=1)
        articles = [
            {"ingredient_nom": "OK", "quantite": 10, "seuil_alerte": 5, "seuil_critique": 2},
            {"ingredient_nom": "Critique", "quantite": 1, "seuil_alerte": 5, "seuil_critique": 2},
            {"ingredient_nom": "Périmé", "quantite": 10, "seuil_alerte": 5, "seuil_critique": 2, "date_peremption": hier},
        ]
        
        result = trier_par_urgence(articles)
        
        assert result[0]["ingredient_nom"] == "Périmé"  # Périmé en premier
        assert result[1]["ingredient_nom"] == "Critique"  # Puis critique
        assert result[2]["ingredient_nom"] == "OK"  # OK à la fin


# ═══════════════════════════════════════════════════════════
# TESTS FORMATER_ARTICLE_INVENTAIRE
# ═══════════════════════════════════════════════════════════

class TestFormaterArticleInventaire:
    """Tests pour formater_article_inventaire."""

    def test_formater_article_complet(self):
        """Formate un article avec tous les champs."""
        article = {
            "ingredient_nom": "Sucre",
            "quantite": 5,
            "unite": "kg",
            "seuil_alerte": 10,
            "seuil_critique": 3,
            "date_peremption": date.today() + timedelta(days=30),
        }
        
        result = formater_article_inventaire(article)
        
        assert result["status_stock"] == "stock_bas"  # 5 <= 10
        assert result["status_peremption"] == "ok"
        assert "emoji_stock" in result
        assert "emoji_peremption" in result
        assert result["jours_avant_peremption"] == 30
        assert "affichage_stock" in result
        assert "affichage_quantite" in result

    def test_formater_article_critique(self):
        """Formate un article critique."""
        article = {
            "ingredient_nom": "Sel",
            "quantite": 1,
            "unite": "kg",
            "seuil_alerte": 5,
            "seuil_critique": 2,
        }
        
        result = formater_article_inventaire(article)
        
        assert result["status_stock"] == "critique"
        assert "❌" in result["emoji_stock"]


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES
# ═══════════════════════════════════════════════════════════

class TestAlertesCritiquesExistent:
    """Tests pour alertes_critiques_existent."""

    def test_avec_article_critique(self):
        """True si article critique."""
        alertes = {"critique": [{"ingredient_nom": "Sel"}], "perime": []}
        
        assert alertes_critiques_existent(alertes) is True

    def test_avec_article_perime(self):
        """True si article périmé."""
        alertes = {"critique": [], "perime": [{"ingredient_nom": "Lait"}]}
        
        assert alertes_critiques_existent(alertes) is True

    def test_sans_alertes_critiques(self):
        """False si pas d'alertes critiques."""
        alertes = {"critique": [], "perime": [], "stock_bas": [{"x": 1}]}
        
        assert alertes_critiques_existent(alertes) is False

    def test_alertes_vides(self):
        """False si toutes alertes vides."""
        alertes = {"critique": [], "perime": []}
        
        assert alertes_critiques_existent(alertes) is False
