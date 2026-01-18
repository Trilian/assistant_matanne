"""
Service Inventaire Unifié (REFACTORING PHASE 2)

✅ Utilise @with_db_session et @with_cache (Phase 1)
✅ Validation Pydantic centralisée
✅ Type hints complets pour meilleur IDE support
✅ Services testables sans Streamlit
"""

import logging
from datetime import date, datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.cache import Cache
from src.core.database import obtenir_contexte_db
from src.core.decorators import with_db_session, with_cache, with_error_handling
from src.core.errors_base import ErreurValidation
from src.core.models import ArticleInventaire
from src.services.base_ai_service import BaseAIService, InventoryAIMixin
from src.services.types import BaseService

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
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
    "Autre",
]

EMPLACEMENTS = ["Frigo", "Congélateur", "Placard", "Cave", "Garde-manger"]

# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════

class SuggestionCourses(BaseModel):
    """Shopping suggestion from IA"""
    nom: str = Field(..., min_length=2)
    quantite: float = Field(..., gt=0)
    unite: str = Field(..., min_length=1)
    priorite: str = Field(..., pattern="^(haute|moyenne|basse)$")
    rayon: str = Field(..., min_length=3)


class ArticleImport(BaseModel):
    """Modèle pour importer un article"""
    nom: str = Field(..., min_length=2)
    quantite: float = Field(..., ge=0)
    quantite_min: float = Field(..., ge=0)
    unite: str = Field(..., min_length=1)
    categorie: str | None = None
    emplacement: str | None = None
    date_peremption: str | None = None  # Format: YYYY-MM-DD


# ═══════════════════════════════════════════════════════════
# SERVICE INVENTAIRE UNIFIÉ
# ═══════════════════════════════════════════════════════════


class InventaireService(BaseService[ArticleInventaire], BaseAIService, InventoryAIMixin):
    """
    Service complet pour l'inventaire.

    ✅ Héritage multiple :
    - BaseService → CRUD optimisé
    - BaseAIService → IA avec rate limiting auto
    - InventoryAIMixin → Contextes métier inventaire

    Fonctionnalités:
    - CRUD optimisé avec cache
    - Alertes stock et péremption
    - Suggestions IA pour courses
    """

    def __init__(self):
        BaseService.__init__(self, ArticleInventaire, cache_ttl=1800)
        BaseAIService.__init__(
            self,
            client=obtenir_client_ia(),
            cache_prefix="inventaire",
            default_ttl=1800,
            default_temperature=0.7,
            service_name="inventaire",
        )

    # ═══════════════════════════════════════════════════════════
    # SECTION 1: CRUD & INVENTAIRE (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    @with_cache(
        ttl=1800,
        key_func=lambda self, emplacement, categorie, include_ok: (
            f"inventaire_{emplacement}_{categorie}_{include_ok}"
        ),
    )
    @with_error_handling(default_return=[])
    @with_db_session
    def get_inventaire_complet(
        self,
        emplacement: str | None = None,
        categorie: str | None = None,
        include_ok: bool = True,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        """Récupère l'inventaire complet avec statuts calculés.

        Retrieves complete inventory with calculated statuses.
        Results are cached for 30 minutes.

        Args:
            emplacement: Optional location filter (Frigo, Congélateur, etc.)
            categorie: Optional category filter
            include_ok: Include items with OK status
            db: Database session (injected by @with_db_session)

        Returns:
            List of dict with article data and calculated status
        """
        query = db.query(ArticleInventaire).options(
            joinedload(ArticleInventaire.ingredient)
        )

        if emplacement:
            query = query.filter(ArticleInventaire.emplacement == emplacement)

        articles = query.all()

        result = []
        today = date.today()

        for article in articles:
            statut = self._calculer_statut(article, today)

            if not include_ok and statut == "ok":
                continue

            if categorie and article.ingredient.categorie != categorie:
                continue

            result.append(
                {
                    "id": article.id,
                    "ingredient_id": article.ingredient_id,
                    "ingredient_nom": article.ingredient.nom,
                    "ingredient_categorie": article.ingredient.categorie,
                    "quantite": article.quantite,
                    "quantite_min": article.quantite_min,
                    "unite": article.ingredient.unite,
                    "emplacement": article.emplacement,
                    "date_peremption": article.date_peremption,
                    "statut": statut,
                    "jours_avant_peremption": self._jours_avant_peremption(article, today),
                }
            )

        logger.info(f"✅ Retrieved complete inventory: {len(result)} items")
        return result

    @with_error_handling(default_return={})
    def get_alertes(self) -> dict[str, list[dict[str, Any]]]:
        """Récupère toutes les alertes d'inventaire.

        Gets all inventory alerts grouped by type.

        Returns:
            Dict with keys: stock_bas, critique, peremption_proche
        """
        inventaire = self.get_inventaire_complet(include_ok=False)

        alertes = {
            "stock_bas": [],
            "critique": [],
            "peremption_proche": [],
        }

        for article in inventaire:
            statut = article["statut"]
            if statut in alertes:
                alertes[statut].append(article)

        logger.info(f"⚠️ Inventory alerts: {sum(len(v) for v in alertes.values())} items")
        return alertes

    # ═══════════════════════════════════════════════════════════
    # SECTION 2: SUGGESTIONS IA (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    @with_cache(ttl=3600, key_func=lambda self: "suggestions_courses_ia")
    @with_error_handling(default_return=[])
    def suggerer_courses_ia(self) -> list[SuggestionCourses]:
        """Suggère des articles à ajouter aux courses via IA.

        Uses Mistral AI to suggest shopping items based on inventory status.
        Results cached for 1 hour.

        Returns:
            List of SuggestionCourses objects, empty list on error
        """
        # Récupérer alertes et contexte
        alertes = self.get_alertes()
        inventaire = self.get_inventaire_complet()

        # Utilisation du Mixin pour résumé inventaire
        context = self.build_inventory_summary(inventaire)

        # Construire prompt
        prompt = self.build_json_prompt(
            context=context,
            task="Suggest 15 priority items to buy",
            json_schema='[{"nom": str, "quantite": float, "unite": str, "priorite": str, "rayon": str}]',
            constraints=[
                "Priority: haute/moyenne/basse",
                "Store sections for organization",
                "Realistic quantities",
                "Focus on critical items first",
                "Respect budget constraints",
            ],
        )

        logger.info("🤖 Generating shopping suggestions with AI")

        # Appel IA avec auto rate limiting & parsing
        suggestions = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=SuggestionCourses,
            system_prompt=self.build_system_prompt(
                role="Smart shopping assistant",
                expertise=[
                    "Stock management",
                    "Inventory optimization",
                    "Budget-aware purchasing",
                    "Seasonal availability",
                ],
                rules=[
                    "Prioritize critical items",
                    "Suggest realistic quantities",
                    "Consider seasonal items",
                    "Group by store section",
                ],
            ),
            max_items=15,
        )

        logger.info(f"✅ Generated {len(suggestions)} shopping suggestions")
        return suggestions

    # ═══════════════════════════════════════════════════════════
    # SECTION 3: HELPERS PRIVÉS (REFACTORED)
    # ═══════════════════════════════════════════════════════════

    def _calculer_statut(self, article: ArticleInventaire, today: date) -> str:
        """Calcule le statut d'un article.
        
        Args:
            article: ArticleInventaire object
            today: Current date for calculations
            
        Returns:
            Status string: 'critique', 'stock_bas', 'peremption_proche', or 'ok'
        """
        if article.date_peremption:
            days_left = (article.date_peremption - today).days
            if days_left <= 7:
                return "peremption_proche"

        if article.quantite < (article.quantite_min * 0.5):
            return "critique"

        if article.quantite < article.quantite_min:
            return "stock_bas"

        return "ok"

    def _jours_avant_peremption(
        self, article: ArticleInventaire, today: date
    ) -> int | None:
        """Calcule jours avant péremption.
        
        Args:
            article: ArticleInventaire object
            today: Current date
            
        Returns:
            Days until expiration or None if no expiration date
        """
        if not article.date_peremption:
            return None
        return (article.date_peremption - today).days

    # ═══════════════════════════════════════════════════════════
    # SECTION 4: HISTORIQUE (Tracking modifications)
    # ═══════════════════════════════════════════════════════════

    @with_error_handling(default_return=True)
    @with_db_session
    def _enregistrer_modification(
        self,
        article: ArticleInventaire,
        type_modification: str,
        quantite_avant: float | None = None,
        quantite_apres: float | None = None,
        quantite_min_avant: float | None = None,
        quantite_min_apres: float | None = None,
        date_peremption_avant: date | None = None,
        date_peremption_apres: date | None = None,
        emplacement_avant: str | None = None,
        emplacement_apres: str | None = None,
        notes: str | None = None,
        db: Session | None = None,
    ) -> bool:
        """Enregistre une modification dans l'historique.
        
        Args:
            article: Article modifié
            type_modification: "ajout", "modification", "suppression"
            quantite_avant/apres: Quantités avant/après
            ... (autres champs avant/après)
            notes: Notes additionnelles
            db: Database session
            
        Returns:
            True if recorded successfully
        """
        from src.core.models import HistoriqueInventaire

        historique = HistoriqueInventaire(
            article_id=article.id,
            ingredient_id=article.ingredient_id,
            type_modification=type_modification,
            quantite_avant=quantite_avant,
            quantite_apres=quantite_apres,
            quantite_min_avant=quantite_min_avant,
            quantite_min_apres=quantite_min_apres,
            date_peremption_avant=date_peremption_avant,
            date_peremption_apres=date_peremption_apres,
            emplacement_avant=emplacement_avant,
            emplacement_apres=emplacement_apres,
            notes=notes,
        )

        db.add(historique)
        db.commit()

        logger.info(f"📝 Historique enregistré: {type_modification} article #{article.id}")
        return True

    @with_error_handling(default_return=[])
    @with_db_session
    def get_historique(
        self, 
        article_id: int | None = None,
        ingredient_id: int | None = None,
        days: int = 30,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        """Récupère l'historique des modifications.
        
        Args:
            article_id: Filtrer par article (optionnel)
            ingredient_id: Filtrer par ingrédient (optionnel)
            days: Historique des N derniers jours
            db: Database session
            
        Returns:
            List of modifications with details
        """
        from src.core.models import HistoriqueInventaire
        from datetime import timedelta

        query = db.query(HistoriqueInventaire).filter(
            HistoriqueInventaire.date_modification >= (date.today() - timedelta(days=days))
        )

        if article_id:
            query = query.filter(HistoriqueInventaire.article_id == article_id)

        if ingredient_id:
            query = query.filter(HistoriqueInventaire.ingredient_id == ingredient_id)

        historique = query.order_by(HistoriqueInventaire.date_modification.desc()).all()

        result = []
        for h in historique:
            result.append({
                "id": h.id,
                "article_id": h.article_id,
                "ingredient_nom": h.ingredient.nom,
                "type": h.type_modification,
                "quantite_avant": h.quantite_avant,
                "quantite_apres": h.quantite_apres,
                "emplacement_avant": h.emplacement_avant,
                "emplacement_apres": h.emplacement_apres,
                "date_peremption_avant": h.date_peremption_avant,
                "date_peremption_apres": h.date_peremption_apres,
                "date_modification": h.date_modification,
                "notes": h.notes,
            })

        logger.info(f"📜 Retrieved {len(result)} historique entries")
        return result

    # ═══════════════════════════════════════════════════════════
    # SECTION 5: GESTION ARTICLES (CREATE/UPDATE/DELETE)
    # ═══════════════════════════════════════════════════════════

    @with_error_handling(default_return=None)
    @with_db_session
    def ajouter_article(
        self,
        ingredient_nom: str,
        quantite: float,
        quantite_min: float = 1.0,
        emplacement: str | None = None,
        date_peremption: date | None = None,
        db: Session | None = None,
    ) -> dict[str, Any] | None:
        """Ajoute un article à l'inventaire.

        Args:
            ingredient_nom: Nom de l'ingrédient
            quantite: Quantité en stock
            quantite_min: Quantité minimum
            emplacement: Lieu de stockage
            date_peremption: Date de péremption
            db: Database session (injected)

        Returns:
            Dict with new article data or None on error
        """
        from src.core.models import Ingredient

        # Trouver ou créer l'ingrédient
        ingredient = db.query(Ingredient).filter(
            Ingredient.nom.ilike(ingredient_nom)
        ).first()

        if not ingredient:
            logger.warning(f"⚠️ Ingrédient '{ingredient_nom}' non trouvé")
            return None

        # Vérifier si existe déjà
        existing = db.query(ArticleInventaire).filter(
            ArticleInventaire.ingredient_id == ingredient.id
        ).first()

        if existing:
            logger.warning(f"⚠️ Article '{ingredient_nom}' existe déjà")
            return None

        # Créer l'article
        article = ArticleInventaire(
            ingredient_id=ingredient.id,
            quantite=quantite,
            quantite_min=quantite_min,
            emplacement=emplacement,
            date_peremption=date_peremption,
        )

        db.add(article)
        db.commit()

        logger.info(f"✅ Article '{ingredient_nom}' ajouté à l'inventaire")
        self.invalidate_cache()

        return {
            "id": article.id,
            "ingredient_nom": ingredient.nom,
            "quantite": quantite,
            "quantite_min": quantite_min,
            "emplacement": emplacement,
            "date_peremption": date_peremption,
        }

    @with_error_handling(default_return=False)
    @with_db_session
    def mettre_a_jour_article(
        self,
        article_id: int,
        quantite: float | None = None,
        quantite_min: float | None = None,
        emplacement: str | None = None,
        date_peremption: date | None = None,
        db: Session | None = None,
    ) -> bool:
        """Met à jour un article de l'inventaire.

        Args:
            article_id: ID de l'article
            quantite: Nouvelle quantité (optionnel)
            quantite_min: Nouveau seuil minimum (optionnel)
            emplacement: Nouvel emplacement (optionnel)
            date_peremption: Nouvelle date de péremption (optionnel)
            db: Database session (injected)

        Returns:
            True if updated, False otherwise
        """
        article = db.query(ArticleInventaire).filter(
            ArticleInventaire.id == article_id
        ).first()

        if not article:
            logger.warning(f"⚠️ Article #{article_id} non trouvé")
            return False

        if quantite is not None:
            quantite_avant = article.quantite
            article.quantite = quantite
        else:
            quantite_avant = None

        quantite_min_avant = None
        if quantite_min is not None:
            quantite_min_avant = article.quantite_min
            article.quantite_min = quantite_min

        emplacement_avant = None
        if emplacement is not None:
            emplacement_avant = article.emplacement
            article.emplacement = emplacement

        date_peremption_avant = None
        if date_peremption is not None:
            date_peremption_avant = article.date_peremption
            article.date_peremption = date_peremption

        db.commit()
        
        # Enregistrer dans historique
        self._enregistrer_modification(
            article=article,
            type_modification="modification",
            quantite_avant=quantite_avant,
            quantite_apres=quantite if quantite is not None else None,
            quantite_min_avant=quantite_min_avant,
            quantite_min_apres=quantite_min if quantite_min is not None else None,
            emplacement_avant=emplacement_avant,
            emplacement_apres=emplacement if emplacement is not None else None,
            date_peremption_avant=date_peremption_avant,
            date_peremption_apres=date_peremption if date_peremption is not None else None,
        )
        
        logger.info(f"✅ Article #{article_id} mis à jour")
        self.invalidate_cache()

        return True

    @with_error_handling(default_return=False)
    @with_db_session
    def supprimer_article(self, article_id: int, db: Session | None = None) -> bool:
        """Supprime un article de l'inventaire.

        Args:
            article_id: ID de l'article
            db: Database session (injected)

        Returns:
            True if deleted, False otherwise
        """
        article = db.query(ArticleInventaire).filter(
            ArticleInventaire.id == article_id
        ).first()

        if not article:
            logger.warning(f"⚠️ Article #{article_id} non trouvé")
            return False

        db.delete(article)
        db.commit()

        logger.info(f"✅ Article #{article_id} supprimé")
        self.invalidate_cache()

        return True

    # ═══════════════════════════════════════════════════════════
    # SECTION 6: GESTION DES PHOTOS
    # ═══════════════════════════════════════════════════════════

    @with_db_session
    @with_error_handling(default_return={})
    def ajouter_photo(
        self,
        article_id: int,
        photo_url: str,
        photo_filename: str,
        db: Session | None = None,
    ) -> dict[str, Any]:
        """Ajoute une photo à un article.
        
        Args:
            article_id: ID de l'article
            photo_url: URL de la photo stockée
            photo_filename: Nom du fichier original
            db: Database session
            
        Returns:
            Updated article data
        """
        article = db.query(ArticleInventaire).filter_by(id=article_id).first()
        if not article:
            raise ErreurValidation(f"Article #{article_id} introuvable")

        # Garde trace de l'ancienne photo (si elle existe)
        old_photo = {
            "url": article.photo_url,
            "filename": article.photo_filename,
        } if article.photo_url else None

        # Met à jour la photo
        article.photo_url = photo_url
        article.photo_filename = photo_filename
        article.photo_uploaded_at = date.today()

        db.add(article)
        db.commit()
        db.refresh(article)

        # Enregistre dans l'historique
        self._enregistrer_modification(
            article_id=article_id,
            ingredient_id=article.ingredient_id,
            type_modification="photo_ajoutee",
            notes=f"Photo ajoutée: {photo_filename}",
            db=db,
        )

        logger.info(f"📸 Photo ajoutée à l'article #{article_id}")
        self.invalidate_cache()

        return {
            "article_id": article.id,
            "photo_url": article.photo_url,
            "photo_filename": article.photo_filename,
            "ancien": old_photo,
        }

    @with_db_session
    @with_error_handling(default_return=False)
    def supprimer_photo(self, article_id: int, db: Session | None = None) -> bool:
        """Supprime la photo d'un article.
        
        Args:
            article_id: ID de l'article
            db: Database session
            
        Returns:
            True if successful
        """
        article = db.query(ArticleInventaire).filter_by(id=article_id).first()
        if not article:
            raise ErreurValidation(f"Article #{article_id} introuvable")

        if not article.photo_url:
            raise ErreurValidation("Cet article n'a pas de photo")

        # Garde trace de la photo supprimée
        old_filename = article.photo_filename

        # Supprime la photo
        article.photo_url = None
        article.photo_filename = None
        article.photo_uploaded_at = None

        db.add(article)
        db.commit()

        # Enregistre dans l'historique
        self._enregistrer_modification(
            article_id=article_id,
            ingredient_id=article.ingredient_id,
            type_modification="photo_supprimee",
            notes=f"Photo supprimée: {old_filename}",
            db=db,
        )

        logger.info(f"🗑️  Photo supprimée de l'article #{article_id}")
        self.invalidate_cache()

        return True

    @with_db_session
    @with_error_handling(default_return=None)
    def obtenir_photo(self, article_id: int, db: Session | None = None) -> dict[str, Any] | None:
        """Récupère les info photo d'un article.
        
        Args:
            article_id: ID de l'article
            db: Database session
            
        Returns:
            Photo info or None if no photo
        """
        article = db.query(ArticleInventaire).filter_by(id=article_id).first()
        if not article or not article.photo_url:
            return None

        return {
            "url": article.photo_url,
            "filename": article.photo_filename,
            "uploaded_at": article.photo_uploaded_at,
        }

    # ═══════════════════════════════════════════════════════════
    # SECTION 8: NOTIFICATIONS & ALERTES
    # ═══════════════════════════════════════════════════════════

    @with_error_handling(default_return={})
    def generer_notifications_alertes(self) -> dict[str, Any]:
        """Génère les notifications d'alertes selon l'état de l'inventaire.
        
        Returns:
            Dict avec notifications créées par type
        """
        from src.services.notifications import obtenir_service_notifications

        service_notifs = obtenir_service_notifications()
        inventaire = self.get_inventaire_complet()
        stats = {
            "stock_critique": [],
            "stock_bas": [],
            "peremption_proche": [],
            "peremption_depassee": [],
        }

        # Vérifie chaque article
        for article_data in inventaire["articles"]:
            article_id = article_data["id"]
            quantite = article_data["quantite"]
            quantite_min = article_data["quantite_min"]
            date_peremption = article_data.get("date_peremption")

            # Check stock critique
            if article_data.get("est_critique"):
                notif = service_notifs.creer_notification_stock_critique(article_data)
                if notif:
                    service_notifs.ajouter_notification(notif)
                    stats["stock_critique"].append(article_data["nom"])

            # Check stock bas
            elif article_data.get("est_stock_bas"):
                notif = service_notifs.creer_notification_stock_bas(article_data)
                if notif:
                    service_notifs.ajouter_notification(notif)
                    stats["stock_bas"].append(article_data["nom"])

            # Check péremption
            if date_peremption:
                jours_avant = (date_peremption - date.today()).days
                if jours_avant <= 7:  # Alerter si <= 7 jours
                    notif = service_notifs.creer_notification_peremption(article_data, jours_avant)
                    if notif:
                        service_notifs.ajouter_notification(notif)
                        if jours_avant <= 0:
                            stats["peremption_depassee"].append(article_data["nom"])
                        else:
                            stats["peremption_proche"].append(article_data["nom"])

        logger.info(
            f"📬 Notifications générées: "
            f"Critique={len(stats['stock_critique'])}, "
            f"Bas={len(stats['stock_bas'])}, "
            f"Péremption={len(stats['peremption_proche']) + len(stats['peremption_depassee'])}"
        )

        return stats

    @with_error_handling(default_return=[])
    def obtenir_alertes_actives(self) -> list[dict[str, Any]]:
        """Récupère les alertes actives pour l'utilisateur.
        
        Returns:
            Liste des notifications non lues
        """
        from src.services.notifications import obtenir_service_notifications

        service_notifs = obtenir_service_notifications()
        notifs = service_notifs.obtenir_notifications(non_lues_seulement=True)

        return [
            {
                "id": notif.id,
                "titre": notif.titre,
                "message": notif.message,
                "icone": notif.icone,
                "type": notif.type_alerte.value,
                "priorite": notif.priorite,
                "article_id": notif.article_id,
                "date": notif.date_creation.isoformat(),
            }
            for notif in notifs
        ]

    # ═══════════════════════════════════════════════════════════
    # SECTION 9: STATISTIQUES & RAPPORTS
    # ═══════════════════════════════════════════════════════════

    @with_error_handling(default_return={})
    def get_statistiques(self) -> dict[str, Any]:
        """Récupère statistiques complètes de l'inventaire.

        Returns:
            Dict with statistics and insights
        """
        inventaire = self.get_inventaire_complet()
        alertes = self.get_alertes()

        if not inventaire:
            return {"total_articles": 0}

        return {
            "total_articles": len(inventaire),
            "total_quantite": sum(a["quantite"] for a in inventaire),
            "emplacements": len(set(a["emplacement"] for a in inventaire if a["emplacement"])),
            "categories": len(set(a["ingredient_categorie"] for a in inventaire)),
            "alertes_totales": sum(len(v) for v in alertes.values()),
            "articles_critiques": len(alertes.get("critique", [])),
            "articles_stock_bas": len(alertes.get("stock_bas", [])),
            "articles_peremption": len(alertes.get("peremption_proche", [])),
            "derniere_maj": max((a.get("derniere_maj") for a in inventaire), default=None),
        }

    @with_error_handling(default_return={})
    def get_stats_par_categorie(self) -> dict[str, dict[str, Any]]:
        """Récupère statistiques par catégorie.

        Returns:
            Dict with per-category statistics
        """
        inventaire = self.get_inventaire_complet()

        categories = {}
        for article in inventaire:
            cat = article["ingredient_categorie"]
            if cat not in categories:
                categories[cat] = {
                    "articles": 0,
                    "quantite_totale": 0,
                    "seuil_moyen": 0,
                    "critiques": 0,
                }

            categories[cat]["articles"] += 1
            categories[cat]["quantite_totale"] += article["quantite"]
            categories[cat]["seuil_moyen"] += article["quantite_min"]
            if article["statut"] == "critique":
                categories[cat]["critiques"] += 1

        # Calculer moyenne des seuils
        for cat in categories:
            if categories[cat]["articles"] > 0:
                categories[cat]["seuil_moyen"] /= categories[cat]["articles"]

        logger.info(f"📊 Statistics for {len(categories)} categories")
        return categories

    @with_error_handling(default_return=[])
    def get_articles_a_prelever(self, date_limite: date | None = None) -> list[dict[str, Any]]:
        """Récupère articles à utiliser en priorité.

        Args:
            date_limite: Date limite de péremption (par défaut aujourd'hui + 3 jours)

        Returns:
            List of articles to use first (FIFO)
        """
        from datetime import timedelta

        if date_limite is None:
            date_limite = date.today() + timedelta(days=3)

        inventaire = self.get_inventaire_complet()

        a_prelever = [
            a for a in inventaire
            if a["date_peremption"] and a["date_peremption"] <= date_limite
        ]

        # Trier par date de péremption (plus ancien d'abord)
        a_prelever.sort(key=lambda x: x["date_peremption"])

        return a_prelever

    # ═══════════════════════════════════════════════════════════
    # SECTION 10: IMPORT/EXPORT AVANCÉ
    # ═══════════════════════════════════════════════════════════

    @with_error_handling(default_return=[])
    def importer_articles(
        self,
        articles_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Importe plusieurs articles en batch.
        
        Args:
            articles_data: Liste des articles à importer (dictionnaires)
            
        Returns:
            Liste des articles importés avec leurs IDs
        """
        resultats: list[dict[str, Any]] = []
        errors: list[str] = []

        for idx, article_data in enumerate(articles_data):
            try:
                # Valide avec Pydantic
                article_import = ArticleImport(**article_data)

                # Cherche ou crée l'ingrédient
                from src.core.models import Ingredient
                from src.core.database import obtenir_contexte_db

                db = obtenir_contexte_db().session

                ingredient = db.query(Ingredient).filter_by(
                    nom=article_import.nom
                ).first()

                if not ingredient:
                    ingredient = Ingredient(
                        nom=article_import.nom,
                        unite=article_import.unite,
                        categorie=article_import.categorie or "Autre",
                    )
                    db.add(ingredient)
                    db.commit()
                    db.refresh(ingredient)

                # Ajoute l'article à l'inventaire
                resultat = self.ajouter_article(
                    ingredient_id=ingredient.id,
                    quantite=article_import.quantite,
                    quantite_min=article_import.quantite_min,
                    emplacement=article_import.emplacement,
                    date_peremption=(
                        date.fromisoformat(article_import.date_peremption)
                        if article_import.date_peremption
                        else None
                    ),
                )

                resultats.append({
                    "nom": article_import.nom,
                    "status": "✅",
                    "message": "Importé avec succès",
                })

            except Exception as e:
                errors.append(f"Ligne {idx + 2}: {str(e)}")
                resultats.append({
                    "nom": article_data.get("nom", "?"),
                    "status": "❌",
                    "message": str(e),
                })

        logger.info(f"✅ {len(resultats) - len(errors)}/{len(resultats)} articles importés")

        return resultats

    @with_error_handling(default_return=None)
    def exporter_inventaire(
        self,
        format_export: str = "csv",
    ) -> str | None:
        """Exporte l'inventaire dans le format demandé.
        
        Args:
            format_export: "csv" ou "json"
            
        Returns:
            Contenu du fichier en string
        """
        inventaire = self.get_inventaire_complet()

        if format_export == "csv":
            return self._exporter_csv(inventaire)
        elif format_export == "json":
            return self._exporter_json(inventaire)
        else:
            raise ErreurValidation(f"Format non supporté: {format_export}")

    def _exporter_csv(self, inventaire: dict[str, Any]) -> str:
        """Exporte en CSV"""
        import io

        output = io.StringIO()

        # Headers
        headers = [
            "Nom",
            "Quantité",
            "Unité",
            "Seuil Min",
            "Emplacement",
            "Catégorie",
            "Date Péremption",
            "État",
        ]
        output.write(",".join(headers) + "\n")

        # Données
        for article in inventaire["articles"]:
            row = [
                article["nom"],
                str(article["quantite"]),
                article.get("unite", ""),
                str(article["quantite_min"]),
                article.get("emplacement", ""),
                article.get("categorie", ""),
                str(article.get("date_peremption", "")),
                article.get("statut", ""),
            ]
            # Échapper les valeurs contenant des virgules
            row = [f'"{v}"' if "," in str(v) else str(v) for v in row]
            output.write(",".join(row) + "\n")

        return output.getvalue()

    def _exporter_json(self, inventaire: dict[str, Any]) -> str:
        """Exporte en JSON"""
        import json

        export_data = {
            "date_export": datetime.utcnow().isoformat(),
            "nombre_articles": len(inventaire["articles"]),
            "articles": inventaire["articles"],
            "statistiques": inventaire.get("statistiques", {}),
        }

        return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)

    def valider_fichier_import(
        self,
        donnees: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Valide les données d'import et retourne un rapport.
        
        Args:
            donnees: Données parsées du fichier
            
        Returns:
            Rapport de validation
        """
        rapport = {
            "valides": 0,
            "invalides": 0,
            "erreurs": [],
            "articles_valides": [],
            "articles_invalides": [],
        }

        for idx, article in enumerate(donnees):
            try:
                article_import = ArticleImport(**article)
                rapport["valides"] += 1
                rapport["articles_valides"].append({
                    "nom": article_import.nom,
                    "quantite": article_import.quantite,
                })
            except Exception as e:
                rapport["invalides"] += 1
                rapport["erreurs"].append({
                    "ligne": idx + 2,
                    "erreur": str(e),
                })
                rapport["articles_invalides"].append(article.get("nom", "?"))

        return rapport

        logger.info(f"🔄 {len(a_prelever)} articles to use first")
        return a_prelever


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON - LAZY LOADING
# ═══════════════════════════════════════════════════════════

_inventaire_service = None

def get_inventaire_service() -> InventaireService:
    """Get or create the global InventaireService instance."""
    global _inventaire_service
    if _inventaire_service is None:
        _inventaire_service = InventaireService()
    return _inventaire_service

inventaire_service = None

__all__ = ["InventaireService", "inventaire_service", "CATEGORIES", "EMPLACEMENTS", "get_inventaire_service"]
