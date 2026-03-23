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

/** Créer un projet */
export async function creerProjet(
  projet: Omit<ProjetMaison, "id" | "taches_count">
): Promise<ProjetMaison> {
  const { data } = await clientApi.post<ProjetMaison>("/maison/projets", projet);
  return data;
}

/** Modifier un projet */
export async function modifierProjet(
  id: number,
  projet: Partial<ProjetMaison>
): Promise<ProjetMaison> {
  const { data } = await clientApi.patch<ProjetMaison>(`/maison/projets/${id}`, projet);
  return data;
}

/** Supprimer un projet */
export async function supprimerProjet(id: number): Promise<void> {
  await clientApi.delete(`/maison/projets/${id}`);
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

/** Créer une tâche d'entretien */
export async function creerTacheEntretien(
  tache: Omit<TacheEntretien, "id">
): Promise<TacheEntretien> {
  const { data } = await clientApi.post<TacheEntretien>("/maison/entretien", tache);
  return data;
}

/** Modifier une tâche d'entretien */
export async function modifierTacheEntretien(
  id: number,
  tache: Partial<TacheEntretien>
): Promise<TacheEntretien> {
  const { data } = await clientApi.patch<TacheEntretien>(`/maison/entretien/${id}`, tache);
  return data;
}

/** Supprimer une tâche d'entretien */
export async function supprimerTacheEntretien(id: number): Promise<void> {
  await clientApi.delete(`/maison/entretien/${id}`);
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

/** Ajouter un élément au jardin */
export async function creerElementJardin(
  element: Omit<ElementJardin, "id">
): Promise<ElementJardin> {
  const { data } = await clientApi.post<ElementJardin>("/maison/jardin", element);
  return data;
}

/** Modifier un élément du jardin */
export async function modifierElementJardin(
  id: number,
  element: Partial<ElementJardin>
): Promise<ElementJardin> {
  const { data } = await clientApi.patch<ElementJardin>(`/maison/jardin/${id}`, element);
  return data;
}

/** Supprimer un élément du jardin */
export async function supprimerElementJardin(id: number): Promise<void> {
  await clientApi.delete(`/maison/jardin/${id}`);
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

/** Créer un stock */
export async function creerStock(
  stock: Omit<StockMaison, "id" | "en_alerte">
): Promise<StockMaison> {
  const { data } = await clientApi.post<StockMaison>("/maison/stocks", stock);
  return data;
}

/** Modifier un stock */
export async function modifierStock(
  id: number,
  stock: Partial<StockMaison>
): Promise<StockMaison> {
  const { data } = await clientApi.patch<StockMaison>(`/maison/stocks/${id}`, stock);
  return data;
}

/** Supprimer un stock */
export async function supprimerStock(id: number): Promise<void> {
  await clientApi.delete(`/maison/stocks/${id}`);
}

// ─── Charges ──────────────────────────────────────────────

/** Lister les charges (factures) */
export async function listerCharges(annee?: number): Promise<ChargesMaison[]> {
  const params = annee ? `?annee=${annee}` : "";
  const { data } = await clientApi.get(`/maison/charges${params}`);
  return data.items ?? data;
}
