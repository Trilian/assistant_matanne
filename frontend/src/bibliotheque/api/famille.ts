// ═══════════════════════════════════════════════════════════
// API Famille
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type {
  ProfilEnfant,
  JalonJules,
  Activite,
  Routine,
  DepenseBudget,
  StatsBudget,
} from "@/types/famille";

// ─── Jules ────────────────────────────────────────────────

/** Obtenir le profil enfant Jules */
export async function obtenirProfilJules(): Promise<ProfilEnfant> {
  const { data } = await clientApi.get<{ items: ProfilEnfant[] }>(
    "/famille/enfants"
  );
  return data.items[0];
}

/** Obtenir les jalons de développement de Jules */
export async function listerJalons(categorie?: string): Promise<JalonJules[]> {
  const params: Record<string, string> = {};
  if (categorie) params.categorie = categorie;
  const { data } = await clientApi.get<{ items: JalonJules[] }>(
    "/famille/enfants/1/jalons",
    { params }
  );
  return data.items;
}

/** Ajouter un jalon */
export async function ajouterJalon(
  jalon: Omit<JalonJules, "id">,
  enfantId: number = 1
): Promise<JalonJules> {
  const { data } = await clientApi.post<JalonJules>(
    `/famille/enfants/${enfantId}/jalons`,
    jalon
  );
  return data;
}

/** Supprimer un jalon */
export async function supprimerJalon(
  jalonId: number,
  enfantId: number = 1
): Promise<void> {
  await clientApi.delete(`/famille/enfants/${enfantId}/jalons/${jalonId}`);
}

// ─── Activités ────────────────────────────────────────────

/** Lister les activités */
export async function listerActivites(
  type?: string,
  dateDebut?: string
): Promise<Activite[]> {
  const params: Record<string, string> = {};
  if (type) params.type = type;
  if (dateDebut) params.date_debut = dateDebut;
  const { data } = await clientApi.get<{ items: Activite[] }>(
    "/famille/activites",
    { params }
  );
  return data.items;
}

/** Créer une activité */
export async function creerActivite(
  activite: Omit<Activite, "id">
): Promise<Activite> {
  const { data } = await clientApi.post<Activite>(
    "/famille/activites",
    activite
  );
  return data;
}

/** Modifier une activité */
export async function modifierActivite(
  id: number,
  activite: Partial<Activite>
): Promise<Activite> {
  const { data } = await clientApi.patch<Activite>(
    `/famille/activites/${id}`,
    activite
  );
  return data;
}

/** Supprimer une activité */
export async function supprimerActivite(id: number): Promise<void> {
  await clientApi.delete(`/famille/activites/${id}`);
}

// ─── Suggestions IA Activités ─────────────────────────────

/** Paramètres pour les suggestions d'activités IA */
export interface ParamsSuggestionsActivites {
  age_mois: number
  meteo?: string
  budget_max?: number
  duree_min?: number
  duree_max?: number
  preferences?: string[]
  nb_suggestions?: number
}

/** Suggestion d'activité retournée par l'IA */
export interface SuggestionActivite {
  nom: string
  description: string
  duree_minutes: number
  budget: number
  lieu: 'interieur' | 'exterieur' | 'mixte'
  competences: string[]
  materiel: string[]
  niveau_effort: 'faible' | 'moyen' | 'eleve'
  adapte_pour: number[]
}

/** Réponse de l'API suggestions */
export interface ReponseSuggestionsActivites {
  total: number
  suggestions: SuggestionActivite[]
  params: ParamsSuggestionsActivites
}

/** Obtenir des suggestions d'activités via IA */
export async function obtenirSuggestionsActivites(
  params: ParamsSuggestionsActivites
): Promise<ReponseSuggestionsActivites> {
  const { data } = await clientApi.post<ReponseSuggestionsActivites>(
    "/famille/activites/suggestions-ia",
    params
  );
  return data;
}

// ─── Routines ─────────────────────────────────────────────

/** Lister les routines */
export async function listerRoutines(): Promise<Routine[]> {
  const { data } = await clientApi.get<{ items: Routine[] }>(
    "/famille/routines"
  );
  return data.items;
}

/** Obtenir une routine */
export async function obtenirRoutine(id: number): Promise<Routine> {
  const { data } = await clientApi.get<Routine>(`/famille/routines/${id}`);
  return data;
}

/** Créer une routine */
export async function creerRoutine(
  routine: Omit<Routine, "id">
): Promise<Routine> {
  const { data } = await clientApi.post<Routine>(
    "/famille/routines",
    routine
  );
  return data;
}

/** Modifier une routine */
export async function modifierRoutine(
  id: number,
  routine: Partial<Routine>
): Promise<Routine> {
  const { data } = await clientApi.patch<Routine>(
    `/famille/routines/${id}`,
    routine
  );
  return data;
}

/** Supprimer une routine */
export async function supprimerRoutine(id: number): Promise<void> {
  await clientApi.delete(`/famille/routines/${id}`);
}

// ─── Budget ───────────────────────────────────────────────

/** Lister les dépenses */
export async function listerDepenses(
  categorie?: string
): Promise<DepenseBudget[]> {
  const params: Record<string, string> = {};
  if (categorie) params.categorie = categorie;
  const { data } = await clientApi.get<{ items: DepenseBudget[] }>(
    "/famille/budget",
    { params }
  );
  return data.items;
}

/** Statistiques budget */
export async function obtenirStatsBudget(): Promise<StatsBudget> {
  const { data } = await clientApi.get<StatsBudget>("/famille/budget/stats");
  return data;
}

/** Ajouter une dépense */
export async function ajouterDepense(
  depense: Omit<DepenseBudget, "id">
): Promise<DepenseBudget> {
  const { data } = await clientApi.post<DepenseBudget>(
    "/famille/budget",
    depense
  );
  return data;
}

/** Supprimer une dépense */
export async function supprimerDepense(id: number): Promise<void> {
  await clientApi.delete(`/famille/budget/${id}`);
}

// ─── Budget IA — Analyse, Prédictions, Anomalies ──────────

export interface PredictionCategorie {
  categorie: string;
  montant_prevu: number;
  tendance: "hausse" | "baisse" | "stable";
  explication: string;
}

export interface PredictionBudget {
  total_prevu: number;
  par_categorie: PredictionCategorie[];
  confiance: number;
  resume: string;
}

export interface AnomalieBudget {
  type: "pic" | "baisse" | "nouvelle_categorie" | "irregularite";
  categorie: string;
  ecart_pourcent: number;
  severite: "info" | "warning" | "danger";
  description: string;
}

export interface SuggestionEconomie {
  titre: string;
  description: string;
  economie_estimee: number;
  categorie: string;
  difficulte: "facile" | "moyen" | "difficile";
}

export interface AnalyseBudgetIA {
  predictions: PredictionBudget | null;
  anomalies: AnomalieBudget[];
  suggestions: SuggestionEconomie[];
  historique: Array<{ mois: number; annee: number; total: number; par_categorie: Record<string, number> }>;
}

/** Analyse IA complète du budget (prédictions + anomalies + suggestions) */
export async function obtenirAnalyseBudgetIA(): Promise<AnalyseBudgetIA> {
  const { data } = await clientApi.get<AnalyseBudgetIA>("/famille/budget/analyse-ia");
  return data;
}

/** Prédictions seules */
export async function obtenirPredictionsBudget(): Promise<{ predictions: PredictionBudget | null; historique: AnalyseBudgetIA["historique"] }> {
  const { data } = await clientApi.get("/famille/budget/predictions");
  return data;
}

/** Anomalies seules */
export async function obtenirAnomaliesBudget(): Promise<{ anomalies: AnomalieBudget[] }> {
  const { data } = await clientApi.get("/famille/budget/anomalies");
  return data;
}

// ─── Anniversaires ────────────────────────────────────────

export interface Anniversaire {
  id: number;
  nom_personne: string;
  date_naissance: string;
  relation: string;
  rappel_jours_avant: number[];
  idees_cadeaux?: string;
  historique_cadeaux?: { annee: number; cadeau: string; budget?: number }[];
  notes?: string;
  actif: boolean;
  age?: number;
  jours_restants?: number;
}

/** Lister les anniversaires */
export async function listerAnniversaires(
  relation?: string
): Promise<Anniversaire[]> {
  const params: Record<string, string> = {};
  if (relation) params.relation = relation;
  const { data } = await clientApi.get<{ items: Anniversaire[] }>(
    "/famille/anniversaires",
    { params }
  );
  return data.items;
}

/** Créer un anniversaire */
export async function creerAnniversaire(
  anniversaire: Omit<Anniversaire, "id" | "actif" | "age" | "jours_restants" | "historique_cadeaux">
): Promise<Anniversaire> {
  const { data } = await clientApi.post<Anniversaire>(
    "/famille/anniversaires",
    anniversaire
  );
  return data;
}

/** Modifier un anniversaire */
export async function modifierAnniversaire(
  id: number,
  patch: Partial<Anniversaire>
): Promise<Anniversaire> {
  const { data } = await clientApi.patch<Anniversaire>(
    `/famille/anniversaires/${id}`,
    patch
  );
  return data;
}

/** Supprimer un anniversaire */
export async function supprimerAnniversaire(id: number): Promise<void> {
  await clientApi.delete(`/famille/anniversaires/${id}`);
}

// ─── Événements familiaux ─────────────────────────────────

export interface EvenementFamilial {
  id: number;
  titre: string;
  date_evenement: string;
  type_evenement: string;
  recurrence: string;
  rappel_jours_avant: number;
  notes?: string;
  participants?: string[];
  actif: boolean;
}

/** Lister les événements familiaux */
export async function listerEvenementsFamiliaux(
  type?: string
): Promise<EvenementFamilial[]> {
  const params: Record<string, string> = {};
  if (type) params.type_evenement = type;
  const { data } = await clientApi.get<{ items: EvenementFamilial[] }>(
    "/famille/evenements",
    { params }
  );
  return data.items;
}

/** Créer un événement familial */
export async function creerEvenementFamilial(
  event: Omit<EvenementFamilial, "id" | "actif">
): Promise<EvenementFamilial> {
  const { data } = await clientApi.post<EvenementFamilial>(
    "/famille/evenements",
    event
  );
  return data;
}

/** Modifier un événement familial */
export async function modifierEvenementFamilial(
  id: number,
  patch: Partial<EvenementFamilial>
): Promise<EvenementFamilial> {
  const { data } = await clientApi.patch<EvenementFamilial>(
    `/famille/evenements/${id}`,
    patch
  );
  return data;
}

/** Supprimer un événement familial */
export async function supprimerEvenementFamilial(
  id: number
): Promise<void> {
  await clientApi.delete(`/famille/evenements/${id}`);
}

// ─── Contexte Familial (Phase M) ─────────────────────────

import type {
  ContexteFamilial,
  AchatFamille,
  RappelFamille,
  CroissanceData,
} from "@/types/famille";

/** Obtenir le contexte familial complet (1 seul appel) */
export async function obtenirContexteFamilial(): Promise<ContexteFamilial> {
  const { data } = await clientApi.get<ContexteFamilial>("/famille/contexte");
  return data;
}

// ─── Suggestions IA (Phase M3) ───────────────────────────

/** Suggestions weekend avec météo auto-injectée */
export async function obtenirSuggestionsWeekend(params?: {
  budget?: number;
  region?: string;
  nb_suggestions?: number;
}): Promise<{ suggestions: string; meteo?: string }> {
  const { data } = await clientApi.post("/famille/weekend/suggestions-ia", params ?? {});
  return data;
}

/** Résumé hebdomadaire IA */
export async function obtenirResumeSemaine(params?: {
  evenements?: string[];
  jalons?: string[];
  humeur_famille?: string;
}): Promise<{ resume: string }> {
  const { data } = await clientApi.post("/famille/journal/resume-semaine", params ?? { evenements: [] });
  return data;
}

/** Rétrospective mensuelle IA */
export async function obtenirRetrospective(params?: {
  mois?: string;
  resumes_semaines?: string[];
  nb_evenements?: number;
  nb_jalons?: number;
}): Promise<{ retrospective: string }> {
  const defaultMois = new Date().toLocaleDateString("fr-FR", { month: "long", year: "numeric" });
  const { data } = await clientApi.post("/famille/journal/retrospective", {
    mois: params?.mois ?? defaultMois,
    resumes_semaines: params?.resumes_semaines ?? [],
    nb_evenements: params?.nb_evenements,
    nb_jalons: params?.nb_jalons,
  });
  return data;
}

/** Suggestions soirée couple IA */
export async function obtenirSuggestionsSoiree(params?: {
  budget?: number;
  duree_heures?: number;
  type_soiree?: string;
  region?: string;
}): Promise<{ suggestions: string }> {
  const { data } = await clientApi.post("/famille/soiree/suggestions-ia", params ?? {});
  return data;
}

/** Suggestions activités avec météo auto (Phase O) */
export async function obtenirSuggestionsActivitesAuto(params?: {
  budget_max?: number;
  duree_max_heures?: number;
  type_prefere?: string;
}): Promise<{ suggestions: string; meteo: string; journee_libre: boolean }> {
  const { data } = await clientApi.post("/famille/activites/suggestions-ia-auto", params ?? {});
  return data;
}

// ─── Achats Famille CRUD (Phase M4/P) ────────────────────

/** Lister les achats (via shopping existant) */
export async function listerAchats(params?: {
  categorie?: string;
  actif?: boolean;
}): Promise<AchatFamille[]> {
  const { data } = await clientApi.get<{ items: AchatFamille[] }>(
    "/famille/shopping",
    { params }
  );
  return data.items;
}

/** Créer un achat */
export async function creerAchat(
  achat: Omit<AchatFamille, "id" | "achete" | "date_achat" | "prix_reel">
): Promise<AchatFamille> {
  const { data } = await clientApi.post<AchatFamille>("/famille/achats", achat);
  return data;
}

/** Modifier un achat */
export async function modifierAchat(
  id: number,
  patch: Partial<AchatFamille>
): Promise<AchatFamille> {
  const { data } = await clientApi.patch<AchatFamille>(
    `/famille/achats/${id}`,
    patch
  );
  return data;
}

/** Marquer un achat comme acheté */
export async function marquerAchatAchete(
  id: number,
  prix_reel?: number
): Promise<void> {
  await clientApi.post(`/famille/achats/${id}/achete`, { prix_reel });
}

/** Supprimer un achat */
export async function supprimerAchat(id: number): Promise<void> {
  await clientApi.delete(`/famille/achats/${id}`);
}

/** Suggestions IA achats/cadeaux (Phase P) */
export interface SuggestionAchat {
  titre: string;
  description: string;
  fourchette_prix?: string | null;
  ou_acheter?: string | null;
  pertinence?: string | null;
}
export async function obtenirSuggestionsAchatsIA(params: {
  type: "anniversaire" | "jalon" | "saison";
  nom?: string;
  age?: number;
  relation?: string;
  budget_max?: number;
  historique_cadeaux?: string[];
  prochains_jalons?: string[];
  saison?: string;
  tailles?: Record<string, string>;
}): Promise<{ suggestions: SuggestionAchat[]; total: number; type: string }> {
  const { data } = await clientApi.post("/famille/achats/suggestions-ia", params);
  return data;
}

// ─── Rappels (Phase Q) ──────────────────────────────────

/** Évaluer les rappels du jour */
export async function evaluerRappelsFamille(): Promise<{
  rappels: RappelFamille[];
  total: number;
}> {
  const { data } = await clientApi.get("/famille/rappels/evaluer");
  return data;
}

/** Envoyer les rappels push */
export async function envoyerRappels(): Promise<{
  envoyes: number;
  message: string;
}> {
  const { data } = await clientApi.post("/famille/rappels/envoyer");
  return data;
}

// ─── Croissance OMS (Phase R) ───────────────────────────

/** Obtenir les données de croissance Jules + normes OMS */
export async function obtenirCroissanceJules(): Promise<CroissanceData> {
  const { data } = await clientApi.get<CroissanceData>(
    "/famille/jules/croissance"
  );
  return data;
}
