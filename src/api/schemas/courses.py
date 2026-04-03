"""
Schémas Pydantic pour les courses.
"""

from datetime import date, datetime

from pydantic import BaseModel, Field

from .base import NomValidatorMixin, QuantiteValidatorMixin


class CourseItemBase(BaseModel, NomValidatorMixin, QuantiteValidatorMixin):
    """Schéma pour un article de liste de courses."""

    nom: str = Field(..., min_length=1, max_length=200)
    quantite: float = 1.0
    unite: str | None = Field(None, max_length=20)
    categorie: str | None = Field(None, max_length=100)
    coche: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom": "Lait demi-écrémé",
                "quantite": 2,
                "unite": "briques",
                "categorie": "produits_frais",
                "coche": False,
            }
        }
    }


class CourseListCreate(BaseModel, NomValidatorMixin):
    """Schéma pour créer une liste de courses."""

    nom: str = Field("Liste de courses", min_length=1, max_length=200)

    model_config = {
        "json_schema_extra": {
            "example": {"nom": "Courses semaine 15"}
        }
    }


class ListeCoursesResume(BaseModel):
    """Résumé d'une liste de courses (pour la liste paginée)."""

    id: int
    nom: str = Field(max_length=200)
    etat: str = Field("brouillon", max_length=30)
    items_count: int = 0
    created_at: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 12,
                "nom": "Courses semaine 15",
                "etat": "brouillon",
                "items_count": 18,
                "created_at": "2026-04-03T09:00:00",
            }
        }
    }


class ArticleResponse(BaseModel):
    """Réponse pour un article de liste."""

    id: int
    nom: str = Field(max_length=200)
    quantite: float
    coche: bool = False
    categorie: str | None = Field(None, max_length=100)


class ListeCoursesResponse(BaseModel):
    """Réponse complète pour une liste de courses."""

    id: int
    nom: str = Field(max_length=200)
    etat: str = Field("brouillon", max_length=30)
    archivee: bool = False
    created_at: datetime | None = None
    items: list[ArticleResponse] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 12,
                "nom": "Courses semaine 15",
                "etat": "brouillon",
                "archivee": False,
                "created_at": "2026-04-03T09:00:00",
                "items": [{"id": 1, "nom": "Lait demi-écrémé", "quantite": 2, "coche": False, "categorie": "produits_frais"}],
            }
        }
    }


class CheckoutArticleRequest(BaseModel):
    """Article à traiter dans un checkout courses -> inventaire."""

    item_id: int = Field(..., ge=1)
    quantite_achetee: float | None = Field(None, gt=0)


class CheckoutCoursesRequest(BaseModel):
    """Payload batch pour marquer des articles achetés et pousser en inventaire."""

    articles: list[CheckoutArticleRequest] = Field(..., min_length=1)
    emplacement_defaut: str | None = Field(None, max_length=100)
    idempotency_key: str | None = Field(None, max_length=128)

    model_config = {
        "json_schema_extra": {
            "example": {
                "articles": [{"item_id": 1, "quantite_achetee": 2}],
                "emplacement_defaut": "frigo",
                "idempotency_key": "courses-2026-04-03-001",
            }
        }
    }


class CheckoutArticleResult(BaseModel):
    """Résultat de traitement d'un article checkout."""

    item_id: int
    ingredient_nom: str = Field(max_length=200)
    statut: str = Field(max_length=30)
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "liste_id": 12,
                "total_demandes": 3,
                "total_traites": 3,
                "total_inventaire_maj": 2,
                "articles": [{"item_id": 1, "ingredient_nom": "Lait demi-écrémé", "statut": "ajoute_inventaire", "quantite_ajoutee": 2, "inventaire_article_id": 55, "coche": True}],
            }
        }
    }


class ScanBarcodeCheckoutRequest(BaseModel):
    """Payload d'un scan code-barres pour checkout magasin."""

    barcode: str = Field(..., min_length=8, max_length=64)
    quantite_achetee: float = Field(1.0, gt=0)
    idempotency_key: str | None = Field(None, max_length=128)

    model_config = {
        "json_schema_extra": {
            "example": {"barcode": "3274080005003", "quantite_achetee": 1, "idempotency_key": "scan-3274080005003-1"}
        }
    }


class ScanBarcodeCheckoutResponse(BaseModel):
    """Résultat du scan checkout (courses + inventaire)."""

    liste_id: int
    barcode: str = Field(max_length=64)
    item_id: int | None = None
    ingredient_nom: str | None = Field(None, max_length=200)
    statut: str = Field(max_length=30)
    quantite_ajoutee: float = 0
    inventaire_article_id: int | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "liste_id": 12,
                "barcode": "3274080005003",
                "item_id": 1,
                "ingredient_nom": "Lait demi-écrémé",
                "statut": "article_trouve",
                "quantite_ajoutee": 1,
                "inventaire_article_id": 55,
            }
        }
    }


class GenererCoursesRequest(BaseModel):
    """Requête pour générer une liste de courses depuis le planning."""

    semaine_debut: date
    soustraire_stock: bool = Field(True, description="Soustraire les quantités en stock")
    nom_liste: str = Field("Courses de la semaine", min_length=1, max_length=200)
    nb_invites: int = Field(0, ge=0, le=20, description="Nombre d'invités à prendre en compte")
    evenements: list[str] = Field(default_factory=list, description="Événements contextuels")

    model_config = {
        "json_schema_extra": {
            "example": {
                "semaine_debut": "2026-04-06",
                "soustraire_stock": True,
                "nom_liste": "Courses semaine 15",
                "nb_invites": 2,
                "evenements": ["brunch dimanche"],
            }
        }
    }


class ArticleGenereResume(BaseModel):
    """Résumé d'un article généré."""

    nom: str = Field(max_length=200)
    quantite: float
    unite: str = Field("", max_length=20)
    rayon: str = Field("Autre", max_length=100)
    en_stock: float = 0


class GenererCoursesResponse(BaseModel):
    """Réponse de la génération de courses depuis planning."""

    liste_id: int
    nom: str = Field(max_length=200)
    total_articles: int
    articles_en_stock: int
    contexte: dict[str, float | int | list[str]] = Field(default_factory=dict)
    articles: list[ArticleGenereResume] = Field(default_factory=list)
    par_rayon: dict[str, int] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "example": {
                "liste_id": 12,
                "nom": "Courses semaine 15",
                "total_articles": 14,
                "articles_en_stock": 3,
                "contexte": {"nb_invites": 2, "evenements": ["brunch dimanche"]},
                "articles": [{"nom": "Lait demi-écrémé", "quantite": 2, "unite": "briques", "rayon": "Produits frais", "en_stock": 0}],
                "par_rayon": {"Produits frais": 4, "Épicerie": 6},
            }
        }
    }
