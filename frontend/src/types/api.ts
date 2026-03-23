// ═══════════════════════════════════════════════════════════
// Types API génériques
// ═══════════════════════════════════════════════════════════

/** Réponse paginée standard du backend */
export interface ReponsePaginee<T> {
  items: T[];
  total: number;
  page: number;
  taille_page: number;
  pages_totales: number;
}

/** Réponse d'erreur API */
export interface ErreurAPI {
  detail: string;
  status_code?: number;
}

/** Token JWT retourné par le login */
export interface ReponseToken {
  access_token: string;
  token_type: string;
  expires_in: number;
}

/** Utilisateur authentifié */
export interface Utilisateur {
  id: string;
  email: string;
  nom: string;
  role: string;
  avatar_url?: string;
}

/** Réponse santé API */
export interface ReponseSante {
  status: string;
  version: string;
  timestamp: string;
  uptime_seconds: number;
}
