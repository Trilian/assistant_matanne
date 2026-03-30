"""
Schémas Pydantic pour les services IA avancée (Phase 6).

Types de réponse utilisés par les 14 services IA.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# 6.1 — Suggestions achats IA
# ═══════════════════════════════════════════════════════════


class SuggestionAchat(BaseModel):
    """Article suggéré à l'achat basé sur l'historique."""

    nom: str = Field(description="Nom du produit")
    raison: str = Field(description="Pourquoi l'acheter maintenant")
    urgence: str = Field(default="normale", description="haute|normale|basse")
    frequence_achat_jours: int | None = Field(default=None, description="Fréquence estimée")
    quantite_suggeree: str | None = Field(default=None)


class SuggestionsAchatsResponse(BaseModel):
    """Réponse des suggestions d'achats."""

    suggestions: list[SuggestionAchat] = Field(default_factory=list)
    nb_produits_analyses: int = Field(default=0)
    periode_analyse_jours: int = Field(default=90)


# ═══════════════════════════════════════════════════════════
# 6.2 — Planning adaptatif
# ═══════════════════════════════════════════════════════════


class PlanningAdaptatif(BaseModel):
    """Planning adapté au contexte (météo, énergie, budget)."""

    recommandations: list[str] = Field(default_factory=list)
    repas_suggerees: list[dict] = Field(default_factory=list)
    activites_suggerees: list[dict] = Field(default_factory=list)
    score_adaptation: int = Field(default=0, ge=0, le=100)
    contexte_utilise: dict = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# 6.3 — Diagnostic plantes photo
# ═══════════════════════════════════════════════════════════


class DiagnosticPlante(BaseModel):
    """Diagnostic d'une plante par analyse photo."""

    nom_plante: str = Field(default="Plante non identifiée")
    etat_general: str = Field(default="inconnu", description="bon|moyen|mauvais|critique")
    problemes_detectes: list[str] = Field(default_factory=list)
    causes_probables: list[str] = Field(default_factory=list)
    traitements_recommandes: list[str] = Field(default_factory=list)
    arrosage_conseil: str | None = Field(default=None)
    exposition_conseil: str | None = Field(default=None)
    confiance: float = Field(default=0.5, ge=0, le=1)


# ═══════════════════════════════════════════════════════════
# 6.4 — Prévision dépenses
# ═══════════════════════════════════════════════════════════


class PrevisionDepenses(BaseModel):
    """Prévision des dépenses en fin de mois."""

    depenses_actuelles: float = Field(default=0)
    prevision_fin_mois: float = Field(default=0)
    budget_mensuel: float = Field(default=0)
    ecart_prevu: float = Field(default=0, description="Positif = sous budget")
    tendance: str = Field(default="stable", description="hausse|stable|baisse")
    postes_vigilance: list[dict] = Field(default_factory=list)
    conseils_economies: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# 6.5 — Idées cadeaux IA
# ═══════════════════════════════════════════════════════════


class IdeeCadeau(BaseModel):
    """Idée de cadeau générée par l'IA."""

    titre: str = Field(description="Nom du cadeau")
    description: str = Field(description="Description courte")
    fourchette_prix: str = Field(description="Ex: 15-25€")
    ou_acheter: str | None = Field(default=None)
    pertinence: str = Field(default="moyenne", description="haute|moyenne|basse")
    raison: str | None = Field(default=None)


class IdeesCadeauxResponse(BaseModel):
    """Réponse des idées cadeaux."""

    idees: list[IdeeCadeau] = Field(default_factory=list)
    destinataire: str = Field(default="")
    occasion: str = Field(default="anniversaire")


# ═══════════════════════════════════════════════════════════
# 6.6 — Analyse photo multi-usage
# ═══════════════════════════════════════════════════════════


class AnalysePhotoMultiUsage(BaseModel):
    """Résultat de l'analyse IA d'une photo (contexte auto-détecté)."""

    contexte_detecte: str = Field(description="recette|plante|maison|document|plat|autre")
    resume: str = Field(description="Résumé de l'analyse")
    details: dict = Field(default_factory=dict)
    actions_suggerees: list[str] = Field(default_factory=list)
    confiance: float = Field(default=0.5, ge=0, le=1)


# ═══════════════════════════════════════════════════════════
# 6.7 — Optimisation routines IA
# ═══════════════════════════════════════════════════════════


class OptimisationRoutine(BaseModel):
    """Suggestion d'optimisation de routine."""

    routine_concernee: str = Field(description="Nom de la routine")
    probleme_identifie: str = Field(description="Ce qui ne va pas")
    suggestion: str = Field(description="Ce qu'il faudrait changer")
    gain_estime: str | None = Field(default=None, description="Ex: 15 min/jour")
    priorite: str = Field(default="moyenne", description="haute|moyenne|basse")


class OptimisationRoutinesResponse(BaseModel):
    """Réponse d'optimisation des routines."""

    optimisations: list[OptimisationRoutine] = Field(default_factory=list)
    score_efficacite_actuel: int = Field(default=0, ge=0, le=100)
    score_efficacite_projete: int = Field(default=0, ge=0, le=100)


# ═══════════════════════════════════════════════════════════
# 6.8 — Analyse documents OCR
# ═══════════════════════════════════════════════════════════


class DocumentAnalyse(BaseModel):
    """Résultat d'analyse OCR d'un document."""

    type_document: str = Field(description="facture|contrat|ordonnance|administratif|autre")
    titre: str = Field(default="Document non identifié")
    date_document: str | None = Field(default=None)
    emetteur: str | None = Field(default=None)
    montant: float | None = Field(default=None)
    informations_cles: list[str] = Field(default_factory=list)
    categorie_suggeree: str | None = Field(default=None)
    actions_suggerees: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# 6.9 — Estimation travaux photo
# ═══════════════════════════════════════════════════════════


class EstimationTravauxPhoto(BaseModel):
    """Estimation de travaux basée sur photo avant/après."""

    type_travaux: str = Field(description="peinture|plomberie|electricite|maconnerie|autre")
    description: str = Field(description="Description des travaux identifiés")
    budget_min: float = Field(default=0)
    budget_max: float = Field(default=0)
    duree_estimee: str | None = Field(default=None, description="Ex: 2-3 jours")
    difficulte: str = Field(default="moyen", description="facile|moyen|difficile|expert")
    diy_possible: bool = Field(default=False)
    artisans_recommandes: list[str] = Field(default_factory=list)
    materiaux_necessaires: list[dict] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# 6.10 — Planning voyage IA
# ═══════════════════════════════════════════════════════════


class JourVoyage(BaseModel):
    """Un jour du planning voyage."""

    jour: int = Field(description="Numéro du jour")
    date: str | None = Field(default=None)
    activites: list[str] = Field(default_factory=list)
    repas_suggerees: list[str] = Field(default_factory=list)
    budget_jour: float | None = Field(default=None)
    conseils: list[str] = Field(default_factory=list)


class PlanningVoyage(BaseModel):
    """Planning de voyage complet généré par l'IA."""

    destination: str = Field(description="Destination")
    duree_jours: int = Field(description="Nombre de jours")
    budget_total_estime: float = Field(default=0)
    jours: list[JourVoyage] = Field(default_factory=list)
    check_list_depart: list[str] = Field(default_factory=list)
    conseils_generaux: list[str] = Field(default_factory=list)
    adaptations_enfant: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# 6.11 — Recommandations énergie
# ═══════════════════════════════════════════════════════════


class RecommandationEnergie(BaseModel):
    """Recommandation d'économie d'énergie."""

    titre: str = Field(description="Titre de la recommandation")
    description: str = Field(description="Description détaillée")
    economie_estimee: str | None = Field(default=None, description="Ex: 10-15% sur le chauffage")
    cout_mise_en_oeuvre: str | None = Field(default=None)
    difficulte: str = Field(default="facile", description="facile|moyen|investissement")
    priorite: str = Field(default="moyenne")
    categorie: str = Field(default="general", description="chauffage|electricite|eau|isolation")


class RecommandationsEnergieResponse(BaseModel):
    """Réponse recommandations énergie."""

    recommandations: list[RecommandationEnergie] = Field(default_factory=list)
    consommation_actuelle_resume: str | None = Field(default=None)
    potentiel_economie_global: str | None = Field(default=None)


# ═══════════════════════════════════════════════════════════
# 6.12 — Prédiction pannes
# ═══════════════════════════════════════════════════════════


class PredictionPanne(BaseModel):
    """Prédiction de panne d'un équipement."""

    equipement: str = Field(description="Nom de l'équipement")
    risque: str = Field(default="faible", description="faible|moyen|eleve|critique")
    probabilite_pct: int = Field(default=0, ge=0, le=100)
    delai_estime: str | None = Field(default=None, description="Ex: 3-6 mois")
    signes_alerte: list[str] = Field(default_factory=list)
    maintenance_preventive: list[str] = Field(default_factory=list)
    cout_remplacement_estime: str | None = Field(default=None)


class PredictionsPannesResponse(BaseModel):
    """Réponse prédictions pannes."""

    predictions: list[PredictionPanne] = Field(default_factory=list)
    nb_equipements_analyses: int = Field(default=0)
    score_sante_global: int = Field(default=0, ge=0, le=100)


# ═══════════════════════════════════════════════════════════
# 6.13 — Suggestions proactives
# ═══════════════════════════════════════════════════════════


class SuggestionProactive(BaseModel):
    """Suggestion proactive (l'app propose sans qu'on demande)."""

    module: str = Field(description="cuisine|famille|maison|jeux|budget")
    titre: str = Field(description="Titre court de la suggestion")
    message: str = Field(description="Message détaillé")
    action_url: str | None = Field(default=None, description="URL d'action dans l'app")
    priorite: str = Field(default="normale", description="haute|normale|basse")
    contexte: str | None = Field(default=None, description="Pourquoi cette suggestion")


class SuggestionsProactivesResponse(BaseModel):
    """Réponse suggestions proactives."""

    suggestions: list[SuggestionProactive] = Field(default_factory=list)
    date_generation: str | None = Field(default=None)


# ═══════════════════════════════════════════════════════════
# 6.14 — Météo → Planning
# ═══════════════════════════════════════════════════════════


class AdaptationMeteo(BaseModel):
    """Adaptation du planning basée sur la météo."""

    type_adaptation: str = Field(description="repas|jardin|activites|entretien")
    condition_meteo: str = Field(description="Ex: pluie, canicule, gel")
    recommandation: str = Field(description="Action recommandée")
    impact: str = Field(default="moyen", description="faible|moyen|fort")


class AdaptationsMeteoResponse(BaseModel):
    """Réponse adaptations météo."""

    adaptations: list[AdaptationMeteo] = Field(default_factory=list)
    meteo_resume: dict = Field(default_factory=dict)
    date_prevision: str | None = Field(default=None)
