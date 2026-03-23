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
