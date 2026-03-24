// ═══════════════════════════════════════════════════════════════
// Types Outils
// ═══════════════════════════════════════════════════════════════

export interface Note {
  id: number;
  titre: string;
  contenu?: string;
  categorie: string;
  couleur?: string;
  epingle: boolean;
  est_checklist: boolean;
  items_checklist?: string;
  tags: string[];
  archive: boolean;
  cree_le?: string;
}

export interface NoteCreate {
  titre: string;
  contenu?: string;
  categorie?: string;
  couleur?: string;
  epingle?: boolean;
  est_checklist?: boolean;
  items_checklist?: string;
  tags?: string[];
}

export interface NotePatch {
  titre?: string;
  contenu?: string;
  categorie?: string;
  couleur?: string;
  epingle?: boolean;
  est_checklist?: boolean;
  items_checklist?: string;
  tags?: string[];
  archive?: boolean;
}

export interface MessageChat {
  role: "user" | "assistant";
  contenu: string;
  horodatage: string;
}

export interface Contact {
  id: number;
  nom: string;
  categorie: string;
  specialite?: string;
  telephone?: string;
  email?: string;
  adresse?: string;
  horaires?: string;
  favori: boolean;
  cree_le?: string;
}

export interface JournalEntree {
  id: number;
  date_entree: string;
  contenu: string;
  humeur?: string;
  energie?: number;
  gratitudes: string[];
  tags: string[];
  cree_le?: string;
}

export interface ReleveEnergie {
  id: number;
  type_energie: string;
  mois: number;
  annee: number;
  consommation: number;
  cout?: number;
  notes?: string;
  cree_le?: string;
}
