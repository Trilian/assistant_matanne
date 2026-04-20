import { clientApi } from "./client";
import type {
  AlerteHabitat,
  AnnonceHabitat,
  CritereImmoHabitat,
  CritereScenarioHabitat,
  HabitatHub,
  HistoriquePlanHabitat,
  PieceHabitat,
  PlanHabitatConfiguration3DServeur,
  PointCarteHabitat,
  PlanHabitat,
  ProjetDecoHabitat,
  ResultatMarcheHabitat,
  ResultatSynchronisationVeilleHabitat,
  ResultatConceptDecoHabitat,
  ResultatImageHabitat,
  ResultatAnalysePlanHabitat,
  ResumeJardinHabitat,
  ScenarioHabitat,
  ZoneJardinHabitat,
  BarometreHabitat,
} from "@/types/habitat";

export async function obtenirHubHabitat(): Promise<HabitatHub> {
  const { data } = await clientApi.get<HabitatHub>("/vision-maison/hub");
  return data;
}

export async function listerScenariosHabitat(): Promise<ScenarioHabitat[]> {
  const { data } = await clientApi.get("/vision-maison/scenarios");
  return data.items ?? [];
}

export async function creerScenarioHabitat(payload: Partial<ScenarioHabitat>): Promise<ScenarioHabitat> {
  const { data } = await clientApi.post("/vision-maison/scenarios", payload);
  return data;
}

export async function comparerScenariosHabitat(): Promise<ScenarioHabitat[]> {
  const { data } = await clientApi.get("/vision-maison/scenarios/comparaison");
  return data.items ?? [];
}

export async function ajouterCritereScenarioHabitat(
  scenarioId: number,
  payload: { nom: string; poids?: number; note?: number; commentaire?: string }
): Promise<CritereScenarioHabitat> {
  const { data } = await clientApi.post(`/vision-maison/scenarios/${scenarioId}/criteres`, payload);
  return data;
}

export async function listerCriteresImmoHabitat(): Promise<CritereImmoHabitat[]> {
  const { data } = await clientApi.get("/vision-maison/criteres-immo");
  return data.items ?? [];
}

export async function listerAnnoncesHabitat(): Promise<AnnonceHabitat[]> {
  const { data } = await clientApi.get("/vision-maison/annonces");
  return data.items ?? [];
}

export async function synchroniserVeilleHabitat(payload?: {
  critere_id?: number;
  limite_par_source?: number;
  sources?: string[];
  envoyer_alertes?: boolean;
}): Promise<ResultatSynchronisationVeilleHabitat> {
  const { data } = await clientApi.post("/vision-maison/veille/synchroniser", payload ?? {});
  return data;
}

export async function listerAlertesHabitat(): Promise<AlerteHabitat[]> {
  const { data } = await clientApi.get("/vision-maison/veille/alertes");
  return data.items ?? [];
}

export async function obtenirCarteHabitat(): Promise<PointCarteHabitat[]> {
  const { data } = await clientApi.get("/vision-maison/veille/carte");
  return data.items ?? [];
}

export async function obtenirMarcheHabitat(payload?: {
  departement?: string;
  code_postal?: string;
  commune?: string;
  type_local?: string;
  nb_pieces_min?: number;
  surface_min_m2?: number;
  limite?: number;
}): Promise<ResultatMarcheHabitat> {
  const { data } = await clientApi.get("/vision-maison/marche/dvf", { params: payload ?? {} });
  return data;
}

export async function obtenirBarometreHabitat(payload?: {
  type_local?: string;
  ma_commune?: string;
  mon_code_postal?: string;
  limite_par_ville?: number;
}): Promise<BarometreHabitat> {
  const { data } = await clientApi.get("/vision-maison/marche/barometre", { params: payload ?? {} });
  return data;
}

export async function listerPlansHabitat(): Promise<PlanHabitat[]> {
  const { data } = await clientApi.get("/vision-maison/plans");
  return data.items ?? [];
}

export async function analyserPlanHabitat(
  planId: number,
  payload?: { prompt_utilisateur?: string; generer_image?: boolean }
): Promise<ResultatAnalysePlanHabitat> {
  const { data } = await clientApi.post(`/vision-maison/plans/${planId}/analyser`, payload ?? {});
  return data;
}

export async function historiquePlanHabitat(planId: number): Promise<HistoriquePlanHabitat[]> {
  const { data } = await clientApi.get(`/vision-maison/plans/${planId}/historique-ia`);
  return data.items ?? [];
}

export async function listerPiecesHabitat(planId: number): Promise<PieceHabitat[]> {
  const { data } = await clientApi.get(`/vision-maison/plans/${planId}/pieces`);
  return data.items ?? [];
}

export async function obtenirConfiguration3DHabitat(planId: number): Promise<PlanHabitatConfiguration3DServeur> {
  const { data } = await clientApi.get(`/vision-maison/plans/${planId}/configuration-3d`);
  return data;
}

export async function sauvegarderConfiguration3DHabitat(
  planId: number,
  payload: Omit<PlanHabitatConfiguration3DServeur, "plan_id">
): Promise<PlanHabitatConfiguration3DServeur> {
  const { data } = await clientApi.put(`/vision-maison/plans/${planId}/configuration-3d`, payload);
  return data;
}

export async function listerProjetsDecoHabitat(): Promise<ProjetDecoHabitat[]> {
  const { data } = await clientApi.get("/vision-maison/deco/projets");
  return data.items ?? [];
}

export async function genererSuggestionsDecoHabitat(
  projetId: number,
  payload?: { brief?: string; generer_image?: boolean }
): Promise<ResultatConceptDecoHabitat> {
  const { data } = await clientApi.post(`/vision-maison/deco/projets/${projetId}/suggestions`, payload ?? {});
  return data;
}

export async function synchroniserDepenseDecoHabitat(
  projetId: number,
  payload: { montant: number; fournisseur?: string; note?: string; categorie_depense?: string }
): Promise<{ projet_id: number; depense_maison_id: number; budget_depense: number }> {
  const { data } = await clientApi.post(`/vision-maison/deco/projets/${projetId}/depenses`, payload);
  return data;
}

export async function genererImageHabitat(payload: {
  prompt: string;
  negative_prompt?: string;
}): Promise<ResultatImageHabitat> {
  const { data } = await clientApi.post("/vision-maison/deco/images", payload);
  return data;
}

export async function listerZonesJardinHabitat(planId?: number): Promise<ZoneJardinHabitat[]> {
  const suffix = typeof planId === "number" ? `?plan_id=${planId}` : "";
  const { data } = await clientApi.get(`/vision-maison/jardin/zones${suffix}`);
  return data.items ?? [];
}

export async function modifierZoneJardinHabitat(
  zoneId: number,
  payload: Partial<ZoneJardinHabitat>
): Promise<ZoneJardinHabitat> {
  const { data } = await clientApi.patch(`/vision-maison/jardin/zones/${zoneId}`, payload);
  return data;
}

export async function obtenirResumeJardinHabitat(planId?: number): Promise<ResumeJardinHabitat> {
  const suffix = typeof planId === "number" ? `?plan_id=${planId}` : "";
  const { data } = await clientApi.get(`/vision-maison/jardin/resume${suffix}`);
  return data;
}
