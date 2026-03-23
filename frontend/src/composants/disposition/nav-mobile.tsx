// ═══════════════════════════════════════════════════════════
// Navigation mobile — Bottom bar (5 icônes)
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, ChefHat, Users, House, Menu } from "lucide-react";
import { cn } from "@/lib/utils";

const ITEMS = [
  { nom: "Accueil", chemin: "/", Icone: Home },
  { nom: "Cuisine", chemin: "/cuisine", Icone: ChefHat },
  { nom: "Famille", chemin: "/famille", Icone: Users },
  { nom: "Maison", chemin: "/maison", Icone: House },
  { nom: "Plus", chemin: "/outils", Icone: Menu },
] as const;

export function NavMobile() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 flex md:hidden border-t bg-background">
      {ITEMS.map(({ nom, chemin, Icone }) => {
        const estActif =
          chemin === "/" ? pathname === "/" : pathname.startsWith(chemin);

        return (
          <Link
            key={chemin}
            href={chemin}
            className={cn(
              "flex flex-1 flex-col items-center gap-1 py-2 text-xs transition-colors",
              estActif
                ? "text-primary"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Icone className="h-5 w-5" />
            <span>{nom}</span>
          </Link>
        );
      })}
    </nav>
  );
}
