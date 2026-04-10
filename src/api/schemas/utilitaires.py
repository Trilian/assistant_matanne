"""
Schémas Pydantic pour les utilitaires (notes, journal, contacts, liens, mots de passe, énergie).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════
# NOTES
# ═══════════════════════════════════════════════════════════


class NoteBase(BaseModel):
    titre: str = Field(..., min_length=1, max_length=200)
    contenu: str | None = Field(None, max_length=5000)
    categorie: str = Field("general", max_length=50)
    couleur: str | None = Field(None, max_length=20)
    epingle: bool = False
    est_checklist: bool = False
    items_checklist: list[dict[str, Any]] | None = None
    tags: list[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "titre": "Courses à compléter",
                "contenu": "Penser aux yaourts et au pain.",
                "categorie": "maison",
                "couleur": "jaune",
                "epingle": True,
                "est_checklist": False,
                "items_checklist": None,
                "tags": ["courses", "urgent"],
            }
        }
    }


class NoteCreate(NoteBase):
    """Création d'une note — hérite tous les champs de NoteBase."""


class NotePatch(BaseModel):
    titre: str | None = Field(None, min_length=1, max_length=200)
    contenu: str | None = Field(None, max_length=5000)
    categorie: str | None = Field(None, max_length=50)
    couleur: str | None = Field(None, max_length=20)
    epingle: bool | None = None
    archive: bool | None = None
    tags: list[str] | None = None


class NoteResponse(BaseModel):
    id: int
    titre: str
    contenu: str | None = Field(None, max_length=5000)
    categorie: str = Field(max_length=50)
    couleur: str | None = Field(None, max_length=20)
    epingle: bool = False
    est_checklist: bool = False
    items_checklist: list[dict[str, Any]] | None = None
    tags: list[str] = Field(default_factory=list)
    archive: bool = False
    cree_le: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 3,
                "titre": "Courses à compléter",
                "contenu": "Penser aux yaourts et au pain.",
                "categorie": "maison",
                "couleur": "jaune",
                "epingle": True,
                "est_checklist": False,
                "items_checklist": None,
                "tags": ["courses", "urgent"],
                "archive": False,
                "cree_le": "2026-04-03T08:10:00",
            }
        }
    }


# ═══════════════════════════════════════════════════════════
# JOURNAL
# ═══════════════════════════════════════════════════════════


class JournalBase(BaseModel):
    date_entree: str = Field(..., description="Date au format YYYY-MM-DD")
    contenu: str = Field(..., min_length=1, max_length=5000)
    humeur: str | None = Field(None, max_length=30)
    energie: int | None = Field(None, ge=1, le=10)
    gratitudes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "date_entree": "2026-04-03",
                "contenu": "Belle promenade au parc avec Jules et goûter au soleil.",
                "humeur": "bonne",
                "energie": 7,
                "gratitudes": ["le beau temps", "temps en famille"],
                "tags": ["famille", "weekend"],
            }
        }
    }


class JournalCreate(JournalBase):
    """Création d'une entrée journal — hérite tous les champs de JournalBase."""


class JournalPatch(BaseModel):
    contenu: str | None = Field(None, max_length=5000)
    humeur: str | None = Field(None, max_length=30)
    energie: int | None = None
    gratitudes: list[str] | None = None
    tags: list[str] | None = None


class JournalResponse(BaseModel):
    id: int
    date_entree: str
    contenu: str = Field(max_length=5000)
    humeur: str | None = Field(None, max_length=30)
    energie: int | None = None
    gratitudes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    cree_le: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 11,
                "date_entree": "2026-04-03",
                "contenu": "Belle promenade au parc avec Jules et goûter au soleil.",
                "humeur": "bonne",
                "energie": 7,
                "gratitudes": ["le beau temps", "temps en famille"],
                "tags": ["famille", "weekend"],
                "cree_le": "2026-04-03T20:30:00",
            }
        }
    }


# ═══════════════════════════════════════════════════════════
# CONTACTS
# ═══════════════════════════════════════════════════════════


class ContactBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=200)
    categorie: str = Field("autre", max_length=50)
    specialite: str | None = Field(None, max_length=100)
    telephone: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=200)
    adresse: str | None = Field(None, max_length=300)
    horaires: str | None = Field(None, max_length=200)
    favori: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom": "Dr Martin",
                "categorie": "sante",
                "specialite": "Pédiatre",
                "telephone": "0601020304",
                "email": "cabinet@example.com",
                "adresse": "12 rue des Lilas, 75012 Paris",
                "horaires": "Lun-Ven 9h-18h",
                "favori": True,
            }
        }
    }


class ContactCreate(ContactBase):
    """Création d'un contact — hérite tous les champs de ContactBase."""


class ContactPatch(BaseModel):
    nom: str | None = Field(None, min_length=1, max_length=200)
    categorie: str | None = Field(None, max_length=50)
    specialite: str | None = Field(None, max_length=100)
    telephone: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=200)
    adresse: str | None = Field(None, max_length=300)
    horaires: str | None = Field(None, max_length=200)
    favori: bool | None = None


class ContactResponse(BaseModel):
    id: int
    nom: str
    categorie: str = Field(max_length=50)
    specialite: str | None = Field(None, max_length=100)
    telephone: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=200)
    adresse: str | None = Field(None, max_length=300)
    horaires: str | None = Field(None, max_length=200)
    favori: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 2,
                "nom": "Dr Martin",
                "categorie": "sante",
                "specialite": "Pédiatre",
                "telephone": "0601020304",
                "email": "cabinet@example.com",
                "adresse": "12 rue des Lilas, 75012 Paris",
                "horaires": "Lun-Ven 9h-18h",
                "favori": True,
            }
        }
    }


# ═══════════════════════════════════════════════════════════
# LIENS FAVORIS
# ═══════════════════════════════════════════════════════════


class LienBase(BaseModel):
    titre: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1, max_length=500)
    categorie: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=1000)
    tags: list[str] = Field(default_factory=list)
    favori: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "titre": "CAF",
                "url": "https://www.caf.fr",
                "categorie": "administratif",
                "description": "Accès aux démarches familiales.",
                "tags": ["famille", "admin"],
                "favori": True,
            }
        }
    }


class LienCreate(LienBase):
    """Création d'un lien favori — hérite tous les champs de LienBase."""


class LienPatch(BaseModel):
    titre: str | None = Field(None, min_length=1, max_length=200)
    url: str | None = Field(None, max_length=500)
    categorie: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=1000)
    tags: list[str] | None = None
    favori: bool | None = None


class LienResponse(BaseModel):
    id: int
    titre: str
    url: str = Field(max_length=500)
    categorie: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=1000)
    tags: list[str] = Field(default_factory=list)
    favori: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 4,
                "titre": "CAF",
                "url": "https://www.caf.fr",
                "categorie": "administratif",
                "description": "Accès aux démarches familiales.",
                "tags": ["famille", "admin"],
                "favori": True,
            }
        }
    }


# ═══════════════════════════════════════════════════════════
# MOTS DE PASSE MAISON
# ═══════════════════════════════════════════════════════════


class MotDePasseBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=200)
    categorie: str = Field("autre", max_length=50)
    identifiant: str | None = Field(None, max_length=200)
    valeur: str = Field(
        ..., min_length=1, max_length=500, description="Valeur en clair (chiffrée au stockage)"
    )
    notes: str | None = Field(None, max_length=1000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom": "WiFi maison",
                "categorie": "reseau",
                "identifiant": "Maison-5G",
                "valeur": "MonMotDePasseFort!2026",
                "notes": "Changer si partage invité prolongé.",
            }
        }
    }


class MotDePasseCreate(MotDePasseBase):
    """Création d'un mot de passe maison — hérite tous les champs de MotDePasseBase."""


class MotDePassePatch(BaseModel):
    nom: str | None = Field(None, min_length=1, max_length=200)
    categorie: str | None = Field(None, max_length=50)
    identifiant: str | None = Field(None, max_length=200)
    valeur: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=1000)


class MotDePasseResponse(BaseModel):
    id: int
    nom: str
    categorie: str = Field(max_length=50)
    identifiant: str | None = Field(None, max_length=200)
    valeur_chiffree: str = Field(max_length=1000)
    notes: str | None = Field(None, max_length=1000)


# ═══════════════════════════════════════════════════════════
# ÉNERGIE
# ═══════════════════════════════════════════════════════════


class EnergieBase(BaseModel):
    type_energie: str = Field(..., pattern=r"^(electricite|gaz|eau)$")
    mois: int = Field(..., ge=1, le=12)
    annee: int = Field(..., ge=2020, le=2035)
    valeur_compteur: float | None = None
    consommation: float | None = None
    unite: str = Field("kWh", max_length=20)
    montant: float | None = None
    notes: str | None = Field(None, max_length=1000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type_energie": "electricite",
                "mois": 4,
                "annee": 2026,
                "valeur_compteur": 12345.6,
                "consommation": 280.4,
                "unite": "kWh",
                "montant": 74.5,
                "notes": "Hausse liée au chauffage d'appoint.",
            }
        }
    }


class EnergieCreate(EnergieBase):
    """Création d'un relevé énergie — hérite tous les champs d'EnergieBase."""


class EnergiePatch(BaseModel):
    valeur_compteur: float | None = None
    consommation: float | None = None
    montant: float | None = None
    notes: str | None = Field(None, max_length=1000)


class EnergieResponse(BaseModel):
    id: int
    type_energie: str
    mois: int
    annee: int
    valeur_compteur: float | None = None
    consommation: float | None = None
    unite: str = Field("kWh", max_length=20)
    montant: float | None = None
    notes: str | None = Field(None, max_length=1000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 6,
                "type_energie": "electricite",
                "mois": 4,
                "annee": 2026,
                "valeur_compteur": 12345.6,
                "consommation": 280.4,
                "unite": "kWh",
                "montant": 74.5,
                "notes": "Hausse liée au chauffage d'appoint.",
            }
        }
    }


# ═══════════════════════════════════════════════════════════
# MINUTEUR
# ═══════════════════════════════════════════════════════════


class MinuteurCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=200)
    duree_secondes: int = Field(..., gt=0, le=86400)
    recette_id: int | None = None

    model_config = {
        "json_schema_extra": {
            "example": {"label": "Cuisson gratin", "duree_secondes": 1800, "recette_id": 42}
        }
    }


class MinuteurPatch(BaseModel):
    label: str | None = Field(None, max_length=200)
    terminee: bool | None = None
    active: bool | None = None


class MinuteurResponse(BaseModel):
    id: int
    label: str = Field(max_length=200)
    duree_secondes: int
    recette_id: int | None = None
    date_debut: str | None = None
    date_fin: str | None = None
    terminee: bool = False
    active: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 2,
                "label": "Cuisson gratin",
                "duree_secondes": 1800,
                "recette_id": 42,
                "date_debut": "2026-04-03T19:00:00",
                "date_fin": None,
                "terminee": False,
                "active": True,
            }
        }
    }
