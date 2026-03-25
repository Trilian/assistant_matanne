// ═══════════════════════════════════════════════════════════
// Carte Alerte Maison — affichage contextuel
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import { AlertTriangle, Info, AlertCircle } from "lucide-react";
import { Badge } from "@/composants/ui/badge";
import type { AlerteMaison } from "@/types/maison";

interface CarteAlerteProps {
  alerte: AlerteMaison;
}

function niveauBadge(niveau: string) {
  const variant =
    niveau === "CRITIQUE" || niveau === "HAUTE"
      ? ("destructive" as const)
      : niveau === "MOYENNE"
        ? ("secondary" as const)
        : ("outline" as const);
  return <Badge variant={variant} className="text-xs">{niveau}</Badge>;
}

function NiveauIcone({ niveau }: { niveau: string }) {
  if (niveau === "CRITIQUE" || niveau === "HAUTE") {
    return <AlertCircle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />;
  }
  if (niveau === "MOYENNE") {
    return <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />;
  }
  return <Info className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />;
}

export function CarteAlerte({ alerte }: CarteAlerteProps) {
  const inner = (
    <div className="flex items-start gap-2 py-2">
      <NiveauIcone niveau={alerte.niveau} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium leading-tight">{alerte.titre}</p>
        <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{alerte.message}</p>
        {alerte.date_echeance && (
          <p className="text-xs text-muted-foreground">
            Échéance : {new Date(alerte.date_echeance).toLocaleDateString("fr-FR")}
          </p>
        )}
      </div>
      {niveauBadge(alerte.niveau)}
    </div>
  );

  if (alerte.action_url) {
    return (
      <Link href={alerte.action_url} className="block hover:bg-accent/30 rounded px-1 transition-colors">
        {inner}
      </Link>
    );
  }
  return <div className="px-1">{inner}</div>;
}
