import type { FieldErrors, UseFormHandleSubmit, UseFormRegister } from "react-hook-form";
import { Loader2 } from "lucide-react";
import { motion } from "framer-motion";

import { Button } from "@/composants/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import type { DonneesArticleCourses } from "@/bibliotheque/validateurs";

type DialogueArticleCoursesProps = {
  ouvert: boolean;
  enAjout: boolean;
  erreursArticle: FieldErrors<DonneesArticleCourses>;
  regArticle: UseFormRegister<DonneesArticleCourses>;
  submitArticle: UseFormHandleSubmit<DonneesArticleCourses>;
  onOpenChange: (ouvert: boolean) => void;
  onAjouterArticle: (data: DonneesArticleCourses) => void;
};

export function DialogueArticleCourses({
  ouvert,
  enAjout,
  erreursArticle,
  regArticle,
  submitArticle,
  onOpenChange,
  onAjouterArticle,
}: DialogueArticleCoursesProps) {
  return (
    <Dialog open={ouvert} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Ajouter un article</DialogTitle>
        </DialogHeader>
        <motion.form
          onSubmit={submitArticle((data) => onAjouterArticle(data))}
          className="space-y-4"
          animate={erreursArticle.nom ? { x: [0, -6, 6, -4, 4, 0] } : { x: 0 }}
          transition={{ duration: 0.35 }}
        >
          <div className="space-y-2">
            <Label htmlFor="nom-article">Nom *</Label>
            <Input id="nom-article" {...regArticle("nom")} placeholder="Ex: Tomates" />
            {erreursArticle.nom && (
              <p className="text-sm text-destructive">{erreursArticle.nom.message}</p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="qte-article">Quantité</Label>
              <Input
                id="qte-article"
                type="number"
                min={0}
                step="any"
                {...regArticle("quantite")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="unite-article">Unité</Label>
              <Input
                id="unite-article"
                {...regArticle("unite")}
                placeholder="kg, L, pièces..."
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="cat-article">Catégorie</Label>
            <Input
              id="cat-article"
              {...regArticle("categorie")}
              placeholder="Fruits, Légumes, Viande..."
            />
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
        </motion.form>
      </DialogContent>
    </Dialog>
  );
}
