// ═══════════════════════════════════════════════════════════
// API Maison
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type {
  ProjetMaison,
  TacheEntretien,
  ElementJardin,
  StockMaison,
  ChargesMaison,
  CalendrierSemis,
  SanteAppareils,
  Meuble,
  BudgetMeublesResume,
  ArticleCellier,
  AlertePeremption,
  StatsCellier,
  Artisan,
  InterventionArtisan,
  StatsArtisans,
  Contrat,
  AlerteContrat,
  ResumeFinancierContrats,
  Garantie,
  IncidentSAV,
  AlerteGarantie,
  AlertePredictiveGarantie,
  StatsGaranties,
  ResultatDossierSAV,
  DiagnosticImmobilier,
  EstimationImmobiliere,
  ActionEcologique,
  DepenseMaison,
  StatsDepenses,
  TraitementNuisible,
  DevisComparatif,
  LigneDevis,
  EntretienSaisonnier,
  ReleveCompteur,
  PieceMaison,
  ObjetMaison,
  StatsHubMaison,
  BriefingMaison,
  AlerteMaison,
  ConseilMaisonHub,
} from "@/types/maison";

// ─── Projets ──────────────────────────────────────────────

/** Lister les projets maison */
export async function listerProjets(
  statut?: string,
  priorite?: string
): Promise<ProjetMaison[]> {
  const params = new URLSearchParams();
  if (statut) params.set("statut", statut);
  if (priorite) params.set("priorite", priorite);
  const qs = params.toString();
  const { data } = await clientApi.get(`/maison/projets${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

/** Créer un projet */
export async function creerProjet(
  projet: Omit<ProjetMaison, "id" | "taches_count">
): Promise<ProjetMaison> {
  const { data } = await clientApi.post<ProjetMaison>("/maison/projets", projet);
  return data;
}

/** Modifier un projet */
export async function modifierProjet(
  id: number,
  projet: Partial<ProjetMaison>
): Promise<ProjetMaison> {
  const { data } = await clientApi.patch<ProjetMaison>(`/maison/projets/${id}`, projet);
  return data;
}

/** Supprimer un projet */
export async function supprimerProjet(id: number): Promise<void> {
  await clientApi.delete(`/maison/projets/${id}`);
}

/** Obtenir un projet par ID */
export async function obtenirProjet(id: number): Promise<ProjetMaison> {
  const { data } = await clientApi.get<ProjetMaison>(`/maison/projets/${id}`);
  return data;
}

export interface MaterielProjet {
  nom: string;
  quantite: number;
  prix_estime?: number;
  magasin_suggere?: string;
  alternatif_eco?: string;
}

export interface EstimationProjet {
  nom_projet: string;
  description_analysee: string;
  budget_estime_min: number;
  budget_estime_max: number;
  duree_estimee_jours: number;
  taches_suggerees: Array<{ nom: string; ordre: number; duree_estimee_min?: number; materiels_requis?: string[] }>;
  materiels_necessaires: MaterielProjet[];
  risques_identifies: string[];
  conseils_ia: string[];
}

/** Estimer un projet avec l'IA (budget, tâches, matériaux) */
export async function estimerProjetIA(id: number): Promise<EstimationProjet> {
  const { data } = await clientApi.post<EstimationProjet>(`/maison/projets/${id}/estimer-ia`);
  return data;
}

/** Lister les tâches d'un projet */
export async function listerTachesProjet(
  projetId: number
): Promise<Array<{ id: number; nom: string; statut?: string; fait?: boolean; priorite?: string }>> {
  const { data } = await clientApi.get(`/maison/projets/${projetId}/taches`);
  return data.items ?? data;
}

// ─── Entretien ────────────────────────────────────────────

/** Lister les tâches d'entretien */
export async function listerTachesEntretien(
  categorie?: string,
  piece?: string
): Promise<TacheEntretien[]> {
  const params = new URLSearchParams();
  if (categorie) params.set("categorie", categorie);
  if (piece) params.set("piece", piece);
  const qs = params.toString();
  const { data } = await clientApi.get(`/maison/entretien${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

/** Créer une tâche d'entretien */
export async function creerTacheEntretien(
  tache: Omit<TacheEntretien, "id">
): Promise<TacheEntretien> {
  const { data } = await clientApi.post<TacheEntretien>("/maison/entretien", tache);
  return data;
}

/** Modifier une tâche d'entretien */
export async function modifierTacheEntretien(
  id: number,
  tache: Partial<TacheEntretien>
): Promise<TacheEntretien> {
  const { data } = await clientApi.patch<TacheEntretien>(`/maison/entretien/${id}`, tache);
  return data;
}

/** Supprimer une tâche d'entretien */
export async function supprimerTacheEntretien(id: number): Promise<void> {
  await clientApi.delete(`/maison/entretien/${id}`);
}

/** Dashboard santé des appareils */
export async function obtenirSanteAppareils(): Promise<SanteAppareils> {
  const { data } = await clientApi.get<SanteAppareils>(
    "/maison/entretien/sante-appareils"
  );
  return data;
}

// ─── Jardin ───────────────────────────────────────────────

/** Lister les éléments du jardin */
export async function listerElementsJardin(
  type_element?: string
): Promise<ElementJardin[]> {
  const params = type_element ? `?type_element=${type_element}` : "";
  const { data } = await clientApi.get(`/maison/jardin${params}`);
  return data.items ?? data;
}

/** Ajouter un élément au jardin */
export async function creerElementJardin(
  element: Omit<ElementJardin, "id">
): Promise<ElementJardin> {
  const { data } = await clientApi.post<ElementJardin>("/maison/jardin", element);
  return data;
}

/** Modifier un élément du jardin */
export async function modifierElementJardin(
  id: number,
  element: Partial<ElementJardin>
): Promise<ElementJardin> {
  const { data } = await clientApi.patch<ElementJardin>(`/maison/jardin/${id}`, element);
  return data;
}

/** Supprimer un élément du jardin */
export async function supprimerElementJardin(id: number): Promise<void> {
  await clientApi.delete(`/maison/jardin/${id}`);
}

/** Calendrier des semis */
export async function obtenirCalendrierSemis(
  mois?: number
): Promise<CalendrierSemis> {
  const params = mois ? `?mois=${mois}` : "";
  const { data } = await clientApi.get<CalendrierSemis>(
    `/maison/jardin/calendrier-semis${params}`
  );
  return data;
}

// ─── Stocks ───────────────────────────────────────────────

/** Lister les stocks maison */
export async function listerStocks(
  categorie?: string,
  alerteOnly?: boolean
): Promise<StockMaison[]> {
  const params = new URLSearchParams();
  if (categorie) params.set("categorie", categorie);
  if (alerteOnly) params.set("alerte_stock", "true");
  const qs = params.toString();
  const { data } = await clientApi.get(`/maison/stocks${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

/** Créer un stock */
export async function creerStock(
  stock: Omit<StockMaison, "id" | "en_alerte">
): Promise<StockMaison> {
  const { data } = await clientApi.post<StockMaison>("/maison/stocks", stock);
  return data;
}

/** Modifier un stock */
export async function modifierStock(
  id: number,
  stock: Partial<StockMaison>
): Promise<StockMaison> {
  const { data } = await clientApi.patch<StockMaison>(`/maison/stocks/${id}`, stock);
  return data;
}

/** Supprimer un stock */
export async function supprimerStock(id: number): Promise<void> {
  await clientApi.delete(`/maison/stocks/${id}`);
}

// ─── Charges ──────────────────────────────────────────────

/** Lister les charges (factures) */
export async function listerCharges(annee?: number): Promise<ChargesMaison[]> {
  const params = annee ? `?annee=${annee}` : "";
  const { data } = await clientApi.get(`/maison/charges${params}`);
  return data.items ?? data;
}

// ─── Meubles ──────────────────────────────────────────────

export async function listerMeubles(statut?: string, piece?: string): Promise<Meuble[]> {
  const params = new URLSearchParams();
  if (statut) params.set("statut", statut);
  if (piece) params.set("piece", piece);
  const qs = params.toString();
  const { data } = await clientApi.get(`/maison/meubles${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

export async function creerMeuble(meuble: Omit<Meuble, "id">): Promise<Meuble> {
  const { data } = await clientApi.post<Meuble>("/maison/meubles", meuble);
  return data;
}

export async function modifierMeuble(id: number, meuble: Partial<Meuble>): Promise<Meuble> {
  const { data } = await clientApi.patch<Meuble>(`/maison/meubles/${id}`, meuble);
  return data;
}

export async function supprimerMeuble(id: number): Promise<void> {
  await clientApi.delete(`/maison/meubles/${id}`);
}

export async function obtenirBudgetMeubles(): Promise<BudgetMeublesResume> {
  const { data } = await clientApi.get<BudgetMeublesResume>("/maison/meubles/budget");
  return data;
}

// ─── Cellier ──────────────────────────────────────────────

export async function listerArticlesCellier(
  categorie?: string,
  emplacement?: string
): Promise<ArticleCellier[]> {
  const params = new URLSearchParams();
  if (categorie) params.set("categorie", categorie);
  if (emplacement) params.set("emplacement", emplacement);
  const qs = params.toString();
  const { data } = await clientApi.get(`/maison/cellier${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

export async function obtenirArticleCellier(id: number): Promise<ArticleCellier> {
  const { data } = await clientApi.get<ArticleCellier>(`/maison/cellier/${id}`);
  return data;
}

export async function creerArticleCellier(
  article: Omit<ArticleCellier, "id">
): Promise<ArticleCellier> {
  const { data } = await clientApi.post<ArticleCellier>("/maison/cellier", article);
  return data;
}

export async function modifierArticleCellier(
  id: number,
  article: Partial<ArticleCellier>
): Promise<ArticleCellier> {
  const { data } = await clientApi.patch<ArticleCellier>(`/maison/cellier/${id}`, article);
  return data;
}

export async function supprimerArticleCellier(id: number): Promise<void> {
  await clientApi.delete(`/maison/cellier/${id}`);
}

export async function ajusterQuantiteCellier(
  id: number,
  delta: number
): Promise<ArticleCellier> {
  const { data } = await clientApi.patch<ArticleCellier>(`/maison/cellier/${id}/quantite`, {
    delta,
  });
  return data;
}

export async function alertesPeremptionCellier(
  jours = 14
): Promise<AlertePeremption[]> {
  const { data } = await clientApi.get(`/maison/cellier/alertes/peremption?jours=${jours}`);
  return data.items ?? data;
}

export async function alertesStockCellier(): Promise<ArticleCellier[]> {
  const { data } = await clientApi.get("/maison/cellier/alertes/stock");
  return data.items ?? data;
}

export async function statsCellier(): Promise<StatsCellier> {
  const { data } = await clientApi.get<StatsCellier>("/maison/cellier/stats");
  return data;
}

// ─── Artisans ─────────────────────────────────────────────

export async function listerArtisans(metier?: string): Promise<Artisan[]> {
  const params = metier ? `?metier=${metier}` : "";
  const { data } = await clientApi.get(`/maison/artisans${params}`);
  return data.items ?? data;
}

export async function obtenirArtisan(id: number): Promise<Artisan> {
  const { data } = await clientApi.get<Artisan>(`/maison/artisans/${id}`);
  return data;
}

export async function creerArtisan(artisan: Omit<Artisan, "id">): Promise<Artisan> {
  const { data } = await clientApi.post<Artisan>("/maison/artisans", artisan);
  return data;
}

export async function modifierArtisan(
  id: number,
  artisan: Partial<Artisan>
): Promise<Artisan> {
  const { data } = await clientApi.patch<Artisan>(`/maison/artisans/${id}`, artisan);
  return data;
}

export async function supprimerArtisan(id: number): Promise<void> {
  await clientApi.delete(`/maison/artisans/${id}`);
}

export async function statsArtisans(): Promise<StatsArtisans> {
  const { data } = await clientApi.get<StatsArtisans>("/maison/artisans/stats");
  return data;
}

export async function listerInterventions(
  artisanId: number
): Promise<InterventionArtisan[]> {
  const { data } = await clientApi.get(`/maison/artisans/${artisanId}/interventions`);
  return data.items ?? data;
}

export async function creerIntervention(
  artisanId: number,
  intervention: Omit<InterventionArtisan, "id" | "artisan_id">
): Promise<InterventionArtisan> {
  const { data } = await clientApi.post<InterventionArtisan>(
    `/maison/artisans/${artisanId}/interventions`,
    intervention
  );
  return data;
}

export async function supprimerIntervention(id: number): Promise<void> {
  await clientApi.delete(`/maison/artisans/interventions/${id}`);
}

// ─── Contrats ─────────────────────────────────────────────

export async function listerContrats(
  typeContrat?: string,
  statut?: string
): Promise<Contrat[]> {
  const params = new URLSearchParams();
  if (typeContrat) params.set("type_contrat", typeContrat);
  if (statut) params.set("statut", statut);
  const qs = params.toString();
  const { data } = await clientApi.get(`/maison/contrats${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

export async function obtenirContrat(id: number): Promise<Contrat> {
  const { data } = await clientApi.get<Contrat>(`/maison/contrats/${id}`);
  return data;
}

export async function creerContrat(contrat: Omit<Contrat, "id">): Promise<Contrat> {
  const { data } = await clientApi.post<Contrat>("/maison/contrats", contrat);
  return data;
}

export async function modifierContrat(
  id: number,
  contrat: Partial<Contrat>
): Promise<Contrat> {
  const { data } = await clientApi.patch<Contrat>(`/maison/contrats/${id}`, contrat);
  return data;
}

export async function supprimerContrat(id: number): Promise<void> {
  await clientApi.delete(`/maison/contrats/${id}`);
}

export async function alertesContrats(jours = 60): Promise<AlerteContrat[]> {
  const { data } = await clientApi.get(`/maison/contrats/alertes?jours=${jours}`);
  return data.items ?? data;
}

export async function resumeFinancierContrats(): Promise<ResumeFinancierContrats> {
  const { data } = await clientApi.get<ResumeFinancierContrats>(
    "/maison/contrats/resume-financier"
  );
  return data;
}

// ─── Garanties ────────────────────────────────────────────

export async function listerGaranties(
  statut?: string,
  piece?: string
): Promise<Garantie[]> {
  const params = new URLSearchParams();
  if (statut) params.set("statut", statut);
  if (piece) params.set("piece", piece);
  const qs = params.toString();
  const { data } = await clientApi.get(`/maison/garanties${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

export async function obtenirGarantie(id: number): Promise<Garantie> {
  const { data } = await clientApi.get<Garantie>(`/maison/garanties/${id}`);
  return data;
}

export async function creerGarantie(garantie: Omit<Garantie, "id">): Promise<Garantie> {
  const { data } = await clientApi.post<Garantie>("/maison/garanties", garantie);
  return data;
}

export async function modifierGarantie(
  id: number,
  garantie: Partial<Garantie>
): Promise<Garantie> {
  const { data } = await clientApi.patch<Garantie>(`/maison/garanties/${id}`, garantie);
  return data;
}

export async function supprimerGarantie(id: number): Promise<void> {
  await clientApi.delete(`/maison/garanties/${id}`);
}

export async function alertesGaranties(jours = 60): Promise<AlerteGarantie[]> {
  const { data } = await clientApi.get(`/maison/garanties/alertes?jours=${jours}`);
  return data.items ?? data;
}

export async function statsGaranties(): Promise<StatsGaranties> {
  const { data } = await clientApi.get<StatsGaranties>("/maison/garanties/stats");
  return data;
}

export async function alertesPredictivesGaranties(horizonMois = 12): Promise<AlertePredictiveGarantie[]> {
  const { data } = await clientApi.get<{ items: AlertePredictiveGarantie[] }>(
    `/maison/garanties/alertes-predictives?horizon_mois=${horizonMois}`
  );
  return data.items ?? [];
}

export async function listerIncidents(garantieId: number): Promise<IncidentSAV[]> {
  const { data } = await clientApi.get(`/maison/garanties/${garantieId}/incidents`);
  return data.items ?? data;
}

export async function creerIncident(
  garantieId: number,
  incident: Omit<IncidentSAV, "id" | "garantie_id">
): Promise<IncidentSAV> {
  const { data } = await clientApi.post<IncidentSAV>(
    `/maison/garanties/${garantieId}/incidents`,
    incident
  );
  return data;
}

export async function modifierIncident(
  id: number,
  incident: Partial<IncidentSAV>
): Promise<IncidentSAV> {
  const { data } = await clientApi.patch<IncidentSAV>(
    `/maison/garanties/incidents/${id}`,
    incident
  );
  return data;
}

// ─── Action SAV 1-clic ────────────────────────────────────

export async function ouvrirDossierSAV(
  garantieId: number,
  description?: string,
  source: string = "frontend"
): Promise<ResultatDossierSAV> {
  const { data } = await clientApi.post<ResultatDossierSAV>(
    `/maison/garanties/${garantieId}/actions/ouvrir-dossier-sav`,
    { description, source }
  );
  return data;
}

// ─── Diagnostics & Estimations ────────────────────────────

export async function listerDiagnostics(): Promise<DiagnosticImmobilier[]> {
  const { data } = await clientApi.get("/maison/diagnostics");
  return data.items ?? data;
}

export async function creerDiagnostic(
  diag: Omit<DiagnosticImmobilier, "id">
): Promise<DiagnosticImmobilier> {
  const { data } = await clientApi.post<DiagnosticImmobilier>("/maison/diagnostics", diag);
  return data;
}

export async function modifierDiagnostic(
  id: number,
  diag: Partial<DiagnosticImmobilier>
): Promise<DiagnosticImmobilier> {
  const { data } = await clientApi.patch<DiagnosticImmobilier>(
    `/maison/diagnostics/${id}`,
    diag
  );
  return data;
}

export async function supprimerDiagnostic(id: number): Promise<void> {
  await clientApi.delete(`/maison/diagnostics/${id}`);
}

export async function alertesDiagnostics(jours = 90): Promise<DiagnosticImmobilier[]> {
  const { data } = await clientApi.get(`/maison/diagnostics/alertes?jours=${jours}`);
  return data.items ?? data;
}

export async function validiteTypesDiagnostics(): Promise<
  Record<string, number>
> {
  const { data } = await clientApi.get("/maison/diagnostics/validite-types");
  return data;
}

export async function listerEstimations(): Promise<EstimationImmobiliere[]> {
  const { data } = await clientApi.get("/maison/estimations");
  return data.items ?? data;
}

export async function derniereEstimation(): Promise<EstimationImmobiliere> {
  const { data } = await clientApi.get<EstimationImmobiliere>(
    "/maison/estimations/derniere"
  );
  return data;
}

export async function creerEstimation(
  estimation: Omit<EstimationImmobiliere, "id">
): Promise<EstimationImmobiliere> {
  const { data } = await clientApi.post<EstimationImmobiliere>(
    "/maison/estimations",
    estimation
  );
  return data;
}

export async function supprimerEstimation(id: number): Promise<void> {
  await clientApi.delete(`/maison/estimations/${id}`);
}

// ─── Éco-Tips ─────────────────────────────────────────────

export async function listerEcoTips(actifOnly = false): Promise<ActionEcologique[]> {
  const params = actifOnly ? "?actif_only=true" : "";
  const { data } = await clientApi.get(`/maison/eco-tips${params}`);
  return data.items ?? data;
}

export async function obtenirEcoTip(id: number): Promise<ActionEcologique> {
  const { data } = await clientApi.get<ActionEcologique>(`/maison/eco-tips/${id}`);
  return data;
}

export async function creerEcoTip(
  action: Omit<ActionEcologique, "id">
): Promise<ActionEcologique> {
  const { data } = await clientApi.post<ActionEcologique>("/maison/eco-tips", action);
  return data;
}

export async function modifierEcoTip(
  id: number,
  action: Partial<ActionEcologique>
): Promise<ActionEcologique> {
  const { data } = await clientApi.patch<ActionEcologique>(`/maison/eco-tips/${id}`, action);
  return data;
}

export async function supprimerEcoTip(id: number): Promise<void> {
  await clientApi.delete(`/maison/eco-tips/${id}`);
}

// ─── Dépenses ─────────────────────────────────────────────

export async function listerDepensesMaison(
  mois?: number,
  annee?: number
): Promise<DepenseMaison[]> {
  const params = new URLSearchParams();
  if (mois) params.set("mois", mois.toString());
  if (annee) params.set("annee", annee.toString());
  const qs = params.toString();
  const { data } = await clientApi.get(`/maison/depenses${qs ? `?${qs}` : ""}`);
  return data.items ?? data;
}

export async function obtenirDepenseMaison(id: number): Promise<DepenseMaison> {
  const { data } = await clientApi.get<DepenseMaison>(`/maison/depenses/${id}`);
  return data;
}

export async function creerDepenseMaison(
  depense: Omit<DepenseMaison, "id">
): Promise<DepenseMaison> {
  const { data } = await clientApi.post<DepenseMaison>("/maison/depenses", depense);
  return data;
}

export async function modifierDepenseMaison(
  id: number,
  depense: Partial<DepenseMaison>
): Promise<DepenseMaison> {
  const { data } = await clientApi.patch<DepenseMaison>(`/maison/depenses/${id}`, depense);
  return data;
}

export async function supprimerDepenseMaison(id: number): Promise<void> {
  await clientApi.delete(`/maison/depenses/${id}`);
}

export async function statsDepensesMaison(): Promise<StatsDepenses> {
  const { data } = await clientApi.get<StatsDepenses>("/maison/depenses/stats");
  return data;
}

export async function historiqueDepensesMaisonCategorie(
  categorie: string,
  nbMois = 12
): Promise<Record<string, number>[]> {
  const { data } = await clientApi.get(
    `/maison/depenses/historique/${encodeURIComponent(categorie)}?nb_mois=${nbMois}`
  );
  return data.items ?? data;
}

export async function historiqueEnergie(
  typeEnergie: string,
  nbMois = 12
): Promise<Record<string, unknown>> {
  const { data } = await clientApi.get(
    `/maison/depenses/energie/${encodeURIComponent(typeEnergie)}?nb_mois=${nbMois}`
  );
  return data;
}

// ─── Nuisibles ────────────────────────────────────────────

export async function listerNuisibles(): Promise<TraitementNuisible[]> {
  const { data } = await clientApi.get("/maison/nuisibles");
  return data.items ?? data;
}

export async function creerTraitementNuisible(
  traitement: Omit<TraitementNuisible, "id">
): Promise<TraitementNuisible> {
  const { data } = await clientApi.post<TraitementNuisible>("/maison/nuisibles", traitement);
  return data;
}

export async function modifierTraitementNuisible(
  id: number,
  traitement: Partial<TraitementNuisible>
): Promise<TraitementNuisible> {
  const { data } = await clientApi.patch<TraitementNuisible>(
    `/maison/nuisibles/${id}`,
    traitement
  );
  return data;
}

export async function supprimerTraitementNuisible(id: number): Promise<void> {
  await clientApi.delete(`/maison/nuisibles/${id}`);
}

export async function prochainsTraitements(
  jours = 30
): Promise<TraitementNuisible[]> {
  const { data } = await clientApi.get(`/maison/nuisibles/prochains?jours=${jours}`);
  return data.items ?? data;
}

// ─── Devis ────────────────────────────────────────────────

export async function listerDevis(projetId?: number): Promise<DevisComparatif[]> {
  const params = projetId ? `?projet_id=${projetId}` : "";
  const { data } = await clientApi.get(`/maison/devis${params}`);
  return data.items ?? data;
}

export async function creerDevis(
  devis: Omit<DevisComparatif, "id" | "lignes">
): Promise<DevisComparatif> {
  const { data } = await clientApi.post<DevisComparatif>("/maison/devis", devis);
  return data;
}

export async function modifierDevis(
  id: number,
  devis: Partial<DevisComparatif>
): Promise<DevisComparatif> {
  const { data } = await clientApi.patch<DevisComparatif>(`/maison/devis/${id}`, devis);
  return data;
}

export async function supprimerDevis(id: number): Promise<void> {
  await clientApi.delete(`/maison/devis/${id}`);
}

export async function ajouterLigneDevis(
  devisId: number,
  ligne: Omit<LigneDevis, "id" | "devis_id">
): Promise<LigneDevis> {
  const { data } = await clientApi.post<LigneDevis>(
    `/maison/devis/${devisId}/lignes`,
    ligne
  );
  return data;
}

export async function choisirDevis(devisId: number): Promise<DevisComparatif> {
  const { data } = await clientApi.post<DevisComparatif>(`/maison/devis/${devisId}/choisir`);
  return data;
}

// ─── Entretien saisonnier ─────────────────────────────────

export async function listerEntretienSaisonnier(): Promise<EntretienSaisonnier[]> {
  const { data } = await clientApi.get("/maison/entretien-saisonnier");
  return data.items ?? data;
}

export async function alertesEntretienSaisonnier(): Promise<EntretienSaisonnier[]> {
  const { data } = await clientApi.get("/maison/entretien-saisonnier/alertes");
  return data.items ?? data;
}

export async function creerEntretienSaisonnier(
  tache: Omit<EntretienSaisonnier, "id">
): Promise<EntretienSaisonnier> {
  const { data } = await clientApi.post<EntretienSaisonnier>(
    "/maison/entretien-saisonnier",
    tache
  );
  return data;
}

export async function supprimerEntretienSaisonnier(id: number): Promise<void> {
  await clientApi.delete(`/maison/entretien-saisonnier/${id}`);
}

export async function marquerEntretienSaisonnierFait(
  id: number
): Promise<EntretienSaisonnier> {
  const { data } = await clientApi.patch<EntretienSaisonnier>(
    `/maison/entretien-saisonnier/${id}/fait`
  );
  return data;
}

export async function resetEntretienSaisonnier(): Promise<void> {
  await clientApi.post("/maison/entretien-saisonnier/reset");
}

// ─── Relevés compteurs ────────────────────────────────────

export async function listerReleves(): Promise<ReleveCompteur[]> {
  const { data } = await clientApi.get("/maison/releves");
  return data.items ?? data;
}

export async function creerReleve(
  releve: Omit<ReleveCompteur, "id">
): Promise<ReleveCompteur> {
  const { data } = await clientApi.post<ReleveCompteur>("/maison/releves", releve);
  return data;
}

export async function supprimerReleve(id: number): Promise<void> {
  await clientApi.delete(`/maison/releves/${id}`);
}

// ─── Tendances énergie ────────────────────────────────────

export interface PointTendanceEnergie {
  mois: string;
  conso: number;
  anomalie: boolean;
  ecart_pct: number;
}
export interface TendancesEnergie {
  type: string;
  points: PointTendanceEnergie[];
  moyenne: number;
  total: number;
}

export async function obtenirTendancesEnergie(
  typeCompteur: "electricite" | "eau" | "gaz" = "electricite",
  nbMois = 12
): Promise<TendancesEnergie> {
  const { data } = await clientApi.get<TendancesEnergie>(
    `/maison/energie/tendances?type_compteur=${typeCompteur}&nb_mois=${nbMois}`
  );
  return data;
}

export interface PrevisionsEnergie {
  type: string;
  mois_prochain: string | null;
  consommation_prevue: number | null;
  tendance: "hausse" | "baisse" | "stable" | "insuffisant";
  confiance: number;
  pente_mensuelle?: number;
  nb_mois_analyses?: number;
  message?: string;
}

export async function obtenirPrevisionsEnergie(
  typeCompteur: "electricite" | "eau" | "gaz" = "electricite",
  nbMois = 6
): Promise<PrevisionsEnergie> {
  const { data } = await clientApi.get<PrevisionsEnergie>(
    `/maison/energie/previsions-ia?type_compteur=${typeCompteur}&nb_mois=${nbMois}`
  );
  return data;
}

// ─── Suggestions IA jardin ────────────────────────────────

export interface TacheJardinIA {
  tache: string;
  saison: string;
}

export async function obtenirSuggestionsIAJardin(): Promise<{
  taches: TacheJardinIA[];
  total: number;
}> {
  const { data } = await clientApi.get("/maison/jardin/suggestions-ia");
  return data;
}

// ─── Visualisation Plan ───────────────────────────────────

export async function listerPieces(etage?: number): Promise<PieceMaison[]> {
  const params = etage !== undefined ? `?etage=${etage}` : "";
  const { data } = await clientApi.get(`/maison/visualisation/pieces${params}`);
  return data.items ?? data;
}

export async function listerEtages(): Promise<number[]> {
  const { data } = await clientApi.get("/maison/visualisation/etages");
  return data.etages ?? data;
}

export async function historiquePiece(
  pieceId: number
): Promise<Record<string, unknown>> {
  const { data } = await clientApi.get(`/maison/visualisation/pieces/${pieceId}/historique`);
  return data;
}

export async function objetsPiece(pieceId: number): Promise<ObjetMaison[]> {
  const { data } = await clientApi.get(`/maison/visualisation/pieces/${pieceId}/objets`);
  return data.items ?? data;
}

export async function obtenirDetailPiece(pieceId: number): Promise<{
  piece: { id: number; nom: string; etage: number; surface_m2: number | null; type_piece: string | null };
  objets: { id: number; nom: string; statut: string | null; categorie: string | null }[];
  nb_taches_retard: number;
}> {
  const { data } = await clientApi.get(`/maison/pieces/${pieceId}/detail`);
  return data;
}

export async function sauvegarderPositions(
  pieces: { id: number; position_x: number; position_y: number }[]
): Promise<void> {
  await clientApi.post("/maison/visualisation/positions", { pieces });
}

// ─── Hub Stats ────────────────────────────────────────────

export async function statsHubMaison(): Promise<StatsHubMaison> {
  const { data } = await clientApi.get<StatsHubMaison>("/maison/hub/stats");
  return data;
}
// ─── Briefing & Alertes ────────────────────────────

/** Briefing quotidien contextuel de la maison */
export async function obtenirBriefingMaison(): Promise<BriefingMaison> {
  const { data } = await clientApi.get<BriefingMaison>("/maison/briefing");
  return data;
}

/** Liste toutes les alertes actives maison */
export async function obtenirAlertesMaison(): Promise<AlerteMaison[]> {
  const { data } = await clientApi.get<AlerteMaison[]>("/maison/alertes");
  return Array.isArray(data) ? data : (data as { items?: AlerteMaison[] }).items ?? [];
}

/** Tâches du jour avec statut */
export async function obtenirTachesJourMaison(): Promise<BriefingMaison["taches_jour_detail"]> {
  const { data } = await clientApi.get<{ items: BriefingMaison["taches_jour_detail"] }>("/maison/taches-jour");
  return data.items ?? (data as unknown as BriefingMaison["taches_jour_detail"]);
}

/** Déclenche l'évaluation et l'envoi des rappels push maison */
export async function envoyerRappelsMaison(): Promise<{ rappels_envoyes: number; rappels_ignores: number; erreurs: string[] }> {
  const { data } = await clientApi.post("/maison/rappels/envoyer", {});
  return data;
}

// ─── Fiche tâche & Guide ────────────────────────────

export interface FicheTache {
  nom: string;
  type_tache: string;
  duree_estimee_min: number;
  difficulte: string;
  etapes: string[];
  produits: string[];
  outils: string[];
  astuce_connectee?: string;
  source?: string;
}

/** Obtenir la fiche détaillée d'une tâche */
export async function obtenirFicheTache(params: {
  type_tache: string;
  id_tache?: string | number;
  nom_tache?: string;
}): Promise<FicheTache> {
  const { data } = await clientApi.get<FicheTache>("/maison/fiche-tache", { params });
  return data;
}

/** Obtenir la fiche via IA si non trouvée en catalogue */
export async function genererFicheTacheIA(nomTache: string, contexte?: string): Promise<FicheTache> {
  const { data } = await clientApi.post<FicheTache>("/maison/fiche-tache-ia", {
    nom_tache: nomTache,
    contexte,
  });
  return data;
}

/** Consulter un guide (lessive, travaux, etc.) */
export async function consulterGuide(params: {
  type_guide: string;
  tache?: string;
  tissu?: string;
  appareil?: string;
  probleme?: string;
}): Promise<Record<string, unknown>> {
  const { data } = await clientApi.get<Record<string, unknown>>("/maison/guide", { params });
  return data;
}

// ─── Planning ménage ────────────────────────────

export interface PlanningSemaine {
  lundi: FicheTache[];
  mardi: FicheTache[];
  mercredi: FicheTache[];
  jeudi: FicheTache[];
  vendredi: FicheTache[];
  samedi: FicheTache[];
  dimanche: FicheTache[];
}

/** Obtenir le planning ménage de la semaine */
export async function obtenirPlanningMenageSemaine(): Promise<PlanningSemaine> {
  const { data } = await clientApi.get<PlanningSemaine>("/maison/menage/planning-semaine");
  return data;
}

/** Initialiser les routines par défaut */
export async function initialiserRoutinesDefaut(): Promise<{ creees: number }> {
  const { data } = await clientApi.post<{ creees: number }>("/maison/routines/initialiser-defaut", {});
  return data;
}

export interface RoutineMaison {
  id: number;
  nom: string;
  description?: string;
  categorie?: string;
  frequence: string;
  actif: boolean;
  moment_journee?: string;
  taches_count?: number;
}

export async function listerRoutinesMaison(): Promise<RoutineMaison[]> {
  const { data } = await clientApi.get<{ items: RoutineMaison[] }>("/maison/routines");
  return data.items ?? [];
}

export async function creerRoutineMaison(
  payload: Omit<RoutineMaison, "id" | "taches_count">
): Promise<RoutineMaison> {
  const { data } = await clientApi.post<RoutineMaison>("/maison/routines", payload);
  return data;
}

export async function modifierRoutineMaison(
  id: number,
  payload: Partial<Omit<RoutineMaison, "id" | "taches_count">>
): Promise<RoutineMaison> {
  const { data } = await clientApi.patch<RoutineMaison>(`/maison/routines/${id}`, payload);
  return data;
}

export async function supprimerRoutineMaison(id: number): Promise<void> {
  await clientApi.delete(`/maison/routines/${id}`);
}

// ─── Domotique ────────────────────────────

export interface CategoriesDomotique {
  categories: {
    id: string;
    nom: string;
    icone: string;
    appareils: {
      id: string;
      nom: string;
      prix_estime: number;
      difficulte_installation: string;
      compatible_avec: string[];
      avantages: string[];
      cas_usage: string[];
    }[];
  }[];
  conseils_generaux: { titre: string; detail: string }[];
}

/** Catalogue domotique avec filtrage par catégorie */
export async function obtenirAstucesDomotique(categorie?: string): Promise<CategoriesDomotique> {
  const params = categorie ? { categorie } : undefined;
  const { data } = await clientApi.get<CategoriesDomotique>("/maison/domotique/astuces", { params });
  return data;
}

// ─── Assistant IA Maison ──────────────────────────────────

export interface ConseilIA {
  conseil?: string;
  message?: string;
  conseils?: string[];
  section: string;
}

/** Obtenir un conseil IA contextuel pour une section Maison */
export async function obtenirConseilIA(section: string): Promise<ConseilIA> {
  const { data } = await clientApi.get<ConseilIA>(`/maison/conseiller/conseil?section=${encodeURIComponent(section)}`);
  return data;
}

/** Obtenir les conseils structurés IA pour le hub Maison (cache 2h) */
export async function obtenirConseilsIA(): Promise<ConseilMaisonHub[]> {
  const { data } = await clientApi.get<{ items: ConseilMaisonHub[] }>("/maison/conseils-ia");
  return data.items ?? [];
}

// ─── Liens d'achat ─────────────────────────────────────────

export interface LienAchat {
  magasin: string;
  url: string;
}

export interface LiensAchatResult {
  produit: string;
  categorie: string;
  liens: LienAchat[];
  categories_disponibles: string[];
}

/** Obtenir des liens d'achat pour un produit selon sa catégorie */
export async function obtenirLiensAchat(produit: string, categorie = "default"): Promise<LiensAchatResult> {
  const { data } = await clientApi.get<LiensAchatResult>("/maison/liens-achat", { params: { produit, categorie } });
  return data;
}

// ─── Inventaire pièces avec objets ─────────────────────────

export interface ObjetInventaire {
  id: number;
  nom: string;
  categorie?: string;
  statut?: string;
  marque?: string;
  modele?: string;
  date_achat?: string;
  prix_achat?: number;
  prix_remplacement_estime?: number;
  notes?: string;
}

export interface PieceAvecObjets {
  piece: string;
  objets: ObjetInventaire[];
}

/** Lister les pièces avec leurs équipements/objets inventoriés */
export async function obtenirPiecesAvecObjets(piece?: string): Promise<{ pieces: PieceAvecObjets[]; total: number }> {
  const params = piece ? { piece } : undefined;
  const { data } = await clientApi.get<{ pieces: PieceAvecObjets[]; total: number }>("/maison/pieces-avec-objets", { params });
  return data;
}

/** Obtenir les suggestions de renouvellement (objets en fin de vie) */
export async function obtenirSuggestionsRenouvellement(): Promise<{ suggestions: ObjetInventaire[]; total: number }> {
  const { data } = await clientApi.get<{ suggestions: ObjetInventaire[]; total: number }>("/maison/suggestions-renouvellement");
  return data;
}

// ─── Fin de vie garantie ────────────────────────────────────

export interface FinVieGarantie {
  garantie_id: number;
  nom?: string;
  ratio: number;
  jours_restants: number | null;
  date_fin?: string;
  alerte?: boolean;
}

/** Évaluer la fin de vie d'une garantie (ratio 0.0 → 1.0) */
export async function evaluerFinVieGarantie(garantieId: number): Promise<FinVieGarantie> {
  const { data } = await clientApi.get<FinVieGarantie>(`/maison/garanties/${garantieId}/fin-vie`);
  return data;
}

// ─── Routines — extensions ─────────────────────────────────

export interface TacheRoutine {
  id: number;
  routine_id: number;
  routine_nom?: string;
  nom: string;
  description?: string;
  ordre?: number;
  heure_prevue?: string;
  fait_le?: string;
  notes?: string;
}

/** Lister toutes les tâches de toutes les routines */
export async function listerToutesLesTachesRoutines(): Promise<TacheRoutine[]> {
  const { data } = await clientApi.get<{ items: TacheRoutine[] }>("/maison/routines/taches");
  return data.items ?? [];
}

/** Lister les tâches d'une routine */
export async function listerTachesRoutine(routineId: number): Promise<TacheRoutine[]> {
  const { data } = await clientApi.get<{ items: TacheRoutine[] }>(`/maison/routines/${routineId}/taches`);
  return data.items ?? [];
}

/** Ajouter une tâche à une routine */
export async function ajouterTacheRoutine(routineId: number, nom: string, description?: string): Promise<TacheRoutine> {
  const { data } = await clientApi.post<TacheRoutine>(`/maison/routines/${routineId}/taches`, { nom, description });
  return data;
}

/** Supprimer une tâche d'une routine */
export async function supprimerTacheRoutine(routineId: number, tacheId: number): Promise<void> {
  await clientApi.delete(`/maison/routines/${routineId}/taches/${tacheId}`);
}

/** Dupliquer une routine existante */
export async function dupliquerRoutine(routineId: number): Promise<RoutineMaison> {
  const { data } = await clientApi.post<RoutineMaison>(`/maison/routines/${routineId}/dupliquer`, {});
  return data;
}

/** Créer une routine via l'IA */
export async function creerRoutineIA(nom: string, description?: string): Promise<RoutineMaison> {
  const { data } = await clientApi.post<RoutineMaison>("/maison/routines/creer-ia", { nom, description });
  return data;
}

/** Associer un objet/équipement à une tâche de routine */
export async function associerRoutineObjet(objetId: number, tacheRoutineId: number | null): Promise<{ id: number; nom: string; tache_routine_id: number | null }> {
  const { data } = await clientApi.patch(`/maison/objets/${objetId}/associer-routine`, { tache_routine_id: tacheRoutineId });
  return data;
}

/** Prioriser les projets via l'IA */
export async function prioriserProjetsIA(): Promise<{ priorites: Array<{ id: number; nom: string; statut: string; priorite: string }>; conseil: string }> {
  const { data } = await clientApi.get("/maison/projets/prioriser-ia");
  return data;
}

// ─── Tâches ponctuelles ───────────────────────────────────

/** Créer une tâche ménagère ponctuelle */
export async function creerTachePonctuelle(data: {
  nom: string;
  piece: string;
  quand: string;
}): Promise<{ id: number | null; nom: string; message: string }> {
  const { data: res } = await clientApi.post("/maison/taches-ponctuelles", data);
  return res;
}

// ─── Planning IA ──────────────────────────────────────────

/** Régénérer le planning ménage IA */
export async function regenererPlanningIA(forcer = false): Promise<PlanningSemaine> {
  const { data } = await clientApi.post<{ planning: PlanningSemaine }>("/maison/menage/planning-semaine-ia/regenerer", { forcer });
  return data.planning ?? (data as unknown as PlanningSemaine);
}

/** Compléter une tâche ménagère */
export async function completerTacheMenage(
  tacheId: number | string,
  heureCompletion?: string
): Promise<void> {
  await clientApi.post(`/maison/menage/taches/${tacheId}/completer`, {
    heure_completion: heureCompletion,
  });
}

// ─── Auto-complétion ──────────────────────────────────────

/** Suggestions de complétion de champ via IA */
export async function autoCompleterChamp(
  champ: string,
  valeur: string,
  contexte?: string
): Promise<{ suggestions: { categorie: string | null; description: string | null; tags: string[] } }> {
  const { data } = await clientApi.post("/maison/assistant/auto-completion", {
    champ_nom: champ,
    valeur_partielle: valeur,
    contexte_page: contexte ?? "general",
  });
  return data;
}