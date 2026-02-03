"""
Tests pour inventaire_logic.py
Couverture cible: 80%+
"""
import pytest
from datetime import date, datetime, timedelta

from src.domains.cuisine.logic.inventaire_logic import (
    # Constantes
    EMPLACEMENTS,
    CATEGORIES,
    STATUS_CONFIG,
    # Calcul de statut
    calculer_status_stock,
    calculer_status_peremption,
    calculer_status_global,
    # Filtrage
    filtrer_par_emplacement,
    filtrer_par_categorie,
    filtrer_par_status,
    filtrer_par_recherche,
)


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests des constantes d'inventaire."""

    def test_emplacements_non_vide(self):
        """Liste des emplacements définie."""
        assert len(EMPLACEMENTS) > 0
        assert "Réfrigérateur" in EMPLACEMENTS
        assert "Congélateur" in EMPLACEMENTS

    def test_categories_non_vide(self):
        """Liste des catégories définie."""
        assert len(CATEGORIES) > 0
        assert "Fruits & Légumes" in CATEGORIES
        assert "Produits laitiers" in CATEGORIES

    def test_status_config_complete(self):
        """Configuration des statuts complète."""
        assert "critique" in STATUS_CONFIG
        assert "stock_bas" in STATUS_CONFIG
        assert "ok" in STATUS_CONFIG
        assert "perime" in STATUS_CONFIG

    def test_status_config_structure(self):
        """Chaque statut a color, emoji, label."""
        for key, config in STATUS_CONFIG.items():
            assert "color" in config
            assert "emoji" in config
            assert "label" in config


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL STATUT STOCK
# ═══════════════════════════════════════════════════════════


class TestCalculStatusStock:
    """Tests pour calculer_status_stock."""

    def test_status_critique(self):
        """Stock critique si quantité <= seuil_critique."""
        article = {"quantite": 1, "seuil_alerte": 5, "seuil_critique": 2}
        assert calculer_status_stock(article) == "critique"

    def test_status_critique_egal_seuil(self):
        """Stock critique si quantité == seuil_critique."""
        article = {"quantite": 2, "seuil_alerte": 5, "seuil_critique": 2}
        assert calculer_status_stock(article) == "critique"

    def test_status_stock_bas(self):
        """Stock bas si quantité entre critique et alerte."""
        article = {"quantite": 4, "seuil_alerte": 5, "seuil_critique": 2}
        assert calculer_status_stock(article) == "stock_bas"

    def test_status_ok(self):
        """Stock OK si quantité > seuil_alerte."""
        article = {"quantite": 10, "seuil_alerte": 5, "seuil_critique": 2}
        assert calculer_status_stock(article) == "ok"

    def test_status_defaults(self):
        """Utilise les valeurs par défaut si non spécifié."""
        article = {"quantite": 1}  # seuil_alerte=5, seuil_critique=2 par défaut
        assert calculer_status_stock(article) == "critique"

    def test_status_quantite_zero(self):
        """Quantité 0 est critique."""
        article = {"quantite": 0}
        assert calculer_status_stock(article) == "critique"


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL STATUT PÉREMPTION
# ═══════════════════════════════════════════════════════════


class TestCalculStatusPeremption:
    """Tests pour calculer_status_peremption."""

    def test_pas_de_date_peremption(self):
        """OK si pas de date de péremption."""
        article = {"nom": "Test"}
        assert calculer_status_peremption(article) == "ok"

    def test_perime_date_passee(self):
        """Périmé si date passée."""
        article = {"date_peremption": date.today() - timedelta(days=1)}
        assert calculer_status_peremption(article) == "perime"

    def test_bientot_perime_dans_7_jours(self):
        """Bientôt périmé si dans 7 jours."""
        article = {"date_peremption": date.today() + timedelta(days=5)}
        assert calculer_status_peremption(article) == "bientot_perime"

    def test_ok_loin(self):
        """OK si péremption loin."""
        article = {"date_peremption": date.today() + timedelta(days=30)}
        assert calculer_status_peremption(article) == "ok"

    def test_date_string_iso(self):
        """Gère les dates en string ISO."""
        date_peremption = (date.today() - timedelta(days=1)).isoformat()
        article = {"date_peremption": date_peremption}
        assert calculer_status_peremption(article) == "perime"

    def test_date_datetime(self):
        """Gère les datetime."""
        article = {"date_peremption": datetime.now() - timedelta(days=1)}
        assert calculer_status_peremption(article) == "perime"

    def test_jours_alerte_personnalise(self):
        """Respect du paramètre jours_alerte."""
        article = {"date_peremption": date.today() + timedelta(days=10)}
        # Avec 7 jours par défaut = OK
        assert calculer_status_peremption(article, jours_alerte=7) == "ok"
        # Avec 14 jours = bientôt périmé
        assert calculer_status_peremption(article, jours_alerte=14) == "bientot_perime"

    def test_date_invalide(self):
        """Retourne OK si date invalide."""
        article = {"date_peremption": "invalid-date"}
        assert calculer_status_peremption(article) == "ok"


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL STATUT GLOBAL
# ═══════════════════════════════════════════════════════════


class TestCalculStatusGlobal:
    """Tests pour calculer_status_global."""

    def test_priorite_perime(self):
        """Périmé est prioritaire sur tout."""
        article = {
            "quantite": 10,  # stock OK
            "date_peremption": date.today() - timedelta(days=1)  # périmé
        }
        result = calculer_status_global(article)
        assert result["status_prioritaire"] == "perime"

    def test_priorite_critique(self):
        """Critique > bientôt périmé."""
        article = {
            "quantite": 1,  # critique
            "seuil_critique": 2,
            "date_peremption": date.today() + timedelta(days=5)  # bientôt périmé
        }
        result = calculer_status_global(article)
        assert result["status_prioritaire"] == "critique"

    def test_priorite_bientot_perime(self):
        """Bientôt périmé > stock bas."""
        article = {
            "quantite": 4,  # stock bas
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "date_peremption": date.today() + timedelta(days=5)  # bientôt périmé
        }
        result = calculer_status_global(article)
        assert result["status_prioritaire"] == "bientot_perime"

    def test_priorite_stock_bas(self):
        """Stock bas si pas de problème péremption."""
        article = {
            "quantite": 4,
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "date_peremption": date.today() + timedelta(days=30)
        }
        result = calculer_status_global(article)
        assert result["status_prioritaire"] == "stock_bas"

    def test_priorite_ok(self):
        """OK si tout va bien."""
        article = {
            "quantite": 10,
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "date_peremption": date.today() + timedelta(days=30)
        }
        result = calculer_status_global(article)
        assert result["status_prioritaire"] == "ok"

    def test_retourne_config(self):
        """Le résultat contient la config du statut."""
        article = {"quantite": 10}
        result = calculer_status_global(article)
        assert "config" in result
        assert "color" in result["config"]
        assert "emoji" in result["config"]


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE
# ═══════════════════════════════════════════════════════════


class TestFiltrageEmplacement:
    """Tests pour filtrer_par_emplacement."""

    @pytest.fixture
    def articles(self):
        return [
            {"nom": "Lait", "emplacement": "Réfrigérateur"},
            {"nom": "Glace", "emplacement": "Congélateur"},
            {"nom": "Pâtes", "emplacement": "Garde-manger"},
        ]

    def test_filtrer_emplacement(self, articles):
        """Filtre par emplacement."""
        result = filtrer_par_emplacement(articles, "Réfrigérateur")
        assert len(result) == 1
        assert result[0]["nom"] == "Lait"

    def test_filtrer_tous(self, articles):
        """'Tous' retourne tout."""
        result = filtrer_par_emplacement(articles, "tous")
        assert len(result) == 3

    def test_filtrer_none(self, articles):
        """None retourne tout."""
        result = filtrer_par_emplacement(articles, None)
        assert len(result) == 3


class TestFiltrageCategorie:
    """Tests pour filtrer_par_categorie."""

    @pytest.fixture
    def articles(self):
        return [
            {"nom": "Lait", "categorie": "Produits laitiers"},
            {"nom": "Pommes", "categorie": "Fruits & Légumes"},
            {"nom": "Yaourt", "categorie": "Produits laitiers"},
        ]

    def test_filtrer_categorie(self, articles):
        """Filtre par catégorie."""
        result = filtrer_par_categorie(articles, "Produits laitiers")
        assert len(result) == 2

    def test_filtrer_toutes(self, articles):
        """'Toutes' retourne tout."""
        result = filtrer_par_categorie(articles, "toutes")
        assert len(result) == 3


class TestFiltrageRecherche:
    """Tests pour filtrer_par_recherche."""

    @pytest.fixture
    def articles(self):
        return [
            {"ingredient_nom": "Lait entier", "notes": "Bio"},
            {"ingredient_nom": "Yaourt nature", "notes": ""},
            {"ingredient_nom": "Crème fraîche", "notes": "Épaisse"},
        ]

    def test_recherche_nom(self, articles):
        """Recherche dans le nom."""
        result = filtrer_par_recherche(articles, "lait")
        assert len(result) == 1

    def test_recherche_case_insensitive(self, articles):
        """Recherche insensible à la casse."""
        result = filtrer_par_recherche(articles, "YAOURT")
        assert len(result) == 1

    def test_recherche_vide(self, articles):
        """Recherche vide retourne tout."""
        result = filtrer_par_recherche(articles, "")
        assert len(result) == 3

    def test_recherche_aucun_resultat(self, articles):
        """Recherche sans résultat."""
        result = filtrer_par_recherche(articles, "inexistant")
        assert len(result) == 0

    def test_recherche_dans_notes(self, articles):
        """Recherche dans les notes."""
        result = filtrer_par_recherche(articles, "bio")
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE COMBINÉ
# ═══════════════════════════════════════════════════════════


class TestFiltrageInventaire:
    """Tests pour filtrer_inventaire (combinaison de filtres)."""

    @pytest.fixture
    def articles(self):
        return [
            {"ingredient_nom": "Lait", "categorie": "Produits laitiers", "emplacement": "Frigo", "quantite": 1, "seuil_critique": 2},
            {"ingredient_nom": "Pommes", "categorie": "Fruits & Légumes", "emplacement": "Frigo", "quantite": 10, "seuil_critique": 2},
            {"ingredient_nom": "Yaourt", "categorie": "Produits laitiers", "emplacement": "Frigo", "quantite": 5, "seuil_critique": 2},
            {"ingredient_nom": "Pain", "categorie": "Épicerie", "emplacement": "Placard", "quantite": 2, "seuil_critique": 2},
        ]

    def test_filtre_unique(self, articles):
        """Un seul filtre appliqué."""
        from src.domains.cuisine.logic.inventaire_logic import filtrer_inventaire
        
        result = filtrer_inventaire(articles, categorie="Produits laitiers")
        assert len(result) == 2

    def test_filtres_combines(self, articles):
        """Plusieurs filtres combinés."""
        from src.domains.cuisine.logic.inventaire_logic import filtrer_inventaire
        
        result = filtrer_inventaire(
            articles, 
            emplacement="Frigo", 
            categorie="Produits laitiers"
        )
        assert len(result) == 2

    def test_sans_filtre(self, articles):
        """Aucun filtre retourne tout."""
        from src.domains.cuisine.logic.inventaire_logic import filtrer_inventaire
        
        result = filtrer_inventaire(articles)
        assert len(result) == 4

    def test_filtre_avec_recherche(self, articles):
        """Filtre avec recherche textuelle."""
        from src.domains.cuisine.logic.inventaire_logic import filtrer_inventaire
        
        result = filtrer_inventaire(articles, recherche="lait")
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES
# ═══════════════════════════════════════════════════════════


class TestCalculerAlertes:
    """Tests pour calculer_alertes."""

    @pytest.fixture
    def articles_varies(self):
        today = date.today()
        return [
            # Stock critique
            {"ingredient_nom": "Lait", "quantite": 1, "seuil_critique": 2, "seuil_alerte": 5},
            # Stock OK
            {"ingredient_nom": "Eau", "quantite": 20, "seuil_critique": 2, "seuil_alerte": 5},
            # Bientôt périmé
            {"ingredient_nom": "Yaourt", "quantite": 10, "seuil_critique": 2, "date_peremption": today + timedelta(days=3)},
            # Périmé
            {"ingredient_nom": "Crème", "quantite": 5, "seuil_critique": 2, "date_peremption": today - timedelta(days=1)},
        ]

    def test_alertes_structure(self, articles_varies):
        """Les alertes ont la bonne structure."""
        from src.domains.cuisine.logic.inventaire_logic import calculer_alertes
        
        alertes = calculer_alertes(articles_varies)
        
        assert "critique" in alertes
        assert "stock_bas" in alertes
        assert "perime" in alertes
        assert "bientot_perime" in alertes

    def test_alerte_critique(self, articles_varies):
        """Détecte les articles en stock critique."""
        from src.domains.cuisine.logic.inventaire_logic import calculer_alertes
        
        alertes = calculer_alertes(articles_varies)
        
        assert len(alertes["critique"]) == 1
        assert alertes["critique"][0]["ingredient_nom"] == "Lait"

    def test_alerte_perime(self, articles_varies):
        """Détecte les articles périmés."""
        from src.domains.cuisine.logic.inventaire_logic import calculer_alertes
        
        alertes = calculer_alertes(articles_varies)
        
        assert len(alertes["perime"]) == 1
        assert alertes["perime"][0]["ingredient_nom"] == "Crème"

    def test_alerte_bientot_perime(self, articles_varies):
        """Détecte les articles bientôt périmés."""
        from src.domains.cuisine.logic.inventaire_logic import calculer_alertes
        
        alertes = calculer_alertes(articles_varies)
        
        assert len(alertes["bientot_perime"]) == 1
        assert alertes["bientot_perime"][0]["ingredient_nom"] == "Yaourt"


class TestCompterAlertes:
    """Tests pour compter_alertes."""

    def test_compte_correct(self):
        """Compte les alertes correctement."""
        from src.domains.cuisine.logic.inventaire_logic import compter_alertes
        
        alertes = {
            "critique": [1, 2, 3],
            "stock_bas": [1],
            "perime": [],
            "bientot_perime": [1, 2],
        }
        
        result = compter_alertes(alertes)
        
        assert result["critique"] == 3
        assert result["stock_bas"] == 1
        assert result["perime"] == 0
        assert result["bientot_perime"] == 2

    def test_compte_vide(self):
        """Compte des alertes vides."""
        from src.domains.cuisine.logic.inventaire_logic import compter_alertes
        
        alertes = {
            "critique": [],
            "stock_bas": [],
            "perime": [],
            "bientot_perime": [],
        }
        
        result = compter_alertes(alertes)
        
        assert all(v == 0 for v in result.values())


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestStatistiquesInventaire:
    """Tests pour calculer_statistiques_inventaire."""

    @pytest.fixture
    def articles(self):
        today = date.today()
        return [
            {"ingredient_nom": "Lait", "quantite": 1, "seuil_critique": 2, "seuil_alerte": 5},
            {"ingredient_nom": "Eau", "quantite": 20, "seuil_critique": 2, "seuil_alerte": 5},
            {"ingredient_nom": "Yaourt", "quantite": 5, "seuil_critique": 2, "date_peremption": today + timedelta(days=3)},
        ]

    def test_statistiques_structure(self, articles):
        """Les statistiques ont la bonne structure."""
        from src.domains.cuisine.logic.inventaire_logic import calculer_statistiques_inventaire
        
        stats = calculer_statistiques_inventaire(articles)
        
        assert "total_articles" in stats
        assert "articles_ok" in stats or "articles_alerte" in stats

    def test_compte_total(self, articles):
        """Compte le total d'articles."""
        from src.domains.cuisine.logic.inventaire_logic import calculer_statistiques_inventaire
        
        stats = calculer_statistiques_inventaire(articles)
        
        assert stats["total_articles"] == 3

    def test_liste_vide(self):
        """Statistiques d'une liste vide."""
        from src.domains.cuisine.logic.inventaire_logic import calculer_statistiques_inventaire
        
        stats = calculer_statistiques_inventaire([])
        
        assert stats["total_articles"] == 0


class TestGroupement:
    """Tests pour les fonctions de groupement."""

    @pytest.fixture
    def articles(self):
        return [
            {"ingredient_nom": "Lait", "emplacement": "Frigo", "categorie": "Produits laitiers"},
            {"ingredient_nom": "Pain", "emplacement": "Placard", "categorie": "Épicerie"},
            {"ingredient_nom": "Yaourt", "emplacement": "Frigo", "categorie": "Produits laitiers"},
        ]

    def test_grouper_par_emplacement(self, articles):
        """Groupe par emplacement."""
        from src.domains.cuisine.logic.inventaire_logic import grouper_par_emplacement
        
        result = grouper_par_emplacement(articles)
        
        assert "Frigo" in result
        assert "Placard" in result
        assert len(result["Frigo"]) == 2
        assert len(result["Placard"]) == 1

    def test_grouper_par_categorie(self, articles):
        """Groupe par catégorie."""
        from src.domains.cuisine.logic.inventaire_logic import grouper_par_categorie
        
        result = grouper_par_categorie(articles)
        
        assert "Produits laitiers" in result
        assert "Épicerie" in result
        assert len(result["Produits laitiers"]) == 2


class TestValidationArticle:
    """Tests pour valider_article_inventaire."""

    def test_article_valide(self):
        """Article avec tous les champs valides."""
        from src.domains.cuisine.logic.inventaire_logic import valider_article_inventaire
        
        article = {
            "ingredient_nom": "Lait",
            "quantite": 5,
            "unite": "L",
            "emplacement": "Frigo"
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is True
        assert len(erreurs) == 0

    def test_article_nom_manquant(self):
        """Article sans nom."""
        from src.domains.cuisine.logic.inventaire_logic import valider_article_inventaire
        
        article = {
            "quantite": 5,
            "unite": "L"
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is False
        assert len(erreurs) > 0

    def test_article_quantite_negative(self):
        """Article avec quantité négative."""
        from src.domains.cuisine.logic.inventaire_logic import valider_article_inventaire
        
        article = {
            "ingredient_nom": "Lait",
            "quantite": -1
        }
        
        valide, erreurs = valider_article_inventaire(article)
        
        assert valide is False


class TestFormatage:
    """Tests pour les fonctions de formatage."""

    def test_formater_article_label(self):
        """Formate l'étiquette d'un article."""
        from src.domains.cuisine.logic.inventaire_logic import formater_article_label
        
        article = {
            "ingredient_nom": "Lait",
            "quantite": 2,
            "unite": "L"
        }
        
        label = formater_article_label(article)
        
        assert "Lait" in label
        assert "2" in label

    def test_formater_inventaire_rapport(self):
        """Formate un rapport d'inventaire."""
        from src.domains.cuisine.logic.inventaire_logic import formater_inventaire_rapport
        
        articles = [
            {"ingredient_nom": "Lait", "quantite": 2, "unite": "L", "emplacement": "Frigo"},
            {"ingredient_nom": "Pain", "quantite": 1, "unite": "unité", "emplacement": "Placard"},
        ]
        
        rapport = formater_inventaire_rapport(articles)
        
        assert "Lait" in rapport
        assert "Pain" in rapport


class TestCalculJoursPeremption:
    """Tests pour calculer_jours_avant_peremption."""

    def test_jours_positifs(self):
        """Calcule les jours restants."""
        from src.domains.cuisine.logic.inventaire_logic import calculer_jours_avant_peremption
        
        today = date.today()
        article = {"date_peremption": today + timedelta(days=5)}
        
        jours = calculer_jours_avant_peremption(article)
        
        assert jours == 5

    def test_jours_negatifs(self):
        """Article périmé (jours négatifs)."""
        from src.domains.cuisine.logic.inventaire_logic import calculer_jours_avant_peremption
        
        today = date.today()
        article = {"date_peremption": today - timedelta(days=3)}
        
        jours = calculer_jours_avant_peremption(article)
        
        assert jours == -3

    def test_sans_date_peremption(self):
        """Article sans date de péremption."""
        from src.domains.cuisine.logic.inventaire_logic import calculer_jours_avant_peremption
        
        article = {"ingredient_nom": "Sel"}
        
        jours = calculer_jours_avant_peremption(article)
        
        assert jours is None

