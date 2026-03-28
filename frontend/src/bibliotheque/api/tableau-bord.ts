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

// ─── Dashboard cuisine ──────────────────────────────────────

export interface DonneesTableauBordCuisine {
  repas_aujourd_hui: { type_repas: string; recette_nom?: string | null }[];
  repas_semaine_count: number;
  repas_consommes_semaine: number;
  nb_recettes: number;
  articles_courses_restants: number;
  alertes_inventaire: number;
  score_anti_gaspillage: number;
  repas_jules_aujourd_hui: {
    type_repas: string;
    plat_jules?: string | null;
    notes_jules?: string | null;
    adaptation_auto?: boolean;
  }[];
  batch_en_cours: boolean;
  batch_session_id: number | null;
}

/** Obtenir le dashboard agrégé du module cuisine */
export async function obtenirDashboardCuisine(): Promise<DonneesTableauBordCuisine> {
  const { data } = await clientApi.get<DonneesTableauBordCuisine>("/dashboard/cuisine");
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

export interface ConfigDashboard {
  config_dashboard: Record<string, boolean>;
}

export interface AlerteContextuelle {
  type: string;
  module: string;
  icone: string;
  titre: string;
  message: string;
  action: string;
}

export interface PointsFamille {
  total_points: number;
  sport: number;
  alimentation: number;
  anti_gaspi: number;
  badges: string[];
  details: {
    activites_garmin: number;
    total_pas: number;
    total_calories: number;
    score_bien_etre: number;
    articles_a_risque: number;
  };
}

/** Obtenir le bilan mensuel IA (mois au format YYYY-MM, défaut = mois courant) */
export async function obtenirBilanMensuel(mois?: string): Promise<BilanMensuel> {
  const params = mois ? `?mois=${mois}` : "";
  const { data } = await clientApi.get<BilanMensuel>(`/dashboard/bilan-mensuel${params}`);
  return data;
}

/** Lire la configuration personnalisée des widgets dashboard */
export async function obtenirConfigDashboard(): Promise<ConfigDashboard> {
  const { data } = await clientApi.get<ConfigDashboard>("/dashboard/config");
  return data;
}

/** Sauvegarder la configuration personnalisée des widgets dashboard */
export async function sauvegarderConfigDashboard(
  configDashboard: Record<string, boolean>
): Promise<ConfigDashboard> {
  const { data } = await clientApi.put<ConfigDashboard>("/dashboard/config", {
    config_dashboard: configDashboard,
  });
  return data;
}

/** Lire les alertes météo contextuelles cross-modules */
export async function obtenirAlertesContextuelles(): Promise<{
  items: AlerteContextuelle[];
  total: number;
}> {
  const { data } = await clientApi.get("/dashboard/alertes-contextuelles");
  return data;
}

/** Lire les points famille gamifiés */
export async function obtenirPointsFamille(): Promise<PointsFamille> {
  const { data } = await clientApi.get<PointsFamille>("/dashboard/points-famille");
  return data;
}

// ─── Score bien-être global (MT-03) ─────────────────────────────────

export interface ScoreBienEtre {
  score_global: number;
  diversite_alimentaire: number;
  score_nutri: number;
  activites_sport: number;
  trend_semaine_precedente: number;
  periode: { debut: string; fin: string };
}

export interface AnomalieFinanciere {
  module: "famille" | "maison" | "jeux";
  categorie: string;
  valeur_courante: number;
  moyenne_reference: number;
  ecart_pourcentage: number;
  gravite: "faible" | "moyenne" | "haute";
  message: string;
}

export interface AnomaliesFinancieresResponse {
  items: AnomalieFinanciere[];
  total: number;
  synthese: {
    depenses_famille_mois: number;
    depenses_maison_mois: number;
    net_jeux_mois: number;
  };
}

/** Obtenir le score bien-être hebdomadaire (alimentation + nutrition + activités) */
export async function obtenirScoreBienEtre(): Promise<ScoreBienEtre> {
  const { data } = await clientApi.get<ScoreBienEtre>("/dashboard/score-bienetre");
  return data;
}

/** Obtenir les anomalies financières cross-modules (famille + maison + jeux). */
export async function obtenirAnomaliesFinancieres(): Promise<AnomaliesFinancieresResponse> {
  const { data } = await clientApi.get<AnomaliesFinancieresResponse>(
    "/dashboard/anomalies-financieres"
  );
  return data;
}
