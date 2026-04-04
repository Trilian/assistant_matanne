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
  DashboardJeux,
  SerieJeux,
  AlerteJeux,
  PredictionMatch,
  ValueBet,
  StatsLoto,
  NumeroRetard,
  TirageEuromillions,
  GrilleEuromillions,
  StatsEuromillions,
  GrilleGeneree,
  PerformanceJeux,
  ResumeMensuel,
  AnalyseIA,
  BacktestResultat,
  NotificationJeux,
} from "@/types/jeux";

// ─── Dashboard ────────────────────────────────────────────

export async function obtenirDashboardJeux(): Promise<DashboardJeux> {
  const { data } = await clientApi.get<DashboardJeux>("/jeux/dashboard");
  return data;
}

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

/** Créer un pari */
export async function creerPari(
  pari: Omit<PariSportif, "id" | "statut" | "gain">
): Promise<PariSportif> {
  const { data } = await clientApi.post<PariSportif>("/jeux/paris", pari);
  return data;
}

/** Modifier un pari (statut, gain) */
export async function modifierPari(
  id: number,
  pari: Partial<PariSportif>
): Promise<PariSportif> {
  const { data } = await clientApi.patch<PariSportif>(`/jeux/paris/${id}`, pari);
  return data;
}

/** Supprimer un pari */
export async function supprimerPari(id: number): Promise<void> {
  await clientApi.delete(`/jeux/paris/${id}`);
}

// ─── Prédictions & Value Bets ─────────────────────────────

export async function obtenirPredictionMatch(matchId: number): Promise<PredictionMatch> {
  const { data } = await clientApi.get<PredictionMatch>(`/jeux/paris/predictions/${matchId}`);
  return data;
}

export async function obtenirValueBets(seuilEv = 5.0): Promise<ValueBet[]> {
  const { data } = await clientApi.get(`/jeux/paris/value-bets?seuil_ev=${seuilEv}`);
  return data.items ?? data;
}

export async function obtenirAnalysePatterns(userId: number): Promise<Record<string, unknown>> {
  const { data } = await clientApi.get<Record<string, unknown>>(`/jeux/paris/analyse-patterns/${userId}`);
  return data;
}

// ─── Séries & Alertes ─────────────────────────────────────

export async function obtenirSeriesActives(
  typeJeu?: string,
  seuil = 2.0
): Promise<SerieJeux[]> {
  const params = new URLSearchParams();
  if (typeJeu) params.set("type_jeu", typeJeu);
  params.set("seuil", String(seuil));
  const { data } = await clientApi.get(`/jeux/series?${params.toString()}`);
  return data.items ?? data;
}

export async function obtenirAlertesJeux(typeJeu?: string): Promise<AlerteJeux[]> {
  const params = typeJeu ? `?type_jeu=${typeJeu}` : "";
  const { data } = await clientApi.get(`/jeux/alertes${params}`);
  return data.items ?? data;
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

export async function obtenirStatsLoto(): Promise<StatsLoto> {
  const { data } = await clientApi.get<StatsLoto>("/jeux/loto/stats");
  return data;
}

export async function obtenirNumerosRetard(seuil = 2.0): Promise<NumeroRetard[]> {
  const { data } = await clientApi.get(`/jeux/loto/numeros-retard?seuil=${seuil}`);
  return data.items ?? data;
}

export async function genererGrilleLoto(
  strategie: "statistique" | "aleatoire" | "ia" = "statistique",
  sauvegarder = false
): Promise<GrilleGeneree> {
  const { data } = await clientApi.post<GrilleGeneree>("/jeux/loto/generer-grille", {
    strategie,
    sauvegarder,
  });
  return data;
}

/** Générer une grille Loto avec IA pondérée */
export async function genererGrilleIAPonderee(
  mode: "chauds" | "froids" | "equilibre" = "equilibre",
  sauvegarder = false
): Promise<{
  numeros: number[];
  numero_chance: number;
  mode: string;
  analyse: string;
  confiance: number;
  sauvegardee: boolean;
}> {
  const { data } = await clientApi.post(
    `/jeux/loto/generer-grille-ia-ponderee?mode=${mode}&sauvegarder=${sauvegarder}`,
    {}
  );
  return data;
}

/** Analyser une grille Loto joueur avec IA */
export async function analyserGrilleJoueur(
  numeros: number[],
  numeroChance: number
): Promise<{
  grille: { numeros: number[]; numero_chance: number };
  note: number;
  points_forts: string[];
  points_faibles: string[];
  recommandations: string[];
  appreciation: string;
}> {
  const params = new URLSearchParams();
  numeros.forEach((n) => params.append("numeros", String(n)));
  params.set("numero_chance", String(numeroChance));

  const { data } = await clientApi.post(
    `/jeux/loto/analyser-grille?${params.toString()}`,
    {}
  );
  return data;
}

// ─── Euromillions ─────────────────────────────────────────

export async function obtenirTiragesEuromillions(): Promise<TirageEuromillions[]> {
  const { data } = await clientApi.get("/jeux/euromillions/tirages");
  return data.items ?? data;
}

export async function obtenirGrillesEuromillions(): Promise<GrilleEuromillions[]> {
  const { data } = await clientApi.get("/jeux/euromillions/grilles");
  return data.items ?? data;
}

export async function creerGrilleEuromillions(
  numeros: number[],
  etoiles: number[],
  estVirtuelle = true
): Promise<GrilleEuromillions> {
  const { data } = await clientApi.post<GrilleEuromillions>("/jeux/euromillions/grilles", {
    numeros,
    etoiles,
    est_virtuelle: estVirtuelle,
  });
  return data;
}

export async function obtenirStatsEuromillions(): Promise<StatsEuromillions> {
  const { data } = await clientApi.get<StatsEuromillions>("/jeux/euromillions/stats");
  return data;
}

export async function genererGrilleEuromillions(
  strategie: "statistique" | "aleatoire" | "ia" = "statistique",
  sauvegarder = false
): Promise<GrilleGeneree> {
  const { data } = await clientApi.post<GrilleGeneree>("/jeux/euromillions/generer-grille", {
    strategie,
    sauvegarder,
  });
  return data;
}

// ─── Performance ──────────────────────────────────────────

export async function obtenirPerformance(mois?: number): Promise<PerformanceJeux> {
  const params = mois ? `?mois=${mois}` : "";
  const { data } = await clientApi.get<PerformanceJeux>(`/jeux/performance${params}`);
  return data;
}

export async function obtenirResumeMensuel(mois?: string): Promise<ResumeMensuel> {
  const params = mois ? `?mois=${mois}` : "";
  const { data } = await clientApi.get<ResumeMensuel>(`/jeux/resume-mensuel${params}`);
  return data;
}

export interface TrancheConfiance {
  tranche: string;
  nb: number;
  gagnes: number;
  taux: number;
}

export async function obtenirPerformanceConfiance(mois?: number): Promise<{ tranches: TrancheConfiance[]; total: number }> {
  const params = mois ? `?mois=${mois}` : "";
  const { data } = await clientApi.get<{ tranches: TrancheConfiance[]; total: number }>(`/jeux/performance/confiance${params}`);
  return data;
}

// ─── Analyse IA ───────────────────────────────────────────

export async function obtenirAnalyseIA(
  type: "paris" | "loto",
  donnees: Record<string, unknown> = {}
): Promise<AnalyseIA> {
  const { data } = await clientApi.post<AnalyseIA>("/jeux/analyse-ia", {
    type,
    data: donnees,
  });
  return data;
}

// ─── Backtest ─────────────────────────────────────────────

export async function obtenirBacktest(
  typeJeu = "loto",
  seuilValue = 2.0,
  nbTirages = 100
): Promise<BacktestResultat> {
  const params = new URLSearchParams({
    type_jeu: typeJeu,
    seuil_value: String(seuilValue),
    nb_tirages: String(nbTirages),
  });
  const { data } = await clientApi.get<BacktestResultat>(`/jeux/backtest?${params.toString()}`);
  return data;
}

// ─── Notifications ────────────────────────────────────────

export async function obtenirNotifications(): Promise<{
  items: NotificationJeux[];
  total_non_lues: number;
}> {
  const { data } = await clientApi.get("/jeux/notifications");
  return data;
}

export async function marquerNotificationLue(id: string): Promise<void> {
  await clientApi.post(`/jeux/notifications/${id}/lue`);
}

// ─── Historique des cotes et heatmap ─────────────────────

export async function obtenirHistoriqueCotes(matchId: number): Promise<{
  match_id: number;
  nb_points: number;
  points: Array<{
    timestamp: string;
    cote_domicile: number | null;
    cote_nul: number | null;
    cote_exterieur: number | null;
    cote_over_25?: number | null;
    cote_under_25?: number | null;
    bookmaker: string;
  }>;
  message?: string;
}> {
  const { data } = await clientApi.get(`/jeux/paris/cotes-historique/${matchId}`);
  return data;
}
