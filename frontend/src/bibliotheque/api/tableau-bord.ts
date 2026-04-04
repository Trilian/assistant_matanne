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

export interface WidgetActionPayload {
  widget_id: string;
  action: string;
  donnees?: Record<string, unknown>;
}

export interface WidgetActionResponse {
  widget_id: string;
  action: string;
  statut: string;
}

export interface WidgetActionHistoriqueItem {
  event_id: string;
  type: string;
  source: string;
  timestamp: string;
  widget_id: string | null;
  action: string | null;
  donnees: Record<string, unknown>;
}

export interface WidgetActionHistoriqueResponse {
  items: WidgetActionHistoriqueItem[];
  total: number;
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

export interface ScoreEcologique {
  score_global: number;
  niveau: "excellent" | "bon" | "vigilance" | "critique";
  modules: {
    cuisine: {
      score: number;
      anti_gaspillage: number;
      produits_ecoscores: number | null;
    };
    maison: {
      score: number;
      energie: number;
      eco_actions: number;
      economie_mensuelle_estimee: number;
    };
  };
  leviers_prioritaires: string[];
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

/** Enregistrer une action utilisateur liée à un widget dashboard */
export async function enregistrerActionWidgetDashboard(
  payload: WidgetActionPayload
): Promise<WidgetActionResponse> {
  const { data } = await clientApi.post<WidgetActionResponse>("/dashboard/widgets/action", {
    widget_id: payload.widget_id,
    action: payload.action,
    donnees: payload.donnees ?? {},
  });
  return data;
}

/** Lire l'historique récent des actions widgets dashboard */
export async function obtenirHistoriqueActionsWidgetsDashboard(
  limite = 10
): Promise<WidgetActionHistoriqueResponse> {
  const { data } = await clientApi.get<WidgetActionHistoriqueResponse>("/dashboard/widgets/actions", {
    params: { limite },
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

export async function obtenirScoreEcologique(): Promise<ScoreEcologique> {
  const { data } = await clientApi.get<ScoreEcologique>("/dashboard/score-ecologique");
  return data;
}

// ─── Score foyer composite ──────────────────────────────────────────

export interface ScoreFoyer {
  score_global: number;
  niveau: "excellent" | "bon" | "vigilance" | "critique";
  trend_semaine_precedente: number;
  composantes: {
    nutrition: number;
    budget: number;
    entretien: number;
    routines: number;
  };
  details: Record<string, number>;
  leviers_prioritaires: string[];
  periode: { debut: string; fin: string };
}

/** Obtenir le score foyer composite (nutrition + budget + entretien + routines) */
export async function obtenirScoreFoyer(): Promise<ScoreFoyer> {
  const { data } = await clientApi.get<ScoreFoyer>("/dashboard/score-foyer");
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

export interface BudgetUnifieDashboard {
  mois: string;
  famille: { depenses: number };
  maison: { depenses: number };
  jeux: { mises: number; gains: number; net: number };
  totaux: {
    depenses_hors_jeux: number;
    depenses_avec_mises_jeux: number;
    impact_global_avec_jeux: number;
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

/** Obtenir l'agrégation budgétaire unifiée (famille + maison + jeux). */
export async function obtenirBudgetUnifieDashboard(): Promise<BudgetUnifieDashboard> {
  const { data } = await clientApi.get<BudgetUnifieDashboard>("/dashboard/budget-unifie");
  return data;
}
// ─── Gamification — Badges & historique  ──────────────

export interface BadgeDefinition {
  badge_type: string;
  badge_label: string;
  categorie: "sport" | "nutrition";
  emoji: string;
  description: string;
  seuil: number;
  unite: string;
  obtenu?: boolean;
  nb_obtenu?: number;
  derniere_date?: string | null;
}

export interface HistoriquePoints {
  semaine_debut: string;
  points_sport: number;
  points_alimentation: number;
  points_anti_gaspi: number;
  total_points: number;
  details: Record<string, unknown>;
}

/** Obtenir le catalogue complet des badges sport + nutrition */
export async function obtenirCatalogueBadges(): Promise<{ items: BadgeDefinition[]; total: number }> {
  const { data } = await clientApi.get("/dashboard/badges/catalogue");
  return data;
}

/** Obtenir les badges d'un utilisateur avec progression */
export async function obtenirBadgesUtilisateur(): Promise<{
  items: BadgeDefinition[];
  total: number;
  obtenus: number;
}> {
  const { data } = await clientApi.get("/dashboard/badges/utilisateur");
  return data;
}

/** Évaluer et attribuer les badges mérités */
export async function evaluerBadges(): Promise<{
  nouveaux_badges: { user_id: number; badge_type: string; badge_label: string; emoji: string; categorie: string }[];
  total_nouveaux: number;
}> {
  const { data } = await clientApi.post("/dashboard/badges/evaluer");
  return data;
}

/** Obtenir l'historique des points sur N semaines */
export async function obtenirHistoriquePoints(nbSemaines = 8): Promise<{
  items: HistoriquePoints[];
  total: number;
}> {
  const { data } = await clientApi.get("/dashboard/historique-points", {
    params: { nb_semaines: nbSemaines },
  });
  return data;
}