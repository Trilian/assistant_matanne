// ═══════════════════════════════════════════════════════════
// API Jeux
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type {
  PariSportif,
  MatchJeu,
  TirageLoto,
  GrilleLoto,
  StatsParis,
} from "@/types/jeux";

// ─── Matchs ───────────────────────────────────────────────

export async function listerMatchs(
  championnat?: string,
  joue?: boolean
): Promise<MatchJeu[]> {
  const params = new URLSearchParams();
  if (championnat) params.set("championnat", championnat);
  if (joue !== undefined) params.set("joue", String(joue));
  const qs = params.toString();
  const { data } = await clientApi.get(`/jeux/matchs${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

// ─── Paris sportifs ───────────────────────────────────────

export async function listerParis(
  statut?: string
): Promise<PariSportif[]> {
  const params = statut ? `?statut=${statut}` : "";
  const { data } = await clientApi.get(`/jeux/paris${params}`);
  return data.items ?? data;
}

export async function obtenirStatsParis(): Promise<StatsParis> {
  const { data } = await clientApi.get<StatsParis>("/jeux/paris/stats");
  return data;
}

// ─── Loto ─────────────────────────────────────────────────

export async function listerTirages(): Promise<TirageLoto[]> {
  const { data } = await clientApi.get("/jeux/loto/tirages");
  return data.items ?? data;
}

export async function listerGrilles(): Promise<GrilleLoto[]> {
  const { data } = await clientApi.get("/jeux/loto/grilles");
  return data.items ?? data;
}
