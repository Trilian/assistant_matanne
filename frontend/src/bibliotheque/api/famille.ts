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
