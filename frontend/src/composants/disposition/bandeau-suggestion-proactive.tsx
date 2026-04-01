"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Lightbulb, ArrowRight } from "lucide-react";
import { Button } from "@/composants/ui/button";

interface SuggestionModule {
  match: (pathname: string) => boolean;
  titre: string;
  message: string;
  lien: string;
}

const SUGGESTIONS: SuggestionModule[] = [
  {
    match: (p) => p.startsWith("/cuisine"),
    titre: "Suggestion IA Cuisine",
    message: "Stock bas détecté: générer automatiquement une liste de courses optimisée.",
    lien: "/cuisine/courses",
  },
  {
    match: (p) => p.startsWith("/famille"),
    titre: "Suggestion IA Famille",
    message: "2 activités adaptées à Jules sont disponibles pour aujourd'hui.",
    lien: "/famille/jules",
  },
  {
    match: (p) => p.startsWith("/maison"),
    titre: "Suggestion IA Maison",
    message: "Planifier 1 tâche d'entretien préventif pour éviter un retard cette semaine.",
    lien: "/maison/finances",
  },
  {
    match: (p) => p.startsWith("/jeux"),
    titre: "Suggestion IA Jeux",
    message: "Une opportunité value bet est détectée avec un risque modéré.",
    lien: "/jeux/performance",
  },
  {
    match: (p) => p === "/" || p.startsWith("/planning"),
    titre: "Suggestion IA Planning",
    message: "Automatiser le planning de la semaine et générer les courses en 1 clic.",
    lien: "/cuisine/ma-semaine",
  },
];

export function BandeauSuggestionProactive() {
  const pathname = usePathname();
  const suggestion = SUGGESTIONS.find((s) => s.match(pathname));

  if (!suggestion) return null;

  return (
    <div className="mx-4 md:mx-6 mt-2 rounded-lg border border-amber-300/60 bg-amber-50/70 dark:border-amber-900/40 dark:bg-amber-950/20 px-3 py-2">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-semibold flex items-center gap-1.5">
            <Lightbulb className="h-4 w-4 text-amber-500" />
            {suggestion.titre}
          </p>
          <p className="text-xs text-muted-foreground mt-0.5">{suggestion.message}</p>
        </div>
        <Button variant="ghost" size="sm" asChild className="shrink-0 h-7 px-2">
          <Link href={suggestion.lien} className="flex items-center gap-1 text-xs">
            Voir
            <ArrowRight className="h-3 w-3" />
          </Link>
        </Button>
      </div>
    </div>
  );
}
