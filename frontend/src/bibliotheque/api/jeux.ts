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
  SuiviResponsable,
  VerificationMise,
  AnalyseIA,
  BacktestResultat,
  NotificationJeux,
  ResultatTicketOCRJeux,
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

export async function obtenirAlertes(typeJeu?: string): Promise<AlerteJeux[]> {
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

// ─── Jeu Responsable ─────────────────────────────────────

export async function obtenirSuiviResponsable(): Promise<SuiviResponsable> {
  const { data } = await clientApi.get<SuiviResponsable>("/jeux/responsable/suivi");
  return data;
}

export async function verifierMise(montant: number): Promise<VerificationMise> {
  const { data } = await clientApi.get<VerificationMise>(
    `/jeux/responsable/verifier-mise?montant=${montant}`
  );
  return data;
}

export async function enregistrerMise(montant: number, typeJeu = "paris"): Promise<void> {
  await clientApi.post("/jeux/responsable/enregistrer-mise", {
    montant,
    type_jeu: typeJeu,
  });
}

export async function modifierLimite(nouvelleLimite: number): Promise<void> {
  await clientApi.put("/jeux/responsable/limite", {
    nouvelle_limite: nouvelleLimite,
  });
}

export async function activerAutoExclusion(nbJours: number): Promise<void> {
  await clientApi.post("/jeux/responsable/auto-exclusion", {
    nb_jours: nbJours,
  });
}

export async function obtenirHistoriqueLimites(nbMois = 12): Promise<unknown[]> {
  const { data } = await clientApi.get(`/jeux/responsable/historique?nb_mois=${nbMois}`);
  return data.items ?? data;
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

// ─── OCR Ticket Jeux ─────────────────────────────────────

export async function analyserTicketJeuxOCR(file: File): Promise<ResultatTicketOCRJeux> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await clientApi.post<ResultatTicketOCRJeux>(
    "/jeux/ocr-ticket",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
}
