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

export interface PreferenceApprise {
  categorie: string;
  valeur: string;
  score_confiance: number;
}

export interface ApprentissagePreferencesResponse {
  semaines_analysees: number;
  influence_active: boolean;
  preferences_favorites: PreferenceApprise[];
  preferences_a_eviter: PreferenceApprise[];
  ajustements_suggestions: string[];
}

export interface BlocPlanificationAuto {
  titre: string;
  items: string[];
}

export interface PlanificationHebdoCompleteResponse {
  semaine_reference: string;
  genere_en_un_clic: boolean;
  blocs: BlocPlanificationAuto[];
  resume: string;
}

export interface EtapeBatchIntelligente {
  ordre: number;
  action: string;
  duree_minutes: number;
}

export interface BatchCookingIntelligentResponse {
  session_nom: string;
  date_session: string;
  recettes_cibles: string[];
  duree_estimee_totale_minutes: number;
  etapes: EtapeBatchIntelligente[];
  conseils: string[];
}

export interface CarteVisuellePartageableResponse {
  type_carte: string;
  format_image: string;
  filename: string;
  contenu_base64: string;
  metadata: Record<string, string>;
}

export interface CarteMagazineTablette {
  titre: string;
  valeur: string;
  accent: string;
  action_url: string;
}

export interface ModeTabletteMagazineResponse {
  titre: string;
  sous_titre: string;
  cartes: CarteMagazineTablette[];
}

export interface CommandeWhatsApp {
  commande: string;
  action: string;
}

export interface WhatsAppConversationnelResponse {
  actif: boolean;
  nb_commandes: number;
  commandes: CommandeWhatsApp[];
}

export interface PrixIngredientCompare {
  ingredient: string;
  frequence_utilisation: number;
  prix_historique_moyen_eur: number | null;
  prix_marche_eur: number | null;
  source_prix: string;
  variation_pct: number | null;
  alerte_soldes: boolean;
}

export interface ComparateurPrixAutomatiqueResponse {
  date_reference: string;
  nb_ingredients_analyses: number;
  ingredients: PrixIngredientCompare[];
  nb_alertes: number;
  alertes: string[];
}

export interface EnergieTempsReelResponse {
  linky_connecte: boolean;
  source: string;
  horodatage: string;
  puissance_instantanee_w: number | null;
  consommation_jour_estimee_kwh: number | null;
  consommation_mois_kwh: number | null;
  tendance: string;
  alertes: string[];
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

export async function obtenirPreferencesApprises(): Promise<ApprentissagePreferencesResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/s22/preferences-apprises");
  return data;
}

export async function obtenirPlanificationHebdoAuto(): Promise<PlanificationHebdoCompleteResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/s22/planification-auto");
  return data;
}

export async function obtenirBatchCookingIntelligent(): Promise<BatchCookingIntelligentResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/s22/batch-cooking-intelligent");
  return data;
}

export async function genererCarteVisuellePartageable(payload: {
  type_carte: "planning" | "recette" | "batch" | "maison";
  titre?: string;
}): Promise<CarteVisuellePartageableResponse> {
  const { data } = await clientApi.post("/api/v1/innovations/phasee/s22/carte-visuelle", payload);
  return data;
}

export async function obtenirModeTabletteMagazine(): Promise<ModeTabletteMagazineResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/s22/mode-tablette-magazine");
  return data;
}

export async function obtenirWhatsAppConversationnel(): Promise<WhatsAppConversationnelResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/s23/whatsapp-conversationnel");
  return data;
}

export async function obtenirComparateurPrixAuto(topN = 20): Promise<ComparateurPrixAutomatiqueResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/s23/comparateur-prix-auto", {
    params: { top_n: topN },
  });
  return data;
}

export async function obtenirEnergieTempsReel(): Promise<EnergieTempsReelResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/s23/energie-temps-reel");
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
