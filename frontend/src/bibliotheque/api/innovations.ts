import { clientApi } from "./client";

export interface ActionPiloteAuto {
  module: string;
  action: string;
  statut: string;
  details: string;
}

export interface ModePiloteAutoResponse {
  actif: boolean;
  niveau_autonomie: string;
  actions: ActionPiloteAuto[];
  recommandations: string[];
}

export interface ScoreFamilleDimension {
  nom: string;
  score: number;
  poids: number;
}

export interface ScoreFamilleHebdoResponse {
  semaine_reference: string;
  score_global: number;
  dimensions: ScoreFamilleDimension[];
  recommandations: string[];
}

export interface JournalFamilialAutoResponse {
  semaine_reference: string;
  titre: string;
  resume: string;
  faits_marquants: string[];
  moments_joyeux: string[];
  points_attention: string[];
}

export interface RapportMensuelPdfResponse {
  mois_reference: string;
  filename: string;
  contenu_base64: string;
}

export async function obtenirModePiloteAuto(): Promise<ModePiloteAutoResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/mode-pilote");
  return data;
}

export async function obtenirScoreFamilleHebdo(): Promise<ScoreFamilleHebdoResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/score-famille-hebdo");
  return data;
}

export async function obtenirJournalFamilialAuto(): Promise<JournalFamilialAutoResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/journal-familial");
  return data;
}

export async function obtenirJournalFamilialPdf(): Promise<RapportMensuelPdfResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/journal-familial/pdf");
  return data;
}

export async function obtenirRapportMensuelPdf(mois?: string): Promise<RapportMensuelPdfResponse> {
  const { data } = await clientApi.get("/api/v1/innovations/phasee/rapport-mensuel/pdf", {
    params: { mois },
  });
  return data;
}

export function telechargerPdfBase64(base64Content: string, filename: string): void {
  const byteCharacters = atob(base64Content);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i += 1) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
