// ═══════════════════════════════════════════════════════════
// Types communs frontend
// ═══════════════════════════════════════════════════════════

export type ValeurDonnee =
  | string
  | number
  | boolean
  | null
  | undefined
  | Date
  | File
  | Blob
  | ValeurDonnee[]
  | { [cle: string]: ValeurDonnee }

export type ObjetDonnees = { [cle: string]: ValeurDonnee }
export type ListeObjetsDonnees = ObjetDonnees[]
