"""
Tests unitaires pour inventaire_logic.py
Module de logique métier séparé de l'UI
"""

import pytest
from datetime import datetime, date, timedelta

from src.modules.cuisine.inventaire_logic import (
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
    filtrer_inventaire,
    # Alertes
    calculer_alertes,
    compter_alertes,
    alertes_critiques_existent,
    # Statistiques
    calculer_statistiques_inventaire,
    calculer_statistiques_par_emplacement,
    calculer_statistiques_par_categorie,
    # Validation
    valider_article_inventaire,
    valider_nouvel_article_inventaire,
    # Formatage
    formater_article_label,
    formater_inventaire_rapport,
    # Utilitaires
    calculer_jours_avant_peremption,
    grouper_par_emplacement,
    grouper_par_categorie,
    trier_par_peremption,
    trier_par_urgence,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def sample_articles_inventaire():
    """Retourne une liste d'articles d'inventaire pour les tests"""
    aujourd_hui = date.today()
    
    return [
        {
            "ingredient_nom": "Lait",
            "quantite": 3,
            "unite": "L",
            "emplacement": "Réfrigérateur",
            "categorie": "Produits laitiers",
            "date_peremption": aujourd_hui + timedelta(days=5),
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "prix_unitaire": 1.5,
        },
        {
            "ingredient_nom": "Farine",
            "quantite": 10,
            "unite": "kg",
            "emplacement": "Garde-manger",
            "categorie": "Épicerie",
            "date_peremption": aujourd_hui + timedelta(days=180),
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "prix_unitaire": 2.0,
        },
        {
            "ingredient_nom": "Poulet",
            "quantite": 1,
            "unite": "kg",
            "emplacement": "Congélateur",
            "categorie": "Viandes & Poissons",
            "date_peremption": aujourd_hui - timedelta(days=1),  # Périmé
            "seuil_alerte": 3,
            "seuil_critique": 1,
            "prix_unitaire": 8.0,
        },
        {
            "ingredient_nom": "Yaourt",
            "quantite": 1,
            "unite": "pièce",
            "emplacement": "Réfrigérateur",
            "categorie": "Produits laitiers",
            "date_peremption": aujourd_hui + timedelta(days=2),  # Bientôt périmé
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "prix_unitaire": 0.5,
        },
    ]


@pytest.fixture
def article_critique():
    """Article avec stock critique"""
    return {
        "ingredient_nom": "Sel",
        "quantite": 1,
        "unite": "kg",
        "emplacement": "Garde-manger",
        "categorie": "Épicerie",
        "seuil_alerte": 5,
        "seuil_critique": 2,
    }


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════

class TestConstantes:
    """Tests pour les constantes du module"""
    
    def test_emplacements_non_vide(self):
        """Les emplacements ne sont pas vides"""
        assert len(EMPLACEMENTS) > 0
        assert "Réfrigérateur" in EMPLACEMENTS
        assert "Congélateur" in EMPLACEMENTS
        assert "Autre" in EMPLACEMENTS
    
    def test_categories_non_vide(self):
        """Les catégories ne sont pas vides"""
        assert len(CATEGORIES) > 0
        assert "Fruits & Légumes" in CATEGORIES
        assert "Autre" in CATEGORIES
    
    def test_status_config_complete(self):
        """La configuration des statuts est complète"""
        statuts_attendus = ["critique", "stock_bas", "ok", "perime", "bientot_perime"]
        for statut in statuts_attendus:
            assert statut in STATUS_CONFIG
            assert "emoji" in STATUS_CONFIG[statut]
            assert "color" in STATUS_CONFIG[statut]


# ═══════════════════════════════════════════════════════════
# TESTS CALCUL DE STATUT
# ═══════════════════════════════════════════════════════════

class TestCalculStatut:
    """Tests pour les fonctions de calcul de statut"""
    
    def test_calculer_status_stock_ok(self):
        """Stock OK au-dessus du seuil"""
        article = {"quantite": 10, "seuil_alerte": 5, "seuil_critique": 2}
        assert calculer_status_stock(article) == "ok"
    
    def test_calculer_status_stock_bas(self):
        """Stock bas entre les seuils"""
        article = {"quantite": 4, "seuil_alerte": 5, "seuil_critique": 2}
        assert calculer_status_stock(article) == "stock_bas"
    
    def test_calculer_status_stock_critique(self):
        """Stock critique sous le seuil critique"""
        article = {"quantite": 1, "seuil_alerte": 5, "seuil_critique": 2}
        assert calculer_status_stock(article) == "critique"
    
    def test_calculer_status_stock_egal_critique(self):
        """Stock égal au seuil critique"""
        article = {"quantite": 2, "seuil_alerte": 5, "seuil_critique": 2}
        assert calculer_status_stock(article) == "critique"
    
    def test_calculer_status_peremption_ok(self):
        """Pas de péremption proche"""
        article = {"date_peremption": date.today() + timedelta(days=30)}
        assert calculer_status_peremption(article) == "ok"
    
    def test_calculer_status_peremption_bientot(self):
        """Péremption dans les 7 jours"""
        article = {"date_peremption": date.today() + timedelta(days=3)}
        assert calculer_status_peremption(article) == "bientot_perime"
    
    def test_calculer_status_peremption_perime(self):
        """Article périmé"""
        article = {"date_peremption": date.today() - timedelta(days=1)}
        assert calculer_status_peremption(article) == "perime"
    
    def test_calculer_status_peremption_sans_date(self):
        """Article sans date de péremption"""
        article = {}
        assert calculer_status_peremption(article) == "ok"
    
    def test_calculer_status_peremption_string_date(self):
        """Date de péremption en format string"""
        date_future = (date.today() + timedelta(days=30)).isoformat()
        article = {"date_peremption": date_future}
        assert calculer_status_peremption(article) == "ok"
    
    def test_calculer_status_peremption_datetime(self):
        """Date de péremption en datetime"""
        date_future = datetime.now() + timedelta(days=30)
        article = {"date_peremption": date_future}
        assert calculer_status_peremption(article) == "ok"
    
    def test_calculer_status_global(self, sample_articles_inventaire):
        """Test du calcul de statut global"""
        article = sample_articles_inventaire[0]  # Lait
        status = calculer_status_global(article)
        
        assert "status_stock" in status
        assert "status_peremption" in status
        assert "status_prioritaire" in status
        assert "config" in status
    
    def test_calculer_status_global_priorite_perime(self):
        """Périmé a la plus haute priorité"""
        article = {
            "quantite": 1,  # critique
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "date_peremption": date.today() - timedelta(days=1)  # périmé
        }
        status = calculer_status_global(article)
        assert status["status_prioritaire"] == "perime"
    
    def test_calculer_status_global_priorite_critique(self):
        """Critique avant bientôt périmé"""
        article = {
            "quantite": 1,  # critique
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "date_peremption": date.today() + timedelta(days=5)  # bientôt périmé
        }
        status = calculer_status_global(article)
        assert status["status_prioritaire"] == "critique"


# ═══════════════════════════════════════════════════════════
# TESTS FILTRAGE
# ═══════════════════════════════════════════════════════════

class TestFiltrage:
    """Tests pour les fonctions de filtrage"""
    
    def test_filtrer_par_emplacement(self, sample_articles_inventaire):
        """Filtre par emplacement"""
        result = filtrer_par_emplacement(sample_articles_inventaire, "Réfrigérateur")
        assert len(result) == 2  # Lait et Yaourt
        assert all(a["emplacement"] == "Réfrigérateur" for a in result)
    
    def test_filtrer_par_emplacement_tous(self, sample_articles_inventaire):
        """Filtre 'tous' retourne tout"""
        result = filtrer_par_emplacement(sample_articles_inventaire, "tous")
        assert len(result) == len(sample_articles_inventaire)
    
    def test_filtrer_par_categorie(self, sample_articles_inventaire):
        """Filtre par catégorie"""
        result = filtrer_par_categorie(sample_articles_inventaire, "Produits laitiers")
        assert len(result) == 2  # Lait et Yaourt
    
    def test_filtrer_par_categorie_toutes(self, sample_articles_inventaire):
        """Filtre 'toutes' retourne tout"""
        result = filtrer_par_categorie(sample_articles_inventaire, "toutes")
        assert len(result) == len(sample_articles_inventaire)
    
    def test_filtrer_par_status(self, sample_articles_inventaire):
        """Filtre par statut calculé"""
        result = filtrer_par_status(sample_articles_inventaire, "perime")
        # Le poulet est périmé
        assert any(a["ingredient_nom"] == "Poulet" for a in result)
    
    def test_filtrer_par_recherche(self, sample_articles_inventaire):
        """Filtre par recherche textuelle"""
        result = filtrer_par_recherche(sample_articles_inventaire, "lait")
        assert len(result) == 1
        assert result[0]["ingredient_nom"] == "Lait"
    
    def test_filtrer_inventaire_combinaison(self, sample_articles_inventaire):
        """Filtrage combiné"""
        result = filtrer_inventaire(
            sample_articles_inventaire,
            emplacement="Réfrigérateur",
            categorie="Produits laitiers"
        )
        assert len(result) == 2  # Lait et Yaourt


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES
# ═══════════════════════════════════════════════════════════

class TestAlertes:
    """Tests pour les fonctions d'alertes"""
    
    def test_calculer_alertes(self, sample_articles_inventaire):
        """Calcule toutes les alertes"""
        alertes = calculer_alertes(sample_articles_inventaire)
        
        assert "critique" in alertes
        assert "stock_bas" in alertes
        assert "perime" in alertes
        assert "bientot_perime" in alertes
        
        # Le lait est en stock_bas (3 < 5)
        assert any(a["ingredient_nom"] == "Lait" for a in alertes["stock_bas"])
        
        # Le poulet est périmé
        assert any(a["ingredient_nom"] == "Poulet" for a in alertes["perime"])
        
        # Le yaourt périme bientôt
        assert any(a["ingredient_nom"] == "Yaourt" for a in alertes["bientot_perime"])
    
    def test_compter_alertes(self, sample_articles_inventaire):
        """Compte les alertes"""
        alertes = calculer_alertes(sample_articles_inventaire)
        counts = compter_alertes(alertes)
        
        assert isinstance(counts, dict)
        assert all(isinstance(v, int) for v in counts.values())
    
    def test_alertes_critiques_existent_true(self, sample_articles_inventaire):
        """Détecte les alertes critiques"""
        alertes = calculer_alertes(sample_articles_inventaire)
        # Il y a au moins un périmé
        assert alertes_critiques_existent(alertes)
    
    def test_alertes_critiques_existent_false(self):
        """Pas d'alertes critiques"""
        alertes = {"critique": [], "stock_bas": [], "perime": [], "bientot_perime": []}
        assert not alertes_critiques_existent(alertes)


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════

class TestStatistiques:
    """Tests pour les fonctions de statistiques"""
    
    def test_calculer_statistiques_inventaire(self, sample_articles_inventaire):
        """Statistiques générales"""
        stats = calculer_statistiques_inventaire(sample_articles_inventaire)
        
        assert stats["total_articles"] == 4
        assert "valeur_totale" in stats
        assert "articles_ok" in stats
        assert "articles_alerte" in stats
        assert "pct_ok" in stats
    
    def test_calculer_statistiques_inventaire_vide(self):
        """Statistiques avec inventaire vide"""
        stats = calculer_statistiques_inventaire([])
        
        assert stats["total_articles"] == 0
        assert stats["valeur_totale"] == 0
    
    def test_calculer_statistiques_par_emplacement(self, sample_articles_inventaire):
        """Statistiques par emplacement"""
        stats = calculer_statistiques_par_emplacement(sample_articles_inventaire)
        
        assert "Réfrigérateur" in stats
        assert "Congélateur" in stats
        assert "Garde-manger" in stats
        
        assert stats["Réfrigérateur"]["count"] == 2
    
    def test_calculer_statistiques_par_categorie(self, sample_articles_inventaire):
        """Statistiques par catégorie"""
        stats = calculer_statistiques_par_categorie(sample_articles_inventaire)
        
        assert "Produits laitiers" in stats
        assert stats["Produits laitiers"]["count"] == 2


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════

class TestValidation:
    """Tests pour les fonctions de validation"""
    
    def test_valider_article_valide(self):
        """Article valide"""
        article = {
            "ingredient_nom": "Test",
            "quantite": 5,
            "seuil_alerte": 5,
            "seuil_critique": 2,
        }
        est_valide, erreurs = valider_article_inventaire(article)
        assert est_valide
        assert len(erreurs) == 0
    
    def test_valider_article_nom_manquant(self):
        """Nom manquant"""
        article = {"quantite": 5}
        est_valide, erreurs = valider_article_inventaire(article)
        assert not est_valide
        assert any("nom" in e.lower() for e in erreurs)
    
    def test_valider_article_quantite_negative(self):
        """Quantité négative"""
        article = {"ingredient_nom": "Test", "quantite": -1}
        est_valide, erreurs = valider_article_inventaire(article)
        assert not est_valide
        assert any("négative" in e for e in erreurs)
    
    def test_valider_article_seuils_incoherents(self):
        """Seuils incohérents"""
        article = {
            "ingredient_nom": "Test",
            "quantite": 5,
            "seuil_alerte": 2,  # Plus petit
            "seuil_critique": 5,  # Plus grand
        }
        est_valide, erreurs = valider_article_inventaire(article)
        assert not est_valide
        assert any("seuil" in e.lower() for e in erreurs)
    
    def test_valider_nouvel_article_valide(self):
        """Création valide"""
        est_valide, result = valider_nouvel_article_inventaire(
            nom="Test",
            quantite=5,
            unite="kg",
            emplacement="Réfrigérateur",
            categorie="Autre"
        )
        assert est_valide
        assert result["ingredient_nom"] == "Test"
        assert "date_ajout" in result
    
    def test_valider_nouvel_article_invalide(self):
        """Création invalide"""
        est_valide, result = valider_nouvel_article_inventaire(
            nom="",
            quantite=-1,
            unite="kg"
        )
        assert not est_valide
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# TESTS FORMATAGE
# ═══════════════════════════════════════════════════════════

class TestFormatage:
    """Tests pour les fonctions de formatage"""
    
    def test_formater_article_label(self, sample_articles_inventaire):
        """Label d'article"""
        article = sample_articles_inventaire[0]  # Lait
        label = formater_article_label(article)
        
        assert "Lait" in label
        assert "3" in label
        assert "L" in label
    
    def test_formater_article_label_perime(self):
        """Label pour article périmé"""
        article = {
            "ingredient_nom": "Test",
            "quantite": 1,
            "unite": "kg",
            "date_peremption": date.today() - timedelta(days=1),
            "seuil_alerte": 5,
            "seuil_critique": 2,
        }
        label = formater_article_label(article)
        assert "⚫" in label  # emoji périmé
    
    def test_formater_inventaire_rapport(self, sample_articles_inventaire):
        """Rapport d'inventaire"""
        rapport = formater_inventaire_rapport(sample_articles_inventaire)
        
        assert "RAPPORT D'INVENTAIRE" in rapport
        assert "RÉSUMÉ" in rapport
        assert "PAR EMPLACEMENT" in rapport


# ═══════════════════════════════════════════════════════════
# TESTS UTILITAIRES
# ═══════════════════════════════════════════════════════════

class TestUtilitaires:
    """Tests pour les fonctions utilitaires"""
    
    def test_calculer_jours_avant_peremption(self):
        """Calcul des jours avant péremption"""
        article = {"date_peremption": date.today() + timedelta(days=5)}
        assert calculer_jours_avant_peremption(article) == 5
    
    def test_calculer_jours_avant_peremption_passe(self):
        """Jours négatifs si périmé"""
        article = {"date_peremption": date.today() - timedelta(days=3)}
        assert calculer_jours_avant_peremption(article) == -3
    
    def test_calculer_jours_avant_peremption_sans_date(self):
        """None si pas de date"""
        article = {}
        assert calculer_jours_avant_peremption(article) is None
    
    def test_grouper_par_emplacement(self, sample_articles_inventaire):
        """Groupement par emplacement"""
        groupes = grouper_par_emplacement(sample_articles_inventaire)
        
        assert "Réfrigérateur" in groupes
        assert len(groupes["Réfrigérateur"]) == 2
    
    def test_grouper_par_categorie(self, sample_articles_inventaire):
        """Groupement par catégorie"""
        groupes = grouper_par_categorie(sample_articles_inventaire)
        
        assert "Produits laitiers" in groupes
        assert len(groupes["Produits laitiers"]) == 2
    
    def test_trier_par_peremption(self, sample_articles_inventaire):
        """Tri par date de péremption"""
        result = trier_par_peremption(sample_articles_inventaire)
        
        # Le périmé (poulet) doit être en premier
        assert result[0]["ingredient_nom"] == "Poulet"
    
    def test_trier_par_urgence(self, sample_articles_inventaire):
        """Tri par urgence"""
        result = trier_par_urgence(sample_articles_inventaire)
        
        # Les périmés/critiques en premier
        first_status = calculer_status_global(result[0])["status_prioritaire"]
        assert first_status in ["perime", "critique"]


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════

class TestEdgeCases:
    """Tests pour les cas limites"""
    
    def test_filtrer_liste_vide(self):
        """Filtrer une liste vide"""
        assert filtrer_par_emplacement([], "Test") == []
        assert filtrer_par_categorie([], "Test") == []
        assert filtrer_par_status([], "Test") == []
    
    def test_alertes_liste_vide(self):
        """Alertes sur liste vide"""
        alertes = calculer_alertes([])
        assert alertes == {"critique": [], "stock_bas": [], "perime": [], "bientot_perime": []}
    
    def test_grouper_liste_vide(self):
        """Grouper une liste vide"""
        assert grouper_par_emplacement([]) == {}
        assert grouper_par_categorie([]) == {}
    
    def test_article_sans_emplacement(self):
        """Article sans emplacement -> 'Autre'"""
        articles = [{"ingredient_nom": "Test"}]
        groupes = grouper_par_emplacement(articles)
        assert "Autre" in groupes
    
    def test_article_sans_categorie(self):
        """Article sans catégorie -> 'Autre'"""
        articles = [{"ingredient_nom": "Test"}]
        groupes = grouper_par_categorie(articles)
        assert "Autre" in groupes
    
    def test_date_peremption_format_invalide(self):
        """Date de péremption en format invalide"""
        article = {"date_peremption": "pas-une-date"}
        status = calculer_status_peremption(article)
        assert status == "ok"  # Traité comme pas de date
