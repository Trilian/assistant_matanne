// ═══════════════════════════════════════════════════════════════
// API Outils
// ═══════════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type { Note, NoteCreate, NotePatch } from "@/types/outils";

// ─── Notes ─────────────────────────────────────────────────────

export async function listerNotes(params?: {
  categorie?: string;
  tag?: string;
  epingle?: boolean;
  archive?: boolean;
  recherche?: string;
}): Promise<Note[]> {
  const sp = new URLSearchParams();
  if (params?.categorie) sp.set("categorie", params.categorie);
  if (params?.tag) sp.set("tag", params.tag);
  if (params?.epingle !== undefined) sp.set("epingle", String(params.epingle));
  if (params?.archive !== undefined) sp.set("archive", String(params.archive));
  if (params?.recherche) sp.set("search", params.recherche);
  const qs = sp.toString();
  const { data } = await clientApi.get(`/utilitaires/notes${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

export async function creerNote(note: NoteCreate): Promise<Note> {
  const { data } = await clientApi.post<Note>("/utilitaires/notes", note);
  return data;
}

export async function modifierNote(id: number, patch: NotePatch): Promise<Note> {
  const { data } = await clientApi.patch<Note>(`/utilitaires/notes/${id}`, patch);
  return data;
}

export async function supprimerNote(id: number): Promise<void> {
  await clientApi.delete(`/utilitaires/notes/${id}`);
}

export async function listerTagsNotes(): Promise<Array<{ tag: string; count: number }>> {
  const { data } = await clientApi.get("/utilitaires/notes/tags");
  return data.items ?? [];
}

// ─── Suggestions IA ────────────────────────────────────────────

export async function obtenirSuggestionsRecettes(
  contexte?: string,
  nombre?: number
): Promise<string[]> {
  const sp = new URLSearchParams();
  if (contexte) sp.set("contexte", contexte);
  if (nombre) sp.set("nombre", String(nombre));
  const qs = sp.toString();
  const { data } = await clientApi.get(`/suggestions/recettes${qs ? `?${qs}` : ""}`);
  return data.suggestions ?? data;
}

// ─── Chat IA Multi-contexte ─────────────────────────────────────

export type ContexteChat = "cuisine" | "famille" | "maison" | "budget" | "general";

export interface MessageChatRequest {
  message: string;
  contexte: ContexteChat;
  historique: Array<{ role: "user" | "assistant"; contenu: string }>;
}

export interface ReponseChatIA {
  reponse: string;
  contexte: ContexteChat;
}

export interface ActionRapide {
  label: string;
  message: string;
}

/** Envoyer un message au chat IA */
export async function envoyerMessageChat(
  payload: MessageChatRequest
): Promise<ReponseChatIA> {
  const { data } = await clientApi.post<ReponseChatIA>(
    "/utilitaires/chat/message",
    payload
  );
  return data;
}

/** Obtenir les actions rapides pour un contexte */
export async function obtenirActionsRapides(
  contexte: ContexteChat = "general"
): Promise<{ actions: ActionRapide[]; contexte: ContexteChat }> {
  const { data } = await clientApi.get("/utilitaires/chat/actions-rapides", {
    params: { contexte },
  });
  return data;
}

