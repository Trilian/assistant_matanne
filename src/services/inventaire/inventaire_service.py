"""
Service Inventaire
Utilise EnhancedCRUDService pour éliminer duplication

Version: 2.0.0
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from src.services.base_enhanced_service import EnhancedCRUDService, StatusTrackingMixin
from src.core.database import get_db_context
from src.core.exceptions import ValidationError, NotFoundError, handle_errors
from src.core.models import ArticleInventaire, Ingredient, ArticleCourses
from src.utils.formatters import format_quantity

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════

CATEGORIES = [
    "Légumes", "Fruits", "Féculents", "Protéines",
    "Laitier", "Épices", "Huiles", "Conserves", "Autre"
]

EMPLACEMENTS = ["Frigo", "Congélateur", "Placard", "Cave", "Autre"]

JOURS_ALERTE_PEREMPTION = 7


# ═══════════════════════════════════════════════════════════════
# HELPERS STATUT (logique métier pure)
# ═══════════════════════════════════════════════════════════════

def calculer_statut_article(
        quantite: float,
        seuil: float,
        date_peremption: Optional[date]
) -> Tuple[str, str]:
    """
    Calcule le statut d'un article

    Returns:
        (statut, icone)
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


# ═══════════════════════════════════════════════════════════════
# SERVICE PRINCIPAL (REFACTORISÉ)
# ═══════════════════════════════════════════════════════════════

class InventaireService(EnhancedCRUDService[ArticleInventaire], StatusTrackingMixin):
    """
    Service inventaire optimisé

    ✅ Hérite de EnhancedCRUDService → élimine 400+ lignes
    ✅ Mixin StatusTracking → ajoute count_by_status()
    ✅ Seulement logique métier spécifique ici
    """

    def __init__(self):
        super().__init__(ArticleInventaire)

    # ═══════════════════════════════════════════════════════════════
    # LECTURE ENRICHIE
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False)
    def get_inventaire_complet(
            self,
            filters: Optional[Dict] = None,
            db: Session = None
    ) -> List[Dict]:
        """
        Inventaire complet avec statuts calculés

        ✅ AVANT : 100+ lignes
        ✅ APRÈS : Utilise advanced_search() de EnhancedCRUDService
        """
        # Récupérer items avec recherche avancée
        items = self.advanced_search(
            search_term=None,
            search_fields=[],
            filters=filters,
            sort_by="nom",
            limit=1000,
            db=db
        )

        # Enrichir avec statuts
        result = []
        for item in items:
            statut, icone = calculer_statut_article(
                item.quantite,
                item.quantite_min,
                item.date_peremption
            )

            jours_peremption = get_jours_avant_peremption(item.date_peremption)

            # Récupérer nom ingrédient
            with get_db_context() as db_local:
                ingredient = db_local.query(Ingredient).get(item.ingredient_id)
                nom = ingredient.nom if ingredient else "Inconnu"
                unite = ingredient.unite if ingredient else "pcs"
                categorie = ingredient.categorie if ingredient else "Autre"

            result.append({
                "id": item.id,
                "nom": nom,
                "categorie": categorie,
                "quantite": item.quantite,
                "unite": unite,
                "seuil": item.quantite_min,
                "emplacement": item.emplacement or "—",
                "date_peremption": item.date_peremption,
                "jours_peremption": jours_peremption,
                "derniere_maj": item.derniere_maj,
                "statut": statut,
                "icone": icone
            })

        return result

    @handle_errors(show_in_ui=False)
    def get_alertes(self, db: Session = None) -> Dict[str, List[Dict]]:
        """
        Alertes critiques

        ✅ Utilise get_inventaire_complet() puis filtre
        """
        inventaire = self.get_inventaire_complet(db=db)

        alertes = {
            "stock_bas": [],
            "peremption_proche": [],
            "critiques": []
        }

        for item in inventaire:
            if item["statut"] == "critique":
                alertes["critiques"].append(item)
            elif item["statut"] == "sous_seuil":
                alertes["stock_bas"].append(item)
            elif item["statut"] == "peremption_proche":
                alertes["peremption_proche"].append(item)

        return alertes

    # ═══════════════════════════════════════════════════════════════
    # AJOUT / MODIFICATION (simplifié)
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
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
            db: Session = None
    ) -> int:
        """
        Ajoute ou modifie un article

        ✅ AVANT : 80 lignes
        ✅ APRÈS : Utilise create()/update() de base
        """
        def _execute(session: Session) -> int:
            # Trouver/créer ingrédient
            ingredient = session.query(Ingredient).filter(
                Ingredient.nom == nom
            ).first()

            if not ingredient:
                ingredient = Ingredient(
                    nom=nom,
                    unite=unite,
                    categorie=categorie
                )
                session.add(ingredient)
                session.flush()

            if article_id:
                # Modification
                updated = self.update(
                    article_id,
                    {
                        "quantite": quantite,
                        "quantite_min": seuil,
                        "emplacement": emplacement,
                        "date_peremption": date_peremption,
                        "derniere_maj": datetime.now()
                    },
                    db=session
                )
                return article_id if updated else None

            # Vérifier si existe déjà
            existant = session.query(ArticleInventaire).filter(
                ArticleInventaire.ingredient_id == ingredient.id
            ).first()

            if existant:
                # Mise à jour
                existant.quantite += quantite
                existant.quantite_min = seuil
                existant.derniere_maj = datetime.now()
                session.commit()
                return existant.id

            # Création
            article = self.create({
                "ingredient_id": ingredient.id,
                "quantite": quantite,
                "quantite_min": seuil,
                "emplacement": emplacement,
                "date_peremption": date_peremption
            }, db=session)

            return article.id

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════════
    # STATISTIQUES (ultra-simplifié)
    # ═══════════════════════════════════════════════════════════════

    def get_stats(self, jours: int = 30, db: Session = None) -> Dict:
        """
        Stats inventaire

        ✅ AVANT : 60+ lignes
        ✅ APRÈS : 10 lignes avec get_generic_stats()
        """
        return self.get_generic_stats(
            group_by_fields=["categorie", "emplacement"],
            count_filters={
                "critiques": {"statut": "critique"},
                "stock_bas": {"statut": "sous_seuil"},
                "peremption": {"statut": "peremption_proche"}
            },
            aggregate_fields={
                "quantite_moyenne": "quantite"
            },
            date_field="derniere_maj",
            days_back=jours,
            db=db
        )

    # ═══════════════════════════════════════════════════════════════
    # AJUSTEMENTS (simplifié)
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def ajuster_quantite(
            self,
            article_id: int,
            delta: float,
            raison: Optional[str] = None,
            db: Session = None
    ) -> Optional[float]:
        """
        Ajuste quantité (+/-)

        ✅ Utilise update() de base
        """
        article = self.get_by_id(article_id, db=db)

        if not article:
            raise NotFoundError(
                f"Article {article_id} non trouvé",
                user_message="Article introuvable"
            )

        nouvelle_quantite = max(0, article.quantite + delta)

        updated = self.update(
            article_id,
            {
                "quantite": nouvelle_quantite,
                "derniere_maj": datetime.now()
            },
            db=db
        )

        return nouvelle_quantite if updated else None

    # ═══════════════════════════════════════════════════════════════
    # INTÉGRATION COURSES
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def ajouter_a_courses(
            self,
            article_id: int,
            quantite: Optional[float] = None,
            db: Session = None
    ) -> bool:
        """Ajoute un article à la liste de courses"""
        def _execute(session: Session) -> bool:
            article = self.get_by_id(article_id, session)

            if not article:
                return False

            # Quantité = manque
            if quantite is None:
                quantite_calculee = max(
                    article.quantite_min - article.quantite,
                    article.quantite_min
                )
            else:
                quantite_calculee = quantite

            # Vérifier si déjà dans courses
            existant = session.query(ArticleCourses).filter(
                ArticleCourses.ingredient_id == article.ingredient_id,
                ArticleCourses.achete == False
            ).first()

            if existant:
                existant.quantite_necessaire = max(
                    existant.quantite_necessaire,
                    quantite_calculee
                )
            else:
                course = ArticleCourses(
                    ingredient_id=article.ingredient_id,
                    quantite_necessaire=quantite_calculee,
                    priorite="haute",
                    suggere_par_ia=False
                )
                session.add(course)

            session.commit()
            return True

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)


# ═══════════════════════════════════════════════════════════════
# INSTANCE GLOBALE
# ═══════════════════════════════════════════════════════════════

inventaire_service = InventaireService()