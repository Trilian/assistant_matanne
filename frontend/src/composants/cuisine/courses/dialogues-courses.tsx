"use client";

import type { BaseSyntheticEvent } from "react";
import { Download, Loader2 } from "lucide-react";
import type { FieldErrors, UseFormRegister } from "react-hook-form";

import { Button } from "@/composants/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/composants/ui/dialog";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import type { DonneesArticleCourses } from "@/bibliotheque/validateurs-cuisine";

export function DialogueAjoutArticle({
  ouvert,
  onOpenChange,
  soumettre,
  regArticle,
  erreursArticle,
  enAjout,
}: {
  ouvert: boolean;
  onOpenChange: (ouvert: boolean) => void;
  soumettre: (event?: BaseSyntheticEvent) => void;
  regArticle: UseFormRegister<DonneesArticleCourses>;
  erreursArticle: FieldErrors<DonneesArticleCourses>;
  enAjout: boolean;
}) {
  return (
    <Dialog open={ouvert} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Ajouter un article</DialogTitle>
        </DialogHeader>
        <form onSubmit={soumettre} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="nom-article">Nom *</Label>
            <Input id="nom-article" {...regArticle("nom")} placeholder="Ex: Tomates" />
            {erreursArticle.nom && <p className="text-sm text-destructive">{erreursArticle.nom.message}</p>}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="qte-article">Quantité</Label>
              <Input id="qte-article" type="number" min={0} step="any" {...regArticle("quantite")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="unite-article">Unité</Label>
              <Input id="unite-article" {...regArticle("unite")} placeholder="kg, L, pièces..." />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="cat-article">Catégorie</Label>
            <Input id="cat-article" {...regArticle("categorie")} placeholder="Fruits, Légumes, Viande..." />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Annuler
            </Button>
            <Button type="submit" disabled={enAjout}>
              {enAjout && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Ajouter
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function DialogueQrPartage({
  ouvert,
  onOpenChange,
  chargementQr,
  qrUrl,
  onTelecharger,
}: {
  ouvert: boolean;
  onOpenChange: (ouvert: boolean) => void;
  chargementQr: boolean;
  qrUrl: string | null;
  onTelecharger: () => void;
}) {
  return (
    <Dialog open={ouvert} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>QR de partage</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Scannez ce QR pour ouvrir la version texte de votre liste de courses.
          </p>
          <div className="flex min-h-48 items-center justify-center rounded-lg border p-4">
            {chargementQr ? (
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            ) : qrUrl ? (
              <img src={qrUrl} alt="QR liste de courses" className="h-52 w-52" />
            ) : (
              <p className="text-sm text-muted-foreground">QR indisponible</p>
            )}
          </div>
          <div className="flex justify-end">
            <Button variant="outline" onClick={onTelecharger} disabled={!qrUrl}>
              <Download className="mr-1 h-4 w-4" />
              Télécharger
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
