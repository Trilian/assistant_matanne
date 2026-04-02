import { clientApi } from "./client";

export interface ActionPiloteAuto {
  module: string;
  action: string;
  statut: string;
  details: string;
}

export interface ModePiloteAutoResponse {
  actif: boolean;
  niveau_autonomie: string;
  actions: ActionPiloteAuto[];
  recommandations: string[];
}

export interface ConfigurationModePiloteRequest {
  actif: boolean;
  niveau_autonomie?: string;
}

export interface ScoreFamilleDimension {
  nom: string;
  score: number;
  poids: number;
}

export interface ScoreFamilleHebdoResponse {
  semaine_reference: string;
  score_global: number;
  dimensions: ScoreFamilleDimension[];
  recommandations: string[];
}

export interface JournalFamilialAutoResponse {
  semaine_reference: string;
  titre: string;
  resume: string;
  faits_marquants: string[];
  moments_joyeux: string[];
  points_attention: string[];
}

export interface RapportMensuelPdfResponse {
  mois_reference: string;
  filename: string;
  contenu_base64: string;
}

export interface SuggestionRepasGarminResponse {
  recette_suggeree: string;
  raison: string;
  temps_total_estime_min: number;
  alternatives: string[];
}

export interface ModeVacancesResponse {
  actif: boolean;
  checklist_voyage_auto: boolean;
  courses_mode_compact: boolean;
  entretien_suspendu: boolean;
  recommandations: string[];
}

export interface InsightQuotidien {
  titre: string;
  message: string;
  module: string;
  priorite: string;
  action_url: string;
}

export interface InsightsQuotidiensResponse {
  date_reference: string;
  limite_journaliere: number;
  nb_insights: number;
  insights: InsightQuotidien[];
}

export interface MeteoImpactModule {
  module: string;
  impact: string;
  actions_recommandees: string[];
}

export interface MeteoContextuelleResponse {
  ville: string;
  saison: string;
  temperature: number | null;
  description: string;
  modules: MeteoImpactModule[];
}

export async function obtenirModePiloteAuto(): Promise<ModePiloteAutoResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/mode-pilote");
  return data;
}

export async function configurerModePiloteAuto(
  payload: ConfigurationModePiloteRequest
): Promise<ModePiloteAutoResponse> {
  const { data } = await clientApi.post("/api/v1/innovations/phasee/mode-pilote/config", payload);
  return data;
}

export async function obtenirScoreFamilleHebdo(): Promise<ScoreFamilleHebdoResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/score-famille-hebdo");
  return data;
}

export async function obtenirJournalFamilialAuto(): Promise<JournalFamilialAutoResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/journal-familial");
  return data;
}

export async function obtenirJournalFamilialPdf(): Promise<RapportMensuelPdfResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/journal-familial/pdf");
  return data;
}

export async function obtenirRapportMensuelPdf(mois?: string): Promise<RapportMensuelPdfResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/rapport-mensuel/pdf", {
    params: { mois },
  });
  return data;
}

export async function obtenirSuggestionRepasGarmin(): Promise<SuggestionRepasGarminResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/garmin-repas-adaptatif");
  return data;
}

export async function obtenirModeVacances(): Promise<ModeVacancesResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/mode-vacances");
  return data;
}

export async function configurerModeVacances(payload: {
  actif: boolean;
  checklist_voyage_auto?: boolean;
}): Promise<ModeVacancesResponse> {
  const { data } = await clientApi.post("/api/v1/innovations/phasee/mode-vacances/config", payload);
  return data;
}

export async function obtenirInsightsQuotidiens(limite = 2): Promise<InsightsQuotidiensResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/insights-quotidiens", {
    params: { limite },
  });
  return data;
}

export async function obtenirMeteoContextuelle(): Promise<MeteoContextuelleResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/meteo-contextuelle");
  return data;
}

export function telechargerPdfBase64(base64Content: string, filename: string): void {
  const byteCharacters = atob(base64Content);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i += 1) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
