// ═══════════════════════════════════════════════════════════
// FAB Actions Rapides — Bouton flottant (+ cercle) pour actions principales
// ═══════════════════════════════════════════════════════════
// Visible sur mobile, sur la droite (mais au-dessus du mobile nav)
// Actions: Ajouter recette, Courses, Dépense, Scan
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Plus,
  ChefHat,
  ShoppingCart,
  Wallet,
  QrCode,
  X,
  StickyNote,
  Timer,
  type LucideIcon,
} from "lucide-react";
import { Button } from "@/composants/ui/button";
import { cn } from "@/bibliotheque/utils";

interface ActionRapide {
  id: string;
  label: string;
  icone: LucideIcon;
  href: string;
  couleur: string;
}

const ACTIONS: ActionRapide[] = [
  {
    id: "recette",
    label: "Nouvelle recette",
    icone: ChefHat,
    href: "/cuisine/recettes/nouveau",
    couleur: "bg-orange-500 hover:bg-orange-600",
  },
  {
    id: "courses",
    label: "Courses",
    icone: ShoppingCart,
    href: "/cuisine/courses",
    couleur: "bg-green-500 hover:bg-green-600",
  },
  {
    id: "depense",
    label: "Dépense",
    icone: Wallet,
    href: "/famille/budget?action=ajouter",
    couleur: "bg-blue-500 hover:bg-blue-600",
  },
  {
    id: "scan",
    label: "Scan",
    icone: QrCode,
    href: "/cuisine/courses?scan=true",
    couleur: "bg-purple-500 hover:bg-purple-600",
  },
  {
    id: "note",
    label: "Note rapide",
    icone: StickyNote,
    href: "/outils/notes?action=nouvelle",
    couleur: "bg-yellow-500 hover:bg-yellow-600",
  },
  {
    id: "minuteur",
    label: "Minuteur",
    icone: Timer,
    href: "/outils/minuteur",
    couleur: "bg-rose-500 hover:bg-rose-600",
  },
];

/**
 * FAB circulaire avec actions rapides
 * Positions des actions en cercle autour du bouton principal
 */
export function FabActionsRapides() {
  const [ouvert, setOuvert] = useState(false);

  // Angles pour positionner les boutons en cercle (6 boutons = 60° d'écart)
  const rayonCercle = 80; // pixels du centre
  const nbActions = ACTIONS.length;

  return (
    <>
      {/* Overlay semi-transparent quand ouvert */}
      {ouvert && (
        <div
          className="fixed inset-0 z-40 md:hidden"
          onClick={() => setOuvert(false)}
          aria-hidden="true"
        />
      )}

      {/* Container FAB - Position fixe au-dessus de la nav mobile */}
      <div className="fixed bottom-24 right-6 z-50 md:hidden">
        {/* Boutons d'action en cercle */}
        {ouvert &&
          ACTIONS.map((action, idx) => {
            // Répartir les actions en demi-cercle (vers le haut-gauche)
            const startAngle = 180;
            const endAngle = 360;
            const stepAngle = (endAngle - startAngle) / (nbActions - 1);
            const angleDeg = startAngle + idx * stepAngle;
            const angle = (angleDeg * Math.PI) / 180;
            const x = rayonCercle * Math.cos(angle);
            const y = rayonCercle * Math.sin(angle) * -1; // Y inversé (vers le haut)

            const Icone = action.icone;

            return (
              <Link
                key={action.id}
                href={action.href}
                onClick={() => setOuvert(false)}
                style={{
                  position: "absolute",
                  transform: `translate(${x}px, ${y}px)`,
                  transition: "all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)",
                  opacity: 1,
                }}
              >
                <Button
                  size="icon"
                  className={cn(
                    "h-12 w-12 rounded-full shadow-lg text-white",
                    action.couleur
                  )}
                  title={action.label}
                  aria-label={action.label}
                >
                  <Icone className="h-5 w-5" />
                </Button>
              </Link>
            );
          })}

        {/* Bouton principal (+ ou X) */}
        <Button
          size="icon"
          className="h-14 w-14 rounded-full shadow-lg bg-accent hover:bg-accent/90 text-accent-foreground"
          onClick={() => setOuvert(!ouvert)}
          aria-label={ouvert ? "Fermer les actions rapides" : "Ouvrir les actions rapides"}
          aria-expanded={ouvert}
        >
          {ouvert ? (
            <X className="h-6 w-6 transition-transform rotate-0" />
          ) : (
            <Plus className="h-6 w-6 transition-transform" />
          )}
        </Button>
      </div>
    </>
  );
}
