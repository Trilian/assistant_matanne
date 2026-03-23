// ═══════════════════════════════════════════════════════════
// API Maison
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type {
  ProjetMaison,
  TacheEntretien,
  ElementJardin,
  StockMaison,
  ChargesMaison,
  CalendrierSemis,
  SanteAppareils,
} from "@/types/maison";

// ─── Projets ──────────────────────────────────────────────

/** Lister les projets maison */
export async function listerProjets(
  statut?: string,
  priorite?: string
): Promise<ProjetMaison[]> {
  const params = new URLSearchParams();
  if (statut) params.set("statut", statut);
  if (priorite) params.set("priorite", priorite);
  const qs = params.toString();
  const { data } = await clientApi.get(`/maison/projets${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

// ─── Entretien ────────────────────────────────────────────

/** Lister les tâches d'entretien */
export async function listerTachesEntretien(
  categorie?: string,
  piece?: string
): Promise<TacheEntretien[]> {
  const params = new URLSearchParams();
  if (categorie) params.set("categorie", categorie);
  if (piece) params.set("piece", piece);
  const qs = params.toString();
  const { data } = await clientApi.get(`/maison/entretien${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

/** Dashboard santé des appareils */
export async function obtenirSanteAppareils(): Promise<SanteAppareils> {
  const { data } = await clientApi.get<SanteAppareils>(
    "/maison/entretien/sante-appareils"
  );
  return data;
}

// ─── Jardin ───────────────────────────────────────────────

/** Lister les éléments du jardin */
export async function listerElementsJardin(
  type_element?: string
): Promise<ElementJardin[]> {
  const params = type_element ? `?type_element=${type_element}` : "";
  const { data } = await clientApi.get(`/maison/jardin${params}`);
  return data.items ?? data;
}

/** Calendrier des semis */
export async function obtenirCalendrierSemis(
  mois?: number
): Promise<CalendrierSemis> {
  const params = mois ? `?mois=${mois}` : "";
  const { data } = await clientApi.get<CalendrierSemis>(
    `/maison/jardin/calendrier-semis${params}`
  );
  return data;
}

// ─── Stocks ───────────────────────────────────────────────

/** Lister les stocks maison */
export async function listerStocks(
  categorie?: string,
  alerteOnly?: boolean
): Promise<StockMaison[]> {
  const params = new URLSearchParams();
  if (categorie) params.set("categorie", categorie);
  if (alerteOnly) params.set("alerte_stock", "true");
  const qs = params.toString();
  const { data } = await clientApi.get(`/maison/stocks${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

// ─── Charges ──────────────────────────────────────────────

/** Lister les charges (factures) */
export async function listerCharges(annee?: number): Promise<ChargesMaison[]> {
  const params = annee ? `?annee=${annee}` : "";
  const { data } = await clientApi.get(`/maison/charges${params}`);
  return data.items ?? data;
}
