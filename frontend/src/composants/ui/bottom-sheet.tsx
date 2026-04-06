// ═════════════════════════════════════════════════════════
// BottomSheet — F10: Feuille modale depuis le bas (mobile)
// Utilise le composant Sheet existant avec side="bottom"
// et ajoute un handle drag visuel + hauteur max adaptée.
// ═════════════════════════════════════════════════════════
"use client";

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/composants/ui/sheet";
import { cn } from "@/bibliotheque/utils";

interface BottomSheetProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  titre?: string;
  description?: string;
  children: React.ReactNode;
  /** Hauteur max du contenu, ex. "60vh" (défaut: 80vh) */
  hauteurMax?: string;
  className?: string;
}

/**
 * BottomSheet — modale glissant depuis le bas sur mobile.
 * Remplace les Dialog sur les petits écrans pour une UX native.
 * Sur desktop, se comporte comme un panel bas standard.
 */
export function BottomSheet({
  open,
  onOpenChange,
  titre,
  description,
  children,
  hauteurMax = "80vh",
  className,
}: BottomSheetProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="bottom"
        className={cn("rounded-t-2xl px-4 pb-safe-area", className)}
        style={{ maxHeight: hauteurMax }}
      >
        {/* Handle drag visuel */}
        <div className="mx-auto mb-3 mt-1 h-1 w-10 rounded-full bg-border" aria-hidden />

        {(titre || description) && (
          <SheetHeader className="mb-4 text-left">
            {titre && <SheetTitle>{titre}</SheetTitle>}
            {description && <SheetDescription>{description}</SheetDescription>}
          </SheetHeader>
        )}

        <div className="overflow-y-auto">{children}</div>
      </SheetContent>
    </Sheet>
  );
}
