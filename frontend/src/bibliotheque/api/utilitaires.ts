// ═══════════════════════════════════════════════════════════
// API Utilitaires — Contacts & Journal
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";

// ─── Types ────────────────────────────────────────────────

export interface ContactUtile {
  id: number;
  nom: string;
  categorie: string;
  specialite?: string;
  telephone?: string;
  email?: string;
  adresse?: string;
  horaires?: string;
  favori: boolean;
}

export interface EntreeJournal {
  id: number;
  date_entree: string;
  contenu: string;
  humeur?: string;
  energie?: number;
  gratitudes: string[];
  tags: string[];
  cree_le?: string;
}

// ─── Contacts ─────────────────────────────────────────────

export async function listerContacts(params?: {
  categorie?: string;
  favori?: boolean;
  search?: string;
}): Promise<ContactUtile[]> {
  const sp = new URLSearchParams();
  if (params?.categorie) sp.set("categorie", params.categorie);
  if (params?.favori !== undefined) sp.set("favori", String(params.favori));
  if (params?.search) sp.set("search", params.search);
  const qs = sp.toString();
  const { data } = await clientApi.get(
    `/utilitaires/contacts${qs ? `?${qs}` : ""}`
  );
  return data.items ?? data;
}

export async function creerContact(
  contact: Omit<ContactUtile, "id">
): Promise<ContactUtile> {
  const { data } = await clientApi.post<ContactUtile>(
    "/utilitaires/contacts",
    contact
  );
  return data;
}

export async function modifierContact(
  id: number,
  patch: Partial<ContactUtile>
): Promise<ContactUtile> {
  const { data } = await clientApi.patch<ContactUtile>(
    `/utilitaires/contacts/${id}`,
    patch
  );
  return data;
}

export async function supprimerContact(id: number): Promise<void> {
  await clientApi.delete(`/utilitaires/contacts/${id}`);
}

// ─── Journal ──────────────────────────────────────────────

export async function listerJournal(params?: {
  humeur?: string;
  limit?: number;
}): Promise<EntreeJournal[]> {
  const sp = new URLSearchParams();
  if (params?.humeur) sp.set("humeur", params.humeur);
  if (params?.limit) sp.set("limit", String(params.limit));
  const qs = sp.toString();
  const { data } = await clientApi.get(
    `/utilitaires/journal${qs ? `?${qs}` : ""}`
  );
  return data.items ?? data;
}

export async function creerEntreeJournal(
  entree: Omit<EntreeJournal, "id" | "cree_le">
): Promise<EntreeJournal> {
  const { data } = await clientApi.post<EntreeJournal>(
    "/utilitaires/journal",
    entree
  );
  return data;
}

export async function modifierEntreeJournal(
  id: number,
  patch: Partial<EntreeJournal>
): Promise<EntreeJournal> {
  const { data } = await clientApi.patch<EntreeJournal>(
    `/utilitaires/journal/${id}`,
    patch
  );
  return data;
}

export async function supprimerEntreeJournal(id: number): Promise<void> {
  await clientApi.delete(`/utilitaires/journal/${id}`);
}
