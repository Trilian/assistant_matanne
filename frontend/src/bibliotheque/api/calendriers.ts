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

// ═══════════════════════════════════════════════════════════
// GOOGLE CALENDAR
// ═══════════════════════════════════════════════════════════

export interface StatutGoogle {
  connected: boolean;
  nom?: string;
  last_sync?: string;
  enabled?: boolean;
  sync_direction?: string;
}

export interface ResultatSync {
  status: string;
  events_imported: number;
  events_exported: number;
  errors: string[];
}

export async function obtenirUrlAuthGoogle(): Promise<{ auth_url: string }> {
  const { data } = await clientApi.get("/calendriers/google/auth-url");
  return data;
}

export async function synchroniserGoogle(): Promise<ResultatSync> {
  const { data } = await clientApi.post("/calendriers/google/sync");
  return data;
}

export async function statutGoogle(): Promise<StatutGoogle> {
  const { data } = await clientApi.get("/calendriers/google/status");
  return data;
}

export async function deconnecterGoogle(): Promise<{ status: string }> {
  const { data } = await clientApi.delete("/calendriers/google/disconnect");
  return data;
}

// ═══════════════════════════════════════════════════════════
// CALENDRIERS iCAL
// ═══════════════════════════════════════════════════════════

export interface CreerCalendrierIcalDto {
  nom: string;
  url: string;
  sync_interval_minutes?: number;
}

/** Ajoute un calendrier iCal externe par URL */
export async function ajouterCalendrierIcal(
  dto: CreerCalendrierIcalDto
): Promise<CalendrierExterne> {
  const { data } = await clientApi.post<CalendrierExterne>("/calendriers", {
    ...dto,
    provider: "ical_url",
    sync_direction: "import",
  });
  return data;
}

/** Supprime un calendrier externe */
export async function supprimerCalendrier(id: number): Promise<void> {
  await clientApi.delete(`/calendriers/${id}`);
}
