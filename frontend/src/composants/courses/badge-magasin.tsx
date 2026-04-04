"use client";

import {
  COULEURS_MAGASINS,
  LIBELLES_MAGASINS,
  type MagasinCible,
} from "@/types/courses";
import { Badge } from "@/composants/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/composants/ui/dropdown-menu";

type BadgeMagasinProps = {
  magasin?: string | null;
  onChanger?: (magasin: string | null) => void;
  taille?: "sm" | "md";
};

const CHOIX_MAGASINS: { value: MagasinCible | null; label: string }[] = [
  { value: "bio_coop", label: "🥬 Bio Coop" },
  { value: "grand_frais", label: "🧀 Grand Frais" },
  { value: "carrefour_drive", label: "🛒 Carrefour Drive" },
  { value: null, label: "❌ Aucun" },
];

export function BadgeMagasin({ magasin, onChanger, taille = "sm" }: BadgeMagasinProps) {
  if (!magasin && !onChanger) return null;

  const estMagasinConnu = magasin && magasin in LIBELLES_MAGASINS;
  const libelle = estMagasinConnu
    ? LIBELLES_MAGASINS[magasin as MagasinCible]
    : magasin || "Aucun";
  const couleurs = estMagasinConnu
    ? COULEURS_MAGASINS[magasin as MagasinCible]
    : "bg-gray-100 text-gray-600 border-gray-300";

  const tailleClasses = taille === "sm" ? "text-xs px-1.5 py-0.5" : "text-sm px-2 py-1";

  const badge = (
    <Badge
      variant="outline"
      className={`${couleurs} ${tailleClasses} cursor-pointer border`}
    >
      {libelle}
    </Badge>
  );

  if (!onChanger) return badge;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>{badge}</DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        {CHOIX_MAGASINS.map(({ value, label }) => (
          <DropdownMenuItem
            key={value ?? "aucun"}
            onClick={() => onChanger(value)}
          >
            {label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
