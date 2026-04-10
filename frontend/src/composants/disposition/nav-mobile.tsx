// ═══════════════════════════════════════════════════════════
// Navigation mobile — Bottom bar (4 onglets + drawer « Plus »)
// Fix 5 : accès Jeux, Outils, Paramètres depuis un drawer
// Idée A : badge alerte rouge sur Famille si rappels urgents
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Home,
  ChefHat,
  Users,
  House,
  MoreHorizontal,
  CalendarRange,
  Gamepad2,
  Wrench,
  Settings,
  Map,
  Sparkles,
} from "lucide-react";
import { cn } from "@/bibliotheque/utils";
import { utiliserBadgesModules } from "@/crochets/utiliser-badges-modules";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/composants/ui/sheet";
import { Badge } from "@/composants/ui/badge";
import { getModuleThemeClass, obtenirModuleDepuisPathname } from "@/bibliotheque/theme-modules";

// 4 onglets principaux
const ITEMS = [
  { nom: "Accueil", chemin: "/", Icone: Home },
  { nom: "Cuisine", chemin: "/cuisine", Icone: ChefHat },
  { nom: "Famille", chemin: "/famille", Icone: Users },
  { nom: "Maison", chemin: "/maison", Icone: House },
] as const;

// Contenu du drawer « Plus »
const PLUS_ITEMS = [
  { nom: "Ma Semaine", chemin: "/ma-semaine", Icone: CalendarRange },
  { nom: "Vision Maison", chemin: "/vision-maison", Icone: Map },
  { nom: "Jeux", chemin: "/jeux", Icone: Gamepad2 },
  { nom: "IA Avancée", chemin: "/ia-avancee", Icone: Sparkles },
  { nom: "Outils", chemin: "/outils", Icone: Wrench },
  { nom: "Paramètres", chemin: "/parametres", Icone: Settings },
] as const;

/** Routes couvertes par l'onglet « Plus » */
const PLUS_PREFIXES = ["/ma-semaine", "/vision-maison", "/jeux", "/ia-avancee", "/outils", "/parametres"];

/**
 * Bottom navigation bar mobile — visible uniquement sur petits écrans (< md).
 * 4 onglets directs + 1 onglet « Plus » qui ouvre un drawer avec le reste.
 */
export function NavMobile() {
  const pathname = usePathname();
  const router = useRouter();
  const [plusOuvert, setPlusOuvert] = useState(false);

  const { badges, badgePlus } = utiliserBadgesModules();

  const estSurPlus = PLUS_PREFIXES.some((p) => pathname.startsWith(p));
  const obtenirBadgeNavigation = (chemin: string) => {
    if (chemin === "/cuisine") return badges.cuisine;
    if (chemin === "/famille") return badges.famille;
    if (chemin === "/maison") return badges.maison;
    if (chemin === "/jeux") return badges.jeux;
    return 0;
  };
  const formaterBadge = (valeur: number) => (valeur > 9 ? "9+" : String(valeur));

  useEffect(() => {
    if (!plusOuvert) return;
    for (const item of PLUS_ITEMS) {
      router.prefetch(item.chemin);
    }
  }, [plusOuvert, router]);

  return (
    <>
      <nav
        aria-label="Navigation mobile"
        className="fixed bottom-0 left-0 right-0 z-50 flex md:hidden border-t bg-background"
      >
        {ITEMS.map(({ nom, chemin, Icone }) => {
          const estActif =
            chemin === "/" ? pathname === "/" : pathname.startsWith(chemin);
          const badgeCount = obtenirBadgeNavigation(chemin);
          const showBadge = badgeCount > 0;

          return (
            <Link
              key={chemin}
              href={chemin}
              onMouseEnter={() => router.prefetch(chemin)}
              onTouchStart={() => router.prefetch(chemin)}
              aria-label={nom}
              aria-current={estActif ? "page" : undefined}
              className={cn(
                "relative flex flex-1 flex-col items-center gap-1 py-2 text-xs transition-colors",
                getModuleThemeClass(obtenirModuleDepuisPathname(chemin)),
                estActif
                  ? "module-accent-text"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <span className="relative">
                <Icone
                  className={cn(
                    "h-5 w-5 transition-transform duration-200",
                    estActif ? "scale-110" : "scale-100"
                  )}
                />
                {showBadge && (
                  <span className="absolute -top-2 -right-2 inline-flex min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[9px] font-semibold text-destructive-foreground">
                    {formaterBadge(badgeCount)}
                  </span>
                )}
              </span>
              <span>{nom}</span>
              {estActif && (
                <span className="absolute bottom-0 h-0.5 w-8 rounded-full module-top-strip animate-in fade-in zoom-in-50" />
              )}
            </Link>
          );
        })}

        {/* Onglet Plus — ouvre le drawer */}
        <button
          onClick={() => setPlusOuvert(true)}
          aria-label="Plus de sections"
          className={cn(
            "relative flex flex-1 flex-col items-center gap-1 py-2 text-xs transition-colors",
            getModuleThemeClass(obtenirModuleDepuisPathname(pathname)),
            estSurPlus ? "module-accent-text" : "text-muted-foreground hover:text-foreground"
          )}
        >
          <span className="relative">
            <MoreHorizontal className="h-5 w-5" />
            {badgePlus > 0 && (
              <span className="absolute -top-2 -right-2 inline-flex min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[9px] font-semibold text-destructive-foreground">
                {formaterBadge(badgePlus)}
              </span>
            )}
          </span>
          <span>Plus</span>
        </button>
      </nav>

      {/* Drawer « Plus » — glisse depuis le bas */}
      <Sheet open={plusOuvert} onOpenChange={setPlusOuvert}>
        <SheetContent side="bottom" className="h-auto rounded-t-2xl pb-8 md:hidden">
          <SheetHeader className="mb-5">
            <SheetTitle className="text-base font-semibold">Navigation</SheetTitle>
            <SheetDescription>
              Accès rapide aux sections secondaires avec leurs badges d'attention.
            </SheetDescription>
          </SheetHeader>
          <div className="grid grid-cols-2 gap-3">
            {PLUS_ITEMS.map(({ nom, chemin, Icone }) => {
              const estActif = pathname.startsWith(chemin);
              const badgeCount = obtenirBadgeNavigation(chemin);
              return (
                <button
                  key={chemin}
                  onMouseEnter={() => router.prefetch(chemin)}
                  onClick={() => {
                    router.push(chemin);
                    setPlusOuvert(false);
                  }}
                  className={cn(
                    "flex flex-col items-center gap-3 rounded-xl border p-5 text-sm font-medium transition-colors",
                    estActif
                      ? "bg-primary text-primary-foreground border-primary"
                      : "hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <div className="relative">
                    <Icone className="h-7 w-7" />
                    {badgeCount > 0 && (
                      <Badge variant="destructive" className="absolute -right-5 -top-3 h-5 min-w-5 px-1 text-[10px]">
                        {formaterBadge(badgeCount)}
                      </Badge>
                    )}
                  </div>
                  {nom}
                </button>
              );
            })}
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
