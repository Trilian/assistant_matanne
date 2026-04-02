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
# PHASE 9 — IA AVANCÉE & INNOVATIONS
# ═══════════════════════════════════════════════════════════


class SuggestionRepasSoirResponse(BaseModel):
    """Suggestion contextualisée "Qu'est-ce qu'on mange ce soir ?"."""

    recette_suggeree: str = ""
    raison: str = ""
    temps_total_estime_min: int = 0
    alternatives: list[str] = Field(default_factory=list)
    ingredients_detectes: list[str] = Field(default_factory=list)


class PatternsAlimentairesResponse(BaseModel):
    """Analyse des habitudes alimentaires sur une période."""

    periode_jours: int = 90
    score_diversite: float = 0.0
    top_recettes: list[str] = Field(default_factory=list)
    categories_sous_representees: list[str] = Field(default_factory=list)
    recommandations: list[str] = Field(default_factory=list)


class CoachRoutinesResponse(BaseModel):
    """Coaching IA pour l'amélioration des routines."""

    score_regularite: float = 0.0
    routines_en_retard: list[str] = Field(default_factory=list)
    blocages_probables: list[str] = Field(default_factory=list)
    ajustements_suggeres: list[str] = Field(default_factory=list)


class AnomalieEnergieDetail(BaseModel):
    """Détail d'une anomalie de consommation."""

    type_energie: str = ""
    mois: str = ""
    ecart_pct: float = 0.0
    severite: str = "faible"
    explication: str = ""


class AnomaliesEnergieResponse(BaseModel):
    """Synthèse anomalies eau/gaz/électricité."""

    nb_anomalies: int = 0
    score_risque: float = 0.0
    anomalies: list[AnomalieEnergieDetail] = Field(default_factory=list)
    recommandations: list[str] = Field(default_factory=list)


class ResumeMensuelIAResponse(BaseModel):
    """Résumé narratif mensuel multi-modules."""

    mois_reference: str = ""
    resume_global: str = ""
    faits_marquants: list[str] = Field(default_factory=list)
    recommandations: list[str] = Field(default_factory=list)


class ActiviteJulesSuggeree(BaseModel):
    """Activité suggérée pour Jules."""

    titre: str = ""
    moment: str = ""
    duree_minutes: int = 0
    en_interieur: bool = False
    raison: str = ""


class PlanningJulesAdaptatifResponse(BaseModel):
    """Planning hebdomadaire d'activités Jules adapté au contexte."""

    semaine_reference: str = ""
    activites: list[ActiviteJulesSuggeree] = Field(default_factory=list)
    recommandations_parents: list[str] = Field(default_factory=list)


class OffreEnergieAlternative(BaseModel):
    """Offre fournisseur énergie alternative."""

    fournisseur: str = ""
    prix_kwh_eur: float = 0.0
    abonnement_mensuel_eur: float = 0.0
    cout_annuel_estime_eur: float = 0.0


class ComparateurEnergieResponse(BaseModel):
    """Comparateur simple d'offres énergie."""

    consommation_annuelle_kwh: float = 0.0
    cout_actuel_estime_eur: float = 0.0
    economie_max_estimee_eur: float = 0.0
    offres: list[OffreEnergieAlternative] = Field(default_factory=list)


class ScoreEcoResponsableResponse(BaseModel):
    """Score éco-responsable mensuel."""

    score_global: float = 0.0
    details: dict[str, float] = Field(default_factory=dict)
    recommandations: list[str] = Field(default_factory=list)


class SaisonnaliteIntelligenteResponse(BaseModel):
    """Adaptations intelligentes selon la saison."""

    saison: str = ""
    recettes_de_saison: list[str] = Field(default_factory=list)
    actions_jardin: list[str] = Field(default_factory=list)
    actions_entretien: list[str] = Field(default_factory=list)
    ajustements_energie: list[str] = Field(default_factory=list)


class ApprentissageHabitudesResponse(BaseModel):
    """Résultat d'apprentissage continu des habitudes."""

    habitudes_detectees: list[str] = Field(default_factory=list)
    ajustements_systeme: list[str] = Field(default_factory=list)
    niveau_confiance: float = 0.0


class AlerteContextuelle(BaseModel):
    """Alerte intelligente contextuelle."""

    titre: str = ""
    description: str = ""
    priorite: str = "moyenne"
    action_suggeree: str = ""


class AlertesContextuellesResponse(BaseModel):
    """Liste des alertes contextuelles proposées."""

    nb_alertes: int = 0
    alertes: list[AlerteContextuelle] = Field(default_factory=list)


class ActionPiloteAutomatique(BaseModel):
    """Action suggeree/executee par le mode pilote automatique."""

    module: str = ""
    action: str = ""
    statut: str = "proposee"
    details: str = ""


class ModePiloteAutomatiqueResponse(BaseModel):
    """Synthese du mode pilote automatique multi-modules."""

    actif: bool = False
    niveau_autonomie: str = "validation_requise"
    actions: list[ActionPiloteAutomatique] = Field(default_factory=list)
    recommandations: list[str] = Field(default_factory=list)


class DimensionScoreFamille(BaseModel):
    """Dimension du score famille hebdomadaire."""

    nom: str = ""
    score: float = 0.0
    poids: float = 0.25


class ScoreFamilleHebdoResponse(BaseModel):
    """Score famille composite hebdomadaire."""

    semaine_reference: str = ""
    score_global: float = 0.0
    dimensions: list[DimensionScoreFamille] = Field(default_factory=list)
    recommandations: list[str] = Field(default_factory=list)


class JournalFamilialAutoResponse(BaseModel):
    """Journal familial automatique genere par IA."""

    semaine_reference: str = ""
    titre: str = ""
    resume: str = ""
    faits_marquants: list[str] = Field(default_factory=list)
    moments_joyeux: list[str] = Field(default_factory=list)
    points_attention: list[str] = Field(default_factory=list)


class RapportMensuelPdfResponse(BaseModel):
    """Metadonnees du rapport mensuel PDF genere."""

    mois_reference: str = ""
    filename: str = ""
    contenu_base64: str = ""


class ModeVacancesResponse(BaseModel):
    """Etat du mode vacances et impacts transverses."""

    actif: bool = False
    checklist_voyage_auto: bool = True
    courses_mode_compact: bool = False
    entretien_suspendu: bool = False
    recommandations: list[str] = Field(default_factory=list)


class InsightQuotidien(BaseModel):
    """Insight IA proactif quotidien."""

    titre: str = ""
    message: str = ""
    module: str = ""
    priorite: str = "normale"
    action_url: str = ""


class InsightsQuotidiensResponse(BaseModel):
    """Liste d'insights IA proactifs du jour (anti-spam)."""

    date_reference: str = ""
    limite_journaliere: int = 2
    nb_insights: int = 0
    insights: list[InsightQuotidien] = Field(default_factory=list)


class MeteoImpactModule(BaseModel):
    """Impact météo pour un module donné."""

    module: str = ""
    impact: str = ""
    actions_recommandees: list[str] = Field(default_factory=list)


class MeteoContextuelleResponse(BaseModel):
    """Synthèse météo contextuelle cross-module."""

    ville: str = ""
    saison: str = ""
    temperature: float | None = None
    description: str = ""
    modules: list[MeteoImpactModule] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# SPRINT 22 — INNOVATIONS AVANCÉES
# ═══════════════════════════════════════════════════════════


class PreferenceApprise(BaseModel):
    """Préférence détectée automatiquement sur l'historique."""

    categorie: str = ""
    valeur: str = ""
    score_confiance: float = 0.0


class ApprentissagePreferencesResponse(BaseModel):
    """Synthèse des préférences apprises et exploitables."""

    semaines_analysees: int = 0
    influence_active: bool = False
    preferences_favorites: list[PreferenceApprise] = Field(default_factory=list)
    preferences_a_eviter: list[PreferenceApprise] = Field(default_factory=list)
    ajustements_suggestions: list[str] = Field(default_factory=list)


class BlocPlanificationAuto(BaseModel):
    """Bloc standard d'une planification hebdo auto."""

    titre: str = ""
    items: list[str] = Field(default_factory=list)


class PlanificationHebdoCompleteResponse(BaseModel):
    """Planification hebdomadaire auto consolidée multi-modules."""

    semaine_reference: str = ""
    genere_en_un_clic: bool = True
    blocs: list[BlocPlanificationAuto] = Field(default_factory=list)
    resume: str = ""


class EtapeBatchIntelligente(BaseModel):
    """Étape recommandée d'un plan batch cooking intelligent."""

    ordre: int = 1
    action: str = ""
    duree_minutes: int = 0


class BatchCookingIntelligentResponse(BaseModel):
    """Plan batch cooking recommandé selon la semaine cible."""

    session_nom: str = ""
    date_session: str = ""
    recettes_cibles: list[str] = Field(default_factory=list)
    duree_estimee_totale_minutes: int = 0
    etapes: list[EtapeBatchIntelligente] = Field(default_factory=list)
    conseils: list[str] = Field(default_factory=list)


class CarteVisuellePartageableResponse(BaseModel):
    """Carte visuelle exportable pour partage (image encodée)."""

    type_carte: str = "planning"
    format_image: str = "image/svg+xml"
    filename: str = ""
    contenu_base64: str = ""
    metadata: dict[str, str] = Field(default_factory=dict)


class CarteMagazineTablette(BaseModel):
    """Carte affichée dans la vue magazine tablette."""

    titre: str = ""
    valeur: str = ""
    accent: str = "neutre"
    action_url: str = ""


class ModeTabletteMagazineResponse(BaseModel):
    """Données de rendu pour le mode tablette magazine."""

    titre: str = ""
    sous_titre: str = ""
    cartes: list[CarteMagazineTablette] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# SPRINT 23 — INNOVATIONS LONG TERME
# ═══════════════════════════════════════════════════════════


class CommandeWhatsApp(BaseModel):
    """Commande textuelle WhatsApp supportée."""

    commande: str = ""
    action: str = ""


class WhatsAppConversationnelResponse(BaseModel):
    """Synthèse des commandes conversationnelles WhatsApp disponibles."""

    actif: bool = True
    nb_commandes: int = 0
    commandes: list[CommandeWhatsApp] = Field(default_factory=list)


class PrixIngredientCompare(BaseModel):
    """Comparaison de prix pour un ingrédient fréquent."""

    ingredient: str = ""
    frequence_utilisation: int = 0
    prix_historique_moyen_eur: float | None = None
    prix_marche_eur: float | None = None
    source_prix: str = "historique"
    variation_pct: float | None = None
    alerte_soldes: bool = False


class ComparateurPrixAutomatiqueResponse(BaseModel):
    """Veille prix automatique sur les ingrédients les plus fréquents."""

    date_reference: str = ""
    nb_ingredients_analyses: int = 0
    ingredients: list[PrixIngredientCompare] = Field(default_factory=list)
    nb_alertes: int = 0
    alertes: list[str] = Field(default_factory=list)


class EnergieTempsReelResponse(BaseModel):
    """Vue énergie quasi temps-réel (Linky si disponible, sinon estimation)."""

    linky_connecte: bool = False
    source: str = "estimation"
    horodatage: str = ""
    puissance_instantanee_w: float | None = None
    consommation_jour_estimee_kwh: float | None = None
    consommation_mois_kwh: float | None = None
    tendance: str = "stable"
    alertes: list[str] = Field(default_factory=list)


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
