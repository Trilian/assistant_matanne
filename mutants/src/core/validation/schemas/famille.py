"""Schémas de validation pour la famille."""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class RoutineInput(BaseModel):
    """
    Input pour créer/modifier une routine.
    """

    nom: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    pour_qui: str = Field(..., description="Enfant associé")
    frequence: str = Field(..., description="Fréquence (quotidien, hebdo, mensuel)")
    is_active: bool = Field(default=True)

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip().capitalize()

    @field_validator("frequence")
    @classmethod
    def valider_frequence(cls, v: str) -> str:
        """Valide la fréquence"""
        frequences_valides = {"quotidien", "hebdomadaire", "mensuel"}
        if v.lower() not in frequences_valides:
            raise ValueError(
                f"Fréquence invalide. Doit être parmi: {', '.join(frequences_valides)}"
            )
        return v.lower()


class TacheRoutineInput(BaseModel):
    """
    Input pour ajouter une tâche à une routine.
    """

    nom: str = Field(..., min_length=1, max_length=200)
    heure: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    description: str | None = Field(None, max_length=500)

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip().capitalize()


class EntreeJournalInput(BaseModel):
    """
    Input pour ajouter une entrée au journal.
    """

    domaine: str = Field(..., description="Domaine (santé, humeur, développement)")
    titre: str = Field(..., min_length=1, max_length=200)
    contenu: str = Field(..., min_length=1, max_length=2000)
    date_entree: date = Field(default_factory=date.today, alias="date")
    tags: list[str] = Field(default_factory=list, max_length=10)

    model_config = {"populate_by_name": True}

    @field_validator("domaine")
    @classmethod
    def valider_domaine(cls, v: str) -> str:
        """Valide le domaine"""
        domaines_valides = {"santé", "humeur", "développement", "comportement"}
        if v.lower() not in domaines_valides:
            raise ValueError(f"Domaine invalide. Doit être parmi: {', '.join(domaines_valides)}")
        return v.lower()

    @field_validator("titre")
    @classmethod
    def nettoyer_titre(cls, v: str) -> str:
        return v.strip().capitalize()


# ═══════════════════════════════════════════════════════════
# CARNET DE SANTÉ
# ═══════════════════════════════════════════════════════════


class VaccinInput(BaseModel):
    """Input pour enregistrer un vaccin."""

    nom_vaccin: str = Field(..., min_length=1, max_length=200)
    type_vaccin: str = Field(default="obligatoire")
    date_injection: date | None = None
    numero_lot: str | None = Field(None, max_length=100)
    rappel_prevu: date | None = None
    medecin: str | None = Field(None, max_length=200)
    lieu: str | None = Field(None, max_length=200)
    notes: str | None = Field(None, max_length=500)
    fait: bool = False

    @field_validator("type_vaccin")
    @classmethod
    def valider_type(cls, v: str) -> str:
        types_valides = {"obligatoire", "recommandé"}
        if v.lower() not in types_valides:
            raise ValueError(f"Type invalide. Doit être parmi: {', '.join(types_valides)}")
        return v.lower()


class RendezVousMedicalInput(BaseModel):
    """Input pour un rendez-vous médical."""

    membre_famille: str = Field(..., min_length=1, max_length=100)
    type_rdv: str = Field(..., min_length=1, max_length=100)
    medecin: str | None = Field(None, max_length=200)
    date_rdv: date
    lieu: str | None = Field(None, max_length=300)
    motif: str | None = Field(None, max_length=1000)
    rappel_jours_avant: int = Field(default=3, ge=0, le=30)

    @field_validator("type_rdv")
    @classmethod
    def valider_type_rdv(cls, v: str) -> str:
        types_valides = {
            "pédiatre",
            "généraliste",
            "dentiste",
            "ophtalmo",
            "spécialiste",
            "autre",
        }
        if v.lower() not in types_valides:
            raise ValueError(f"Type RDV invalide. Doit être parmi: {', '.join(types_valides)}")
        return v.lower()


class MesureCroissanceInput(BaseModel):
    """Input pour une mesure de croissance."""

    date_mesure: date = Field(default_factory=date.today)
    poids_kg: float | None = Field(None, gt=0, le=30)
    taille_cm: float | None = Field(None, gt=0, le=200)
    perimetre_cranien_cm: float | None = Field(None, gt=0, le=60)
    notes: str | None = Field(None, max_length=500)


# ═══════════════════════════════════════════════════════════
# CONTACTS
# ═══════════════════════════════════════════════════════════


class ContactInput(BaseModel):
    """Input pour un contact familial."""

    nom: str = Field(..., min_length=1, max_length=200)
    prenom: str | None = Field(None, max_length=200)
    categorie: str = Field(..., min_length=1)
    sous_categorie: str | None = Field(None, max_length=100)
    telephone: str | None = Field(None, max_length=20)
    telephone_2: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=200)
    adresse: str | None = Field(None, max_length=300)
    code_postal: str | None = Field(None, max_length=10)
    ville: str | None = Field(None, max_length=100)
    horaires: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=1000)
    lien_maps: str | None = Field(None, max_length=500)
    est_urgence: bool = False

    @field_validator("categorie")
    @classmethod
    def valider_categorie(cls, v: str) -> str:
        categories_valides = {
            "medical",
            "garde",
            "education",
            "administration",
            "famille",
            "urgence",
        }
        if v.lower() not in categories_valides:
            raise ValueError(
                f"Catégorie invalide. Doit être parmi: {', '.join(categories_valides)}"
            )
        return v.lower()

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip()


# ═══════════════════════════════════════════════════════════
# ANNIVERSAIRES ET ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════


class AnniversaireInput(BaseModel):
    """Input pour un anniversaire."""

    nom_personne: str = Field(..., min_length=1, max_length=200)
    date_naissance: date
    relation: str = Field(..., min_length=1)
    rappel_jours_avant: list[int] = Field(default=[7, 1, 0])
    idees_cadeaux: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=1000)

    @field_validator("relation")
    @classmethod
    def valider_relation(cls, v: str) -> str:
        relations_valides = {
            "parent",
            "enfant",
            "grand_parent",
            "oncle_tante",
            "cousin",
            "ami",
            "collègue",
        }
        if v.lower() not in relations_valides:
            raise ValueError(f"Relation invalide. Doit être parmi: {', '.join(relations_valides)}")
        return v.lower()

    @field_validator("nom_personne")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip()


class EvenementFamilialInput(BaseModel):
    """Input pour un événement familial."""

    titre: str = Field(..., min_length=1, max_length=200)
    date_evenement: date
    type_evenement: str = Field(..., min_length=1)
    recurrence: str = Field(default="unique")
    rappel_jours_avant: int = Field(default=7, ge=0, le=60)
    notes: str | None = Field(None, max_length=1000)
    participants: list[str] = Field(default_factory=list)

    @field_validator("type_evenement")
    @classmethod
    def valider_type(cls, v: str) -> str:
        types_valides = {
            "anniversaire",
            "fete",
            "vacances",
            "rentree",
            "tradition",
            "autre",
        }
        if v.lower() not in types_valides:
            raise ValueError(f"Type invalide. Doit être parmi: {', '.join(types_valides)}")
        return v.lower()

    @field_validator("recurrence")
    @classmethod
    def valider_recurrence(cls, v: str) -> str:
        valides = {"annuelle", "mensuelle", "unique"}
        if v.lower() not in valides:
            raise ValueError(f"Récurrence invalide. Doit être parmi: {', '.join(valides)}")
        return v.lower()

    @field_validator("titre")
    @classmethod
    def nettoyer_titre(cls, v: str) -> str:
        return v.strip().capitalize()


# ═══════════════════════════════════════════════════════════
# VOYAGE
# ═══════════════════════════════════════════════════════════


class VoyageInput(BaseModel):
    """Input pour un voyage."""

    titre: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=200)
    date_depart: date
    date_retour: date
    type_voyage: str = Field(default="vacances")
    budget_prevu: float | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=2000)
    participants: list[str] = Field(default_factory=list)

    @field_validator("date_retour")
    @classmethod
    def valider_dates(cls, v: date, info) -> date:
        depart = info.data.get("date_depart")
        if depart and v < depart:
            raise ValueError("La date de retour doit être après la date de départ")
        return v

    @field_validator("type_voyage")
    @classmethod
    def valider_type(cls, v: str) -> str:
        types_valides = {
            "weekend",
            "vacances",
            "city_trip",
            "camping",
            "famille",
            "professionnel",
        }
        if v.lower() not in types_valides:
            raise ValueError(f"Type invalide. Doit être parmi: {', '.join(types_valides)}")
        return v.lower()

    @field_validator("titre", "destination")
    @classmethod
    def nettoyer_texte(cls, v: str) -> str:
        return v.strip()


class ChecklistArticleInput(BaseModel):
    """Input pour un article de checklist voyage."""

    nom: str = Field(..., min_length=1, max_length=200)
    categorie: str = Field(default="autre", max_length=50)
    quantite: int = Field(default=1, ge=1)
    coche: bool = False


class TemplateChecklistInput(BaseModel):
    """Input pour un template de checklist."""

    nom: str = Field(..., min_length=1, max_length=200)
    type_voyage: str | None = None
    membre: str = Field(default="commun")
    articles: list[ChecklistArticleInput] = Field(default_factory=list)
    description: str | None = Field(None, max_length=500)


# ═══════════════════════════════════════════════════════════
# DOCUMENTS
# ═══════════════════════════════════════════════════════════


class DocumentInput(BaseModel):
    """Input pour un document familial."""

    titre: str = Field(..., min_length=1, max_length=200)
    categorie: str = Field(..., min_length=1)
    membre_famille: str = Field(..., min_length=1, max_length=100)
    date_document: date | None = None
    date_expiration: date | None = None
    notes: str | None = Field(None, max_length=1000)
    tags: list[str] = Field(default_factory=list)
    rappel_expiration_jours: int = Field(default=30, ge=0)

    @field_validator("categorie")
    @classmethod
    def valider_categorie(cls, v: str) -> str:
        categories_valides = {
            "administratif",
            "medical",
            "scolaire",
            "assurance",
            "finance",
            "autre",
        }
        if v.lower() not in categories_valides:
            raise ValueError(
                f"Catégorie invalide. Doit être parmi: {', '.join(categories_valides)}"
            )
        return v.lower()

    @field_validator("titre")
    @classmethod
    def nettoyer_titre(cls, v: str) -> str:
        return v.strip()


# ═══════════════════════════════════════════════════════════
# ALBUM / SOUVENIRS
# ═══════════════════════════════════════════════════════════


class SouvenirInput(BaseModel):
    """Input pour un souvenir familial."""

    titre: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    date_souvenir: date = Field(default_factory=date.today)
    lieu: str | None = Field(None, max_length=200)
    personnes_presentes: list[str] = Field(default_factory=list)
    emotion: str | None = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("emotion")
    @classmethod
    def valider_emotion(cls, v: str | None) -> str | None:
        if v is None:
            return v
        emotions_valides = {
            "joie",
            "fierté",
            "émotion",
            "rire",
            "surprise",
            "tendresse",
        }
        if v.lower() not in emotions_valides:
            raise ValueError(f"Émotion invalide. Doit être parmi: {', '.join(emotions_valides)}")
        return v.lower()

    @field_validator("titre")
    @classmethod
    def nettoyer_titre(cls, v: str) -> str:
        return v.strip().capitalize()
