// ═══════════════════════════════════════════════════════════
// Scan ticket de caisse → import courses automatique
// ═══════════════════════════════════════════════════════════

"use client";

import { useRef, useState } from "react";
import { Camera, Upload, Loader2, Check, X, ShoppingCart, Receipt } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Label } from "@/composants/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete } from "@/crochets/utiliser-api";
import {
  analyserTicketCaisse,
  listerListesCourses,
  creerListeCourses,
} from "@/bibliotheque/api/courses";
import type { ResultatOCRTicket, ArticleOCRBrut } from "@/bibliotheque/api/courses";
import type { ListeCourses } from "@/types/courses";

export default function PageScanTicket() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [chargement, setChargement] = useState(false);
  const [resultat, setResultat] = useState<ResultatOCRTicket | null>(null);
  const [listeSelectionnee, setListeSelectionnee] = useState<string>("");
  const [importEnCours, setImportEnCours] = useState(false);
  const [articlesSelectionnes, setArticlesSelectionnes] = useState<Set<number>>(new Set());

  const { data: listes = [] } = utiliserRequete<ListeCourses[]>(
    ["listes-courses"],
    listerListesCourses
  );

  async function onFichier(file: File) {
    if (!file.type.startsWith("image/")) {
      toast.error("Veuillez sélectionner une image (JPEG, PNG, WebP)");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      toast.error("Image trop volumineuse (max 10 Mo)");
      return;
    }

    // Prévisualisation
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(file);

    setChargement(true);
    setResultat(null);
    setArticlesSelectionnes(new Set());

    try {
      // Mode aperçu d'abord (pas de liste_id)
      const data = await analyserTicketCaisse(file);
      setResultat(data);
      if (data.success && data.donnees_ocr) {
        // Sélectionner tous les articles par défaut
        setArticlesSelectionnes(
          new Set(data.donnees_ocr.articles.map((_, i) => i))
        );
        toast.success(
          `${data.donnees_ocr.articles.length} article(s) détecté(s)`
        );
      } else {
        toast.error(data.message || "Analyse OCR incomplète");
      }
    } catch {
      toast.error("Impossible d'analyser le ticket");
    } finally {
      setChargement(false);
    }
  }

  function toggleArticle(index: number) {
    setArticlesSelectionnes((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  }

  async function importerArticles() {
    if (!resultat?.donnees_ocr) return;
    if (!listeSelectionnee) {
      toast.error("Sélectionnez une liste de courses");
      return;
    }

    const articlesChoisis = resultat.donnees_ocr.articles.filter((_, i) =>
      articlesSelectionnes.has(i)
    );
    if (articlesChoisis.length === 0) {
      toast.error("Aucun article sélectionné");
      return;
    }

    const listeId =
      listeSelectionnee === "__nouveau__"
        ? null
        : parseInt(listeSelectionnee, 10);

    setImportEnCours(true);
    try {
      let idFinal = listeId;

      if (listeSelectionnee === "__nouveau__") {
        const magasin = resultat.donnees_ocr.magasin ?? "Ticket scanné";
        const nouvelleListe = await creerListeCourses(
          `Courses — ${magasin}`
        );
        idFinal = (nouvelleListe as { id?: number }).id ?? null;
      }

      if (!idFinal) {
        toast.error("Impossible de créer la liste");
        return;
      }

      // Ré-analyser avec liste_id pour import côté serveur
      // On renvoie le fichier — récupéré depuis l'input (ref)
      const fileInput = inputRef.current;
      const file = fileInput?.files?.[0];
      if (!file) {
        toast.error("Fichier introuvable, veuillez re-sélectionner l'image");
        return;
      }

      const importData = await analyserTicketCaisse(file, idFinal);
      if (importData.success) {
        toast.success(
          `${importData.articles_importes.length} article(s) ajouté(s) à la liste`
        );
        setResultat(importData);
      } else {
        toast.error(importData.message || "Échec de l'import");
      }
    } catch {
      toast.error("Erreur lors de l'import");
    } finally {
      setImportEnCours(false);
    }
  }

  const articles: ArticleOCRBrut[] = resultat?.donnees_ocr?.articles ?? [];
  const dejImporte = (resultat?.articles_importes?.length ?? 0) > 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Receipt className="h-6 w-6" />
          Scan ticket de caisse
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Photographiez un ticket et importez automatiquement les articles dans
          une liste de courses.
        </p>
      </div>

      {/* Upload */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            Photo du ticket
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) void onFichier(f);
            }}
          />

          <div
            className="rounded-lg border-2 border-dashed p-8 text-center cursor-pointer hover:bg-accent/30 transition-colors"
            onClick={() => inputRef.current?.click()}
          >
            <Upload className="h-10 w-10 mx-auto mb-2 text-muted-foreground" />
            <p className="font-medium">Appuyez pour prendre/choisir une photo</p>
            <p className="text-xs text-muted-foreground mt-1">
              JPEG, PNG, WebP — 10 Mo max
            </p>
          </div>

          {preview && (
            <img
              src={preview}
              alt="Aperçu ticket"
              className="max-h-64 w-full rounded-lg object-contain border"
            />
          )}

          {chargement && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Analyse OCR en cours…
            </div>
          )}
        </CardContent>
      </Card>

      {/* Résultats OCR */}
      {resultat?.donnees_ocr && articles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <ShoppingCart className="h-5 w-5" />
                Articles détectés
              </span>
              <Badge variant="secondary">{articles.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Infos ticket */}
            {(resultat.donnees_ocr.magasin || resultat.donnees_ocr.total != null) && (
              <div className="flex gap-4 text-sm text-muted-foreground flex-wrap">
                {resultat.donnees_ocr.magasin && (
                  <span>🏪 {resultat.donnees_ocr.magasin}</span>
                )}
                {resultat.donnees_ocr.date && (
                  <span>📅 {resultat.donnees_ocr.date}</span>
                )}
                {resultat.donnees_ocr.total != null && (
                  <span>💰 {resultat.donnees_ocr.total.toFixed(2)} €</span>
                )}
              </div>
            )}

            {/* Liste articles avec checkboxes */}
            <div className="divide-y">
              {articles.map((art, i) => (
                <label
                  key={i}
                  className="flex items-center gap-3 py-2 cursor-pointer hover:bg-accent/20 rounded px-1"
                >
                  <input
                    type="checkbox"
                    checked={articlesSelectionnes.has(i)}
                    onChange={() => toggleArticle(i)}
                    className="h-4 w-4 rounded"
                  />
                  <span className="flex-1 text-sm">{art.description}</span>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {art.quantite > 1 && `×${art.quantite} `}
                    {art.prix_total != null && `${art.prix_total.toFixed(2)} €`}
                  </span>
                </label>
              ))}
            </div>

            <p className="text-xs text-muted-foreground">
              {articlesSelectionnes.size} / {articles.length} article(s) sélectionné(s)
            </p>

            {/* Sélecteur liste + bouton import */}
            {!dejImporte && (
              <div className="space-y-3 pt-2 border-t">
                <div className="space-y-1">
                  <Label>Liste de courses cible</Label>
                  <Select
                    value={listeSelectionnee}
                    onValueChange={setListeSelectionnee}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choisir une liste…" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="__nouveau__">
                        ✨ Créer une nouvelle liste
                      </SelectItem>
                      {listes.map((l) => (
                        <SelectItem key={l.id} value={String(l.id)}>
                          {l.nom}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <Button
                  onClick={importerArticles}
                  disabled={importEnCours || articlesSelectionnes.size === 0}
                  className="w-full"
                >
                  {importEnCours ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Import en cours…
                    </>
                  ) : (
                    <>
                      <ShoppingCart className="h-4 w-4 mr-2" />
                      Importer {articlesSelectionnes.size} article(s)
                    </>
                  )}
                </Button>
              </div>
            )}

            {/* Confirmation import */}
            {dejImporte && (
              <div className="rounded-lg bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 p-3 flex items-center gap-2 text-sm text-green-700 dark:text-green-300">
                <Check className="h-4 w-4 flex-shrink-0" />
                {resultat.articles_importes.length} article(s) importé(s) avec
                succès dans la liste.
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Aucun article détecté */}
      {resultat && !chargement && articles.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            <X className="h-10 w-10 mx-auto mb-2 opacity-30" />
            <p className="text-sm">
              Aucun article détecté. Essayez avec une photo plus nette ou mieux
              éclairée.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
