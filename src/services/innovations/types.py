"""
Types Pydantic pour les services Innovations — Phase 10.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# 10.4 — BILAN ANNUEL IA
# ═══════════════════════════════════════════════════════════


class SectionBilanAnnuel(BaseModel):
    """Section d'un bilan annuel."""

    titre: str = ""
    resume: str = ""
    metriques: dict = Field(default_factory=dict)
    points_forts: list[str] = Field(default_factory=list)
    axes_amelioration: list[str] = Field(default_factory=list)


class BilanAnnuelResponse(BaseModel):
    """Réponse du bilan annuel IA."""

    annee: int = 0
    resume_global: str = ""
    sections: list[SectionBilanAnnuel] = Field(default_factory=list)
    score_global: float = 0.0
    recommandations: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# 10.5 — SCORE BIEN-ÊTRE FAMILIAL
# ═══════════════════════════════════════════════════════════


class DimensionBienEtre(BaseModel):
    """Dimension du score bien-être."""

    nom: str = ""
    score: float = 0.0
    poids: float = 0.25
    detail: str = ""
    tendance: str = "stable"  # hausse, baisse, stable


class ScoreBienEtreResponse(BaseModel):
    """Score bien-être familial composite."""

    score_global: float = 0.0
    niveau: str = "bon"  # excellent, bon, moyen, attention
    dimensions: list[DimensionBienEtre] = Field(default_factory=list)
    historique_7j: list[float] = Field(default_factory=list)
    conseils: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# 10.17 — ENRICHISSEMENT CONTACTS IA
# ═══════════════════════════════════════════════════════════


class ContactEnrichi(BaseModel):
    """Contact enrichi par IA."""

    contact_id: int = 0
    nom: str = ""
    categorie_suggeree: str = ""
    rappel_relationnel: str = ""
    derniere_interaction_jours: int | None = None
    actions_suggerees: list[str] = Field(default_factory=list)


class EnrichissementContactsResponse(BaseModel):
    """Réponse enrichissement contacts."""

    contacts_enrichis: list[ContactEnrichi] = Field(default_factory=list)
    nb_contacts_analyses: int = 0
    nb_contacts_sans_nouvelles: int = 0


# ═══════════════════════════════════════════════════════════
# 10.18 — ANALYSE TENDANCES LOTO
# ═══════════════════════════════════════════════════════════


class TendanceLoto(BaseModel):
    """Tendance statistique loto."""

    numero: int = 0
    frequence: float = 0.0
    retard_tirages: int = 0
    score_tendance: float = 0.0


class AnalyseTendancesLotoResponse(BaseModel):
    """Analyse des tendances Loto/EuroMillions."""

    jeu: str = "loto"
    nb_tirages_analyses: int = 0
    numeros_chauds: list[TendanceLoto] = Field(default_factory=list)
    numeros_froids: list[TendanceLoto] = Field(default_factory=list)
    combinaison_suggeree: list[int] = Field(default_factory=list)
    analyse_ia: str = ""


# ═══════════════════════════════════════════════════════════
# 10.19 — OPTIMISATION PARCOURS MAGASIN
# ═══════════════════════════════════════════════════════════


class ArticleRayon(BaseModel):
    """Article assigné à un rayon."""

    nom: str = ""
    rayon: str = ""
    ordre: int = 0


class ParcoursOptimiseResponse(BaseModel):
    """Parcours magasin optimisé."""

    articles_par_rayon: dict[str, list[str]] = Field(default_factory=dict)
    ordre_rayons: list[str] = Field(default_factory=list)
    nb_articles: int = 0
    temps_estime_minutes: int = 0


# ═══════════════════════════════════════════════════════════
# 10.8 — VEILLE EMPLOI
# ═══════════════════════════════════════════════════════════


class OffreEmploi(BaseModel):
    """Offre d'emploi détectée."""

    titre: str = ""
    entreprise: str = ""
    localisation: str = ""
    type_contrat: str = ""
    mode_travail: str = ""  # remote, hybrid, onsite
    url: str = ""
    date_publication: str = ""
    salaire_estime: str = ""
    score_pertinence: float = 0.0


class CriteresVeilleEmploi(BaseModel):
    """Critères de veille emploi configurables."""

    domaine: str = "RH"
    mots_cles: list[str] = Field(default_factory=lambda: ["RH", "ressources humaines"])
    type_contrat: list[str] = Field(default_factory=lambda: ["CDI", "consultant"])
    mode_travail: list[str] = Field(default_factory=lambda: ["télétravail", "hybride"])
    rayon_km: int = 30
    frequence: str = "quotidien"


class VeilleEmploiResponse(BaseModel):
    """Résultat de la veille emploi."""

    offres: list[OffreEmploi] = Field(default_factory=list)
    nb_offres_trouvees: int = 0
    criteres_utilises: CriteresVeilleEmploi = Field(default_factory=CriteresVeilleEmploi)
    derniere_execution: str = ""


# ═══════════════════════════════════════════════════════════
# 10.3 — MODE INVITÉ
# ═══════════════════════════════════════════════════════════


class LienInviteResponse(BaseModel):
    """Réponse de création d'un lien invité."""

    token: str = ""
    url: str = ""
    expire_dans_heures: int = 48
    modules_autorises: list[str] = Field(default_factory=list)
    nom_invite: str = ""


class DonneesInviteResponse(BaseModel):
    """Données accessibles par un invité."""

    enfant: dict = Field(default_factory=dict)
    routines: list[dict] = Field(default_factory=list)
    repas_semaine: list[dict] = Field(default_factory=list)
    contacts_urgence: list[dict] = Field(default_factory=list)
    notes: str = ""
