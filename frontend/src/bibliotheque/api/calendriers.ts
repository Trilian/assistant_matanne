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

export interface RecurrenceAnalysee {
  frequence: "DAILY" | "WEEKLY" | "MONTHLY" | "YEARLY" | "UNKNOWN";
  intervalle: number;
  joursSemaine: string[];
}

const MAP_JOURS: Record<string, string> = {
  MO: "lundi",
  TU: "mardi",
  WE: "mercredi",
  TH: "jeudi",
  FR: "vendredi",
  SA: "samedi",
  SU: "dimanche",
};

export function analyserRecurrenceRule(recurrenceRule?: string): RecurrenceAnalysee {
  if (!recurrenceRule) {
    return { frequence: "UNKNOWN", intervalle: 1, joursSemaine: [] };
  }

  const segments = recurrenceRule
    .split(";")
    .map((part) => part.trim())
    .filter(Boolean)
    .reduce<Record<string, string>>((acc, part) => {
      const [k, v] = part.split("=");
      if (k && v) acc[k.toUpperCase()] = v.toUpperCase();
      return acc;
    }, {});

  const freqRaw = segments.FREQ;
  const frequence =
    freqRaw === "DAILY" ||
    freqRaw === "WEEKLY" ||
    freqRaw === "MONTHLY" ||
    freqRaw === "YEARLY"
      ? freqRaw
      : "UNKNOWN";

  const intervalle = Number.parseInt(segments.INTERVAL ?? "1", 10);
  const byDay = (segments.BYDAY ?? "")
    .split(",")
    .map((d) => d.trim())
    .filter(Boolean)
    .map((d) => MAP_JOURS[d] ?? d.toLowerCase());

  return {
    frequence,
    intervalle: Number.isFinite(intervalle) && intervalle > 0 ? intervalle : 1,
    joursSemaine: byDay,
  };
}

export function recurrenceLisible(recurrenceRule?: string): string {
  const parsed = analyserRecurrenceRule(recurrenceRule);
  if (parsed.frequence === "UNKNOWN") return "";

  if (parsed.frequence === "DAILY") {
    return parsed.intervalle === 1
      ? "Tous les jours"
      : `Tous les ${parsed.intervalle} jours`;
  }

  if (parsed.frequence === "WEEKLY") {
    if (parsed.joursSemaine.length > 0) {
      return `Chaque ${parsed.joursSemaine.join(", ")}`;
    }
    return parsed.intervalle === 1
      ? "Toutes les semaines"
      : `Toutes les ${parsed.intervalle} semaines`;
  }

  if (parsed.frequence === "MONTHLY") {
    return parsed.intervalle === 1
      ? "Tous les mois"
      : `Tous les ${parsed.intervalle} mois`;
  }

  return parsed.intervalle === 1 ? "Tous les ans" : `Tous les ${parsed.intervalle} ans`;
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

// ═══════════════════════════════════════════════════════════
// CALENDRIER SCOLAIRE AUTO (INNO-14)
// ═══════════════════════════════════════════════════════════

export interface ActivationCalendrierScolaireResult {
  zone: string;
  calendrier_id: number;
  evenements_importes: number;
  events_planning_ajustes: number;
  ajustement_planning: boolean;
  success: boolean;
}

export async function listerZonesScolaires(): Promise<string[]> {
  const { data } = await clientApi.get<{ zones: string[] }>("/calendriers/scolaire/zones");
  return data.zones ?? [];
}

export async function activerCalendrierScolaireAuto(params: {
  zone: string;
  ajuster_planning?: boolean;
}): Promise<ActivationCalendrierScolaireResult> {
  const search = new URLSearchParams();
  search.set("zone", params.zone);
  search.set("ajuster_planning", String(params.ajuster_planning ?? true));
  const { data } = await clientApi.post<ActivationCalendrierScolaireResult>(
    `/calendriers/scolaire/activer?${search.toString()}`
  );
  return data;
}
