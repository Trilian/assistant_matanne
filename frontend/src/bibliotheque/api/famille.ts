// ═══════════════════════════════════════════════════════════
// API Famille
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
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
