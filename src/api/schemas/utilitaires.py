"""
Schémas Pydantic pour les utilitaires (notes, journal, contacts, liens, mots de passe, énergie).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# NOTES
# ═══════════════════════════════════════════════════════════


class NoteBase(BaseModel):
    titre: str = Field(..., min_length=1, max_length=200)
    contenu: str | None = None
    categorie: str = "general"
    couleur: str | None = None
    epingle: bool = False
    est_checklist: bool = False
    items_checklist: list[dict] | None = None
    tags: list[str] = Field(default_factory=list)


class NoteCreate(NoteBase):
    """Création d'une note — hérite tous les champs de NoteBase."""


class NotePatch(BaseModel):
    titre: str | None = Field(None, min_length=1, max_length=200)
    contenu: str | None = None
    categorie: str | None = None
    couleur: str | None = None
    epingle: bool | None = None
    archive: bool | None = None
    tags: list[str] | None = None


class NoteResponse(BaseModel):
    id: int
    titre: str
    contenu: str | None = None
    categorie: str
    couleur: str | None = None
    epingle: bool = False
    est_checklist: bool = False
    items_checklist: list[dict] | None = None
    tags: list[str] = Field(default_factory=list)
    archive: bool = False
    cree_le: str | None = None


# ═══════════════════════════════════════════════════════════
# JOURNAL
# ═══════════════════════════════════════════════════════════


class JournalBase(BaseModel):
    date_entree: str = Field(..., description="Date au format YYYY-MM-DD")
    contenu: str = Field(..., min_length=1)
    humeur: str | None = None
    energie: int | None = Field(None, ge=1, le=10)
    gratitudes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class JournalCreate(JournalBase):
    """Création d'une entrée journal — hérite tous les champs de JournalBase."""


class JournalPatch(BaseModel):
    contenu: str | None = None
    humeur: str | None = None
    energie: int | None = None
    gratitudes: list[str] | None = None
    tags: list[str] | None = None


class JournalResponse(BaseModel):
    id: int
    date_entree: str
    contenu: str
    humeur: str | None = None
    energie: int | None = None
    gratitudes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    cree_le: str | None = None


# ═══════════════════════════════════════════════════════════
# CONTACTS
# ═══════════════════════════════════════════════════════════


class ContactBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=200)
    categorie: str = "autre"
    specialite: str | None = None
    telephone: str | None = None
    email: str | None = None
    adresse: str | None = None
    horaires: str | None = None
    favori: bool = False


class ContactCreate(ContactBase):
    """Création d'un contact — hérite tous les champs de ContactBase."""


class ContactPatch(BaseModel):
    nom: str | None = Field(None, min_length=1, max_length=200)
    categorie: str | None = None
    specialite: str | None = None
    telephone: str | None = None
    email: str | None = None
    adresse: str | None = None
    horaires: str | None = None
    favori: bool | None = None


class ContactResponse(BaseModel):
    id: int
    nom: str
    categorie: str
    specialite: str | None = None
    telephone: str | None = None
    email: str | None = None
    adresse: str | None = None
    horaires: str | None = None
    favori: bool = False


# ═══════════════════════════════════════════════════════════
# LIENS FAVORIS
# ═══════════════════════════════════════════════════════════


class LienBase(BaseModel):
    titre: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1)
    categorie: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    favori: bool = False


class LienCreate(LienBase):
    """Création d'un lien favori — hérite tous les champs de LienBase."""


class LienPatch(BaseModel):
    titre: str | None = Field(None, min_length=1, max_length=200)
    url: str | None = None
    categorie: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    favori: bool | None = None


class LienResponse(BaseModel):
    id: int
    titre: str
    url: str
    categorie: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    favori: bool = False


# ═══════════════════════════════════════════════════════════
# MOTS DE PASSE MAISON
# ═══════════════════════════════════════════════════════════


class MotDePasseBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=200)
    categorie: str = "autre"
    identifiant: str | None = None
    valeur: str = Field(..., min_length=1, description="Valeur en clair (chiffrée au stockage)")
    notes: str | None = None


class MotDePasseCreate(MotDePasseBase):
    """Création d'un mot de passe maison — hérite tous les champs de MotDePasseBase."""


class MotDePassePatch(BaseModel):
    nom: str | None = Field(None, min_length=1, max_length=200)
    categorie: str | None = None
    identifiant: str | None = None
    valeur: str | None = None
    notes: str | None = None


class MotDePasseResponse(BaseModel):
    id: int
    nom: str
    categorie: str
    identifiant: str | None = None
    valeur_chiffree: str
    notes: str | None = None


# ═══════════════════════════════════════════════════════════
# ÉNERGIE
# ═══════════════════════════════════════════════════════════


class EnergieBase(BaseModel):
    type_energie: str = Field(..., pattern=r"^(electricite|gaz|eau)$")
    mois: int = Field(..., ge=1, le=12)
    annee: int = Field(..., ge=2020, le=2035)
    valeur_compteur: float | None = None
    consommation: float | None = None
    unite: str = "kWh"
    montant: float | None = None
    notes: str | None = None


class EnergieCreate(EnergieBase):
    """Création d'un relevé énergie — hérite tous les champs d'EnergieBase."""


class EnergiePatch(BaseModel):
    valeur_compteur: float | None = None
    consommation: float | None = None
    montant: float | None = None
    notes: str | None = None


class EnergieResponse(BaseModel):
    id: int
    type_energie: str
    mois: int
    annee: int
    valeur_compteur: float | None = None
    consommation: float | None = None
    unite: str = "kWh"
    montant: float | None = None
    notes: str | None = None


# ═══════════════════════════════════════════════════════════
# MINUTEUR
# ═══════════════════════════════════════════════════════════


class MinuteurCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=200)
    duree_secondes: int = Field(..., gt=0, le=86400)
    recette_id: int | None = None


class MinuteurPatch(BaseModel):
    label: str | None = None
    terminee: bool | None = None
    active: bool | None = None


class MinuteurResponse(BaseModel):
    id: int
    label: str
    duree_secondes: int
    recette_id: int | None = None
    date_debut: str | None = None
    date_fin: str | None = None
    terminee: bool = False
    active: bool = False
