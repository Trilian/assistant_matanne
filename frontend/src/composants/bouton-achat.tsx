// ─── BoutonAchat ──────────────────────────────────────────────
// Bouton fantôme ouvrant un menu déroulant vers les 2 marchands principaux.
// Usage: <BoutonAchat article={{ nom: "Farine T65" }} />

"use client";

import { ShoppingCart, ExternalLink } from "lucide-react";
import { Button } from "@/composants/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/composants/ui/dropdown-menu";

interface BoutonAchatProps {
  /** Article cible (au minimum son nom) */
  article: { nom: string; quantite?: number | string };
  /** Taille du bouton (défaut: "sm") */
  taille?: "sm" | "xs";
}

const MARCHANDS = [
  {
    nom: "Amazon",
    emoji: "📦",
    url: (q: string) =>
      `https://www.amazon.fr/s?k=${encodeURIComponent(q)}`,
  },
  {
    nom: "Cdiscount",
    emoji: "🛒",
    url: (q: string) =>
      `https://www.cdiscount.com/search/10/${encodeURIComponent(q)}.html`,
  },
];

export function BoutonAchat({ article, taille = "sm" }: BoutonAchatProps) {
  const query =
    article.quantite
      ? `${article.quantite} ${article.nom}`
      : article.nom;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className={taille === "xs" ? "h-6 w-6" : "h-7 w-7"}
          title={`Acheter : ${article.nom}`}
        >
          <ShoppingCart className={taille === "xs" ? "h-3 w-3" : "h-3.5 w-3.5"} />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {MARCHANDS.map((m) => (
          <DropdownMenuItem key={m.nom} asChild>
            <a
              href={m.url(query)}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2"
            >
              <span>{m.emoji}</span>
              <span>{m.nom}</span>
              <ExternalLink className="h-3 w-3 ml-auto text-muted-foreground" />
            </a>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
