"""
Schémas Pydantic pour les courses.
"""

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from .base import NomValidatorMixin, QuantiteValidatorMixin


class CourseItemBase(BaseModel, NomValidatorMixin, QuantiteValidatorMixin):
    """Schéma pour un article de liste de courses."""

    nom: str = Field(..., min_length=1, max_length=200)
    quantite: float = 1.0
    unite: str | None = Field(None, max_length=20)
    categorie: str | None = Field(None, max_length=100)
    coche: bool = False
    magasin_cible: str | None = Field(
        None,
        max_length=50,
        description="Magasin cible (bio_coop, grand_frais, carrefour_drive, autre)",
    )
    prix_estime: float | None = Field(None, ge=0, description="Prix unitaire estimé ou observé")

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom": "Lait demi-écrémé",
                "quantite": 2,
                "unite": "briques",
                "categorie": "produits_frais",
                "coche": False,
                "magasin_cible": "carrefour_drive",
                "prix_estime": 2.35,
            }
        }
    }


class CourseListCreate(BaseModel, NomValidatorMixin):
    """Schéma pour créer une liste de courses."""

    nom: str = Field("Liste de courses", min_length=1, max_length=200)

    model_config = {"json_schema_extra": {"example": {"nom": "Courses semaine 15"}}}


class ListeCoursesResume(BaseModel):
    """Résumé d'une liste de courses (pour la liste paginée)."""

    id: int
    nom: str = Field(max_length=200)
    etat: str = Field("brouillon", max_length=30)
    items_count: int = 0
    checked_count: int = 0
    created_at: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 12,
                "nom": "Courses semaine 15",
                "etat": "brouillon",
                "items_count": 18,
                "checked_count": 6,
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
    magasin_cible: str | None = Field(None, max_length=50)
    prix_estime: float | None = None


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
                "items": [
                    {
                        "id": 1,
                        "nom": "Lait demi-écrémé",
                        "quantite": 2,
                        "coche": False,
                        "categorie": "produits_frais",
                    }
                ],
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
                "articles": [
                    {
                        "item_id": 1,
                        "ingredient_nom": "Lait demi-écrémé",
                        "statut": "ajoute_inventaire",
                        "quantite_ajoutee": 2,
                        "inventaire_article_id": 55,
                        "coche": True,
                    }
                ],
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
            "example": {
                "barcode": "3274080005003",
                "quantite_achetee": 1,
                "idempotency_key": "scan-3274080005003-1",
            }
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

    @field_validator("rayon", mode="before")
    @classmethod
    def normaliser_rayon(cls, v: object) -> str:
        """Convertit None (retourné par l'IA) en valeur par défaut."""
        return v if isinstance(v, str) and v.strip() else "Autre"


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
                "articles": [
                    {
                        "nom": "Lait demi-écrémé",
                        "quantite": 2,
                        "unite": "briques",
                        "rayon": "Produits frais",
                        "en_stock": 0,
                    }
                ],
                "par_rayon": {"Produits frais": 4, "Épicerie": 6},
            }
        }
    }


# ═══════════════════════════════════════════════════════════
# CORRESPONDANCES CARREFOUR DRIVE
# ═══════════════════════════════════════════════════════════


class CorrespondanceDriveCreate(BaseModel):
    """Création/mise à jour d'une correspondance article → produit Carrefour Drive."""

    nom_article: str = Field(..., min_length=1, max_length=200)
    ingredient_id: int | None = None
    produit_drive_id: str = Field(..., min_length=1, max_length=100)
    produit_drive_nom: str = Field(..., min_length=1, max_length=300)
    produit_drive_ean: str | None = Field(None, max_length=50)
    produit_drive_url: str | None = Field(None, max_length=500)
    quantite_par_defaut: float = Field(1.0, gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom_article": "Lessive",
                "produit_drive_id": "3274080005003",
                "produit_drive_nom": "Lessive liquide Skip Active Clean 37 lavages",
                "produit_drive_ean": "3274080005003",
                "produit_drive_url": "https://www.carrefour.fr/p/lessive-liquide-skip-3274080005003",
                "quantite_par_defaut": 1.0,
            }
        }
    }


class CorrespondanceDriveResponse(BaseModel):
    """Réponse pour une correspondance Drive."""

    id: int
    nom_article: str
    ingredient_id: int | None = None
    produit_drive_id: str
    produit_drive_nom: str
    produit_drive_ean: str | None = None
    produit_drive_url: str | None = None
    quantite_par_defaut: float = 1.0
    nb_utilisations: int = 0
    actif: bool = True


class ArticleDriveResponse(BaseModel):
    """Article de liste enrichi avec sa correspondance Drive."""

    id: int
    nom: str
    ingredient_id: int | None = None
    quantite: float
    coche: bool = False
    categorie: str | None = None
    correspondance: CorrespondanceDriveResponse | None = None
