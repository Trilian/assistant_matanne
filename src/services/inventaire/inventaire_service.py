"""
Service Inventaire - CRUD Optimisé

Service principal pour la gestion de l'inventaire avec :
- Opérations CRUD complètes
- Calcul automatique des statuts (stock bas, péremption)
- Recherche avancée
- Statistiques enrichies
- Gestion des seuils d'alerte
"""
import logging
from datetime import date, timedelta
from typing import Dict, List, Optional

from src.core import (
    BaseService,
    obtenir_contexte_db,
    handle_errors,
    Cache,
    ErreurValidation,
    ErreurNonTrouve,
)
from src.core.models import ArticleInventaire, Ingredient
from src.utils import find_or_create_ingredient

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES MÉTIER
# ═══════════════════════════════════════════════════════════

CATEGORIES = [
    "Légumes",
    "Fruits",
    "Féculents",
    "Protéines",
    "Laitier",
    "Épices & Condiments",
    "Conserves",
    "Surgelés",
    "Autre"
]

EMPLACEMENTS = [
    "Frigo",
    "Congélateur",
    "Placard",
    "Cave",
    "Garde-manger"
]


# ═══════════════════════════════════════════════════════════
# SERVICE INVENTAIRE
# ═══════════════════════════════════════════════════════════

class InventaireService(BaseService[ArticleInventaire]):
    """
    Service CRUD pour l'inventaire.

    Fonctionnalités spécifiques :
    - Calcul automatique des statuts (ok, sous_seuil, critique, peremption_proche)
    - Enrichissement avec données ingrédient
    - Alertes automatiques
    - Statistiques par catégorie/emplacement
    """

    def __init__(self):
        """Initialise le service avec cache 30min."""
        super().__init__(ArticleInventaire, cache_ttl=1800)

    # ═══════════════════════════════════════════════════════════
    # LECTURE ENRICHIE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_inventaire_complet(
            self,
            filters: Optional[Dict] = None,
            include_ok: bool = True
    ) -> List[Dict]:
        """
        Récupère l'inventaire complet avec statuts calculés.

        Args:
            filters: Filtres optionnels (categorie, emplacement, etc.)
            include_ok: Inclure les articles OK ou seulement les alertes

        Returns:
            Liste d'articles enrichis avec statuts

        Example:
            >>> inventaire = inventaire_service.get_inventaire_complet()
            >>> critiques = [a for a in inventaire if a["statut"] == "critique"]
        """
        # Charger articles avec ingrédients
        articles = self.get_all(filters=filters, limit=1000)

        result = []
        today = date.today()

        for article in articles:
            enriched = self._enrich_article(article, today)

            # Filtrer si demandé
            if not include_ok and enriched["statut"] == "ok":
                continue

            result.append(enriched)

        logger.debug(f"Inventaire complet: {len(result)} articles")
        return result

    def _enrich_article(self, article: ArticleInventaire, today: date) -> Dict:
        """
        Enrichit un article avec toutes les infos calculées.

        Args:
            article: Article inventaire
            today: Date du jour

        Returns:
            Dict enrichi avec statut, jours_peremption, etc.
        """
        # Données de base
        enriched = {
            "id": article.id,
            "ingredient_id": article.ingredient_id,
            "nom": article.ingredient.nom if article.ingredient else "Inconnu",
            "categorie": article.ingredient.categorie or "Autre" if article.ingredient else "Autre",
            "quantite": article.quantite,
            "unite": article.ingredient.unite if article.ingredient else "pcs",
            "quantite_min": article.quantite_min,
            "emplacement": article.emplacement,
            "date_peremption": article.date_peremption,
            "derniere_maj": article.derniere_maj,
        }

        # Calculer statut
        statut = "ok"
        jours_peremption = None

        # 1. Vérifier péremption
        if article.date_peremption:
            delta = (article.date_peremption - today).days
            jours_peremption = delta

            if delta <= 0:
                statut = "perime"
            elif delta <= 3:
                statut = "critique"  # Péremption imminente
            elif delta <= 7:
                statut = "peremption_proche"

        # 2. Vérifier stock
        if article.quantite < article.quantite_min * 0.5:
            # Stock critique (< 50% du seuil)
            if statut == "ok":
                statut = "critique"
        elif article.quantite < article.quantite_min:
            # Stock sous le seuil
            if statut == "ok":
                statut = "sous_seuil"

        enriched["statut"] = statut
        enriched["jours_peremption"] = jours_peremption

        return enriched

    # ═══════════════════════════════════════════════════════════
    # CRÉATION/MISE À JOUR
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=None)
    def create_article(self, article_data: Dict) -> int:
        """
        Crée un article inventaire.

        Args:
            article_data: Données article
                {"nom": "Tomates", "categorie": "Légumes", "quantite": 5, ...}

        Returns:
            ID de l'article créé
        """
        with obtenir_contexte_db() as db:
            # Trouver ou créer ingrédient
            ingredient_id = find_or_create_ingredient(
                nom=article_data["nom"],
                unite=article_data.get("unite", "pcs"),
                categorie=article_data.get("categorie", "Autre"),
                db=db
            )

            # Créer article
            article = ArticleInventaire(
                ingredient_id=ingredient_id,
                quantite=article_data["quantite"],
                quantite_min=article_data.get("quantite_min", 1.0),
                emplacement=article_data.get("emplacement"),
                date_peremption=article_data.get("date_peremption"),
            )

            db.add(article)
            db.commit()
            db.refresh(article)

            Cache.invalider(dependencies=["inventaire"])

            logger.info(f"Article inventaire créé: {article_data['nom']} (ID: {article.id})")
            return article.id

    @handle_errors(show_in_ui=True, fallback_value=False)
    def ajuster_stock(
            self,
            article_id: int,
            delta: float,
            raison: Optional[str] = None
    ) -> bool:
        """
        Ajuste le stock d'un article.

        Args:
            article_id: ID de l'article
            delta: Variation (+/-) de quantité
            raison: Raison de l'ajustement (optionnel)

        Returns:
            True si succès

        Example:
            >>> # Ajouter 2 kg
            >>> inventaire_service.ajuster_stock(42, +2.0, "Achat")
            >>> # Retirer 0.5 kg
            >>> inventaire_service.ajuster_stock(42, -0.5, "Utilisation")
        """
        with obtenir_contexte_db() as db:
            article = db.query(ArticleInventaire).get(article_id)

            if not article:
                raise ErreurNonTrouve(
                    f"Article {article_id} introuvable",
                    message_utilisateur="Article introuvable"
                )

            # Calculer nouvelle quantité (minimum 0)
            nouvelle_quantite = max(0, article.quantite + delta)

            article.quantite = nouvelle_quantite
            db.commit()

            Cache.invalider(dependencies=[f"inventaire_{article_id}", "inventaire"])

            logger.info(
                f"Stock ajusté: article {article_id} "
                f"({article.quantite} -> {nouvelle_quantite})"
                + (f" - {raison}" if raison else "")
            )

            return True

    # ═══════════════════════════════════════════════════════════
    # RECHERCHE & FILTRES
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_articles_alertes(self) -> List[Dict]:
        """
        Récupère uniquement les articles en alerte.

        Returns:
            Articles avec statut critique, sous_seuil ou peremption_proche
        """
        inventaire = self.get_inventaire_complet(include_ok=False)

        # Trier par priorité (critique > peremption_proche > sous_seuil)
        priorite = {"critique": 0, "peremption_proche": 1, "sous_seuil": 2}

        return sorted(
            inventaire,
            key=lambda a: priorite.get(a["statut"], 99)
        )

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_articles_peremption_proche(self, jours_max: int = 7) -> List[Dict]:
        """
        Récupère articles proches de la péremption.

        Args:
            jours_max: Nombre de jours maximum avant péremption

        Returns:
            Articles avec péremption <= jours_max
        """
        inventaire = self.get_inventaire_complet()

        return [
            a for a in inventaire
            if a.get("jours_peremption") is not None
               and 0 <= a["jours_peremption"] <= jours_max
        ]

    @handle_errors(show_in_ui=False, fallback_value=[])
    def search_articles(
            self,
            search_term: Optional[str] = None,
            categorie: Optional[str] = None,
            emplacement: Optional[str] = None,
            statut: Optional[str] = None,
            limit: int = 100
    ) -> List[Dict]:
        """
        Recherche multi-critères dans l'inventaire.

        Args:
            search_term: Terme de recherche (nom article)
            categorie: Filtrer par catégorie
            emplacement: Filtrer par emplacement
            statut: Filtrer par statut (ok, sous_seuil, etc.)
            limit: Nombre max de résultats

        Returns:
            Liste d'articles matchant
        """
        filters = {}

        if emplacement:
            filters["emplacement"] = emplacement

        inventaire = self.get_inventaire_complet(filters=filters)

        # Filtrer post-chargement
        results = inventaire

        if search_term:
            search_lower = search_term.lower()
            results = [
                a for a in results
                if search_lower in a["nom"].lower()
            ]

        if categorie:
            results = [a for a in results if a["categorie"] == categorie]

        if statut:
            results = [a for a in results if a["statut"] == statut]

        return results[:limit]

    # ═══════════════════════════════════════════════════════════
    # STATISTIQUES
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value={})
    def get_stats_inventaire(self) -> Dict:
        """
        Retourne statistiques complètes de l'inventaire.

        Returns:
            Dict avec stats par catégorie, emplacement, statut
        """
        inventaire = self.get_inventaire_complet()

        # Grouper par catégorie
        by_categorie = {}
        by_emplacement = {}
        by_statut = {"ok": 0, "sous_seuil": 0, "critique": 0, "peremption_proche": 0}

        for article in inventaire:
            # Par catégorie
            cat = article["categorie"]
            by_categorie[cat] = by_categorie.get(cat, 0) + 1

            # Par emplacement
            emp = article["emplacement"] or "Non défini"
            by_emplacement[emp] = by_emplacement.get(emp, 0) + 1

            # Par statut
            statut = article["statut"]
            if statut in by_statut:
                by_statut[statut] += 1

        return {
            "total": len(inventaire),
            "by_categorie": by_categorie,
            "by_emplacement": by_emplacement,
            "by_statut": by_statut,
            "nb_alertes": by_statut["critique"] + by_statut["sous_seuil"] + by_statut["peremption_proche"],
        }


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON
# ═══════════════════════════════════════════════════════════

inventaire_service = InventaireService()