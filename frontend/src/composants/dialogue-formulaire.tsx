// ═══════════════════════════════════════════════════════════
// DialogueFormulaire — Composant réutilisable CRUD dialog
// ═══════════════════════════════════════════════════════════

"use client";

import { type ReactNode } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface DialogueFormulaireProps {
  ouvert: boolean;
  onClose: () => void;
  titre: string;
  children: ReactNode;
  onSubmit: () => void;
  enCours?: boolean;
  texteBouton?: string;
}

export function DialogueFormulaire({
  ouvert,
  onClose,
  titre,
  children,
  onSubmit,
  enCours = false,
  texteBouton = "Enregistrer",
}: DialogueFormulaireProps) {
  return (
    <Dialog open={ouvert} onOpenChange={(v) => !v && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{titre}</DialogTitle>
        </DialogHeader>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
          className="space-y-4"
        >
          {children}
          <Button type="submit" className="w-full" disabled={enCours}>
            {enCours ? "En cours..." : texteBouton}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
