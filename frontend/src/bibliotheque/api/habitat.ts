import { clientApi } from "./client";
import type {
  AnnonceHabitat,
  CritereImmoHabitat,
  CritereScenarioHabitat,
  HabitatHub,
  PieceHabitat,
  PlanHabitat,
  ProjetDecoHabitat,
  ScenarioHabitat,
  ZoneJardinHabitat,
} from "@/types/habitat";

export async function obtenirHubHabitat(): Promise<HabitatHub> {
  const { data } = await clientApi.get<HabitatHub>("/habitat/hub");
  return data;
}

export async function listerScenariosHabitat(): Promise<ScenarioHabitat[]> {
  const { data } = await clientApi.get("/habitat/scenarios");
  return data.items ?? [];
}

export async function creerScenarioHabitat(payload: Partial<ScenarioHabitat>): Promise<ScenarioHabitat> {
  const { data } = await clientApi.post("/habitat/scenarios", payload);
  return data;
}

export async function comparerScenariosHabitat(): Promise<ScenarioHabitat[]> {
  const { data } = await clientApi.get("/habitat/scenarios/comparaison");
  return data.items ?? [];
}

export async function ajouterCritereScenarioHabitat(
  scenarioId: number,
  payload: { nom: string; poids?: number; note?: number; commentaire?: string }
): Promise<CritereScenarioHabitat> {
  const { data } = await clientApi.post(`/habitat/scenarios/${scenarioId}/criteres`, payload);
  return data;
}

export async function listerCriteresImmoHabitat(): Promise<CritereImmoHabitat[]> {
  const { data } = await clientApi.get("/habitat/criteres-immo");
  return data.items ?? [];
}

export async function listerAnnoncesHabitat(): Promise<AnnonceHabitat[]> {
  const { data } = await clientApi.get("/habitat/annonces");
  return data.items ?? [];
}

export async function listerPlansHabitat(): Promise<PlanHabitat[]> {
  const { data } = await clientApi.get("/habitat/plans");
  return data.items ?? [];
}

export async function listerPiecesHabitat(planId: number): Promise<PieceHabitat[]> {
  const { data } = await clientApi.get(`/habitat/plans/${planId}/pieces`);
  return data.items ?? [];
}

export async function listerProjetsDecoHabitat(): Promise<ProjetDecoHabitat[]> {
  const { data } = await clientApi.get("/habitat/deco/projets");
  return data.items ?? [];
}

export async function listerZonesJardinHabitat(planId?: number): Promise<ZoneJardinHabitat[]> {
  const suffix = typeof planId === "number" ? `?plan_id=${planId}` : "";
  const { data } = await clientApi.get(`/habitat/jardin/zones${suffix}`);
  return data.items ?? [];
}
