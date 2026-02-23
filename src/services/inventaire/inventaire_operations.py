"""
Mixin Opérations pour le service inventaire.

Contient les opérations CRUD, gestion des photos et suggestions IA:
- Ajout, modification et suppression d'articles
- Gestion des photos d'articles
- Suggestions de courses via IA
"""

from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.errors_base import ErreurValidation
from src.core.models import ArticleInventaire
from src.services.core.events.bus import obtenir_bus

from .types import SuggestionCourses

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class InventaireOperationsMixin:
    """Mixin pour les opérations CRUD, photos et suggestions IA.

    Méthodes déléguées depuis ServiceInventaire:
    - ajouter_article: ajout d'un article à l'inventaire
    - mettre_a_jour_article: mise à jour d'un article
    - supprimer_article: suppression d'un article
    - ajouter_photo: ajout de photo à un article
    - supprimer_photo: suppression de photo
    - obtenir_photo: récupération des infos photo
    - suggerer_courses_ia: suggestions de courses via IA

    Utilise self.get_inventaire_complet(), self._enregistrer_modification(),
    self.invalidate_cache(), self.build_inventory_summary(),
    self.call_with_list_parsing_sync() du service principal
    (cooperative mixin pattern).
    """

    # ═══════════════════════════════════════════════════════════
    # GESTION ARTICLES (CREATE/UPDATE/DELETE)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
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
        ingredient = db.query(Ingredient).filter(Ingredient.nom.ilike(ingredient_nom)).first()

        if not ingredient:
            logger.warning(f"⚠️ Ingrédient '{ingredient_nom}' non trouvé")
            return None

        # Vérifier si existe déjà
        existing = (
            db.query(ArticleInventaire)
            .filter(ArticleInventaire.ingredient_id == ingredient.id)
            .first()
        )

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

        # Émettre événement domaine
        obtenir_bus().emettre(
            "stock.modifie",
            {
                "article_id": article.id,
                "ingredient": ingredient.nom,
                "quantite": quantite,
                "raison": "ajout",
            },
            source="inventaire",
        )

        return {
            "id": article.id,
            "ingredient_nom": ingredient.nom,
            "quantite": quantite,
            "quantite_min": quantite_min,
            "emplacement": emplacement,
            "date_peremption": date_peremption,
        }

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
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
        article = db.query(ArticleInventaire).filter(ArticleInventaire.id == article_id).first()

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

        # Émettre événement domaine
        obtenir_bus().emettre(
            "stock.modifie",
            {"article_id": article_id, "quantite": quantite, "raison": "modification"},
            source="inventaire",
        )

        return True

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def supprimer_article(self, article_id: int, db: Session | None = None) -> bool:
        """Supprime un article de l'inventaire.

        Args:
            article_id: ID de l'article
            db: Database session (injected)

        Returns:
            True if deleted, False otherwise
        """
        article = db.query(ArticleInventaire).filter(ArticleInventaire.id == article_id).first()

        if not article:
            logger.warning(f"⚠️ Article #{article_id} non trouvé")
            return False

        db.delete(article)
        db.commit()

        logger.info(f"✅ Article #{article_id} supprimé")
        self.invalidate_cache()

        # Émettre événement domaine
        obtenir_bus().emettre(
            "stock.modifie",
            {"article_id": article_id, "raison": "suppression"},
            source="inventaire",
        )

        return True

    # ═══════════════════════════════════════════════════════════
    # GESTION DES PHOTOS
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
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
        old_photo = (
            {
                "url": article.photo_url,
                "filename": article.photo_filename,
            }
            if article.photo_url
            else None
        )

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

        logger.info(f"📝¸ Photo ajoutée à l'article #{article_id}")
        self.invalidate_cache()

        return {
            "article_id": article.id,
            "photo_url": article.photo_url,
            "photo_filename": article.photo_filename,
            "ancien": old_photo,
        }

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
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

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
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
    # SUGGESTIONS IA
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=3600, key_func=lambda self: "suggestions_courses_ia")
    def suggerer_courses_ia(self) -> list[SuggestionCourses]:  # pragma: no cover
        """Suggère des articles à ajouter aux courses via IA.

        Uses Mistral AI to suggest shopping items based on inventory status.
        Results cached for 1 hour.

        Returns:
            List of SuggestionCourses objects, empty list on error
        """
        # Récupérer contexte inventaire
        inventaire = self.get_inventaire_complet()

        # Utilisation du Mixin pour résumé inventaire
        context = self.build_inventory_summary(inventaire)

        # Construire prompt - FORCE JSON STRICT ET CLAIR
        prompt = f"""GENERATE 15 SHOPPING ITEMS IN JSON FORMAT ONLY.

{context}

OUTPUT ONLY THIS JSON (no other text, no markdown, no code blocks):

{{"items": [{{"nom": "Milk", "quantite": 2, "unite": "L", "priorite": "haute", "rayon": "Laitier"}}, {{"nom": "Eggs", "quantite": 1, "unite": "box", "priorite": "haute", "rayon": "Laitier"}}]}}

RULES:
1. Return ONLY valid JSON - nothing before or after
2. Generate 15 shopping items based on inventory alerts
3. All fields required: nom, quantite, unite, priorite, rayon
4. priorite must be: haute, moyenne, or basse (haute for critical items)
5. rayon: Fruits & Légumes, Laitier, Viande, Épicerie, Surgelé, Boulangerie, Hygiène
6. quantite: realistic amounts for family use
7. No explanations, no text, ONLY JSON"""

        logger.info("🤖 Generating shopping suggestions with AI")

        # Appel IA avec auto rate limiting & parsing
        suggestions = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=SuggestionCourses,
            system_prompt="Return ONLY valid JSON. No text before or after JSON.",
            max_items=15,
            temperature=0.5,
            max_tokens=2500,
        )

        logger.info(f"✅ Generated {len(suggestions)} shopping suggestions")
        return suggestions
