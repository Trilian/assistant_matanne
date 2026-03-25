// ═══════════════════════════════════════════════════════════
// API Tableau de bord
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";

export interface DonneesTableauBord {
  repas_aujourd_hui: { type_repas: string; recette_nom?: string }[];
  alertes_inventaire: number;
  articles_courses_restants: number;
  activites_semaine: number;
  taches_entretien_urgentes: number;
  suggestion_diner?: string;
}

/** Obtenir les données agrégées du tableau de bord */
export async function obtenirTableauBord(): Promise<DonneesTableauBord> {
  const { data } = await clientApi.get<DonneesTableauBord>("/dashboard");
  return data;
}

// ─── Bilan mensuel IA ───────────────────────────────────────

export interface BilanMensuelDonnees {
  depenses: { total: number; nb_transactions: number; par_categorie: Record<string, number> };
  repas: { total_planifies: number; repartition: Record<string, number> };
  activites: { total: number; noms: string[] };
  entretien: { taches_completees: number; taches_en_retard: number };
}

export interface BilanMensuel {
  mois: string;
  donnees: BilanMensuelDonnees;
  synthese_ia: string;
}

/** Obtenir le bilan mensuel IA (mois au format YYYY-MM, défaut = mois courant) */
export async function obtenirBilanMensuel(mois?: string): Promise<BilanMensuel> {
  const params = mois ? `?mois=${mois}` : "";
  const { data } = await clientApi.get<BilanMensuel>(`/dashboard/bilan-mensuel${params}`);
  return data;
}
