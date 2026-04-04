// ═══════════════════════════════════════════════════════════
// API Famille
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type { ObjetDonnees } from "@/types/commun";
import type {
  ProfilEnfant,
  JalonJules,
  Activite,
  Routine,
  DepenseBudget,
  StatsBudget,
} from "@/types/famille";

// ─── Jules ────────────────────────────────────────────────

/** Obtenir le profil enfant Jules */
export async function obtenirProfilJules(): Promise<ProfilEnfant> {
  const { data } = await clientApi.get<{ items: ProfilEnfant[] }>(
    "/famille/enfants"
  );
  return data.items[0];
}

/** Obtenir les jalons de développement de Jules */
export async function listerJalons(categorie?: string): Promise<JalonJules[]> {
  const params: Record<string, string> = {};
  if (categorie) params.categorie = categorie;
  const { data } = await clientApi.get<{ items: JalonJules[] }>(
    "/famille/enfants/1/jalons",
    { params }
  );
  return data.items;
}

/** Ajouter un jalon */
export async function ajouterJalon(
  jalon: Omit<JalonJules, "id">,
  enfantId: number = 1
): Promise<JalonJules> {
  const { data } = await clientApi.post<JalonJules>(
    `/famille/enfants/${enfantId}/jalons`,
    jalon
  );
  return data;
}

/** Supprimer un jalon */
export async function supprimerJalon(
  jalonId: number,
  enfantId: number = 1
): Promise<void> {
  await clientApi.delete(`/famille/enfants/${enfantId}/jalons/${jalonId}`);
}

// ─── Activités ────────────────────────────────────────────

/** Lister les activités */
export async function listerActivites(
  type?: string,
  dateDebut?: string
): Promise<Activite[]> {
  const params: Record<string, string> = {};
  if (type) params.type = type;
  if (dateDebut) params.date_debut = dateDebut;
  const { data } = await clientApi.get<{ items: Activite[] }>(
    "/famille/activites",
    { params }
  );
  return data.items;
}

/** Créer une activité */
export async function creerActivite(
  activite: Omit<Activite, "id">
): Promise<Activite> {
  const { data } = await clientApi.post<Activite>(
    "/famille/activites",
    activite
  );
  return data;
}

/** Modifier une activité */
export async function modifierActivite(
  id: number,
  activite: Partial<Activite>
): Promise<Activite> {
  const { data } = await clientApi.patch<Activite>(
    `/famille/activites/${id}`,
    activite
  );
  return data;
}

/** Supprimer une activité */
export async function supprimerActivite(id: number): Promise<void> {
  await clientApi.delete(`/famille/activites/${id}`);
}

// ─── Suggestions IA Activités ─────────────────────────────

/** Paramètres pour les suggestions d'activités IA */
export interface ParamsSuggestionsActivites {
  age_mois: number
  meteo?: string
  budget_max?: number
  duree_min?: number
  duree_max?: number
  preferences?: string[]
  nb_suggestions?: number
}

/** Suggestion d'activité retournée par l'IA */
export interface SuggestionActivite {
  nom: string
  description: string
  duree_minutes: number
  budget: number
  lieu: 'interieur' | 'exterieur' | 'mixte'
  competences: string[]
  materiel: string[]
  niveau_effort: 'faible' | 'moyen' | 'eleve'
  adapte_pour: number[]
}

/** Réponse de l'API suggestions */
export interface ReponseSuggestionsActivites {
  total: number
  suggestions: SuggestionActivite[]
  params: ParamsSuggestionsActivites
}

/** Obtenir des suggestions d'activités via IA */
export async function obtenirSuggestionsActivites(
  params: ParamsSuggestionsActivites
): Promise<ReponseSuggestionsActivites> {
  const { data } = await clientApi.post<ReponseSuggestionsActivites>(
    "/famille/activites/suggestions-ia",
    params
  );
  return data;
}

// ─── Routines ─────────────────────────────────────────────

/** Lister les routines */
export async function listerRoutines(): Promise<Routine[]> {
  const { data } = await clientApi.get<{ items: Routine[] }>(
    "/famille/routines"
  );
  return data.items;
}

/** Obtenir une routine */
export async function obtenirRoutine(id: number): Promise<Routine> {
  const { data } = await clientApi.get<Routine>(`/famille/routines/${id}`);
  return data;
}

/** Créer une routine */
export async function creerRoutine(
  routine: Omit<Routine, "id">
): Promise<Routine> {
  const { data } = await clientApi.post<Routine>(
    "/famille/routines",
    routine
  );
  return data;
}

/** Modifier une routine */
export async function modifierRoutine(
  id: number,
  routine: Partial<Routine>
): Promise<Routine> {
  const { data } = await clientApi.patch<Routine>(
    `/famille/routines/${id}`,
    routine
  );
  return data;
}

/** Supprimer une routine */
export async function supprimerRoutine(id: number): Promise<void> {
  await clientApi.delete(`/famille/routines/${id}`);
}

// ─── Budget ───────────────────────────────────────────────

/** Lister les dépenses */
export async function listerDepenses(
  categorie?: string
): Promise<DepenseBudget[]> {
  const params: Record<string, string> = {};
  if (categorie) params.categorie = categorie;
  const { data } = await clientApi.get<{ items: DepenseBudget[] }>(
    "/famille/budget",
    { params }
  );
  return data.items;
}

/** Statistiques budget */
export async function obtenirStatsBudget(): Promise<StatsBudget> {
  const { data } = await clientApi.get<StatsBudget>("/famille/budget/stats");
  return data;
}

/** Ajouter une dépense */
export async function ajouterDepense(
  depense: Omit<DepenseBudget, "id">
): Promise<DepenseBudget> {
  const { data } = await clientApi.post<DepenseBudget>(
    "/famille/budget",
    depense
  );
  return data;
}

/** Supprimer une dépense */
export async function supprimerDepense(id: number): Promise<void> {
  await clientApi.delete(`/famille/budget/${id}`);
}

// ─── Budget IA — Analyse, Prédictions, Anomalies ──────────

export interface PredictionCategorie {
  categorie: string;
  montant_prevu: number;
  tendance: "hausse" | "baisse" | "stable";
  explication: string;
}

export interface PredictionBudget {
  total_prevu: number;
  par_categorie: PredictionCategorie[];
  confiance: number;
  resume: string;
}

export interface AnomalieBudget {
  type: "pic" | "baisse" | "nouvelle_categorie" | "irregularite";
  categorie: string;
  ecart_pourcent: number;
  severite: "info" | "warning" | "danger";
  description: string;
}

export interface SuggestionEconomie {
  titre: string;
  description: string;
  economie_estimee: number;
  categorie: string;
  difficulte: "facile" | "moyen" | "difficile";
}

export interface AnalyseBudgetIA {
  predictions: PredictionBudget | null;
  anomalies: AnomalieBudget[];
  suggestions: SuggestionEconomie[];
  historique: Array<{ mois: number; annee: number; total: number; par_categorie: Record<string, number> }>;
}

/** Analyse IA complète du budget (prédictions + anomalies + suggestions) */
export async function obtenirAnalyseBudgetIA(): Promise<AnalyseBudgetIA> {
  const { data } = await clientApi.get<AnalyseBudgetIA>("/famille/budget/analyse-ia");
  return data;
}

/** Prédictions seules */
export async function obtenirPredictionsBudget(): Promise<{ predictions: PredictionBudget | null; historique: AnalyseBudgetIA["historique"] }> {
  const { data } = await clientApi.get("/famille/budget/predictions");
  return data;
}

/** Anomalies seules */
export async function obtenirAnomaliesBudget(): Promise<{ anomalies: AnomalieBudget[] }> {
  const { data } = await clientApi.get("/famille/budget/anomalies");
  return data;
}

// ─── Anniversaires ────────────────────────────────────────

export interface Anniversaire {
  id: number;
  nom_personne: string;
  date_naissance: string;
  relation: string;
  rappel_jours_avant: number[];
  idees_cadeaux?: string;
  historique_cadeaux?: { annee: number; cadeau: string; budget?: number }[];
  notes?: string;
  actif: boolean;
  age?: number;
  jours_restants?: number;
}

export interface ItemChecklistAnniversaire {
  id: number;
  checklist_id: number;
  categorie: string;
  libelle: string;
  budget_estime?: number;
  budget_reel?: number;
  fait: boolean;
  priorite: string;
  responsable?: string;
  quand?: string;
  source: "auto" | "manuel";
  score_pertinence?: number;
  raison_suggestion?: string;
  ordre: number;
  notes?: string;
  cree_le?: string;
}

export interface ChecklistAnniversaire {
  id: number;
  anniversaire_id: number;
  nom: string;
  budget_total?: number;
  budget_depense: number;
  budget_restant: number;
  date_limite?: string;
  completee: boolean;
  maj_auto_le?: string;
  items_total: number;
  items_faits: number;
  taux_completion: number;
  items_par_categorie: Record<string, ItemChecklistAnniversaire[]>;
  cree_le?: string;
}

export interface ChecklistAnniversairePreview {
  anniversaire_id: number;
  nom_personne: string;
  age: number;
  jours_restants: number;
  profil: string;
  budget_total_suggere: number;
  items_auto: Array<{
    categorie: string;
    libelle: string;
    budget_estime?: number;
    priorite: string;
    quand?: string;
    source: "auto";
    score_pertinence?: number;
    raison_suggestion?: string;
    ordre: number;
  }>;
  genere_le: string;
}

/** Lister les anniversaires */
export async function listerAnniversaires(
  relation?: string
): Promise<Anniversaire[]> {
  const params: Record<string, string> = {};
  if (relation) params.relation = relation;
  const { data } = await clientApi.get<{ items: Anniversaire[] }>(
    "/famille/anniversaires",
    { params }
  );
  return data.items;
}

/** Créer un anniversaire */
export async function creerAnniversaire(
  anniversaire: Omit<Anniversaire, "id" | "actif" | "age" | "jours_restants" | "historique_cadeaux">
): Promise<Anniversaire> {
  const { data } = await clientApi.post<Anniversaire>(
    "/famille/anniversaires",
    anniversaire
  );
  return data;
}

/** Modifier un anniversaire */
export async function modifierAnniversaire(
  id: number,
  patch: Partial<Anniversaire>
): Promise<Anniversaire> {
  const { data } = await clientApi.patch<Anniversaire>(
    `/famille/anniversaires/${id}`,
    patch
  );
  return data;
}

/** Supprimer un anniversaire */
export async function supprimerAnniversaire(id: number): Promise<void> {
  await clientApi.delete(`/famille/anniversaires/${id}`);
}

/** Aperçu dynamique checklist anniversaire (sans persistance) */
export async function obtenirChecklistAnniversaireAuto(
  anniversaireId: number
): Promise<ChecklistAnniversairePreview> {
  const { data } = await clientApi.get<ChecklistAnniversairePreview>(
    `/famille/anniversaires/${anniversaireId}/checklist-auto`
  );
  return data;
}

/** Synchronise la checklist auto et retourne la checklist active */
export async function synchroniserChecklistAnniversaireAuto(
  anniversaireId: number,
  forceRecalculBudget = false
): Promise<ChecklistAnniversaire> {
  const { data } = await clientApi.post<ChecklistAnniversaire>(
    `/famille/anniversaires/${anniversaireId}/checklist-auto/synchroniser`,
    { force_recalcul_budget: forceRecalculBudget }
  );
  return data;
}

/** Liste les checklists d'un anniversaire */
export async function listerChecklistsAnniversaire(
  anniversaireId: number
): Promise<ChecklistAnniversaire[]> {
  const { data } = await clientApi.get<{ items: ChecklistAnniversaire[] }>(
    `/famille/anniversaires/${anniversaireId}/checklists`
  );
  return data.items;
}

/** Ajoute un item manuel dans une checklist anniversaire */
export async function ajouterItemChecklistAnniversaire(
  anniversaireId: number,
  checklistId: number,
  payload: {
    categorie: string;
    libelle: string;
    budget_estime?: number;
    priorite?: string;
    responsable?: string;
    quand?: string;
    ordre?: number;
    notes?: string;
  }
): Promise<ItemChecklistAnniversaire> {
  const { data } = await clientApi.post<ItemChecklistAnniversaire>(
    `/famille/anniversaires/${anniversaireId}/checklists/${checklistId}/items`,
    payload
  );
  return data;
}

/** Met à jour un item checklist anniversaire */
export async function modifierItemChecklistAnniversaire(
  anniversaireId: number,
  checklistId: number,
  itemId: number,
  patch: Partial<
    Pick<
      ItemChecklistAnniversaire,
      "fait" | "budget_reel" | "budget_estime" | "priorite" | "responsable" | "quand" | "notes" | "libelle" | "categorie"
    >
  >
): Promise<ItemChecklistAnniversaire> {
  const { data } = await clientApi.patch<ItemChecklistAnniversaire>(
    `/famille/anniversaires/${anniversaireId}/checklists/${checklistId}/items/${itemId}`,
    patch
  );
  return data;
}

/** Obtenir les items d'une checklist anniversaire (avec filtre catégorie optionnel) */
export async function obtenirChecklistAnniversaireItems(
  checklistId: number,
  categorie?: string
): Promise<ItemChecklistAnniversaire[]> {
  const params: Record<string, string> = {};
  if (categorie) params.categorie = categorie;
  const { data } = await clientApi.get<{ items?: ItemChecklistAnniversaire[] } | ItemChecklistAnniversaire[]>(
    `/famille/checklists-anniversaire/${checklistId}/items`,
    { params }
  );
  return Array.isArray(data) ? data : (data.items ?? []);
}

/** Met à jour l'état fait/non-fait d'un item checklist anniversaire */
export async function mettreAJourItemChecklist(
  checklistId: number,
  itemId: number,
  fait: boolean,
  prixReel?: number
): Promise<ItemChecklistAnniversaire> {
  const payload: ObjetDonnees = { fait };
  if (prixReel !== undefined) payload.prix_reel = prixReel;
  const { data } = await clientApi.patch<ItemChecklistAnniversaire>(
    `/famille/checklists-anniversaire/${checklistId}/items/${itemId}`,
    payload
  );
  return data;
}

/** Envoie un item checklist anniversaire vers les achats */
export async function itemChecklistVersAchat(
  checklistId: number,
  itemId: number
): Promise<{ achat_id: number }> {
  const { data } = await clientApi.post<{ achat_id: number }>(
    `/famille/checklists-anniversaire/${checklistId}/items/${itemId}/vers-achats`
  );
  return data;
}

// ─── Événements familiaux ─────────────────────────────────

export interface EvenementFamilial {
  id: number;
  titre: string;
  date_evenement: string;
  type_evenement: string;
  recurrence: string;
  rappel_jours_avant: number;
  notes?: string;
  participants?: string[];
  actif: boolean;
}

/** Lister les événements familiaux */
export async function listerEvenementsFamiliaux(
  type?: string
): Promise<EvenementFamilial[]> {
  const params: Record<string, string> = {};
  if (type) params.type_evenement = type;
  const { data } = await clientApi.get<{ items: EvenementFamilial[] }>(
    "/famille/evenements",
    { params }
  );
  return data.items;
}

/** Créer un événement familial */
export async function creerEvenementFamilial(
  event: Omit<EvenementFamilial, "id" | "actif">
): Promise<EvenementFamilial> {
  const { data } = await clientApi.post<EvenementFamilial>(
    "/famille/evenements",
    event
  );
  return data;
}

/** Modifier un événement familial */
export async function modifierEvenementFamilial(
  id: number,
  patch: Partial<EvenementFamilial>
): Promise<EvenementFamilial> {
  const { data } = await clientApi.patch<EvenementFamilial>(
    `/famille/evenements/${id}`,
    patch
  );
  return data;
}

/** Supprimer un événement familial */
export async function supprimerEvenementFamilial(
  id: number
): Promise<void> {
  await clientApi.delete(`/famille/evenements/${id}`);
}

// ─── Contexte familial ───────────────────────────────────

import type {
  ContexteFamilial,
  AchatFamille,
  RappelFamille,
} from "@/types/famille";

/** Obtenir le contexte familial complet (1 seul appel) */
export async function obtenirContexteFamilial(): Promise<ContexteFamilial> {
  const { data } = await clientApi.get<ContexteFamilial>("/famille/contexte");
  return data;
}

// ─── Suggestions IA ──────────────────────────────────────

/** Suggestions weekend avec météo auto-injectée */
export async function obtenirSuggestionsWeekend(params?: {
  budget?: number;
  region?: string;
  nb_suggestions?: number;
}): Promise<{ suggestions: string; meteo?: string }> {
  const { data } = await clientApi.post("/famille/weekend/suggestions-ia", params ?? {});
  return data;
}

/** Convertit une activite weekend en activite famille */
export async function convertirWeekendEnActivite(
  activiteId: number
): Promise<{ succes: boolean; weekend_id: number; activite_famille_id: number }> {
  const { data } = await clientApi.post<{ succes: boolean; weekend_id: number; activite_famille_id: number }>(
    `/famille/weekend/${activiteId}/convertir-activite`
  );
  return data;
}

export interface SuggestionActiviteSoir {
  meteo: string;
  temperature_c?: number | null;
  niveau_energie: "douce" | "moderee" | "dynamique";
  recommandation: string;
  raison: string;
  alternatives: string[];
  source: string[];
}

/** Suggestions soirée couple IA */
export async function obtenirSuggestionsSoiree(params?: {
  budget?: number;
  duree_heures?: number;
  type_soiree?: string;
  region?: string;
}): Promise<{ suggestions: string }> {
  const { data } = await clientApi.post("/famille/soiree/suggestions-ia", params ?? {});
  return data;
}

/** Suggestion d'activité du soir contextualisée par Garmin et météo */
export async function obtenirSuggestionActiviteSoir(): Promise<SuggestionActiviteSoir> {
  const { data } = await clientApi.get<SuggestionActiviteSoir>("/famille/activites/suggestion-soir");
  return data;
}

/** Suggestions d'activités avec météo automatique */
export async function obtenirSuggestionsActivitesAuto(params?: {
  budget_max?: number;
  duree_max_heures?: number;
  type_prefere?: string;
}): Promise<{
  suggestions: string;
  suggestions_struct?: Array<{
    titre: string;
    description: string;
    type: string;
    duree_minutes: number;
    lieu: string;
  }>;
  meteo: string;
  journee_libre: boolean;
}> {
  const { data } = await clientApi.post("/famille/activites/suggestions-ia-auto", params ?? {});
  return data;
}

// ─── Achats famille CRUD ─────────────────────────────────

/** Lister les achats (route canonique) */
export async function listerAchats(params?: {
  categorie?: string;
  achete?: boolean;
  pour_qui?: string;
  a_revendre?: boolean;
}): Promise<AchatFamille[]> {
  const { data } = await clientApi.get<{ items: AchatFamille[] }>(
    "/famille/achats",
    { params }
  );
  return data.items;
}

/** Créer un achat */
export async function creerAchat(
  achat: Omit<AchatFamille, "id" | "achete" | "date_achat" | "prix_reel">
): Promise<AchatFamille> {
  const { data } = await clientApi.post<AchatFamille>("/famille/achats", achat);
  return data;
}

/** Modifier un achat */
export async function modifierAchat(
  id: number,
  patch: Partial<AchatFamille>
): Promise<AchatFamille> {
  const { data } = await clientApi.patch<AchatFamille>(
    `/famille/achats/${id}`,
    patch
  );
  return data;
}

/** Marquer un achat comme acheté */
export async function marquerAchatAchete(
  id: number,
  prix_reel?: number
): Promise<void> {
  await clientApi.post(`/famille/achats/${id}/achete`, { prix_reel });
}

/** Supprimer un achat */
export async function supprimerAchat(id: number): Promise<void> {
  await clientApi.delete(`/famille/achats/${id}`);
}

/** Marquer un achat comme vendu */
export async function marquerAchatVendu(id: number): Promise<void> {
  await clientApi.post(`/famille/achats/${id}/vendu`);
}

/** Générer une annonce LBC pour un article */
export async function genererAnnonceLBC(
  id: number,
  payload: { nom: string; description?: string; etat_usage?: string; prix_cible?: number }
): Promise<{ annonce: string }> {
  const { data } = await clientApi.post<{ annonce: string }>(
    `/famille/achats/${id}/annonce-lbc`,
    payload
  );
  return data;
}

/** Marquer une routine comme complétée aujourd'hui */
export async function completerRoutine(
  id: number
): Promise<{ id: number; nom: string; derniere_completion: string }> {
  const { data } = await clientApi.patch<{ id: number; nom: string; derniere_completion: string }>(
    `/famille/routines/${id}/completer`
  );
  return data;
}

/** Résumé budget du mois courant vs précédent */
export async function obtenirResumeBudgetMois(): Promise<{
  mois_courant: string;
  total_courant: number;
  total_precedent: number | null;
  variation_pct: number | null;
  achats_par_categorie: Record<string, number>;
}> {
  const { data } = await clientApi.get("/famille/budget/resume-mois");
  return data;
}

/** Lire la configuration garde/crèche */
export async function lireConfigGarde(): Promise<{
  semaines_fermeture: Array<{ debut: string; fin: string; label: string }>;
  nom_creche: string;
  zone_academique: string;
  annee_courante: number | null;
}> {
  const { data } = await clientApi.get("/famille/config/garde");
  return data;
}

/** Sauvegarder la configuration garde/crèche */
export async function sauvegarderConfigGarde(payload: {
  semaines_fermeture: Array<{ debut: string; fin: string; label: string }>;
  nom_creche: string;
  zone_academique: string;
}): Promise<void> {
  await clientApi.put("/famille/config/garde", payload);
}

/** Lire les préférences familiales (tailles, style, intérêts) */
export async function lirePreferencesFamille(): Promise<{
  taille_vetements_anne: Record<string, string>;
  taille_vetements_mathieu: Record<string, string>;
  style_achats_anne: ObjetDonnees;
  style_achats_mathieu: ObjetDonnees;
  interets_gaming: string[];
  interets_culture: string[];
  equipement_activites: ObjetDonnees;
}> {
  const { data } = await clientApi.get("/famille/config/preferences");
  return data;
}

/** Sauvegarder les préférences familiales */
export async function sauvegarderPreferencesFamille(payload: {
  taille_vetements_anne: Record<string, string>;
  taille_vetements_mathieu: Record<string, string>;
  style_achats_anne: ObjetDonnees;
  style_achats_mathieu: ObjetDonnees;
  interets_gaming: string[];
  interets_culture: string[];
  equipement_activites: ObjetDonnees;
}): Promise<void> {
  await clientApi.put("/famille/config/preferences", payload);
}

/** Jours sans crèche pour un mois */
export async function joursSansCReche(mois?: string): Promise<{
  mois: string;
  jours: Array<{ date: string; label: string | null }>;
  total: number;
}> {
  const { data } = await clientApi.get("/famille/planning/jours-sans-creche", {
    params: mois ? { mois } : undefined,
  });
  return data;
}

/** Suggestions IA pour un séjour */
export async function obtenirSuggestionsSejourIA(payload: {
  destination: string;
  nb_jours?: number;
  age_jules_mois?: number;
}): Promise<{ suggestions: string; destination: string }> {
  const { data } = await clientApi.post("/famille/weekend/suggestions-sejour", payload);
  return data;
}

/** Suggestions IA pour les achats et cadeaux */
export interface SuggestionAchat {
  titre: string;
  description: string;
  fourchette_prix?: string | null;
  ou_acheter?: string | null;
  pertinence?: string | null;
}
export async function obtenirSuggestionsAchatsIA(params: {
  type: "anniversaire" | "jalon" | "saison";
  nom?: string;
  age?: number;
  relation?: string;
  budget_max?: number;
  historique_cadeaux?: string[];
  prochains_jalons?: string[];
  saison?: string;
  tailles?: Record<string, string>;
}): Promise<{ suggestions: SuggestionAchat[]; total: number; type: string }> {
  const { data } = await clientApi.post("/famille/achats/suggestions-ia", params);
  return data;
}

/** Suggestions IA proactives (anniversaires, jalons, saison) */
export async function obtenirSuggestionsAchatsAuto(params?: {
  budget_max?: number;
  relation_defaut?: string;
}): Promise<{
  suggestions: Array<SuggestionAchat & { source: "anniversaire" | "jalon" | "saison" }>;
  groupes: {
    anniversaire: SuggestionAchat[];
    jalon: SuggestionAchat[];
    saison: SuggestionAchat[];
  };
  total: number;
}> {
  const { data } = await clientApi.post("/famille/achats/suggestions", params ?? {});
  return data;
}

/** Suggestions IA enrichies avec 6 triggers configurables */
export async function obtenirSuggestionsAchatsEnrichies(payload: {
  triggers: string[];
  pour_qui?: string;
  destination?: string;
  ville?: string;
  budget?: number;
  age_jules_mois?: number;
}): Promise<{
  items: Array<{
    titre: string;
    description: string;
    fourchette_prix?: string | null;
    ou_acheter?: string | null;
    pertinence?: string | null;
    source?: string;
  }>;
  total: number;
}> {
  const { data } = await clientApi.post("/famille/achats/suggestions-ia-enrichies", payload);
  return data;
}

// ─── Rappels ─────────────────────────────────────────────

/** Évaluer les rappels du jour */
export async function evaluerRappelsFamille(): Promise<{
  rappels: RappelFamille[];
  total: number;
}> {
  const { data } = await clientApi.get("/famille/rappels/evaluer");
  return data;
}

/** Envoyer les rappels push */
export async function envoyerRappels(): Promise<{
  envoyes: number;
  message: string;
}> {
  const { data } = await clientApi.post("/famille/rappels/envoyer");
  return data;
}

// ─── Aliments exclus Jules ──────────────────────────────

/** Obtenir les aliments exclus pour Jules */
export async function obtenirAlimentsExclus(): Promise<{ aliments_exclus: string[] }> {
  const { data } = await clientApi.get<{ aliments_exclus: string[] }>(
    "/famille/jules/aliments-exclus"
  );
  return data;
}

/** Sauvegarder la liste des aliments exclus pour Jules */
export async function sauvegarderAlimentsExclus(
  aliments: string[]
): Promise<{ aliments_exclus: string[] }> {
  const { data } = await clientApi.put<{ aliments_exclus: string[] }>(
    "/famille/jules/aliments-exclus",
    { aliments_exclus: aliments }
  );
  return data;
}

// ─── Coaching hebdomadaire Jules ────────────────────────

export interface CoachingJules {
  semaine: string;
  conseils: string[];
  alertes: string[];
  points_positifs: string[];
  prochain_rdv?: string;
  resume: string;
}

/** Obtenir le coaching hebdomadaire IA pour Jules */
export async function obtenirCoachingHebdo(): Promise<CoachingJules> {
  const { data } = await clientApi.get<CoachingJules>(
    "/famille/jules/coaching-hebdo"
  );
  return data;
}
