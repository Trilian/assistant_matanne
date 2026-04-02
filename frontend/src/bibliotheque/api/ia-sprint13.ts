import { clientApi } from "./client";

const API_PREFIX = "/api/v1/ia/sprint13";

export interface PredictionConsommationRequest {
  ingredient_nom: string;
  stock_actuel_kg: number;
  historique_achat_mensuel: number[];
}

export interface PredictionConsommationResponse {
  prochaine_consommation_estimee_j: number;
  confiance_prediction: number;
}

export interface MealPlanningDay {
  date: string;
  petit_dejeuner: string;
  dejeuner: string;
  diner: string;
}

export interface AnalyseVarietePlanningRequest {
  planning_repas: MealPlanningDay[];
}

export interface AnalyseVarieteResponse {
  variete_score: number;
  equilibre_nutritionnel: string;
  categories_presentes: string[];
}

export interface MeteoContexte {
  date: string;
  meteo: string;
  activites_suggerees: string[];
  recommandations?: string[];
}

export interface AnalyseImpactsMeteoRequest {
  previsions_7j: Array<{
    date: string;
    meteo: string;
    temperature_min: number;
    temperature_max: number;
    precipitation_mm: number;
  }>;
  saison: string;
}

export interface AnalyseHabitudeRequest {
  habitude_nom: string;
  historique_7j: number[];
  description_contexte?: string;
}

export interface AnalyseHabitudeResponse {
  compliance_rate: number;
  tendance: string;
  score_tendance: number;
}

export interface EstimationProjetMaisonRequest {
  projet_description: string;
  surface_m2: number;
  type_maison: string;
  contraintes?: string[];
}

export interface EstimationProjetResponse {
  cout_estime_min: number;
  cout_estime_max: number;
  duree_estimee_j: number;
  professionnel_recommande?: boolean;
  complexite_estimee?: string;
}

export interface DonneesNutritionPersonneRequest {
  personne_nom: string;
  age_ans: number;
  sexe: "M" | "F";
  activite_niveau: string;
  recettes_semaine: string[];
  objectif_sante?: string;
  donnees_garmin_semaine?: unknown;
}

export interface DonneesNutritionnellesResponse {
  calories_journalieres_recommandees: number;
  proteines_g_j: number;
  glucides_g_j: number;
  lipides_g_j: number;
  notes_personnalisees?: string;
}

export async function predireConsommationInventaire(
  body: PredictionConsommationRequest
): Promise<PredictionConsommationResponse> {
  const { data } = await clientApi.post<PredictionConsommationResponse>(
    `${API_PREFIX}/inventaire/prediction-consommation`,
    body
  );
  return data;
}

export async function analyserVarietePlanningRepas(
  body: AnalyseVarietePlanningRequest
): Promise<AnalyseVarieteResponse> {
  const { data } = await clientApi.post<AnalyseVarieteResponse>(
    `${API_PREFIX}/planning/analyse-variete`,
    body
  );
  return data;
}

export async function analyserImpactsMeteo(
  body: AnalyseImpactsMeteoRequest
): Promise<MeteoContexte[]> {
  const { data } = await clientApi.post<MeteoContexte[]>(`${API_PREFIX}/meteo/impacts`, body);
  return data;
}

export async function analyserHabitudeFamille(
  body: AnalyseHabitudeRequest
): Promise<AnalyseHabitudeResponse> {
  const { data } = await clientApi.post<AnalyseHabitudeResponse>(`${API_PREFIX}/habitudes/analyse`, body);
  return data;
}

export async function estimerProjetMaison(
  body: EstimationProjetMaisonRequest
): Promise<EstimationProjetResponse> {
  const { data } = await clientApi.post<EstimationProjetResponse>(`${API_PREFIX}/maison/projets/estimation`, body);
  return data;
}

export async function analyserNutritionPersonne(
  body: DonneesNutritionPersonneRequest
): Promise<DonneesNutritionnellesResponse> {
  const { data } = await clientApi.post<DonneesNutritionnellesResponse>(`${API_PREFIX}/nutrition/personne`, body);
  return data;
}
