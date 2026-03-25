// ═══════════════════════════════════════════════════════════
// Upload Ticket — OCR IA pour extraction de données
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useRef, useCallback } from "react";
import {
  Camera,
  Upload,
  Loader2,
  Check,
  X,
  ReceiptText,
  Pencil,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Card,
  CardContent,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { toast } from "sonner";
import { clientApi } from "@/bibliotheque/api/client";

// ── Types ──

interface ArticleExtrait {
  description: string;
  quantite: number;
  prix_unitaire: number | null;
  prix_total: number;
}

interface DonneesTicket {
  magasin: string | null;
  date: string | null;
  articles: ArticleExtrait[];
  sous_total: number | null;
  tva: number | null;
  total: number | null;
  mode_paiement: string | null;
  categorie_suggeree: string;
}

interface ResultatOCR {
  success: boolean;
  message: string;
  donnees: DonneesTicket | null;
}

interface UploadTicketProps {
  ouvert: boolean;
  onFermer: () => void;
  onCreerDepense: (depense: {
    montant: number;
    categorie: string;
    description: string;
    magasin?: string;
  }) => void;
}

// ── Composant principal ──

export function UploadTicket({ ouvert, onFermer, onCreerDepense }: UploadTicketProps) {
  const [etape, setEtape] = useState<"upload" | "analyse" | "resultat">("upload");
  const [preview, setPreview] = useState<string | null>(null);
  const [donnees, setDonnees] = useState<DonneesTicket | null>(null);
  const [chargement, setChargement] = useState(false);
  const [montantEdite, setMontantEdite] = useState("");
  const [categorieEditee, setCategorieEditee] = useState("alimentation");
  const [descriptionEditee, setDescriptionEditee] = useState("");
  const [magasinEdite, setMagasinEdite] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const reinitialiser = useCallback(() => {
    setEtape("upload");
    setPreview(null);
    setDonnees(null);
    setChargement(false);
    setMontantEdite("");
    setCategorieEditee("alimentation");
    setDescriptionEditee("");
    setMagasinEdite("");
  }, []);

  const fermer = useCallback(() => {
    reinitialiser();
    onFermer();
  }, [reinitialiser, onFermer]);

  const gererFichier = useCallback(async (fichier: File) => {
    if (!fichier.type.startsWith("image/")) {
      toast.error("Veuillez sélectionner une image (JPEG, PNG)");
      return;
    }

    // Preview
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(fichier);

    // Upload + analyse
    setEtape("analyse");
    setChargement(true);

    try {
      const formData = new FormData();
      formData.append("file", fichier);

      const { data } = await clientApi.post<ResultatOCR>(
        "/famille/budget/ocr-ticket",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      if (data.success && data.donnees) {
        setDonnees(data.donnees);
        setMontantEdite(data.donnees.total?.toString() ?? "");
        setCategorieEditee(data.donnees.categorie_suggeree || "alimentation");
        setDescriptionEditee(
          data.donnees.articles.length > 0
            ? `${data.donnees.articles.length} article(s)`
            : "Ticket de caisse"
        );
        setMagasinEdite(data.donnees.magasin ?? "");
        setEtape("resultat");
        toast.success("Ticket analysé avec succès !");
      } else {
        toast.error(data.message || "Échec de l'analyse");
        setEtape("upload");
      }
    } catch {
      toast.error("Erreur lors de l'analyse du ticket");
      setEtape("upload");
    } finally {
      setChargement(false);
    }
  }, []);

  const gererDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const fichier = e.dataTransfer.files[0];
      if (fichier) gererFichier(fichier);
    },
    [gererFichier]
  );

  const validerDepense = useCallback(() => {
    if (!montantEdite || parseFloat(montantEdite) <= 0) {
      toast.error("Montant invalide");
      return;
    }

    onCreerDepense({
      montant: parseFloat(montantEdite),
      categorie: categorieEditee,
      description: descriptionEditee || "Ticket scanné",
      magasin: magasinEdite || undefined,
    });

    toast.success("Dépense créée à partir du ticket");
    fermer();
  }, [montantEdite, categorieEditee, descriptionEditee, magasinEdite, onCreerDepense, fermer]);

  return (
    <Dialog open={ouvert} onOpenChange={(o) => !o && fermer()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ReceiptText className="h-5 w-5" />
            Scanner un ticket
          </DialogTitle>
        </DialogHeader>

        {/* Étape 1 : Upload */}
        {etape === "upload" && (
          <div
            className="flex flex-col items-center gap-4 rounded-lg border-2 border-dashed p-8 cursor-pointer
              hover:border-primary/50 hover:bg-accent/30 transition-colors"
            onDragOver={(e) => e.preventDefault()}
            onDrop={gererDrop}
            onClick={() => inputRef.current?.click()}
          >
            <Camera className="h-12 w-12 text-muted-foreground" />
            <div className="text-center">
              <p className="text-sm font-medium">
                Glissez un ticket ou cliquez pour choisir
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                JPEG, PNG • Max 10 Mo
              </p>
            </div>
            <Button variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-1" />
              Choisir une image
            </Button>
            <input
              ref={inputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) gererFichier(f);
              }}
            />
          </div>
        )}

        {/* Étape 2 : Analyse en cours */}
        {etape === "analyse" && (
          <div className="flex flex-col items-center gap-4 py-8">
            {preview && (
              <img
                src={preview}
                alt="Ticket"
                className="h-32 w-auto rounded-lg object-contain opacity-50"
              />
            )}
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">
              Analyse du ticket en cours...
            </p>
          </div>
        )}

        {/* Étape 3 : Résultat */}
        {etape === "resultat" && donnees && (
          <div className="space-y-4">
            {/* Résumé extraction */}
            <Card>
              <CardContent className="pt-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Magasin</span>
                  <span className="text-sm font-medium">{donnees.magasin || "—"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Date</span>
                  <span className="text-sm font-medium">{donnees.date || "—"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Articles</span>
                  <span className="text-sm font-medium">{donnees.articles.length}</span>
                </div>
                {donnees.articles.length > 0 && (
                  <div className="border-t pt-2 mt-2 max-h-32 overflow-y-auto space-y-1">
                    {donnees.articles.map((a, i) => (
                      <div key={i} className="flex items-center justify-between text-xs">
                        <span className="truncate flex-1 mr-2">{a.description}</span>
                        <span className="tabular-nums font-medium">{a.prix_total.toFixed(2)} €</span>
                      </div>
                    ))}
                  </div>
                )}
                <div className="flex items-center justify-between border-t pt-2 font-semibold">
                  <span>Total</span>
                  <span>{donnees.total?.toFixed(2) ?? "—"} €</span>
                </div>
              </CardContent>
            </Card>

            {/* Formulaire éditable */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Pencil className="h-4 w-4" />
                Vérifier et ajuster
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label className="text-xs">Montant (€)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={montantEdite}
                    onChange={(e) => setMontantEdite(e.target.value)}
                  />
                </div>
                <div>
                  <Label className="text-xs">Catégorie</Label>
                  <Input
                    value={categorieEditee}
                    onChange={(e) => setCategorieEditee(e.target.value)}
                  />
                </div>
              </div>
              <div>
                <Label className="text-xs">Description</Label>
                <Input
                  value={descriptionEditee}
                  onChange={(e) => setDescriptionEditee(e.target.value)}
                />
              </div>
              <div>
                <Label className="text-xs">Magasin</Label>
                <Input
                  value={magasinEdite}
                  onChange={(e) => setMagasinEdite(e.target.value)}
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <Button
                variant="outline"
                className="flex-1"
                onClick={reinitialiser}
              >
                <X className="h-4 w-4 mr-1" />
                Recommencer
              </Button>
              <Button className="flex-1" onClick={validerDepense}>
                <Check className="h-4 w-4 mr-1" />
                Créer la dépense
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
