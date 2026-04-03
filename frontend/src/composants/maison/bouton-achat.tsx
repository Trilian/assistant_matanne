// Bouton d'achat avec URL directe (variante maison)
// Utilisé pour les meubles, projets et équipements avec liens spécifiques.

"use client";

import { ExternalLink, ShoppingCart } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { cn } from "@/bibliotheque/utils";

interface BoutonAchatMaisonProps {
  url: string;
  label?: string;
  size?: "sm" | "xs";
  className?: string;
}

export function BoutonAchat({ url, label, size = "sm", className }: BoutonAchatMaisonProps) {
  const isXs = size === "xs";
  return (
    <Button
      variant="ghost"
      size={isXs ? "icon" : "sm"}
      className={cn(isXs ? "h-6 w-6" : "h-7 px-2 gap-1", className)}
      asChild
    >
      <a href={url} target="_blank" rel="noopener noreferrer">
        <ShoppingCart className={cn("shrink-0", isXs ? "h-3 w-3" : "h-3.5 w-3.5")} />
        {!isXs && (
          <>
            <span className="text-xs">{label ?? "Voir"}</span>
            <ExternalLink className="h-3 w-3 opacity-60" />
          </>
        )}
      </a>
    </Button>
  );
}
