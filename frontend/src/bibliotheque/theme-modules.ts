export type ModuleThemeKey =
  | "principal"
  | "cuisine"
  | "famille"
  | "maison"
  | "habitat"
  | "jeux"
  | "outils"
  | "planning"
  | "ia"
  | "parametres"
  | "admin";

const META_MODULE: Record<ModuleThemeKey, { label: string; emoji: string }> = {
  principal: { label: "Accueil", emoji: "🏠" },
  cuisine: { label: "Cuisine", emoji: "🍽️" },
  famille: { label: "Famille", emoji: "👨‍👩‍👦" },
  maison: { label: "Maison", emoji: "🏡" },
  habitat: { label: "Vision Maison", emoji: "🗺️" },
  jeux: { label: "Jeux", emoji: "🎯" },
  outils: { label: "Outils", emoji: "🛠️" },
  planning: { label: "Planning", emoji: "📅" },
  ia: { label: "IA avancée", emoji: "✨" },
  parametres: { label: "Paramètres", emoji: "⚙️" },
  admin: { label: "Admin", emoji: "🔐" },
};

const PREFIXES_MODULE: Array<{ prefix: string; module: ModuleThemeKey }> = [
  { prefix: "/cuisine", module: "cuisine" },
  { prefix: "/famille", module: "famille" },
  { prefix: "/maison", module: "maison" },
  { prefix: "/vision-maison", module: "habitat" },
  { prefix: "/jeux", module: "jeux" },
  { prefix: "/outils", module: "outils" },
  { prefix: "/planning", module: "planning" },
  { prefix: "/ia-avancee", module: "ia" },
  { prefix: "/parametres", module: "parametres" },
  { prefix: "/admin", module: "admin" },
  { prefix: "/ma-semaine", module: "planning" },
  { prefix: "/ma-journee", module: "planning" },
  { prefix: "/focus", module: "planning" },
];

export function obtenirModuleDepuisPathname(pathname: string): ModuleThemeKey {
  const match = PREFIXES_MODULE.find((item) => pathname.startsWith(item.prefix));
  return match?.module ?? "principal";
}

export function getAccentVarName(moduleKey: ModuleThemeKey): string {
  return `--${moduleKey}`;
}

export function getModuleThemeClass(moduleKey: ModuleThemeKey): string {
  return `module-theme-${moduleKey}`;
}

export function obtenirMetaModule(moduleKey: ModuleThemeKey): { label: string; emoji: string } {
  return META_MODULE[moduleKey] ?? META_MODULE.principal;
}
