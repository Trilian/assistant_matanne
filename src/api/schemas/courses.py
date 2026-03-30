"""
Schémas Pydantic pour les courses.
"""

from datetime import date, datetime

from pydantic import BaseModel, Field

from .base import NomValidatorMixin, QuantiteValidatorMixin


class CourseItemBase(BaseModel, NomValidatorMixin, QuantiteValidatorMixin):
    """Schéma pour un article de liste de courses."""

    nom: str
    quantite: float = 1.0
    unite: str | None = None
    categorie: str | None = None
    coche: bool = False


class CourseListCreate(BaseModel, NomValidatorMixin):
    """Schéma pour créer une liste de courses."""

    nom: str = Field("Liste de courses", min_length=1)


class ListeCoursesResume(BaseModel):
    """Résumé d'une liste de courses (pour la liste paginée)."""

    id: int
    nom: str
    items_count: int = 0
    created_at: datetime | None = None


class ArticleResponse(BaseModel):
    """Réponse pour un article de liste."""

    id: int
    nom: str
    quantite: float
    coche: bool = False
    categorie: str | None = None


class ListeCoursesResponse(BaseModel):
    """Réponse complète pour une liste de courses."""

    id: int
    nom: str
    archivee: bool = False
    created_at: datetime | None = None
    items: list[ArticleResponse] = Field(default_factory=list)


class CheckoutArticleRequest(BaseModel):
    """Article à traiter dans un checkout courses -> inventaire."""

    item_id: int = Field(..., ge=1)
    quantite_achetee: float | None = Field(None, gt=0)


class CheckoutCoursesRequest(BaseModel):
    """Payload batch pour marquer des articles achetés et pousser en inventaire."""

    articles: list[CheckoutArticleRequest] = Field(..., min_length=1)
    emplacement_defaut: str | None = None
    idempotency_key: str | None = Field(None, max_length=128)


class CheckoutArticleResult(BaseModel):
    """Résultat de traitement d'un article checkout."""

    item_id: int
    ingredient_nom: str
    statut: str
    quantite_ajoutee: float = 0
    inventaire_article_id: int | None = None
    coche: bool = False


class CheckoutCoursesResponse(BaseModel):
    """Résultat global d'un checkout batch courses -> inventaire."""

    liste_id: int
    total_demandes: int
    total_traites: int
    total_inventaire_maj: int
    articles: list[CheckoutArticleResult] = Field(default_factory=list)


class ScanBarcodeCheckoutRequest(BaseModel):
    """Payload d'un scan code-barres pour checkout magasin."""

    barcode: str = Field(..., min_length=8)
    quantite_achetee: float = Field(1.0, gt=0)
    idempotency_key: str | None = Field(None, max_length=128)


class ScanBarcodeCheckoutResponse(BaseModel):
    """Résultat du scan checkout (courses + inventaire)."""

    liste_id: int
    barcode: str
    item_id: int | None = None
    ingredient_nom: str | None = None
    statut: str
    quantite_ajoutee: float = 0
    inventaire_article_id: int | None = None


class GenererCoursesRequest(BaseModel):
    """Requête pour générer une liste de courses depuis le planning."""

    semaine_debut: date
    soustraire_stock: bool = Field(True, description="Soustraire les quantités en stock")
    nom_liste: str = Field("Courses de la semaine", min_length=1, max_length=200)
    nb_invites: int = Field(0, ge=0, le=20, description="Nombre d'invités à prendre en compte")
    evenements: list[str] = Field(default_factory=list, description="Événements contextuels")


class ArticleGenereResume(BaseModel):
    """Résumé d'un article généré."""

    nom: str
    quantite: float
    unite: str = ""
    rayon: str = "Autre"
    en_stock: float = 0


class GenererCoursesResponse(BaseModel):
    """Réponse de la génération de courses depuis planning."""

    liste_id: int
    nom: str
    total_articles: int
    articles_en_stock: int
    contexte: dict[str, float | int | list[str]] = Field(default_factory=dict)
    articles: list[ArticleGenereResume] = Field(default_factory=list)
    par_rayon: dict[str, int] = Field(default_factory=dict)
