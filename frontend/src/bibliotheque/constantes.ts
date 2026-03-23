// ═══════════════════════════════════════════════════════════
// Constantes de l'application
// ═══════════════════════════════════════════════════════════

/** URL de base de l'API backend */
export const URL_API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** URL Supabase */
export const URL_SUPABASE = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";

/** Clé anonyme Supabase */
export const CLE_SUPABASE = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";

/** Préfixe des routes API */
export const PREFIXE_API = "/api/v1";

/** TTL du cache TanStack Query (5 minutes) */
export const DUREE_CACHE_MS = 5 * 60 * 1000;

/** Nombre d'éléments par page par défaut */
export const TAILLE_PAGE_DEFAUT = 20;

/** Navigation principale */
export const NAVIGATION = [
  { nom: "Accueil", chemin: "/", icone: "Home" },
  { nom: "Cuisine", chemin: "/cuisine", icone: "ChefHat" },
  { nom: "Famille", chemin: "/famille", icone: "Users" },
  { nom: "Planning", chemin: "/planning", icone: "Calendar" },
  { nom: "Maison", chemin: "/maison", icone: "House" },
  { nom: "Jeux", chemin: "/jeux", icone: "Gamepad2" },
  { nom: "Outils", chemin: "/outils", icone: "Wrench" },
  { nom: "Paramètres", chemin: "/parametres", icone: "Settings" },
] as const;

/** Navigation mobile (bottom bar) — 5 items max */
export const NAVIGATION_MOBILE = [
  { nom: "Accueil", chemin: "/", icone: "Home" },
  { nom: "Cuisine", chemin: "/cuisine", icone: "ChefHat" },
  { nom: "Famille", chemin: "/famille", icone: "Users" },
  { nom: "Maison", chemin: "/maison", icone: "House" },
  { nom: "Plus", chemin: "/outils", icone: "Menu" },
] as const;
