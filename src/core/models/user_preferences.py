"""
Modèles pour les préférences utilisateur et l'apprentissage IA.

Contient :
- UserPreference : Préférences alimentaires persistantes
- RecipeFeedback : Feedbacks 👍/👎 pour apprentissage
- OpenFoodFactsCache : Cache des produits scannés
- ExternalCalendarConfig : Configuration calendriers externes
"""

import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .recettes import Recette


def utc_now() -> datetime:
    """Retourne datetime UTC aware."""
    return datetime.now(UTC)


# ═══════════════════════════════════════════════════════════
# ÉNUMÉRATIONS
# ═══════════════════════════════════════════════════════════


class FeedbackType(enum.StrEnum):
    """Types de feedback pour les recettes."""

    LIKE = "like"
    DISLIKE = "dislike"
    NEUTRAL = "neutral"


class CalendarProvider(enum.StrEnum):
    """Providers de calendriers externes."""

    GOOGLE = "google"
    APPLE = "apple"
    OUTLOOK = "outlook"
    ICAL_URL = "ical_url"


# ═══════════════════════════════════════════════════════════
# PRÉFÉRENCES UTILISATEUR
# ═══════════════════════════════════════════════════════════


class UserPreference(Base):
    """Préférences alimentaires et familiales de l'utilisateur.

    Stockage persistant pour l'apprentissage IA des goûts.

    Attributes:
        user_id: Identifiant utilisateur (UUID Supabase ou string)
        nb_adultes: Nombre d'adultes dans le foyer
        jules_present: Si Jules mange avec la famille
        jules_age_mois: Âge de Jules en mois
        temps_semaine: Temps de cuisine en semaine (rapide/normal/long)
        temps_weekend: Temps de cuisine le weekend
        aliments_exclus: Liste JSON des aliments à éviter
        aliments_favoris: Liste JSON des aliments préférés
        poisson_par_semaine: Nombre de repas poisson souhaités
        vegetarien_par_semaine: Nombre de repas végétariens souhaités
        viande_rouge_max: Maximum de repas viande rouge
        robots: Liste JSON des robots cuisine disponibles
        magasins_preferes: Liste JSON des magasins préférés
    """

    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    # Famille
    nb_adultes: Mapped[int] = mapped_column(Integer, default=2)
    jules_present: Mapped[bool] = mapped_column(Boolean, default=True)
    jules_age_mois: Mapped[int] = mapped_column(Integer, default=19)

    # Temps de cuisine
    temps_semaine: Mapped[str] = mapped_column(String(20), default="normal")
    temps_weekend: Mapped[str] = mapped_column(String(20), default="long")

    # Préférences alimentaires (JSONB - stocke des listes)
    aliments_exclus: Mapped[list[str]] = mapped_column(JSONB, default=list)
    aliments_favoris: Mapped[list[str]] = mapped_column(JSONB, default=list)

    # Équilibre souhaité
    poisson_par_semaine: Mapped[int] = mapped_column(Integer, default=2)
    vegetarien_par_semaine: Mapped[int] = mapped_column(Integer, default=1)
    viande_rouge_max: Mapped[int] = mapped_column(Integer, default=2)

    # Équipements et magasins (JSONB - stocke des listes)
    robots: Mapped[list[str]] = mapped_column(JSONB, default=list)
    magasins_preferes: Mapped[list[str]] = mapped_column(JSONB, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    def __repr__(self) -> str:
        return f"<UserPreference(user_id='{self.user_id}', adultes={self.nb_adultes})>"


# ═══════════════════════════════════════════════════════════
# FEEDBACKS RECETTES (APPRENTISSAGE IA)
# ═══════════════════════════════════════════════════════════


class RecipeFeedback(Base):
    """Feedback utilisateur sur une recette (👍/👎).

    Permet l'apprentissage IA des goûts pour améliorer les suggestions.

    Attributes:
        user_id: Identifiant utilisateur
        recette_id: ID de la recette concernée
        feedback: Type de feedback (like/dislike/neutral)
        contexte: Contexte du feedback (ex: "trop long", "enfants adorent")
        notes: Notes additionnelles
    """

    __tablename__ = "recipe_feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    recette_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recettes.id", ondelete="CASCADE"), nullable=False, index=True
    )

    feedback: Mapped[str] = mapped_column(
        String(20), nullable=False, default=FeedbackType.NEUTRAL.value
    )
    contexte: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    # Contraintes
    __table_args__ = (
        UniqueConstraint("user_id", "recette_id", name="uq_user_recipe_feedback"),
        CheckConstraint("feedback IN ('like', 'dislike', 'neutral')", name="ck_feedback_type"),
    )

    # Relations
    recette: Mapped["Recette"] = relationship(back_populates="feedbacks")

    def __repr__(self) -> str:
        return f"<RecipeFeedback(user='{self.user_id}', recette={self.recette_id}, feedback='{self.feedback}')>"


# ═══════════════════════════════════════════════════════════
# CACHE OPENFOODFACTS
# ═══════════════════════════════════════════════════════════


class OpenFoodFactsCache(Base):
    """Cache persistant des produits OpenFoodFacts.

    Évite les appels API répétitifs pour les produits déjà scannés.

    Attributes:
        code_barres: Code EAN du produit (unique)
        nom: Nom du produit
        marque: Marque
        categorie: Catégorie principale
        nutriscore: Note Nutri-Score (A-E)
        nova_group: Groupe NOVA (1-4)
        ecoscore: Note Eco-Score (A-E)
        nutrition_data: Données nutritionnelles complètes (JSONB)
        image_url: URL de l'image produit
    """

    __tablename__ = "openfoodfacts_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    code_barres: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)

    nom: Mapped[str | None] = mapped_column(String(300))
    marque: Mapped[str | None] = mapped_column(String(200))
    categorie: Mapped[str | None] = mapped_column(String(200))

    # Scores
    nutriscore: Mapped[str | None] = mapped_column(String(1))
    nova_group: Mapped[int | None] = mapped_column(Integer)
    ecoscore: Mapped[str | None] = mapped_column(String(1))

    # Données complètes
    nutrition_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    allergenes: Mapped[dict[str, Any] | None] = mapped_column(JSONB, default=list)
    image_url: Mapped[str | None] = mapped_column(String(500))

    # Timestamps
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    def __repr__(self) -> str:
        return f"<OpenFoodFactsCache(code='{self.code_barres}', nom='{self.nom}')>"


# ═══════════════════════════════════════════════════════════
# CONFIGURATION CALENDRIERS EXTERNES
# ═══════════════════════════════════════════════════════════


class ExternalCalendarConfig(Base):
    """Configuration d'un calendrier externe (Google, Apple, etc.).

    Stocke les tokens OAuth et paramètres de synchronisation.

    Attributes:
        user_id: Identifiant utilisateur
        provider: Type de calendrier (google, apple, outlook, ical_url)
        name: Nom affiché du calendrier
        calendar_url: URL du calendrier (pour iCal)
        access_token: Token d'accès OAuth
        refresh_token: Token de rafraîchissement OAuth
        token_expiry: Date d'expiration du token
        sync_enabled: Synchronisation active
        last_sync: Dernière synchronisation
    """

    __tablename__ = "external_calendar_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    provider: Mapped[str] = mapped_column(
        String(20), nullable=False, default=CalendarProvider.GOOGLE.value
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, default="Mon Calendrier")

    # URL pour iCal
    calendar_url: Mapped[str | None] = mapped_column(String(500))

    # OAuth tokens
    access_token: Mapped[str | None] = mapped_column(Text)
    refresh_token: Mapped[str | None] = mapped_column(Text)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime)

    # Paramètres
    sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_direction: Mapped[str] = mapped_column(String(20), default="import")  # import/export/both

    # Timestamps
    last_sync: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    # Contraintes
    __table_args__ = (
        UniqueConstraint("user_id", "provider", "name", name="uq_user_calendar"),
        CheckConstraint(
            "provider IN ('google', 'apple', 'outlook', 'ical_url')", name="ck_calendar_provider"
        ),
    )

    def __repr__(self) -> str:
        return f"<ExternalCalendarConfig(user='{self.user_id}', provider='{self.provider}')>"
