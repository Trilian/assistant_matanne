"use client";

import { Mic, MicOff } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { utiliserReconnaissanceVocale } from "@/crochets/utiliser-reconnaissance-vocale";
import { cn } from "@/bibliotheque/utils";

interface BoutonVocalProps {
  onResultat: (texte: string) => void;
  placeholder?: string;
  className?: string;
  variante?: "default" | "outline" | "ghost";
  taille?: "default" | "sm" | "lg" | "icon";
}

export function BoutonVocal({
  onResultat,
  placeholder = "Parlez...",
  className,
  variante = "outline",
  taille = "icon",
}: BoutonVocalProps) {
  const { enEcoute, demarrerEcoute, arreterEcoute, estSupporte, erreur } =
    utiliserReconnaissanceVocale({
      onResultat,
    });

  if (!estSupporte) return null;

  return (
    <div className={cn("relative inline-flex items-center", className)}>
      <Button
        type="button"
        variant={variante}
        size={taille}
        onClick={enEcoute ? arreterEcoute : demarrerEcoute}
        aria-label={enEcoute ? "Arrêter l'écoute" : placeholder}
        className={cn(
          "relative",
          enEcoute && "text-destructive ring-2 ring-destructive/30"
        )}
      >
        {enEcoute ? (
          <>
            <MicOff className="h-4 w-4" aria-hidden="true" />
            <span aria-hidden="true" className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-destructive animate-pulse" />
          </>
        ) : (
           <Mic className="h-4 w-4" aria-hidden="true" />
        )}
      </Button>
      {erreur && (
        <span className="ml-2 text-xs text-destructive max-w-[200px] truncate">
          {erreur}
        </span>
      )}
    </div>
  );
}
