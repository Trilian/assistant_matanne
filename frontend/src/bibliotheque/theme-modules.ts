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

const PREFIXES_MODULE: Array<{ prefix: string; module: ModuleThemeKey }> = [
  { prefix: "/cuisine", module: "cuisine" },
  { prefix: "/famille", module: "famille" },
  { prefix: "/maison", module: "maison" },
  { prefix: "/habitat", module: "habitat" },
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
