// ═══════════════════════════════════════════════════════════
// API Calendriers — Sync externes
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";

export interface CalendrierExterne {
  id: number;
  provider: string;
  nom: string;
  url?: string;
  enabled: boolean;
  sync_interval_minutes: number;
  last_sync: string | null;
  sync_direction: string;
  evenements_count?: number;
}

export interface EvenementCalendrier {
  id: number;
  uid?: string;
  titre: string;
  description?: string;
  date_debut: string;
  date_fin?: string;
  lieu?: string;
  all_day: boolean;
  recurrence_rule?: string;
  rappel_minutes?: number;
  source_calendrier_id?: number;
}

/** Lister les calendriers externes */
export async function listerCalendriers(
  provider?: string
): Promise<CalendrierExterne[]> {
  const params = provider ? `?provider=${encodeURIComponent(provider)}` : "";
  const { data } = await clientApi.get(`/calendriers${params}`);
  return data.items ?? data;
}

/** Obtenir un calendrier par ID */
export async function obtenirCalendrier(id: number): Promise<CalendrierExterne> {
  const { data } = await clientApi.get<CalendrierExterne>(`/calendriers/${id}`);
  return data;
}

/** Lister les événements de calendrier */
export async function listerEvenements(params?: {
  calendrier_id?: number;
  date_debut?: string;
  date_fin?: string;
}): Promise<EvenementCalendrier[]> {
  const searchParams = new URLSearchParams();
  if (params?.calendrier_id) searchParams.set("calendrier_id", String(params.calendrier_id));
  if (params?.date_debut) searchParams.set("date_debut", params.date_debut);
  if (params?.date_fin) searchParams.set("date_fin", params.date_fin);
  const qs = searchParams.toString();
  const { data } = await clientApi.get(`/calendriers/evenements${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

/** Obtenir les événements d'aujourd'hui */
export async function evenementsAujourdHui(): Promise<EvenementCalendrier[]> {
  const { data } = await clientApi.get("/calendriers/evenements/aujourd-hui");
  return data.items ?? data;
}

/** Obtenir les événements de la semaine */
export async function evenementsSemaine(): Promise<EvenementCalendrier[]> {
  const { data } = await clientApi.get("/calendriers/evenements/semaine");
  return data.items ?? data;
}
