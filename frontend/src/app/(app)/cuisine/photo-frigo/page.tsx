"use client";

import { useState, useRef } from "react";
import {
  Camera,
  ImagePlus,
  Loader2,
  ChefHat,
  X,
  Clock,
  AlertCircle,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { utiliserMutation } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import { toast } from "sonner";

interface IngredientDetecte {
  nom: string;
  quantite_estimee?: string;
  confiance: number;
}

interface RecetteSuggestion {
  nom: string;
  description: string;
  temps_preparation?: number;
  ingredients_utilises: string[];
  ingredients_manquants: string[];
}

interface ResultatPhotoFrigo {
  ingredients_detectes: IngredientDetecte[];
  recettes_suggerees: RecetteSuggestion[];
}

export default function PhotoFrigoPage() {
  const [preview, setPreview] = useState<string | null>(null);
  const [fichier, setFichier] = useState<File | null>(null);
  const [resultat, setResultat] = useState<ResultatPhotoFrigo | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const analyseMutation = utiliserMutation(
    async () => {
      if (!fichier) throw new Error("Aucun fichier sélectionné");
      const formData = new FormData();
      formData.append("file", fichier);
      const { data } = await clientApi.post(
        "/api/v1/suggestions/photo-frigo",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      return data as ResultatPhotoFrigo;
    },
    {
      onSuccess: (data: ResultatPhotoFrigo) => {
        setResultat(data);
        toast.success(
          `${data.ingredients_detectes.length} ingrédients détectés, ${data.recettes_suggerees.length} recettes suggérées`
        );
      },
      onError: () => toast.error("Erreur lors de l'analyse de la photo"),
    }
  );

  const handleFichier = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      toast.error("L'image ne doit pas dépasser 10 MB");
      return;
    }
    setFichier(file);
    setResultat(null);
    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const reinitialiser = () => {
    setPreview(null);
    setFichier(null);
    setResultat(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          📸 Photo Frigo → Recettes
        </h1>
        <p className="text-muted-foreground">
          Prenez une photo de votre frigo et obtenez des suggestions de recettes
        </p>
      </div>

      {/* Upload */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            Photo du frigo
          </CardTitle>
          <CardDescription>
            Prenez une photo ou importez une image de vos ingrédients
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFichier}
            className="hidden"
          />

          {preview ? (
            <div className="relative">
              <img
                src={preview}
                alt="Aperçu frigo"
                className="w-full max-h-[400px] object-contain rounded-lg border"
              />
              <Button
                variant="destructive"
                size="icon"
                className="absolute top-2 right-2"
                onClick={reinitialiser}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div
              className="flex flex-col items-center justify-center gap-4 rounded-lg border-2 border-dashed p-12 cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => inputRef.current?.click()}
            >
              <ImagePlus className="h-12 w-12 text-muted-foreground" />
              <div className="text-center">
                <p className="font-medium">
                  Cliquez pour importer ou prendre une photo
                </p>
                <p className="text-sm text-muted-foreground">
                  JPEG, PNG — max 10 MB
                </p>
              </div>
            </div>
          )}

          {fichier && (
            <Button
              onClick={() => analyseMutation.mutate(undefined)}
              disabled={analyseMutation.isPending}
              className="w-full"
            >
              {analyseMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyse en cours...
                </>
              ) : (
                <>
                  <ChefHat className="mr-2 h-4 w-4" />
                  Analyser et suggérer des recettes
                </>
              )}
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Résultats */}
      {resultat && (
        <>
          {/* Ingrédients détectés */}
          <Card>
            <CardHeader>
              <CardTitle>
                🥕 Ingrédients détectés ({resultat.ingredients_detectes.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {resultat.ingredients_detectes.map((ing, i) => (
                  <Badge
                    key={i}
                    variant={ing.confiance > 0.8 ? "default" : "secondary"}
                    className="text-sm py-1 px-3"
                  >
                    {ing.nom}
                    {ing.quantite_estimee && (
                      <span className="ml-1 opacity-70">
                        ({ing.quantite_estimee})
                      </span>
                    )}
                  </Badge>
                ))}
              </div>
              {resultat.ingredients_detectes.length === 0 && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <AlertCircle className="h-4 w-4" />
                  Aucun ingrédient détecté. Essayez avec une photo plus claire.
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recettes suggérées */}
          <Card>
            <CardHeader>
              <CardTitle>
                🍳 Recettes suggérées ({resultat.recettes_suggerees.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {resultat.recettes_suggerees.map((recette, i) => (
                <div
                  key={i}
                  className="rounded-lg border p-4 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">{recette.nom}</h3>
                    {recette.temps_preparation && (
                      <Badge variant="outline" className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {recette.temps_preparation} min
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {recette.description}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {recette.ingredients_utilises.map((ing, j) => (
                      <Badge key={j} variant="default" className="text-xs">
                        ✓ {ing}
                      </Badge>
                    ))}
                    {recette.ingredients_manquants.map((ing, j) => (
                      <Badge key={j} variant="destructive" className="text-xs">
                        ✗ {ing}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
              {resultat.recettes_suggerees.length === 0 && (
                <p className="text-muted-foreground text-center py-4">
                  Aucune recette suggérée. Essayez d&apos;avoir plus d&apos;ingrédients visibles.
                </p>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
