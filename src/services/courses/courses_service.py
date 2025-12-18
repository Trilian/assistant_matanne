"""
Service Courses - CRUD et Logique Métier
Version refactorisée - Tout en un endroit
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import logging

from src.core.database import get_db_context
from src.core.models import (
from src.utils.formatters import format_quantity, format_quantity_with_unit
    ArticleCourses, Ingredient, ArticleInventaire,
    Recette, RecetteIngredient, RepasPlanning, PlanningHebdomadaire
)
from src.core.base_service import BaseService

logger = logging.getLogger(__name__)


# ===================================
# CONSTANTES
# ===================================

MAGASINS_CONFIG = {
    "Grand Frais": {
        "rayons": ["Fruits & Légumes", "Boucherie", "Poissonnerie", "Fromage", "Traiteur", "Boulangerie", "Epicerie"],
        "couleur": "#4CAF50",
        "specialite": "frais"
    },
    "Thiriet": {
        "rayons": ["Entrées", "Poissons", "Viandes", "Plats Cuisinés", "Légumes", "Desserts", "Pain"],
        "couleur": "#2196F3",
        "specialite": "surgelés"
    },
    "Cora": {
        "rayons": ["Fruits & Légumes", "Boucherie", "Poissonnerie", "Crèmerie", "Epicerie", "Surgelés", "Boissons"],
        "couleur": "#FF5722",
        "specialite": "tout"
    }
}


# ===================================
# SERVICE PRINCIPAL
# ===================================

class CoursesService(BaseService[ArticleCourses]):
    """Service complet pour la gestion des courses"""

    def __init__(self):
        super().__init__(ArticleCourses)

    # ===================================
    # LECTURE OPTIMISÉE
    # ===================================

    def get_liste_active(
            self,
            filters: Optional[Dict] = None,
            db: Session = None
    ) -> List[Dict]:
        """
        Liste active avec toutes les infos

        Returns:
            Liste de dicts enrichis {id, nom, quantite, unite, priorite, ia, etc.}
        """
        if db:
            return self._do_get_liste(db, achetes=False, filters=filters)

        with get_db_context() as db:
            return self._do_get_liste(db, achetes=False, filters=filters)

    def get_liste_achetee(
            self,
            jours: int = 30,
            db: Session = None
    ) -> List[Dict]:
        """Historique des achats"""
        if db:
            return self._do_get_liste(db, achetes=True, jours=jours)

        with get_db_context() as db:
            return self._do_get_liste(db, achetes=True, jours=jours)

    def _do_get_liste(
            self,
            db: Session,
            achetes: bool,
            filters: Optional[Dict] = None,
            jours: Optional[int] = None
    ) -> List[Dict]:
        """Implémentation interne"""
        query = db.query(
            ArticleCourses.id,
            Ingredient.nom,
            Ingredient.categorie,
            ArticleCourses.quantite_necessaire,
            Ingredient.unite,
            ArticleCourses.priorite,
            ArticleCourses.achete,
            ArticleCourses.suggere_par_ia,
            ArticleCourses.rayon_magasin,
            ArticleCourses.magasin_cible,
            ArticleCourses.notes,
            ArticleCourses.cree_le,
            ArticleCourses.achete_le
        ).join(
            Ingredient, ArticleCourses.ingredient_id == Ingredient.id
        ).filter(
            ArticleCourses.achete == achetes
        )

        # Filtre temporel pour historique
        if achetes and jours:
            date_limite = datetime.now() - timedelta(days=jours)
            query = query.filter(ArticleCourses.achete_le >= date_limite)

        # Filtres additionnels
        if filters:
            if filters.get("priorite"):
                query = query.filter(ArticleCourses.priorite == filters["priorite"])
            if filters.get("magasin"):
                query = query.filter(ArticleCourses.magasin_cible == filters["magasin"])
            if filters.get("ia_only"):
                query = query.filter(ArticleCourses.suggere_par_ia == True)

        # Tri
        if achetes:
            query = query.order_by(ArticleCourses.achete_le.desc())
        else:
            query = query.order_by(
                ArticleCourses.priorite.desc(),
                Ingredient.nom
            )

        items = query.all()

        return [{
            "id": i.id,
            "nom": i.nom,
            "categorie": i.categorie or "Autre",
            "quantite": i.quantite_necessaire,
            "unite": i.unite,
            "priorite": i.priorite,
            "achete": i.achete,
            "ia": i.suggere_par_ia,
            "rayon": i.rayon_magasin,
            "magasin": i.magasin_cible,
            "notes": i.notes,
            "cree_le": i.cree_le,
            "achete_le": i.achete_le
        } for i in items]

    def get_organisation_par_rayons(
            self,
            magasin: str,
            db: Session = None
    ) -> Dict[str, List[Dict]]:
        """
        Organise la liste par rayons du magasin

        Returns:
            {"Rayon1": [articles...], "Rayon2": [...]}
        """
        items = self.get_liste_active(db=db)

        rayons_config = MAGASINS_CONFIG.get(magasin, {}).get("rayons", ["Autre"])

        organisation = {rayon: [] for rayon in rayons_config}
        organisation["Autre"] = []

        for item in items:
            rayon = item.get("rayon") or "Autre"
            if rayon in organisation:
                organisation[rayon].append(item)
            else:
                organisation["Autre"].append(item)

        # Supprimer rayons vides
        return {k: v for k, v in organisation.items() if v}

    # ===================================
    # CRÉATION / MODIFICATION
    # ===================================

    def ajouter(
            self,
            nom: str,
            quantite: float,
            unite: str,
            priorite: str = "moyenne",
            rayon: Optional[str] = None,
            magasin: Optional[str] = None,
            ia_suggere: bool = False,
            notes: Optional[str] = None,
            db: Session = None
    ) -> int:
        """
        Ajoute un article (ou fusionne si existe)

        Returns:
            ID de l'article créé/modifié
        """
        if db:
            return self._do_ajouter(db, nom, quantite, unite, priorite, rayon, magasin, ia_suggere, notes)

        with get_db_context() as db:
            return self._do_ajouter(db, nom, quantite, unite, priorite, rayon, magasin, ia_suggere, notes)

    def _do_ajouter(
            self,
            db: Session,
            nom: str,
            quantite: float,
            unite: str,
            priorite: str,
            rayon: Optional[str],
            magasin: Optional[str],
            ia_suggere: bool,
            notes: Optional[str]
    ) -> int:
        """Implémentation interne"""
        # Trouver/créer ingrédient
        ingredient = db.query(Ingredient).filter(
            Ingredient.nom == nom
        ).first()

        if not ingredient:
            ingredient = Ingredient(nom=nom, unite=unite)
            db.add(ingredient)
            db.flush()

        # Vérifier si existe déjà (non acheté)
        existant = db.query(ArticleCourses).filter(
            ArticleCourses.ingredient_id == ingredient.id,
            ArticleCourses.achete == False
        ).first()

        if existant:
            # Fusion intelligente
            existant.quantite_necessaire = max(existant.quantite_necessaire, quantite)

            # Upgrade priorité si nécessaire
            priorites = {"basse": 1, "moyenne": 2, "haute": 3}
            if priorites.get(priorite, 2) > priorites.get(existant.priorite, 2):
                existant.priorite = priorite

            # Conserver notes
            if notes:
                existant.notes = f"{existant.notes or ''}\n{notes}".strip()

            db.commit()
            article_id = existant.id
            logger.info(f"Article fusionné: {nom}")
        else:
            # Création
            article = ArticleCourses(
                ingredient_id=ingredient.id,
                quantite_necessaire=quantite,
                priorite=priorite,
                suggere_par_ia=ia_suggere,
                rayon_magasin=rayon,
                magasin_cible=magasin,
                notes=notes
            )
            db.add(article)
            db.flush()
            article_id = article.id
            db.commit()
            logger.info(f"Article créé: {nom}")

        return article_id

    def ajouter_batch(
            self,
            articles: List[Dict],
            db: Session = None
    ) -> int:
        """
        Ajoute plusieurs articles en batch

        Args:
            articles: Liste de dicts avec {nom, quantite, unite, priorite, ...}

        Returns:
            Nombre d'articles ajoutés
        """
        if db:
            count = 0
            for art in articles:
                self._do_ajouter(
                    db,
                    art["nom"],
                    art["quantite"],
                    art["unite"],
                    art.get("priorite", "moyenne"),
                    art.get("rayon"),
                    art.get("magasin"),
                    art.get("ia", False),
                    art.get("notes")
                )
                count += 1
            return count

        with get_db_context() as db:
            count = 0
            for art in articles:
                self._do_ajouter(
                    db,
                    art["nom"],
                    art["quantite"],
                    art["unite"],
                    art.get("priorite", "moyenne"),
                    art.get("rayon"),
                    art.get("magasin"),
                    art.get("ia", False),
                    art.get("notes")
                )
                count += 1
            return count

    def modifier_quantite(
            self,
            article_id: int,
            nouvelle_quantite: float,
            db: Session = None
    ) -> bool:
        """Modifie la quantité d'un article"""
        if db:
            article = db.query(ArticleCourses).get(article_id)
            if article:
                article.quantite_necessaire = nouvelle_quantite
                db.commit()
                return True
            return False

        with get_db_context() as db:
            article = db.query(ArticleCourses).get(article_id)
            if article:
                article.quantite_necessaire = nouvelle_quantite
                db.commit()
                return True
            return False

    # ===================================
    # ACHAT
    # ===================================

    def marquer_achete(
            self,
            article_id: int,
            ajouter_au_stock: bool = False,
            db: Session = None
    ) -> bool:
        """
        Marque un article comme acheté

        Args:
            article_id: ID article
            ajouter_au_stock: Si True, ajoute automatiquement à l'inventaire
        """
        if db:
            return self._do_marquer_achete(db, article_id, ajouter_au_stock)

        with get_db_context() as db:
            return self._do_marquer_achete(db, article_id, ajouter_au_stock)

    def _do_marquer_achete(
            self,
            db: Session,
            article_id: int,
            ajouter_au_stock: bool
    ) -> bool:
        """Implémentation interne"""
        article = db.query(ArticleCourses).get(article_id)

        if not article:
            return False

        article.achete = True
        article.achete_le = datetime.now()

        # Ajout au stock si demandé
        if ajouter_au_stock:
            stock = db.query(ArticleInventaire).filter(
                ArticleInventaire.ingredient_id == article.ingredient_id
            ).first()

            if stock:
                stock.quantite += article.quantite_necessaire
                stock.derniere_maj = datetime.now()
            else:
                stock = ArticleInventaire(
                    ingredient_id=article.ingredient_id,
                    quantite=article.quantite_necessaire,
                    quantite_min=1.0
                )
                db.add(stock)

        db.commit()
        logger.info(f"Article {article_id} marqué acheté (stock: {ajouter_au_stock})")
        return True

    def marquer_tous_achetes(
            self,
            article_ids: List[int],
            ajouter_au_stock: bool = False,
            db: Session = None
    ) -> int:
        """Marque plusieurs articles comme achetés"""
        if db:
            count = 0
            for aid in article_ids:
                if self._do_marquer_achete(db, aid, ajouter_au_stock):
                    count += 1
            return count

        with get_db_context() as db:
            count = 0
            for aid in article_ids:
                if self._do_marquer_achete(db, aid, ajouter_au_stock):
                    count += 1
            return count

    # ===================================
    # NETTOYAGE
    # ===================================

    def nettoyer_achetes(
            self,
            jours: int = 30,
            db: Session = None
    ) -> int:
        """
        Supprime les articles achetés de plus de X jours

        Returns:
            Nombre supprimé
        """
        if db:
            date_limite = datetime.now() - timedelta(days=jours)
            count = db.query(ArticleCourses).filter(
                ArticleCourses.achete == True,
                ArticleCourses.achete_le < date_limite
            ).delete()
            db.commit()
            logger.info(f"{count} articles achetés nettoyés (>{jours}j)")
            return count

        with get_db_context() as db:
            date_limite = datetime.now() - timedelta(days=jours)
            count = db.query(ArticleCourses).filter(
                ArticleCourses.achete == True,
                ArticleCourses.achete_le < date_limite
            ).delete()
            db.commit()
            logger.info(f"{count} articles achetés nettoyés (>{jours}j)")
            return count

    # ===================================
    # GÉNÉRATION AUTOMATIQUE
    # ===================================

    def generer_depuis_stock_bas(
            self,
            db: Session = None
    ) -> List[Dict]:
        """
        Génère suggestions depuis stock bas

        Returns:
            Liste de dicts {nom, quantite, unite, priorite, raison}
        """
        if db:
            return self._do_generer_stock_bas(db)

        with get_db_context() as db:
            return self._do_generer_stock_bas(db)

    def _do_generer_stock_bas(self, db: Session) -> List[Dict]:
        """Implémentation"""
        items = db.query(
            Ingredient.nom,
            Ingredient.unite,
            ArticleInventaire.quantite,
            ArticleInventaire.quantite_min
        ).join(
            ArticleInventaire,
            Ingredient.id == ArticleInventaire.ingredient_id
        ).filter(
            ArticleInventaire.quantite < ArticleInventaire.quantite_min
        ).all()

        suggestions = []
        for nom, unite, qty, seuil in items:
            manque = max(seuil - qty, seuil)
            suggestions.append({
                "nom": nom,
                "quantite": manque,
                "unite": unite,
                "priorite": "haute",
                "raison": f"Stock: {qty:.1f}/{format_quantity(seuil)}"
            })

        logger.info(f"{len(suggestions)} articles en stock bas détectés")
        return suggestions

    def generer_depuis_repas_planifies(
            self,
            jours: int = 7,
            db: Session = None
    ) -> List[Dict]:
        """
        Génère depuis repas planifiés

        Returns:
            Liste consolidée d'articles
        """
        if db:
            return self._do_generer_repas(db, jours)

        with get_db_context() as db:
            return self._do_generer_repas(db, jours)

    def _do_generer_repas(self, db: Session, jours: int) -> List[Dict]:
        """Implémentation"""
        today = date.today()
        date_fin = today + timedelta(days=jours)

        # Récupérer recettes planifiées
        repas = db.query(
            Recette.id,
            Recette.nom
        ).join(
            RepasPlanning,
            Recette.id == RepasPlanning.recette_id
        ).filter(
            RepasPlanning.date.between(today, date_fin),
            RepasPlanning.statut != "terminé"
        ).all()

        # Consolider ingrédients
        consolidated = {}

        for recette_id, recette_nom in repas:
            ingredients = db.query(
                Ingredient.nom,
                RecetteIngredient.quantite,
                Ingredient.unite
            ).join(
                RecetteIngredient,
                Ingredient.id == RecetteIngredient.ingredient_id
            ).filter(
                RecetteIngredient.recette_id == recette_id
            ).all()

            for nom, qty, unite in ingredients:
                # Vérifier stock
                stock = db.query(ArticleInventaire).join(
                    Ingredient
                ).filter(
                    Ingredient.nom == nom
                ).first()

                qty_dispo = stock.quantite if stock else 0
                manque = max(qty - qty_dispo, 0)

                if manque > 0:
                    key = f"{nom}_{unite}"
                    if key in consolidated:
                        consolidated[key]["quantite"] += manque
                        consolidated[key]["recettes"].add(recette_nom)
                    else:
                        consolidated[key] = {
                            "nom": nom,
                            "quantite": manque,
                            "unite": unite,
                            "priorite": "moyenne",
                            "recettes": {recette_nom}
                        }

        # Formatter
        suggestions = []
        for item in consolidated.values():
            recettes_list = list(item["recettes"])[:2]
            recettes_str = ", ".join(recettes_list)
            if len(item["recettes"]) > 2:
                recettes_str += f" +{len(item['recettes'])-2}"

            suggestions.append({
                "nom": item["nom"],
                "quantite": item["quantite"],
                "unite": item["unite"],
                "priorite": item["priorite"],
                "raison": f"Pour: {recettes_str}"
            })

        logger.info(f"{len(suggestions)} articles générés depuis repas ({jours}j)")
        return suggestions

    # ===================================
    # STATISTIQUES
    # ===================================

    def get_stats(
            self,
            jours: int = 30,
            db: Session = None
    ) -> Dict:
        """
        Statistiques complètes

        Returns:
            Dict avec métriques diverses
        """
        if db:
            return self._do_get_stats(db, jours)

        with get_db_context() as db:
            return self._do_get_stats(db, jours)

    def _do_get_stats(self, db: Session, jours: int) -> Dict:
        """Implémentation"""
        date_limite = datetime.now() - timedelta(days=jours)

        # Actifs
        actifs = db.query(ArticleCourses).filter(
            ArticleCourses.achete == False
        ).all()

        # Achetés
        achetes = db.query(ArticleCourses).filter(
            ArticleCourses.achete == True,
            ArticleCourses.achete_le >= date_limite
        ).all()

        # Articles fréquents
        articles_freq = {}
        for a in achetes:
            ing = db.query(Ingredient).get(a.ingredient_id)
            nom = ing.nom if ing else "Inconnu"
            articles_freq[nom] = articles_freq.get(nom, 0) + 1

        # Tri
        top_articles = dict(
            sorted(articles_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        )

        return {
            "total_actifs": len(actifs),
            "total_achetes": len(achetes),
            "part_ia": len([a for a in actifs if a.suggere_par_ia]),
            "part_ia_achetes": len([a for a in achetes if a.suggere_par_ia]),
            "moyenne_semaine": len(achetes) / max(jours // 7, 1),
            "prioritaires": len([a for a in actifs if a.priorite == "haute"]),
            "articles_frequents": top_articles
        }


# ===================================
# INSTANCE GLOBALE
# ===================================

courses_service = CoursesService()