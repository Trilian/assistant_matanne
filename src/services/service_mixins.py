"""
Service Mixins - Fonctionnalités Métier Réutilisables
Mixins extraits des patterns communs des services existants
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
import logging

from src.core.cache import Cache
from src.core.errors import handle_errors, NotFoundError
from src.core.database import get_db_context

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# STATUS TRACKING MIXIN
# ═══════════════════════════════════════════════════════════════

class StatusTrackingMixin:
    """
    Mixin pour tracking de statut

    Usage:
        class CoursesService(BaseServiceOptimized, StatusTrackingMixin):
            pass
    """

    @handle_errors(show_in_ui=False, fallback_value={})
    def count_by_status(
            self,
            status_field: str = "statut",
            db: Session = None
    ) -> Dict[str, int]:
        """
        Compte par statut

        Returns:
            {"ok": 10, "critique": 2}
        """
        stats = self.get_stats(
            group_by_fields=[status_field],
            db=db
        )
        return stats.get(f"by_{status_field}", {})

    @handle_errors(show_in_ui=True)
    def mark_as(
            self,
            item_id: int,
            status_field: str,
            status_value: str,
            db: Session = None
    ) -> bool:
        """
        Marque un item avec un statut

        Example:
            service.mark_as(123, "statut", "terminé")
        """
        return self.update(
            item_id,
            {status_field: status_value},
            db=db
        ) is not None


# ═══════════════════════════════════════════════════════════════
# SOFT DELETE MIXIN
# ═══════════════════════════════════════════════════════════════

class SoftDeleteMixin:
    """
    Mixin pour suppression logique (soft delete)

    Usage:
        class RecetteService(BaseServiceOptimized, SoftDeleteMixin):
            pass
    """

    @handle_errors(show_in_ui=True)
    def soft_delete(
            self,
            item_id: int,
            deleted_field: str = "deleted",
            db: Session = None
    ) -> bool:
        """Marque comme supprimé sans supprimer"""
        return self.update(
            item_id,
            {
                deleted_field: True,
                "deleted_at": datetime.now()
            },
            db=db
        ) is not None

    @handle_errors(show_in_ui=True)
    def restore(
            self,
            item_id: int,
            deleted_field: str = "deleted",
            db: Session = None
    ) -> bool:
        """Restaure un item supprimé"""
        return self.update(
            item_id,
            {
                deleted_field: False,
                "deleted_at": None
            },
            db=db
        ) is not None

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_deleted(
            self,
            deleted_field: str = "deleted",
            limit: int = 100,
            db: Session = None
    ):
        """Récupère les items supprimés"""
        return self.get_all(
            filters={deleted_field: True},
            limit=limit,
            db=db
        )


# ═══════════════════════════════════════════════════════════════
# INGREDIENT MANAGEMENT MIXIN
# ═══════════════════════════════════════════════════════════════

class IngredientManagementMixin:
    """
    Mixin pour gestion unifiée des ingrédients

    Évite duplication entre inventaire/courses/recettes

    Usage:
        class InventaireService(BaseServiceOptimized, IngredientManagementMixin):
            pass
    """

    @staticmethod
    def find_or_create_ingredient(
            nom: str,
            unite: str,
            categorie: Optional[str] = None,
            db: Session = None
    ) -> int:
        """
        Trouve ou crée un ingrédient

        Returns:
            ingredient_id
        """
        from src.core.models import Ingredient

        def _execute(session: Session) -> int:
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

            return ingredient.id

        if db:
            return _execute(db)

        with get_db_context() as session:
            return _execute(session)

    @staticmethod
    def batch_find_or_create_ingredients(
            items: List[Dict],  # [{"nom": str, "unite": str, "categorie": str}]
            db: Session = None
    ) -> Dict[str, int]:
        """
        Batch création ingrédients

        Returns:
            {"nom": ingredient_id}
        """
        from src.core.models import Ingredient

        def _execute(session: Session) -> Dict[str, int]:
            result = {}

            # Chercher existants
            noms = [item["nom"] for item in items]
            existants = session.query(Ingredient).filter(
                Ingredient.nom.in_(noms)
            ).all()

            for ing in existants:
                result[ing.nom] = ing.id

            # Créer manquants
            for item in items:
                if item["nom"] not in result:
                    ingredient = Ingredient(
                        nom=item["nom"],
                        unite=item["unite"],
                        categorie=item.get("categorie")
                    )
                    session.add(ingredient)
                    session.flush()
                    result[item["nom"]] = ingredient.id

            return result

        if db:
            return _execute(db)

        with get_db_context() as session:
            return _execute(session)

    @staticmethod
    def enrich_with_ingredient_info(
            items: List[Any],
            ingredient_id_field: str = "ingredient_id",
            db: Session = None
    ) -> List[Dict]:
        """
        Enrichit liste d'items avec infos ingrédient

        Évite N+1 queries (1 seule query pour tous les ingrédients)
        """
        from src.core.models import Ingredient

        def _execute(session: Session) -> List[Dict]:
            result = []

            # Récupérer tous ingrédients en 1 query
            ingredient_ids = [
                getattr(item, ingredient_id_field)
                for item in items
            ]
            ingredients = session.query(Ingredient).filter(
                Ingredient.id.in_(ingredient_ids)
            ).all()

            # Mapper
            ing_map = {ing.id: ing for ing in ingredients}

            for item in items:
                ing_id = getattr(item, ingredient_id_field)
                ingredient = ing_map.get(ing_id)

                if not ingredient:
                    continue

                # Construire dict enrichi
                enriched = {
                    "id": item.id,
                    "nom": ingredient.nom,
                    "categorie": ingredient.categorie or "Autre",
                    "unite": ingredient.unite,
                }

                # Ajouter attributs de l'item
                for attr in ["quantite", "priorite", "achete", "notes",
                             "quantite_min", "emplacement", "date_peremption"]:
                    if hasattr(item, attr):
                        enriched[attr] = getattr(item, attr)

                result.append(enriched)

            return result

        if db:
            return _execute(db)

        with get_db_context() as session:
            return _execute(session)


# ═══════════════════════════════════════════════════════════════
# EXPORT/IMPORT MIXIN
# ═══════════════════════════════════════════════════════════════

class ExportImportMixin:
    """
    Mixin pour export/import génériques

    Usage:
        class RecetteService(BaseServiceOptimized, ExportImportMixin):
            pass
    """

    @handle_errors(show_in_ui=False, fallback_value="")
    def export_to_json(
            self,
            filters: Optional[Dict] = None,
            limit: int = 1000
    ) -> str:
        """
        Exporte en JSON

        Returns:
            String JSON
        """
        import json

        items = self.get_all(filters=filters, limit=limit)

        # Convertir en dicts
        data = [self._model_to_dict(item) for item in items]

        return json.dumps(data, indent=2, ensure_ascii=False, default=str)

    @handle_errors(show_in_ui=False, fallback_value="")
    def export_to_csv(
            self,
            filters: Optional[Dict] = None,
            columns: Optional[List[str]] = None,
            limit: int = 1000
    ) -> str:
        """
        Exporte en CSV

        Returns:
            String CSV
        """
        import csv
        import io

        items = self.get_all(filters=filters, limit=limit)

        if not items:
            return ""

        output = io.StringIO()

        # Auto-detect colonnes
        if not columns:
            columns = [col.name for col in items[0].__table__.columns]

        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()

        for item in items:
            row = {}
            for col in columns:
                value = getattr(item, col, None)
                # Convertir datetime
                if isinstance(value, (datetime, date)):
                    value = value.isoformat()
                row[col] = value

            writer.writerow(row)

        return output.getvalue()


# ═══════════════════════════════════════════════════════════════
# PRIORITY MANAGEMENT MIXIN
# ═══════════════════════════════════════════════════════════════

class PriorityManagementMixin:
    """
    Mixin pour gestion de priorités

    Utilisé par courses, projets, etc.
    """

    PRIORITY_ORDER = {"haute": 3, "moyenne": 2, "basse": 1}

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_by_priority(
            self,
            priority: str,
            priority_field: str = "priorite",
            limit: int = 100,
            db: Session = None
    ):
        """Récupère items par priorité"""
        return self.get_all(
            filters={priority_field: priority},
            limit=limit,
            db=db
        )

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_ordered_by_priority(
            self,
            priority_field: str = "priorite",
            limit: int = 100,
            db: Session = None
    ):
        """Récupère items triés par priorité (haute → basse)"""
        items = self.get_all(limit=limit, db=db)

        return sorted(
            items,
            key=lambda x: self.PRIORITY_ORDER.get(
                getattr(x, priority_field, "moyenne"),
                2
            ),
            reverse=True
        )


# ═══════════════════════════════════════════════════════════════
# THRESHOLD ALERTING MIXIN
# ═══════════════════════════════════════════════════════════════

class ThresholdAlertingMixin:
    """
    Mixin pour alertes basées sur seuils

    Utilisé par inventaire (stock bas), etc.
    """

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_below_threshold(
            self,
            value_field: str,
            threshold_field: str,
            filters: Optional[Dict] = None,
            db: Session = None
    ):
        """
        Récupère items en-dessous du seuil

        Example:
            get_below_threshold("quantite", "quantite_min")
        """
        all_items = self.get_all(filters=filters, limit=1000, db=db)

        return [
            item for item in all_items
            if getattr(item, value_field, 0) < getattr(item, threshold_field, 0)
        ]

    @handle_errors(show_in_ui=False, fallback_value={})
    def get_threshold_stats(
            self,
            value_field: str,
            threshold_field: str,
            db: Session = None
    ) -> Dict:
        """
        Stats sur les seuils

        Returns:
            {
                "total": 100,
                "below_threshold": 15,
                "percentage": 15.0
            }
        """
        all_items = self.get_all(limit=1000, db=db)

        total = len(all_items)
        below = len([
            item for item in all_items
            if getattr(item, value_field, 0) < getattr(item, threshold_field, 0)
        ])

        return {
            "total": total,
            "below_threshold": below,
            "percentage": round((below / total * 100) if total > 0 else 0, 1)
        }


# ═══════════════════════════════════════════════════════════════
# DATE RANGE FILTERING MIXIN
# ═══════════════════════════════════════════════════════════════

class DateRangeFilteringMixin:
    """
    Mixin pour filtrage par plage de dates

    Utilisé par planning, projets, bien-être, etc.
    """

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_by_date_range(
            self,
            date_field: str,
            start_date: date,
            end_date: date,
            additional_filters: Optional[Dict] = None,
            db: Session = None
    ):
        """Récupère items dans une plage de dates"""
        filters = additional_filters or {}

        # Utilise le système de filtres avancés
        filters[date_field] = {
            "gte": start_date,
            "lte": end_date
        }

        return self.get_all(filters=filters, limit=1000, db=db)

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_this_week(
            self,
            date_field: str,
            db: Session = None
    ):
        """Récupère items de cette semaine"""
        from datetime import timedelta

        today = date.today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)

        return self.get_by_date_range(date_field, start, end, db=db)

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_this_month(
            self,
            date_field: str,
            db: Session = None
    ):
        """Récupère items de ce mois"""
        today = date.today()
        start = today.replace(day=1)

        # Dernier jour du mois
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end = today.replace(month=today.month + 1, day=1)

        from datetime import timedelta
        end = end - timedelta(days=1)

        return self.get_by_date_range(date_field, start, end, db=db)


# ═══════════════════════════════════════════════════════════════
# VALIDATION MIXIN
# ═══════════════════════════════════════════════════════════════

class ValidationMixin:
    """
    Mixin pour validations métier
    """

    @staticmethod
    def validate_positive(value: float, field_name: str = "valeur"):
        """Valide qu'un nombre est positif"""
        from src.core.errors import ValidationError

        if value < 0:
            raise ValidationError(
                f"{field_name} négatif: {value}",
                user_message=f"{field_name} doit être positif"
            )

    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]):
        """Valide que les champs requis sont présents"""
        from src.core.errors import ValidationError

        missing = [f for f in required_fields if not data.get(f)]

        if missing:
            raise ValidationError(
                f"Champs manquants: {missing}",
                user_message=f"Champs obligatoires manquants: {', '.join(missing)}"
            )

    @staticmethod
    def validate_date_not_past(value: date, field_name: str = "date"):
        """Valide qu'une date n'est pas passée"""
        from src.core.errors import ValidationError

        if value < date.today():
            raise ValidationError(
                f"{field_name} dans le passé",
                user_message=f"{field_name} ne peut être passée"
            )