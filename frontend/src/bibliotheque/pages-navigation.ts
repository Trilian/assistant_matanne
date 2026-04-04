// ═══════════════════════════════════════════════════════════
// Pages Navigation — Source unique de toutes les pages de l'app
// Utilisé par : MenuCommandes (Ctrl+K), BoutonEpingler (étoile),
//              BarreLaterale (section Récents)
// ═══════════════════════════════════════════════════════════

import type { ElementType } from "react";
import {
  Home,
  ChefHat,
  Users,
  House,
  Gamepad2,
  Wrench,
  BookOpen,
  CalendarDays,
  ShoppingCart,
  Package,
  CookingPot,
  Leaf,
  Baby,
  ClipboardList,
  RotateCw,
  Wallet,
  Hammer,
  Sprout,
  SprayCan,
  Receipt,
  Banknote,
  Zap,
  Wine,
  FileText,
  ClipboardCheck,
  Trophy,
  Dices,
  TrendingUp,
  MessageSquare,
  ArrowLeftRight,
  CloudSun,
  Timer,
  Mic,
  StickyNote,
  Cake,
  Contact,
  Layers,
  Camera,
  Apple,
  ShoppingBag,
  CalendarCheck,
  Wifi,
  CalendarRange,
  Settings,
  Map,
  Sparkles,
  MapPin,
  Scale,
} from "lucide-react";

export interface PageNavigation {
  nom: string;
  chemin: string;
  categorie: string;
  Icone: ElementType;
  keywords?: string[];
}

export const PAGES_NAVIGATION: PageNavigation[] = [
  // Principal
  { nom: "Accueil", chemin: "/", categorie: "Principal", Icone: Home },
  { nom: "Focus", chemin: "/focus", categorie: "Principal", Icone: Zap, keywords: ["essentiel", "jour", "rappels", "meteo"] },
  { nom: "Ma Semaine", chemin: "/ma-semaine", categorie: "Principal", Icone: CalendarCheck, keywords: ["semaine", "planning", "vue globale", "repas", "activites", "matchs"] },

  // Cuisine
  { nom: "Cuisine", chemin: "/cuisine", categorie: "Cuisine", Icone: ChefHat },
  { nom: "Recettes", chemin: "/cuisine/recettes", categorie: "Cuisine", Icone: BookOpen, keywords: ["plats", "repas"] },
  { nom: "Planning Repas", chemin: "/cuisine/planning", categorie: "Cuisine", Icone: CalendarDays, keywords: ["semaine", "menu"] },
  { nom: "Ma Semaine", chemin: "/cuisine/ma-semaine", categorie: "Cuisine", Icone: CalendarCheck, keywords: ["planning", "hebdo"] },
  { nom: "Courses", chemin: "/cuisine/courses", categorie: "Cuisine", Icone: ShoppingCart, keywords: ["achats", "liste"] },
  { nom: "Inventaire", chemin: "/cuisine/inventaire", categorie: "Cuisine", Icone: Package, keywords: ["stock", "frigo"] },
  { nom: "Batch Cooking", chemin: "/cuisine/batch-cooking", categorie: "Cuisine", Icone: CookingPot, keywords: ["preparation", "avance"] },
  { nom: "Anti-Gaspillage", chemin: "/cuisine/anti-gaspillage", categorie: "Cuisine", Icone: Leaf, keywords: ["restes", "eco"] },
  { nom: "Photo Frigo", chemin: "/cuisine/photo-frigo", categorie: "Cuisine", Icone: Camera, keywords: ["scan"] },

  // Famille
  { nom: "Famille", chemin: "/famille", categorie: "Famille", Icone: Users },
  { nom: "Jules", chemin: "/famille/jules", categorie: "Famille", Icone: Baby, keywords: ["enfant", "bebe", "developpement"] },
  { nom: "Activités", chemin: "/famille/activites", categorie: "Famille", Icone: ClipboardList, keywords: ["sortie", "loisirs"] },
  { nom: "Routines", chemin: "/famille/routines", categorie: "Famille", Icone: RotateCw, keywords: ["habitudes", "quotidien"] },
  { nom: "Budget Famille", chemin: "/famille/budget", categorie: "Famille", Icone: Wallet, keywords: ["argent", "finances"] },
  { nom: "Weekend", chemin: "/famille/weekend", categorie: "Famille", Icone: CalendarDays, keywords: ["sortie", "we"] },
  { nom: "Anniversaires", chemin: "/famille/anniversaires", categorie: "Famille", Icone: Cake, keywords: ["fetes", "dates"] },
  { nom: "Contacts", chemin: "/famille/contacts", categorie: "Famille", Icone: Contact, keywords: ["annuaire", "telephone"] },
  { nom: "Journal", chemin: "/famille/journal", categorie: "Famille", Icone: BookOpen, keywords: ["memoires", "notes"] },
  { nom: "Documents", chemin: "/famille/documents", categorie: "Famille", Icone: FileText, keywords: ["fichiers", "papiers"] },
  { nom: "Calendriers", chemin: "/famille/calendriers", categorie: "Famille", Icone: CalendarDays, keywords: ["google", "ical", "sync", "agenda"] },

  // Maison - Gestion
  { nom: "Maison", chemin: "/maison", categorie: "Maison", Icone: House },
  { nom: "Habitat", chemin: "/habitat", categorie: "Habitat", Icone: Map, keywords: ["logement", "immo", "deco", "jardin"] },
  { nom: "Scenarios Habitat", chemin: "/habitat/scenarios", categorie: "Habitat", Icone: Home, keywords: ["comparaison", "decision"] },
  { nom: "Veille Immo", chemin: "/habitat/veille-immo", categorie: "Habitat", Icone: ShoppingBag, keywords: ["annonces", "immobilier"] },
  { nom: "Marche Habitat", chemin: "/habitat/marche", categorie: "Habitat", Icone: TrendingUp, keywords: ["dvf", "prix", "transactions"] },
  { nom: "Plans Habitat", chemin: "/habitat/plans", categorie: "Habitat", Icone: Layers, keywords: ["plans", "pieces", "architecture"] },
  { nom: "Deco Habitat", chemin: "/habitat/deco", categorie: "Habitat", Icone: House, keywords: ["interieur", "meubles", "style"] },
  { nom: "Jardin Habitat", chemin: "/habitat/jardin", categorie: "Habitat", Icone: Sprout, keywords: ["paysagisme", "zones", "terrain"] },
  { nom: "Projets Maison", chemin: "/maison/projets", categorie: "Maison - Gestion", Icone: Hammer, keywords: ["travaux", "renovation"] },
  { nom: "Ménage", chemin: "/maison/menage", categorie: "Maison - Entretien", Icone: SprayCan, keywords: ["nettoyage", "proprete"] },
  { nom: "Jardin", chemin: "/maison/jardin", categorie: "Maison - Jardin", Icone: Sprout, keywords: ["plantes", "potager"] },
  { nom: "Entretien", chemin: "/maison/entretien", categorie: "Maison - Entretien", Icone: SprayCan, keywords: ["maintenance", "reparation"] },
  { nom: "Domotique", chemin: "/maison/domotique", categorie: "Maison - Tech", Icone: Wifi, keywords: ["smart", "connecte"] },
  { nom: "Charges", chemin: "/maison/charges", categorie: "Maison - Finances", Icone: Receipt, keywords: ["factures", "mensuel"] },
  { nom: "Dépenses", chemin: "/maison/depenses", categorie: "Maison - Finances", Icone: Banknote, keywords: ["budget", "argent"] },
  { nom: "Énergie", chemin: "/maison/energie", categorie: "Maison - Finances", Icone: Zap, keywords: ["electricite", "consommation"] },
  { nom: "Stocks", chemin: "/maison/stocks", categorie: "Maison - Stocks", Icone: Package, keywords: ["reserve", "cave"] },
  { nom: "Cellier", chemin: "/maison/cellier", categorie: "Maison - Stocks", Icone: Wine, keywords: ["vin", "bouteilles"] },
  { nom: "Artisans", chemin: "/maison/artisans", categorie: "Maison - Admin", Icone: Wrench, keywords: ["contacts", "pro"] },
  { nom: "Diagnostics", chemin: "/maison/diagnostics", categorie: "Maison - Admin", Icone: ClipboardCheck, keywords: ["dpe", "controle"] },
  { nom: "Visualisation Maison", chemin: "/maison/visualisation", categorie: "Maison - Vue", Icone: Layers, keywords: ["plan", "vue"] },
  { nom: "Éco-Tips", chemin: "/maison/eco-tips", categorie: "Maison - Écologie", Icone: Leaf, keywords: ["economie", "energie"] },

  // Jeux
  { nom: "Jeux", chemin: "/jeux", categorie: "Jeux", Icone: Gamepad2 },
  { nom: "Paris Sportifs", chemin: "/jeux/paris", categorie: "Jeux", Icone: Trophy, keywords: ["pari", "sport"] },
  { nom: "Loto", chemin: "/jeux/loto", categorie: "Jeux", Icone: Dices, keywords: ["tirage", "fdj"] },
  { nom: "EuroMillions", chemin: "/jeux/euromillions", categorie: "Jeux", Icone: Dices, keywords: ["euro", "tirage"] },
  { nom: "Bankroll", chemin: "/jeux/bankroll", categorie: "Jeux", Icone: TrendingUp, keywords: ["capital", "mise", "kelly"] },
  { nom: "Performance Jeux", chemin: "/jeux/performance", categorie: "Jeux", Icone: TrendingUp, keywords: ["stats", "resultats"] },

  // Outils
  { nom: "Outils", chemin: "/outils", categorie: "Outils", Icone: Wrench },
  { nom: "Chat IA", chemin: "/outils/chat-ia", categorie: "Outils", Icone: MessageSquare, keywords: ["assistant", "question"] },
  { nom: "Assistant vocal", chemin: "/outils/assistant-vocal", categorie: "Outils", Icone: Mic, keywords: ["micro", "voix", "commande"] },
  { nom: "Google Assistant", chemin: "/outils/google-assistant", categorie: "Outils", Icone: Sparkles, keywords: ["intents", "actions", "fulfillment", "google"] },
  { nom: "Convertisseur", chemin: "/outils/convertisseur", categorie: "Outils", Icone: ArrowLeftRight, keywords: ["unite", "mesure"] },
  { nom: "Météo", chemin: "/outils/meteo", categorie: "Outils", Icone: CloudSun, keywords: ["previsions", "temps"] },
  { nom: "Minuteur", chemin: "/outils/minuteur", categorie: "Outils", Icone: Timer, keywords: ["chrono", "cuisson"] },
  { nom: "Notes", chemin: "/outils/notes", categorie: "Outils", Icone: StickyNote, keywords: ["memo", "pense-bete"] },
  { nom: "Nutritionniste", chemin: "/outils/nutritionniste", categorie: "Outils", Icone: Apple, keywords: ["sante", "calories"] },

  // Configuration
  { nom: "Paramètres", chemin: "/parametres", categorie: "Configuration", Icone: Settings },
  { nom: "Planning", chemin: "/planning", categorie: "Configuration", Icone: CalendarRange },

  // IA Avancée
  { nom: "IA Avancée", chemin: "/ia-avancee", categorie: "IA", Icone: Sparkles, keywords: ["intelligence artificielle", "suggestions", "optimisation", "ai"] },
  { nom: "Suggestions Achats", chemin: "/ia-avancee/suggestions-achats", categorie: "IA", Icone: ShoppingCart, keywords: ["shopping", "liste", "courses"] },
  { nom: "Planning Adaptatif", chemin: "/ia-avancee/planning-adaptatif", categorie: "IA", Icone: CalendarDays, keywords: ["repas", "menu", "semaine"] },
  { nom: "Diagnostic Plantes", chemin: "/ia-avancee/diagnostic-plante", categorie: "IA", Icone: Sprout, keywords: ["jardin", "sante", "plante"] },
  { nom: "Prévision Dépenses", chemin: "/ia-avancee/prevision-depenses", categorie: "IA", Icone: TrendingUp, keywords: ["budget", "fin de mois", "prevision"] },
  { nom: "Suggestions Cadeaux", chemin: "/ia-avancee/idees-cadeaux", categorie: "IA", Icone: Cake, keywords: ["noel", "anniversaire", "present"] },
  { nom: "Analyse Photos", chemin: "/ia-avancee/analyse-photo", categorie: "IA", Icone: Camera, keywords: ["photo", "analyse", "contexte"] },
  { nom: "Optimisation Routines", chemin: "/ia-avancee/optimisation-routines", categorie: "IA", Icone: RotateCw, keywords: ["temps", "efficacite", "habitudes"] },
  { nom: "Analyse Documents", chemin: "/ia-avancee/analyse-document", categorie: "IA", Icone: FileText, keywords: ["document", "classement", "contrat"] },
  { nom: "Estimation Travaux", chemin: "/ia-avancee/estimation-travaux", categorie: "IA", Icone: Hammer, keywords: ["bricolage", "reparation", "cout"] },
  { nom: "Planning Voyage", chemin: "/ia-avancee/planning-voyage", categorie: "IA", Icone: MapPin, keywords: ["vacances", "destination", "itineraire"] },
  { nom: "Économies Énergie", chemin: "/ia-avancee/recommandations-energie", categorie: "IA", Icone: Zap, keywords: ["conso", "electricite", "eco"] },
  { nom: "Prédiction Pannes", chemin: "/ia-avancee/prediction-pannes", categorie: "IA", Icone: Wrench, keywords: ["maintenance", "prevention", "repair"] },
  { nom: "Suggestions Proactives", chemin: "/ia-avancee/suggestions-proactives", categorie: "IA", Icone: Sparkles, keywords: ["alertes", "actions", "contexte"] },
  { nom: "Adaptation Météo", chemin: "/ia-avancee/adaptations-meteo", categorie: "IA", Icone: CloudSun, keywords: ["previsions", "planning", "meteorologie"] },
  { nom: "Comparateur Recettes", chemin: "/ia-avancee/comparateur-recettes", categorie: "IA", Icone: Scale, keywords: ["nutrition", "calories", "macros", "comparaison"] },
];

/** Map chemin → nom lisible — dérivée automatiquement de PAGES_NAVIGATION */
export const NOMS_PAGES: Record<string, string> = Object.fromEntries(
  PAGES_NAVIGATION.map((p) => [p.chemin, p.nom])
);
