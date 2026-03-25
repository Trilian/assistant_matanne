// ═══════════════════════════════════════════════════════════
// Dialogue Import Recette — Import depuis URL ou PDF
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Upload, Link2, Loader2 } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { importerRecetteURL } from "@/bibliotheque/api/recettes";
import { Button } from "@/composants/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/composants/ui/dialog";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";

interface DialogueImportRecetteProps {
  onSuccess?: () => void;
}

/**
 * Dialogue pour importer une recette depuis URL ou PDF.
 * Utilise l'IA backend pour extraire les données automatiquement.
 */
export function DialogueImportRecette({ onSuccess }: DialogueImportRecetteProps) {
  const [open, setOpen] = useState(false);
  const [url, setUrl] = useState("");
  const [ongletActif, setOngletActif] = useState<"url" | "pdf">("url");
  const queryClient = useQueryClient();

  // Mutation pour import URL
  const mutationURL = useMutation({
    mutationFn: importerRecetteURL,
    onSuccess: (data) => {
      toast.success(`✅ "${data.nom}" importée avec succès !`);
      queryClient.invalidateQueries({ queryKey: ["recettes"] });
      setOpen(false);
      setUrl("");
      onSuccess?.();
    },
    onError: (error: any) => {
      toast.error(
        error.response?.data?.detail ||
          "Impossible d'importer la recette. Vérifiez l'URL."
      );
    },
  });

  const handleImportURL = () => {
    if (!url.trim()) {
      toast.error("Veuillez entrer une URL valide.");
      return;
    }

    // Validation basique URL
    try {
      new URL(url);
    } catch {
      toast.error("L'URL fournie n'est pas valide.");
      return;
    }

    mutationURL.mutate(url);
  };

  const handleImportPDF = () => {
    toast.info("L'import PDF sera disponible prochainement.");
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Upload className="h-4 w-4 mr-2" />
          Importer
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Importer une recette</DialogTitle>
          <DialogDescription>
            Importez une recette depuis une URL ou un fichier PDF.
            L'IA analysera le contenu automatiquement.
          </DialogDescription>
        </DialogHeader>

        <Tabs value={ongletActif} onValueChange={(v) => setOngletActif(v as "url" | "pdf")}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="url">
              <Link2 className="h-4 w-4 mr-2" />
              URL
            </TabsTrigger>
            <TabsTrigger value="pdf" disabled>
              <Upload className="h-4 w-4 mr-2" />
              PDF (bientôt)
            </TabsTrigger>
          </TabsList>

          <TabsContent value="url" className="space-y-4 pt-4">
            <div className="space-y-2">
              <Label htmlFor="url">URL de la recette</Label>
              <Input
                id="url"
                type="url"
                placeholder="https://www.marmiton.org/recettes/..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !mutationURL.isPending) {
                    handleImportURL();
                  }
                }}
                disabled={mutationURL.isPending}
              />
              <p className="text-xs text-muted-foreground">
                Formats supportés : Marmiton, CuisineAZ, 750g, et la plupart des sites culinaires.
              </p>
            </div>

            {mutationURL.isPending && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Analyse de la recette en cours...</span>
              </div>
            )}
          </TabsContent>

          <TabsContent value="pdf" className="space-y-4 pt-4">
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-sm text-muted-foreground mb-2">
                Glissez-déposez un fichier PDF ici
              </p>
              <p className="text-xs text-muted-foreground">
                ou cliquez pour sélectionner
              </p>
            </div>
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => setOpen(false)}
            disabled={mutationURL.isPending}
          >
            Annuler
          </Button>
          <Button
            onClick={ongletActif === "url" ? handleImportURL : handleImportPDF}
            disabled={mutationURL.isPending || (ongletActif === "url" && !url.trim())}
          >
            {mutationURL.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Importation...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Importer
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
