// ═══════════════════════════════════════════════════════════
// API Planning
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type { PlanningSemaine, RepasPlanning, CreerRepasPlanningDTO } from "@/types/planning";

/** Obtenir le planning de la semaine courante ou spécifiée */
export async function obtenirPlanningSemaine(dateDebut?: string): Promise<PlanningSemaine> {
  const params = dateDebut ? `?date_debut=${dateDebut}` : "";
  const { data } = await clientApi.get<PlanningSemaine>(`/planning/semaine${params}`);
  return data;
}

/** Ajouter/modifier un repas dans le planning */
export async function definirRepas(dto: CreerRepasPlanningDTO): Promise<RepasPlanning> {
  const { data } = await clientApi.post<RepasPlanning>("/planning/repas", dto);
  return data;
}

/** Supprimer un repas du planning */
export async function supprimerRepas(id: number): Promise<void> {
  await clientApi.delete(`/planning/repas/${id}`);
}

/** Générer un planning IA pour la semaine */
export async function genererPlanningSemaine(
  preferences?: string
): Promise<PlanningSemaine> {
  const { data } = await clientApi.post<PlanningSemaine>("/planning/generer", {
    preferences,
  });
  return data;
}

/** Exporter le planning en iCalendar (.ics) et déclencher le téléchargement */
export async function exporterPlanningIcal(semaines = 2): Promise<void> {
  const response = await clientApi.get(`/planning/export/ical?semaines=${semaines}`, {
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const a = document.createElement("a");
  a.href = url;
  a.download = "planning-repas.ics";
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
