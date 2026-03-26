// ═══════════════════════════════════════════════════════════
// Navigation mobile — Bottom bar (4 onglets + drawer « Plus »)
// Fix 5 : accès Jeux, Outils, Paramètres depuis un drawer
// Idée A : badge alerte rouge sur Famille si rappels urgents
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
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
} from "lucide-react";
import { cn } from "@/bibliotheque/utils";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { evaluerRappelsFamille } from "@/bibliotheque/api/famille";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/composants/ui/sheet";
import type { RappelFamille } from "@/types/famille";

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
  { nom: "Jeux", chemin: "/jeux", Icone: Gamepad2 },
  { nom: "Outils", chemin: "/outils", Icone: Wrench },
  { nom: "Paramètres", chemin: "/parametres", Icone: Settings },
] as const;

/** Routes couvertes par l'onglet « Plus » */
const PLUS_PREFIXES = ["/ma-semaine", "/jeux", "/outils", "/parametres"];

/**
 * Bottom navigation bar mobile — visible uniquement sur petits écrans (< md).
 * 4 onglets directs + 1 onglet « Plus » qui ouvre un drawer avec le reste.
 */
export function NavMobile() {
  const pathname = usePathname();
  const router = useRouter();
  const [plusOuvert, setPlusOuvert] = useState(false);

  const { data: rappelsData } = utiliserRequete<{ rappels: RappelFamille[]; total: number }>(
    ["famille", "rappels", "badge"],
    evaluerRappelsFamille,
    { staleTime: 5 * 60 * 1000, refetchInterval: 10 * 60 * 1000 }
  );
  const nbRappelsDanger = rappelsData?.rappels?.filter((r) => r.priorite === "danger").length ?? 0;

  const estSurPlus = PLUS_PREFIXES.some((p) => pathname.startsWith(p));

  return (
    <>
      <nav
        aria-label="Navigation mobile"
        className="fixed bottom-0 left-0 right-0 z-50 flex md:hidden border-t bg-background"
      >
        {ITEMS.map(({ nom, chemin, Icone }) => {
          const estActif =
            chemin === "/" ? pathname === "/" : pathname.startsWith(chemin);
          const showBadge = chemin === "/famille" && nbRappelsDanger > 0;

          return (
            <Link
              key={chemin}
              href={chemin}
              aria-label={nom}
              aria-current={estActif ? "page" : undefined}
              className={cn(
                "flex flex-1 flex-col items-center gap-1 py-2 text-xs transition-colors",
                estActif
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <span className="relative">
                <Icone className="h-5 w-5" />
                {showBadge && (
                  <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-destructive border-2 border-background" />
                )}
              </span>
              <span>{nom}</span>
            </Link>
          );
        })}

        {/* Onglet Plus — ouvre le drawer */}
        <button
          onClick={() => setPlusOuvert(true)}
          aria-label="Plus de sections"
          className={cn(
            "flex flex-1 flex-col items-center gap-1 py-2 text-xs transition-colors",
            estSurPlus ? "text-primary" : "text-muted-foreground hover:text-foreground"
          )}
        >
          <MoreHorizontal className="h-5 w-5" />
          <span>Plus</span>
        </button>
      </nav>

      {/* Drawer « Plus » — glisse depuis le bas */}
      <Sheet open={plusOuvert} onOpenChange={setPlusOuvert}>
        <SheetContent side="bottom" className="h-auto rounded-t-2xl pb-8 md:hidden">
          <SheetHeader className="mb-5">
            <SheetTitle className="text-base font-semibold">Navigation</SheetTitle>
          </SheetHeader>
          <div className="grid grid-cols-2 gap-3">
            {PLUS_ITEMS.map(({ nom, chemin, Icone }) => {
              const estActif =
                chemin === "/" ? pathname === "/" : pathname.startsWith(chemin);
              return (
                <button
                  key={chemin}
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
                  <Icone className="h-7 w-7" />
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
