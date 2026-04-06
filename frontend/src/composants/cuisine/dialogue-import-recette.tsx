// ═══════════════════════════════════════════════════════════
// Dialogue Import Recette — Import depuis URL ou PDF
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useRef } from "react";
import { Upload, Link2, Loader2 } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { importerRecetteURL, importerRecettesLot, importerRecettePDF, obtenirDoublonsRecettes } from "@/bibliotheque/api/recettes";
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

interface ErreurApiAvecDetail {
  response?: {
    data?: {
      detail?: string;
    };
  };
}

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
  const [urlsLot, setUrlsLot] = useState("");
  const [ongletActif, setOngletActif] = useState<"url" | "lot" | "pdf">("url");
  const [fichierPDF, setFichierPDF] = useState<File | null>(null);
  const inputFileRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  // Mutation pour import URL
  const mutationURL = useMutation({
    mutationFn: importerRecetteURL,
    onSuccess: async (data) => {
      toast.success(`✅ "${data.nom}" importée avec succès !`);
      queryClient.invalidateQueries({ queryKey: ["recettes"] });
      setOpen(false);
      setUrl("");
      // Vérification doublon post-import
      try {
        const doublons = await obtenirDoublonsRecettes(0.75);
        if (doublons.total > 0) {
          toast.warning(`⚠️ Doublon possible détecté — "${doublons.items[0].recette_a.nom}" ressemble à une recette existante.`, { duration: 6000 });
        }
      } catch { /* silencieux */ }
      onSuccess?.();
    },
    onError: (error: ErreurApiAvecDetail) => {
      toast.error(
        error.response?.data?.detail ||
          "Impossible d'importer la recette. Vérifiez l'URL."
      );
    },
  });

  const mutationLot = useMutation({
    mutationFn: importerRecettesLot,
    onSuccess: (data) => {
      toast.success(`✅ ${data.importees} recette(s) importée(s)${data.echouees ? `, ${data.echouees} en échec` : ""}`);
      queryClient.invalidateQueries({ queryKey: ["recettes"] });
      setOpen(false);
      setUrlsLot("");
      onSuccess?.();
    },
    onError: () => {
      toast.error("Impossible d'importer les recettes en lot.");
    },
  });

  // Mutation pour import PDF
  const mutationPDF = useMutation({
    mutationFn: importerRecettePDF,
    onSuccess: async (data) => {
      toast.success(`✅ "${data.nom}" importée depuis PDF avec succès !`);
      queryClient.invalidateQueries({ queryKey: ["recettes"] });
      setOpen(false);
      setFichierPDF(null);
      // Vérification doublon post-import
      try {
        const doublons = await obtenirDoublonsRecettes(0.75);
        if (doublons.total > 0) {
          toast.warning(`⚠️ Doublon possible détecté — "${doublons.items[0].recette_a.nom}" ressemble à une recette existante.`, { duration: 6000 });
        }
      } catch { /* silencieux */ }
      onSuccess?.();
    },
    onError: (error: ErreurApiAvecDetail) => {
      toast.error(
        error.response?.data?.detail ||
          "Impossible d'extraire la recette du PDF."
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

  const handleImportLot = () => {
    const urls = urlsLot
      .split(/\r?\n/)
      .map((ligne) => ligne.trim())
      .filter(Boolean);

    if (urls.length === 0) {
      toast.error("Ajoutez au moins une URL.");
      return;
    }

    mutationLot.mutate(urls);
  };

  const handleImportPDF = () => {
    if (!fichierPDF) {
      toast.error("Veuillez sélectionner un fichier PDF.");
      return;
    }

    mutationPDF.mutate(fichierPDF);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        toast.error("Seuls les fichiers PDF sont acceptés.");
        return;
      }
      setFichierPDF(file);
    }
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
            L&apos;IA analysera le contenu automatiquement.
          </DialogDescription>
        </DialogHeader>

        <Tabs value={ongletActif} onValueChange={(v) => setOngletActif(v as "url" | "pdf")}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="url">
              <Link2 className="h-4 w-4 mr-2" />
              URL
            </TabsTrigger>
            <TabsTrigger value="lot">
              <Link2 className="h-4 w-4 mr-2" />
              Lot
            </TabsTrigger>
            <TabsTrigger value="pdf">
              <Upload className="h-4 w-4 mr-2" />
              PDF
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

          <TabsContent value="lot" className="space-y-4 pt-4">
            <div className="space-y-2">
              <Label htmlFor="urls-lot">URLs des recettes (une par ligne)</Label>
              <textarea
                id="urls-lot"
                className="min-h-32 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder={"https://www.marmiton.org/...\nhttps://www.cuisineaz.com/..."}
                value={urlsLot}
                onChange={(e) => setUrlsLot(e.target.value)}
                disabled={mutationLot.isPending}
              />
              <p className="text-xs text-muted-foreground">
                Import rapide de plusieurs recettes d'un coup.
              </p>
            </div>

            {mutationLot.isPending && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Import du lot en cours...</span>
              </div>
            )}
          </TabsContent>

          <TabsContent value="pdf" className="space-y-4 pt-4">
            <div 
              className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => inputFileRef.current?.click()}
            >
              <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              {fichierPDF ? (
                <div>
                  <p className="text-sm font-medium mb-2">{fichierPDF.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(fichierPDF.size / 1024).toFixed(2)} KB
                  </p>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      setFichierPDF(null);
                    }}
                  >
                    Changer de fichier
                  </Button>
                </div>
              ) : (
                <div>
                  <p className="text-sm text-muted-foreground mb-2">
                    Cliquez pour sélectionner un fichier PDF
                  </p>
                  <p className="text-xs text-muted-foreground">
                    ou glissez-déposez ici
                  </p>
                </div>
              )}
            </div>
            <input
              ref={inputFileRef}
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleFileSelect}
            />

            {mutationPDF.isPending && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Extraction de la recette du PDF...</span>
              </div>
            )}
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => setOpen(false)}
            disabled={mutationURL.isPending || mutationLot.isPending || mutationPDF.isPending}
          >
            Annuler
          </Button>
          <Button
            onClick={ongletActif === "url" ? handleImportURL : ongletActif === "lot" ? handleImportLot : handleImportPDF}
            disabled={
              mutationURL.isPending || 
              mutationLot.isPending || 
              mutationPDF.isPending || 
              (ongletActif === "url" && !url.trim()) ||
              (ongletActif === "lot" && !urlsLot.trim()) ||
              (ongletActif === "pdf" && !fichierPDF)
            }
          >
            {(mutationURL.isPending || mutationLot.isPending || mutationPDF.isPending) ? (
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
