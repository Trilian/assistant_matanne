"""
Service Inventaire - CRUD et Logique Métier
Version refactorisée avec prédictions et alertes
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from src.core.database import get_db_context
from src.core.models import (
    ArticleInventaire,
    Ingredient,
    ArticleCourses,
    Recette,
    RecetteIngredient,
)
from src.utils.formatters import format_quantity, format_quantity_with_unit


from src.core.base_service import BaseService

# Formatters (après les imports de base pour éviter import circulaire)
from src.utils.formatters import format_quantity, format_quantity_with_unit

logger = logging.getLogger(__name__)


# ===================================
# CONSTANTES
# ===================================

CATEGORIES = [
    "Légumes",
    "Fruits",
    "Féculents",
    "Protéines",
    "Laitier",
    "Épices",
    "Huiles",
    "Conserves",
    "Autre",
]

EMPLACEMENTS = ["Frigo", "Congélateur", "Placard", "Cave", "Autre"]

JOURS_ALERTE_PEREMPTION = 7


# ===================================
# HELPERS STATUT
# ===================================


def calculer_statut_article(
    quantite: float, seuil: float, date_peremption: Optional[date]
) -> Tuple[str, str]:
    """
    Calcule le statut d'un article

    Returns:
        (statut: str, icone: str)
        Statuts: "ok", "sous_seuil", "peremption_proche", "critique"
    """
    sous_seuil = quantite < seuil

    peremption_proche = False
    if date_peremption:
        jours_restants = (date_peremption - date.today()).days
        peremption_proche = 0 <= jours_restants <= JOURS_ALERTE_PEREMPTION

    if sous_seuil and peremption_proche:
        return "critique", "🔴"
    elif peremption_proche:
        return "peremption_proche", "⏳"
    elif sous_seuil:
        return "sous_seuil", "⚠️"
    else:
        return "ok", "✅"


def get_jours_avant_peremption(date_peremption: Optional[date]) -> Optional[int]:
    """Calcule jours avant péremption"""
    if not date_peremption:
        return None

    delta = (date_peremption - date.today()).days
    return delta if delta >= 0 else 0


# ===================================
# SERVICE PRINCIPAL
# ===================================


class InventaireService(BaseService[ArticleInventaire]):
    """Service complet de gestion d'inventaire"""

    def __init__(self):
        super().__init__(ArticleInventaire)

    # ===================================
    # LECTURE ENRICHIE
    # ===================================

    def get_inventaire_complet(
        self, filters: Optional[Dict] = None, db: Session = None
    ) -> List[Dict]:
        """
        Récupère l'inventaire complet avec toutes les infos

        Returns:
            Liste de dicts enrichis avec statut, alertes, etc.
        """
        if db:
            return self._do_get_inventaire(db, filters)

        with get_db_context() as db:
            return self._do_get_inventaire(db, filters)

    def _do_get_inventaire(self, db: Session, filters: Optional[Dict]) -> List[Dict]:
        """Implémentation"""
        query = db.query(
            ArticleInventaire.id,
            Ingredient.nom,
            Ingredient.categorie,
            ArticleInventaire.quantite,
            Ingredient.unite,
            ArticleInventaire.quantite_min,
            ArticleInventaire.emplacement,
            ArticleInventaire.date_peremption,
            ArticleInventaire.derniere_maj,
        ).join(Ingredient, ArticleInventaire.ingredient_id == Ingredient.id)

        # Appliquer filtres
        if filters:
            if filters.get("categorie"):
                query = query.filter(Ingredient.categorie == filters["categorie"])
            if filters.get("emplacement"):
                query = query.filter(ArticleInventaire.emplacement == filters["emplacement"])
            if filters.get("sous_seuil_only"):
                query = query.filter(ArticleInventaire.quantite < ArticleInventaire.quantite_min)

        items = query.order_by(Ingredient.nom).all()

        # Enrichir avec statuts
        result = []
        for item in items:
            statut, icone = calculer_statut_article(
                item.quantite, item.quantite_min, item.date_peremption
            )

            jours_peremption = get_jours_avant_peremption(item.date_peremption)

            result.append(
                {
                    "id": item.id,
                    "nom": item.nom,
                    "categorie": item.categorie or "Autre",
                    "quantite": item.quantite,
                    "unite": item.unite,
                    "seuil": item.quantite_min,
                    "emplacement": item.emplacement or "—",
                    "date_peremption": item.date_peremption,
                    "jours_peremption": jours_peremption,
                    "derniere_maj": item.derniere_maj,
                    "statut": statut,
                    "icone": icone,
                }
            )

        return result

    def get_alertes(self, db: Session = None) -> Dict[str, List[Dict]]:
        """
        Récupère toutes les alertes critiques

        Returns:
            Dict avec {stock_bas: [...], peremption_proche: [...], critiques: [...]}
        """
        inventaire = self.get_inventaire_complet(db=db)

        alertes = {"stock_bas": [], "peremption_proche": [], "critiques": []}

        for item in inventaire:
            if item["statut"] == "critique":
                alertes["critiques"].append(item)
            elif item["statut"] == "sous_seuil":
                alertes["stock_bas"].append(item)
            elif item["statut"] == "peremption_proche":
                alertes["peremption_proche"].append(item)

        return alertes

    # ===================================
    # AJOUT / MODIFICATION
    # ===================================

    def ajouter_ou_modifier(
        self,
        nom: str,
        categorie: str,
        quantite: float,
        unite: str,
        seuil: float,
        emplacement: Optional[str] = None,
        date_peremption: Optional[date] = None,
        article_id: Optional[int] = None,
        db: Session = None,
    ) -> int:
        """
        Ajoute ou modifie un article

        Returns:
            ID de l'article
        """
        if db:
            return self._do_ajouter_modifier(
                db, nom, categorie, quantite, unite, seuil, emplacement, date_peremption, article_id
            )

        with get_db_context() as db:
            return self._do_ajouter_modifier(
                db, nom, categorie, quantite, unite, seuil, emplacement, date_peremption, article_id
            )

    def _do_ajouter_modifier(
        self,
        db: Session,
        nom: str,
        categorie: str,
        quantite: float,
        unite: str,
        seuil: float,
        emplacement: Optional[str],
        date_peremption: Optional[date],
        article_id: Optional[int],
    ) -> int:
        """Implémentation"""
        # Trouver/créer ingrédient
        ingredient = db.query(Ingredient).filter(Ingredient.nom == nom).first()

        if not ingredient:
            ingredient = Ingredient(nom=nom, unite=unite, categorie=categorie)
            db.add(ingredient)
            db.flush()

        if article_id:
            # Modification
            article = db.query(ArticleInventaire).get(article_id)
            if article:
                article.quantite = quantite
                article.quantite_min = seuil
                article.emplacement = emplacement
                article.date_peremption = date_peremption
                article.derniere_maj = datetime.now()
                db.commit()
                logger.info(f"Article {article_id} modifié")
                return article_id

        # Vérifier si existe déjà
        existant = (
            db.query(ArticleInventaire)
            .filter(ArticleInventaire.ingredient_id == ingredient.id)
            .first()
        )

        if existant:
            # Mise à jour
            existant.quantite += quantite
            existant.quantite_min = seuil
            existant.derniere_maj = datetime.now()
            db.commit()
            logger.info(f"Article existant mis à jour: {nom}")
            return existant.id

        # Création
        article = ArticleInventaire(
            ingredient_id=ingredient.id,
            quantite=quantite,
            quantite_min=seuil,
            emplacement=emplacement,
            date_peremption=date_peremption,
        )
        db.add(article)
        db.commit()
        db.refresh(article)

        logger.info(f"Nouvel article créé: {nom}")
        return article.id

    # ===================================
    # AJUSTEMENT QUANTITÉ
    # ===================================

    def ajuster_quantite(
        self, article_id: int, delta: float, raison: Optional[str] = None, db: Session = None
    ) -> Optional[float]:
        """
        Ajuste la quantité (+ ou -)

        Returns:
            Nouvelle quantité ou None si erreur
        """
        if db:
            article = db.query(ArticleInventaire).get(article_id)
            if article:
                article.quantite = max(0, article.quantite + delta)
                article.derniere_maj = datetime.now()
                db.commit()
                logger.info(f"Quantité ajustée: {article_id} ({delta:+.1f})")
                return article.quantite
            return None

        with get_db_context() as db:
            article = db.query(ArticleInventaire).get(article_id)
            if article:
                article.quantite = max(0, article.quantite + delta)
                article.derniere_maj = datetime.now()
                db.commit()
                logger.info(f"Quantité ajustée: {article_id} ({delta:+.1f})")
                return article.quantite
            return None

    # ===================================
    # INTÉGRATION COURSES
    # ===================================

    def ajouter_a_courses(
        self, article_id: int, quantite: Optional[float] = None, db: Session = None
    ) -> bool:
        """
        Ajoute un article à la liste de courses

        Args:
            article_id: ID article inventaire
            quantite: Quantité (si None, calcule manque)

        Returns:
            True si ajouté
        """
        if db:
            return self._do_ajouter_courses(db, article_id, quantite)

        with get_db_context() as db:
            return self._do_ajouter_courses(db, article_id, quantite)

    def _do_ajouter_courses(self, db: Session, article_id: int, quantite: Optional[float]) -> bool:
        """Implémentation"""
        article = db.query(ArticleInventaire).get(article_id)

        if not article:
            return False

        # Calculer quantité manquante
        if quantite is None:
            quantite = max(article.quantite_min - article.quantite, article.quantite_min)

        # Vérifier si déjà dans courses
        existant = (
            db.query(ArticleCourses)
            .filter(
                ArticleCourses.ingredient_id == article.ingredient_id,
                ArticleCourses.achete == False,
            )
            .first()
        )

        if existant:
            existant.quantite_necessaire = max(existant.quantite_necessaire, quantite)
        else:
            course = ArticleCourses(
                ingredient_id=article.ingredient_id,
                quantite_necessaire=quantite,
                priorite="haute",
                suggere_par_ia=False,
            )
            db.add(course)

        db.commit()
        logger.info(f"Article {article_id} ajouté aux courses")
        return True

    # ===================================
    # VÉRIFICATION RECETTE
    # ===================================

    def verifier_faisabilite_recette(
        self, recette_id: int, db: Session = None
    ) -> Tuple[bool, List[str]]:
        """
        Vérifie si une recette est faisable avec le stock

        Returns:
            (faisable: bool, manquants: List[str])
        """
        if db:
            return self._do_verifier_recette(db, recette_id)

        with get_db_context() as db:
            return self._do_verifier_recette(db, recette_id)

    def _do_verifier_recette(self, db: Session, recette_id: int) -> Tuple[bool, List[str]]:
        """Implémentation"""
        recette = db.query(Recette).get(recette_id)

        if not recette:
            return False, ["Recette introuvable"]

        manquants = []

        for recette_ing in recette.ingredients:
            stock = (
                db.query(ArticleInventaire)
                .filter(ArticleInventaire.ingredient_id == recette_ing.ingredient_id)
                .first()
            )

            qty_dispo = stock.quantite if stock else 0

            if qty_dispo < recette_ing.quantite:
                manque = recette_ing.quantite - qty_dispo
                manquants.append(
                    f"{recette_ing.ingredient.nom} (manque: {format_quantity(manque)} {recette_ing.unite})"
                )

        return len(manquants) == 0, manquants

    def deduire_recette(self, recette_id: int, db: Session = None) -> Tuple[bool, str]:
        """
        Déduit les ingrédients d'une recette du stock

        Returns:
            (succès: bool, message: str)
        """
        if db:
            return self._do_deduire_recette(db, recette_id)

        with get_db_context() as db:
            return self._do_deduire_recette(db, recette_id)

    def _do_deduire_recette(self, db: Session, recette_id: int) -> Tuple[bool, str]:
        """Implémentation"""
        faisable, manquants = self._do_verifier_recette(db, recette_id)

        if not faisable:
            return False, f"Stock insuffisant: {', '.join(manquants[:3])}"

        recette = db.query(Recette).get(recette_id)

        for recette_ing in recette.ingredients:
            stock = (
                db.query(ArticleInventaire)
                .filter(ArticleInventaire.ingredient_id == recette_ing.ingredient_id)
                .first()
            )

            if stock:
                stock.quantite = max(0, stock.quantite - recette_ing.quantite)
                stock.derniere_maj = datetime.now()

        db.commit()
        logger.info(f"Recette {recette_id} déduite du stock")
        return True, f"Stock mis à jour pour '{recette.nom}'"

    # ===================================
    # STATISTIQUES
    # ===================================

    def get_stats(self, db: Session = None) -> Dict:
        """
        Statistiques complètes

        Returns:
            Dict avec métriques diverses
        """
        if db:
            inventaire = self._do_get_inventaire(db, None)
        else:
            inventaire = self.get_inventaire_complet()

        alertes = {"critiques": 0, "stock_bas": 0, "peremption_proche": 0}

        categories_count = {}

        for item in inventaire:
            if item["statut"] == "critique":
                alertes["critiques"] += 1
            elif item["statut"] == "sous_seuil":
                alertes["stock_bas"] += 1
            elif item["statut"] == "peremption_proche":
                alertes["peremption_proche"] += 1

            cat = item["categorie"]
            categories_count[cat] = categories_count.get(cat, 0) + 1

        return {
            "total_articles": len(inventaire),
            "total_critiques": alertes["critiques"],
            "total_stock_bas": alertes["stock_bas"],
            "total_peremption": alertes["peremption_proche"],
            "categories": categories_count,
            "emplacements": {},  # TODO si besoin
        }


# ===================================
# INSTANCE GLOBALE
# ===================================

inventaire_service = InventaireService()
