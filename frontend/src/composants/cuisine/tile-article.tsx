// ═══════════════════════════════════════════════════════════
// TileArticle — Tuile style Bring! pour articles de courses
// ═══════════════════════════════════════════════════════════

"use client";

import {
  Apple,
  Beef,
  Milk,
  Wheat,
  Snowflake,
  Wine,
  Cookie,
  ShoppingBag,
  Check,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/bibliotheque/utils";

const ICONES_CATEGORIES: Record<string, { icone: LucideIcon; couleur: string }> = {
  "Fruits": { icone: Apple, couleur: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" },
  "Légumes": { icone: Apple, couleur: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300" },
  "Viande": { icone: Beef, couleur: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300" },
  "Poisson": { icone: Beef, couleur: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300" },
  "Laitier": { icone: Milk, couleur: "bg-sky-100 text-sky-700 dark:bg-sky-900 dark:text-sky-300" },
  "Produits laitiers": { icone: Milk, couleur: "bg-sky-100 text-sky-700 dark:bg-sky-900 dark:text-sky-300" },
  "Épicerie": { icone: Wheat, couleur: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300" },
  "Surgelés": { icone: Snowflake, couleur: "bg-cyan-100 text-cyan-700 dark:bg-cyan-900 dark:text-cyan-300" },
  "Boissons": { icone: Wine, couleur: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300" },
  "Boulangerie": { icone: Cookie, couleur: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300" },
};

const DEFAUT = { icone: ShoppingBag, couleur: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300" };

interface TileArticleProps {
  nom: string;
  quantite?: number;
  unite?: string;
  categorie?: string;
  estCoche?: boolean;
  onClick?: () => void;
  onLongPress?: () => void;
}

export function TileArticle({
  nom,
  quantite,
  unite,
  categorie,
  estCoche = false,
  onClick,
  onLongPress,
}: TileArticleProps) {
  const { icone: Icone, couleur } = ICONES_CATEGORIES[categorie ?? ""] ?? DEFAUT;

  return (
    <button
      type="button"
      onClick={onClick}
      onContextMenu={(e) => {
        e.preventDefault();
        onLongPress?.();
      }}
      className={cn(
        "relative flex flex-col items-center justify-center gap-1 rounded-xl p-3 w-full aspect-square transition-all",
        "border hover:shadow-md active:scale-95",
        estCoche
          ? "bg-muted/50 opacity-60 border-muted"
          : couleur
      )}
    >
      {estCoche && (
        <div className="absolute top-1.5 right-1.5 rounded-full bg-green-600 p-0.5">
          <Check className="h-3 w-3 text-white" />
        </div>
      )}
      <Icone className={cn("h-6 w-6", estCoche && "opacity-50")} />
      <span
        className={cn(
          "text-xs font-medium text-center line-clamp-2 leading-tight",
          estCoche && "line-through"
        )}
      >
        {nom}
      </span>
      {quantite != null && quantite > 0 && (
        <span className="text-[10px] text-muted-foreground">
          {quantite}{unite ? ` ${unite}` : ""}
        </span>
      )}
    </button>
  );
}
