// ═══════════════════════════════════════════════════════════
// API Phase B — Prédictions, IA, Bridges, Flux
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";

// ── Types ────────────────────────────────────────────

export interface PredictionCourses {
  nom: string;
  categorie: string;
  frequence_jours: number;
  score_confiance: number;
  derniere_date: string | null;
}

export interface HabitudesAchat {
  article: string;
  frequence_moyenne_jours: number;
  quantite_moyenne: number;
  nb_achats: number;
}

export interface PrevisionBudget {
  mois: string;
  depenses_actuelles: number;
  prevision_fin_mois: number;
  budget_reference: number | null;
  ecart_prevu_pct: number | null;
  par_categorie: Record<string, { actuel: number; prevu: number }>;
}

export interface AnomalieBudget {
  categorie: string;
  depense: number;
  reference: number;
  pourcentage: number;
  niveau: string;
}

export interface ResumeHebdo {
  semaine: string;
  resume: string;
  sections: Record<string, unknown>;
}

export interface DiagnosticMaison {
  probleme: string;
  diagnostic: string;
  solutions: string[];
  urgence: string;
  cout_estime: string | null;
}

export interface PlanningAdapte {
  planning: Record<string, unknown>;
  contexte: Record<string, unknown>;
}

export interface BatchCookingPlan {
  plan: Record<string, unknown>;
}

export interface ConseilJules {
  conseils: Record<string, unknown>;
}

export interface ChecklistVoyage {
  checklist: Record<string, unknown>;
}

export interface ScoreEcologique {
  score: Record<string, unknown>;
}

export interface AnalyseNutritionnelle {
  analyse: Record<string, unknown>;
}

export interface OptimisationEnergie {
  recommandations: Record<string, unknown>;
}

export interface StreakRoutine {
  nom: string;
  streak: number;
  meilleur_streak: number;
  taux_completion: number;
}

export interface ComparaisonEnergieMois {
  mois: number;
  mois_nom: string;
  annee_n: number;
  annee_n1: number;
  ecart_pct: number;
  tendance: string;
}

export interface ComparaisonEnergie {
  type_energie: string;
  annee_n: number;
  annee_n1: number;
  mois: ComparaisonEnergieMois[];
  total_n: number;
  total_n1: number;
  ecart_total_pct: number;
}

export interface SuggestionEntretien {
  equipement: string;
  categorie: string | null;
  age_annees: number;
  seuil_revision: number;
  suggestion: string;
  priorite: string;
}

export interface FluxCuisine {
  etape_actuelle: string;
  planning: { id: number; semaine: string } | null;
  courses: {
    id: number;
    articles: number;
    coches: number;
    progression: number;
  } | null;
  actions_suivantes: { action: string; label: string; url: string }[];
}

export interface DigestQuotidien {
  date: string;
  jour: string;
  repas: { type: string; recette: string }[];
  routines: { routine: string; taches_restantes: number }[];
  entretien: { nom: string; priorite: string }[];
  nb_sections: number;
}

export interface FeedbackItem {
  recette_id: number;
  note: number;
  commentaire?: string;
  mange?: boolean;
}

export interface DocumentExpire {
  id: number;
  titre: string;
  date_expiration: string;
  jours_restants: number;
  type_document: string;
}

export interface BridgeRecolteRecette {
  ingredient: string;
  recettes: string[];
}

// ── Prédictions ──────────────────────────────────────

export async function obtenirPredictionsCourses(
  limite = 20
): Promise<PredictionCourses[]> {
  const { data } = await clientApi.get<PredictionCourses[]>(
    "/predictions/courses",
    { params: { limite } }
  );
  return data;
}

export async function obtenirHabitudesAchat(): Promise<HabitudesAchat[]> {
  const { data } = await clientApi.get<HabitudesAchat[]>(
    "/predictions/habitudes"
  );
  return data;
}

// ── Budget IA ────────────────────────────────────────

export async function obtenirPrevisionBudget(): Promise<PrevisionBudget> {
  const { data } = await clientApi.get<PrevisionBudget>(
    "/ia/budget/prevision"
  );
  return data;
}

export async function obtenirAnomaliesBudget(): Promise<AnomalieBudget[]> {
  const { data } = await clientApi.get<AnomalieBudget[]>(
    "/ia/budget/anomalies"
  );
  return data;
}

export async function categoriserDepense(
  description: string
): Promise<{ categorie: string; confiance: number }> {
  const { data } = await clientApi.post("/ia/budget/categoriser", {
    description,
  });
  return data;
}

// ── Résumé hebdomadaire ──────────────────────────────

export async function obtenirResumeHebdo(): Promise<ResumeHebdo> {
  const { data } = await clientApi.get<ResumeHebdo>("/ia/resume-hebdo");
  return data;
}

// ── Diagnostic maison ────────────────────────────────

export async function diagnostiquerTexte(
  description: string,
  zone?: string
): Promise<DiagnosticMaison> {
  const { data } = await clientApi.post<DiagnosticMaison>(
    "/ia/diagnostic/texte",
    { description, zone }
  );
  return data;
}

// ── Planning adaptatif ───────────────────────────────

export async function obtenirPlanningAdapte(): Promise<PlanningAdapte> {
  const { data } = await clientApi.get<PlanningAdapte>(
    "/ia/planning-adapte"
  );
  return data;
}

// ── Batch cooking IA ────────────────────────────────

export async function obtenirBatchCookingPlan(
  nb_personnes = 4,
  nb_repas = 5
): Promise<BatchCookingPlan> {
  const { data } = await clientApi.get<BatchCookingPlan>(
    "/ia/batch-cooking-plan",
    { params: { nb_personnes, nb_repas } }
  );
  return data;
}

// ── Jules IA ────────────────────────────────────────

export async function obtenirConseilJules(): Promise<ConseilJules> {
  const { data } = await clientApi.get<ConseilJules>("/ia/conseil-jules");
  return data;
}

// ── Voyage IA ───────────────────────────────────────

export async function genererChecklistVoyage(
  destination: string,
  date_depart: string,
  duree_jours: number,
  nb_adultes = 2,
  nb_enfants = 1
): Promise<ChecklistVoyage> {
  const { data } = await clientApi.post<ChecklistVoyage>(
    "/ia/checklist-voyage",
    { destination, date_depart, duree_jours, nb_adultes, nb_enfants }
  );
  return data;
}

// ── Score écologique ────────────────────────────────

export async function obtenirScoreEcologique(
  recette_ids: number[]
): Promise<ScoreEcologique> {
  const { data } = await clientApi.post<ScoreEcologique>(
    "/ia/score-ecologique",
    { recette_ids }
  );
  return data;
}

// ── Nutrition IA ────────────────────────────────────

export async function obtenirAnalyseNutritionnelle(): Promise<AnalyseNutritionnelle> {
  const { data } = await clientApi.get<AnalyseNutritionnelle>(
    "/ia/analyse-nutritionnelle"
  );
  return data;
}

// ── Énergie IA ──────────────────────────────────────

export async function obtenirOptimisationEnergie(): Promise<OptimisationEnergie> {
  const { data } = await clientApi.get<OptimisationEnergie>(
    "/ia/optimisation-energie"
  );
  return data;
}

// ── Bridges ─────────────────────────────────────────

export async function obtenirDocumentsExpires(): Promise<DocumentExpire[]> {
  const { data } = await clientApi.get<DocumentExpire[]>(
    "/bridges/documents-expires"
  );
  return data;
}

export async function obtenirRecolteRecettes(
  ingredient: string,
  quantite_kg?: number
): Promise<BridgeRecolteRecette> {
  const { data } = await clientApi.get<BridgeRecolteRecette>(
    "/bridges/recolte-recettes",
    { params: { ingredient, quantite_kg } }
  );
  return data;
}

// ── Intra-modules (B.6) ─────────────────────────────

export async function obtenirStreakRoutines(): Promise<
  Record<string, StreakRoutine>
> {
  const { data } = await clientApi.get<Record<string, StreakRoutine>>(
    "/intra/routines-streak"
  );
  return data;
}

export async function obtenirComparaisonEnergie(
  type_energie = "electricite"
): Promise<ComparaisonEnergie> {
  const { data } = await clientApi.get<ComparaisonEnergie>(
    "/intra/energie-comparaison",
    { params: { type_energie } }
  );
  return data;
}

export async function obtenirSuggestionsEntretienAge(): Promise<
  SuggestionEntretien[]
> {
  const { data } = await clientApi.get<SuggestionEntretien[]>(
    "/intra/suggestions-entretien-age"
  );
  return data;
}

// ── Flux utilisateur (B.7) ──────────────────────────

export async function obtenirFluxCuisine(
  planningId?: number
): Promise<FluxCuisine> {
  const { data } = await clientApi.get<FluxCuisine>(
    "/flux/cuisine-3-clics",
    { params: planningId ? { planning_id: planningId } : {} }
  );
  return data;
}

export async function obtenirDigestQuotidien(): Promise<DigestQuotidien> {
  const { data } = await clientApi.get<DigestQuotidien>(
    "/flux/digest-quotidien"
  );
  return data;
}

export async function marquerTacheFait(
  tacheId: number
): Promise<{
  tache_id: number;
  nom: string;
  fait: boolean;
  prochaine_fois: string;
  frequence: string;
}> {
  const { data } = await clientApi.post(`/flux/marquer-fait/${tacheId}`);
  return data;
}

export async function envoyerFeedbackSemaine(
  feedbacks: FeedbackItem[]
): Promise<{ nb_feedbacks: number; score_moyen: number }> {
  const { data } = await clientApi.post("/flux/feedback-semaine", {
    feedbacks,
  });
  return data;
}
