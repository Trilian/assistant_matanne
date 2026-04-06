"use client";

import { useState, useRef, useEffect } from "react";
import {
  Camera,
  ImagePlus,
  Loader2,
  ChefHat,
  X,
  Clock,
  AlertCircle,
  Plus,
  PackagePlus,
  History,
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
import { ajouterArticlesBulk } from "@/bibliotheque/api/inventaire";
import { toast } from "sonner";

type Zone = "frigo" | "placard" | "congelateur";

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

interface RecetteBD {
  id: number;
  nom: string;
  description: string;
  nb_ingredients_matches: number;
  pourcentage_match: number;
  ingredients_utilises: string[];
}

interface ResultatPhotoFrigo {
  ingredients_detectes: IngredientDetecte[];
  recettes_suggerees: RecetteSuggestion[];
  recettes_db: RecetteBD[];
  sync_possible: boolean;
}

interface AnalyseHistorique {
  date: string;
  zone: Zone;
  nb_ingredients: number;
  nb_recettes: number;
}

const ZONES: { value: Zone; label: string; emoji: string }[] = [
  { value: "frigo", label: "Réfrigérateur", emoji: "🧊" },
  { value: "placard", label: "Placard", emoji: "🗄️" },
  { value: "congelateur", label: "Congélateur", emoji: "❄️" },
];

const LS_KEY = "photo_frigo_historique";

function chargerHistorique(): AnalyseHistorique[] {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY) ?? "[]");
  } catch {
    return [];
  }
}

function sauvegarderHistorique(entry: AnalyseHistorique) {
  const hist = chargerHistorique();
  hist.unshift(entry);
  localStorage.setItem(LS_KEY, JSON.stringify(hist.slice(0, 5)));
}

function ContenuPhotoFrigo() {
  const [preview, setPreview] = useState<string | null>(null);
  const [fichier, setFichier] = useState<File | null>(null);
  const [resultat, setResultat] = useState<ResultatPhotoFrigo | null>(null);
  const [zonesSelectionnees, setZonesSelectionnees] = useState<Zone[]>(["frigo"]);
  const [historique, setHistorique] = useState<AnalyseHistorique[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const zonePrincipale = zonesSelectionnees[0] ?? "frigo";

  useEffect(() => {
    setHistorique(chargerHistorique());
  }, []);

  const analyseMutation = utiliserMutation(
    async () => {
      if (!fichier) throw new Error("Aucun fichier sélectionné");
      const formData = new FormData();
      formData.append("file", fichier);
      const params = new URLSearchParams();
      zonesSelectionnees.forEach((z) => params.append("zones", z));
      const { data } = await clientApi.post(
        `/api/v1/suggestions/photo-frigo?${params.toString()}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      return data as ResultatPhotoFrigo;
    },
    {
      onSuccess: (data: ResultatPhotoFrigo) => {
        setResultat(data);
        const entry: AnalyseHistorique = {
          date: new Date().toISOString(),
          zone: zonePrincipale,
          nb_ingredients: data.ingredients_detectes.length,
          nb_recettes: data.recettes_suggerees.length + data.recettes_db.length,
        };
        sauvegarderHistorique(entry);
        setHistorique(chargerHistorique());
        toast.success(
          `${data.ingredients_detectes.length} ingrédients détectés, ${data.recettes_db.length + data.recettes_suggerees.length} recettes trouvées`
        );
      },
      onError: () => toast.error("Erreur lors de l'analyse de la photo"),
    }
  );

  const ajouterToutMutation = utiliserMutation(
    async () => {
      if (!resultat) throw new Error("Pas de résultat");
      const articles = resultat.ingredients_detectes.map((ing) => ({
        nom: ing.nom,
        quantite: ing.quantite_estimee ? parseFloat(ing.quantite_estimee) || 1 : 1,
      }));
      return ajouterArticlesBulk(articles, zonePrincipale);
    },
    {
      onSuccess: (data) => toast.success(data.message),
      onError: () => toast.error("Erreur lors de l'ajout au stock"),
    }
  );

  const ajouterUnMutation = utiliserMutation(
    async (nom: string) => {
      return ajouterArticlesBulk([{ nom, quantite: 1 }], zonePrincipale);
    },
    {
      onSuccess: (data) => toast.success(data.message),
      onError: () => toast.error("Erreur lors de l'ajout"),
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

  const basculerZone = (zone: Zone) => {
    setZonesSelectionnees((precedentes) => {
      if (precedentes.includes(zone)) {
        if (precedentes.length === 1) {
          return precedentes;
        }
        return precedentes.filter((z) => z !== zone);
      }
      return [...precedentes, zone];
    });
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

      {/* Zone selector */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Zone à analyser</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            {ZONES.map((z) => (
              <button
                key={z.value}
                onClick={() => basculerZone(z.value)}
                className={`flex flex-col items-center gap-1 rounded-lg border-2 px-4 py-3 text-sm font-medium transition-colors ${
                  zonesSelectionnees.includes(z.value)
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border hover:border-primary/50 hover:bg-muted/50"
                }`}
              >
                <span className="text-2xl">{z.emoji}</span>
                {z.label}
              </button>
            ))}
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            Sélection multiple activée: {zonesSelectionnees.length} zone(s) analysée(s).
          </p>
        </CardContent>
      </Card>

      {/* Upload */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            {zonesSelectionnees.length === 1
              ? `Photo du ${ZONES.find((z) => z.value === zonePrincipale)?.label.toLowerCase()}`
              : `Photo multi-zones (${zonesSelectionnees.length})`}
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
                alt="Aperçu"
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
              <div className="flex items-center justify-between">
                <CardTitle>
                  🥕 Ingrédients détectés ({resultat.ingredients_detectes.length})
                </CardTitle>
                {resultat.sync_possible && resultat.ingredients_detectes.length > 0 && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => ajouterToutMutation.mutate(undefined)}
                    disabled={ajouterToutMutation.isPending}
                  >
                    {ajouterToutMutation.isPending ? (
                      <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                    ) : (
                      <PackagePlus className="mr-2 h-3 w-3" />
                    )}
                    Ajouter tout au stock
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {resultat.ingredients_detectes.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {resultat.ingredients_detectes.map((ing, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-1 rounded-full border bg-background pl-3 pr-1 py-1"
                    >
                      <span className="text-sm font-medium">{ing.nom}</span>
                      {ing.quantite_estimee && (
                        <span className="text-xs text-muted-foreground">
                          ({ing.quantite_estimee})
                        </span>
                      )}
                      <Badge
                        variant={ing.confiance > 0.8 ? "default" : "secondary"}
                        className="text-xs ml-1"
                      >
                        {Math.round(ing.confiance * 100)}%
                      </Badge>
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-6 w-6 ml-1"
                        onClick={() => ajouterUnMutation.mutate(ing.nom)}
                        title="Ajouter au stock"
                      >
                        <Plus className="h-3 w-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <AlertCircle className="h-4 w-4" />
                  Aucun ingrédient détecté. Essayez avec une photo plus claire.
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recettes de la base — DB matches */}
          {resultat.recettes_db.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>
                  📚 Vos recettes ({resultat.recettes_db.length})
                </CardTitle>
                <CardDescription>
                  Recettes de votre collection correspondant aux ingrédients
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {resultat.recettes_db.map((recette) => (
                  <div key={recette.id} className="rounded-lg border p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">{recette.nom}</h3>
                      <Badge
                        variant={recette.pourcentage_match >= 70 ? "default" : "secondary"}
                        className="text-xs"
                      >
                        {Math.round(recette.pourcentage_match)}% match
                      </Badge>
                    </div>
                    {recette.description && (
                      <p className="text-sm text-muted-foreground">{recette.description}</p>
                    )}
                    <div className="flex flex-wrap gap-1">
                      {recette.ingredients_utilises.map((ing, j) => (
                        <Badge key={j} variant="outline" className="text-xs">
                          ✓ {ing}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Suggestions IA */}
          <Card>
            <CardHeader>
              <CardTitle>
                ✨ Suggestions IA ({resultat.recettes_suggerees.length})
              </CardTitle>
              <CardDescription>Idées de recettes générées par l&apos;IA</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {resultat.recettes_suggerees.map((recette, i) => (
                <div key={i} className="rounded-lg border p-4 space-y-2">
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
                  Aucune suggestion IA. Essayez d&apos;avoir plus d&apos;ingrédients visibles.
                </p>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Historique */}
      {historique.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <History className="h-4 w-4" />
              Historique récent
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {historique.map((h, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-sm rounded-lg border px-3 py-2"
                >
                  <div className="flex items-center gap-2">
                    <span>{ZONES.find((z) => z.value === h.zone)?.emoji}</span>
                    <span className="font-medium">
                      {ZONES.find((z) => z.value === h.zone)?.label}
                    </span>
                    <span className="text-muted-foreground">
                      — {h.nb_ingredients} ingrédients, {h.nb_recettes} recettes
                    </span>
                  </div>
                  <span className="text-muted-foreground text-xs">
                    {new Date(h.date).toLocaleDateString("fr-FR", {
                      day: "numeric",
                      month: "short",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function PhotoFrigoPage() {
  return <ContenuPhotoFrigo />;
}
