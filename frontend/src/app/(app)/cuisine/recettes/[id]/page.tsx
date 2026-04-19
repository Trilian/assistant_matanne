// ═══════════════════════════════════════════════════════════
// Recette — Détail d'une recette
// ═══════════════════════════════════════════════════════════

"use client";

import { use, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  CalendarDays,
  Camera,
  Clock,
  Users,
  ChefHat,
  Edit,
  ImageIcon,
  Trash2,
  Heart,
  Printer,
  Baby,
  ShoppingCart,
  Sparkles,
  Pencil,
  Check,
  X,
  Upload,
} from "lucide-react";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { Textarea } from "@/composants/ui/textarea";
import { Input } from "@/composants/ui/input";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import {
  exporterRecettePdf,
  genererPhotoRecetteIA,
  genererVersionJules,
  genererVersionRobot,
  obtenirRecette,
  supprimerRecette,
  enrichirInstructionsRecette,
  uploaderPhotoRecette,
  sauvegarderVersionRobot,
  type AdaptationRobotManuelle,
} from "@/bibliotheque/api/recettes";
import { obtenirScoreEcologiqueRecette } from "@/bibliotheque/api/ia-avancee";
import { formaterDuree } from "@/bibliotheque/utils";
import { ConvertisseurInline } from "@/composants/cuisine/convertisseur-inline";
import { BadgeEcoscore } from "@/composants/cuisine/badge-ecoscore";
import { RadarNutritionFamille } from "@/composants/graphiques/radar-nutrition-famille";
import { toast } from "sonner";
import { useEffect } from "react";
import { utiliserStoreUI } from "@/magasins/store-ui";
import type { VersionRecette } from "@/types/recettes";

export default function PageDetailRecette({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const invalider = utiliserInvalidation();
  const { definirTitrePage } = utiliserStoreUI();

  // État local
  const [editRobot, setEditRobot] = useState<string | null>(null);
  const [robotForm, setRobotForm] = useState<Partial<AdaptationRobotManuelle>>({});
  const [modeCuisson, setModeCuisson] = useState<"standard" | "cookeo" | "monsieur_cuisine" | "airfryer">("standard");
  const [dialogRobotOuvert, setDialogRobotOuvert] = useState(false);
  const [robotSelectionne, setRobotSelectionne] = useState<"cookeo" | "monsieur_cuisine" | "airfryer">("cookeo");
  const inputPhotoRef = useRef<HTMLInputElement | null>(null);

  const { data: recette, isLoading } = utiliserRequete(
    ["recette", id],
    () => obtenirRecette(Number(id))
  );

  const { data: ecoScore } = utiliserRequete(
    ["recette-ecoscore", id],
    () => obtenirScoreEcologiqueRecette(Number(id)),
    { enabled: !!recette, staleTime: 10 * 60 * 1000, retry: false }
  );

  useEffect(() => {
    if (recette?.nom) definirTitrePage(recette.nom);
    return () => definirTitrePage(null);
  }, [recette?.nom, definirTitrePage]);

  const { mutate: supprimer, isPending: enSuppression } = utiliserMutation(
    () => supprimerRecette(Number(id)),
    {
      onSuccess: () => {
        invalider(["recettes"]);
        toast.success("Recette supprimée");
        router.push("/cuisine/recettes");
      },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  const { mutate: adapterPourJules, isPending: enVersionJules } = utiliserMutation(
    () => genererVersionJules(Number(id)),
    {
      onSuccess: () => {
        invalider(["recette", id]);
        toast.success("Version Jules générée et sauvegardée");
      },
      onError: () => toast.error("Impossible de générer la version Jules"),
    }
  );

  const { mutate: genererPhotoIA, isPending: enGenerationPhotoIA } = utiliserMutation(
    () => genererPhotoRecetteIA(Number(id)),
    {
      onSuccess: () => {
        invalider(["recette", id]);
        toast.success("Photo générée !");
      },
      onError: () => toast.error("Impossible de générer une photo"),
    }
  );

  const { mutate: uploaderPhoto, isPending: enUploadPhoto } = utiliserMutation(
    (file: File) => uploaderPhotoRecette(Number(id), file),
    {
      onSuccess: () => {
        invalider(["recette", id]);
        toast.success("Photo mise à jour");
      },
      onError: () => toast.error("Erreur lors de l'upload"),
    }
  );

  const { mutate: sauvegarderRobot, isPending: enSauvegardeRobot } = utiliserMutation(
    (payload: AdaptationRobotManuelle) => sauvegarderVersionRobot(Number(id), payload),
    {
      onSuccess: () => {
        invalider(["recette", id]);
        setEditRobot(null);
        toast.success("Instructions robot sauvegardées");
      },
      onError: () => toast.error("Erreur lors de la sauvegarde"),
    }
  );

  const { mutate: enrichirInstructions, isPending: enEnrichissement } = utiliserMutation(
    () => enrichirInstructionsRecette(Number(id)),
    {
      onSuccess: () => {
        invalider(["recette", id]);
        toast.success("Instructions générées par l'IA");
      },
      onError: () => toast.error("Impossible de générer les instructions"),
    }
  );

  const { mutate: genererRobot, isPending: enGenerationRobot } = utiliserMutation(
    (robot: "cookeo" | "monsieur_cuisine" | "airfryer") => genererVersionRobot(Number(id), robot),
    {
      onSuccess: (_data, robot) => {
        invalider(["recette", id]);
        setDialogRobotOuvert(false);
        setModeCuisson(robot);
        toast.success("Instructions robot générées par l'IA");
      },
      onError: () => toast.error("Impossible de générer les instructions robot"),
    }
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!recette) {
    return (
      <div className="flex flex-col items-center gap-4 py-12">
        <ChefHat className="h-12 w-12 text-muted-foreground" />
        <p className="font-medium">Recette non trouvée</p>
        <Button variant="outline" asChild>
          <Link href="/cuisine/recettes">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Retour aux recettes
          </Link>
        </Button>
      </div>
    );
  }

  const tempsTotal =
    (recette.temps_preparation ?? 0) + (recette.temps_cuisson ?? 0);
  const nutritionDisponible = [
    recette.calories,
    recette.proteines,
    recette.lipides,
    recette.glucides,
  ].some((valeur) => (valeur ?? 0) > 0);

  return (
    <div className="space-y-6 print:space-y-3">
      {/* Navigation */}
      <div className="flex items-center gap-2 print:hidden">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/cuisine/recettes">
            <ArrowLeft className="mr-1 h-4 w-4" />
            Recettes
          </Link>
        </Button>
      </div>

      {/* En-tête */}
      <div className="flex flex-col gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            {recette.nom}
            {recette.est_favori && (
              <Heart className="h-5 w-5 text-red-500 fill-red-500" />
            )}
          </h1>
          {recette.description && (
            <p className="text-muted-foreground mt-1">{recette.description}</p>
          )}
          <div className="flex flex-wrap gap-2 mt-3">
            {recette.categorie && (
              <Badge variant="secondary">{recette.categorie}</Badge>
            )}
            {recette.difficulte && (
              <Badge variant="outline">{recette.difficulte}</Badge>
            )}
            {recette.tags?.map((tag) => (
              <Badge key={tag} variant="outline">
                {tag}
              </Badge>
            ))}
            <BadgeEcoscore grade={ecoScore?.score} />
            {recette.genere_par_ia && (
              <Badge variant="outline" className="text-purple-600 border-purple-300">
                🤖 Générée par l'IA
              </Badge>
            )}
          </div>
        </div>

        {/* Actions principales — Ajouter au planning et Ingrédients → Courses */}
        <div className="flex flex-wrap gap-2 print:hidden">
          <Button variant="default" asChild>
            <Link href={`/cuisine/planning?ajouter_recette=${id}`}>
              <CalendarDays className="mr-2 h-4 w-4" />
              Ajouter au planning
            </Link>
          </Button>
          <Button variant="default" asChild>
            <Link href={`/cuisine/courses?ingredients=${id}`}>
              <ShoppingCart className="mr-2 h-4 w-4" />
              Ingrédients → Courses
            </Link>
          </Button>
        </div>

        {/* Actions supplémentaires */}
        <div className="flex gap-2 flex-wrap print:hidden">
          <Button variant="outline" size="sm" onClick={() => adapterPourJules(undefined)} disabled={enVersionJules}>
            <Baby className="mr-1 h-4 w-4" />
            {enVersionJules ? "Génération..." : recette.version_jules ? "Regénérer Jules (IA)" : "Version Jules (IA)"}
          </Button>
          <Button variant="outline" size="sm" onClick={() => setDialogRobotOuvert(true)}>
            <Sparkles className="mr-1 h-4 w-4" />
            Générer pour un robot
          </Button>
          <Button variant="outline" size="sm" onClick={() => window.print()}>
            <Printer className="mr-1 h-4 w-4" />
            Imprimer
          </Button>
          <Button variant="outline" size="sm" onClick={() => exporterRecettePdf(Number(id)).catch(() => toast.error("Erreur export PDF"))}>
            <Printer className="mr-1 h-4 w-4" />
            PDF
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link href={`/cuisine/recettes/${id}/modifier`}>
              <Edit className="mr-1 h-4 w-4" />
              Modifier
            </Link>
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => {
              if (confirm("Supprimer cette recette ?")) supprimer(undefined);
            }}
            disabled={enSuppression}
          >
            <Trash2 className="mr-1 h-4 w-4" />
            Supprimer
          </Button>
        </div>
      </div>

      {/* Version Jules — lecture seule, géré par l'IA */}
      {recette.version_jules && (
        <CarteAdaptationJules version={recette.version_jules} />
      )}

      {/* Photo du plat */}
      <div className="print:hidden">
        <input
          ref={inputPhotoRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          aria-label="Choisir une photo du plat"
          title="Choisir une photo du plat"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) uploaderPhoto(file);
            e.target.value = "";
          }}
        />
        {recette.image_url ? (
          <div className="relative rounded-xl overflow-hidden">
            <img
              src={recette.image_url}
              alt={recette.nom}
              className="w-full max-h-64 object-cover"
            />
            <div className="absolute bottom-2 right-2 flex gap-2">
              <Button
                size="sm"
                variant="secondary"
                onClick={() => genererPhotoIA(undefined)}
                disabled={enGenerationPhotoIA || enUploadPhoto}
              >
                <Sparkles className="h-3.5 w-3.5 mr-1" />
                {enGenerationPhotoIA ? "Génération..." : "Régénérer"}
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => inputPhotoRef.current?.click()}
                disabled={enUploadPhoto || enGenerationPhotoIA}
              >
                <Upload className="h-3.5 w-3.5 mr-1" />
                {enUploadPhoto ? "Upload..." : "Changer"}
              </Button>
            </div>
          </div>
        ) : (
          <div className="border-2 border-dashed rounded-xl p-5 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-3 text-muted-foreground">
              <ImageIcon className="h-8 w-8 shrink-0" />
              <div>
                <p className="text-sm font-medium text-foreground">Aucune photo</p>
                <p className="text-xs">Générée par l'IA ou importée manuellement</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => genererPhotoIA(undefined)}
                disabled={enGenerationPhotoIA || enUploadPhoto}
              >
                <Sparkles className="h-3.5 w-3.5 mr-1" />
                {enGenerationPhotoIA ? "Génération..." : "Générer avec l'IA"}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => inputPhotoRef.current?.click()}
                disabled={enUploadPhoto || enGenerationPhotoIA}
              >
                <Upload className="h-3.5 w-3.5 mr-1" />
                {enUploadPhoto ? "Upload..." : "Uploader"}
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Métriques */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {recette.temps_preparation != null && (
          <Card>
            <CardContent className="flex items-center gap-2 py-3">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">
                  {formaterDuree(recette.temps_preparation)}
                </p>
                <p className="text-xs text-muted-foreground">Préparation</p>
              </div>
            </CardContent>
          </Card>
        )}
        {recette.temps_cuisson != null && (
          <Card>
            <CardContent className="flex items-center gap-2 py-3">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">
                  {formaterDuree(recette.temps_cuisson)}
                </p>
                <p className="text-xs text-muted-foreground">Cuisson</p>
              </div>
            </CardContent>
          </Card>
        )}
        {recette.portions != null && (
          <Card>
            <CardContent className="flex items-center gap-2 py-3">
              <Users className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">{recette.portions}</p>
                <p className="text-xs text-muted-foreground">Portions</p>
              </div>
            </CardContent>
          </Card>
        )}

      </div>


      {nutritionDisponible && (
        <Card className="overflow-hidden border-sky-200/70 bg-sky-50/40 dark:border-sky-900/50 dark:bg-sky-950/10">
          <CardHeader>
            <CardTitle className="text-lg">Radar nutritionnel</CardTitle>
            <CardDescription>
              Projection par portion comparée à une journée type pour mieux équilibrer la semaine.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)] lg:items-center">
            <RadarNutritionFamille
              nbJours={1}
              totaux={{
                calories: recette.calories ?? 0,
                proteines: recette.proteines ?? 0,
                lipides: recette.lipides ?? 0,
                glucides: recette.glucides ?? 0,
              }}
            />
            <div className="space-y-2 text-sm">
              <p className="font-medium">Repères par portion</p>
              <ul className="space-y-1 text-muted-foreground">
                <li>Calories : <span className="font-medium text-foreground">{recette.calories ?? 0}</span></li>
                <li>Protéines : <span className="font-medium text-foreground">{recette.proteines ?? 0} g</span></li>
                <li>Lipides : <span className="font-medium text-foreground">{recette.lipides ?? 0} g</span></li>
                <li>Glucides : <span className="font-medium text-foreground">{recette.glucides ?? 0} g</span></li>
              </ul>
              <p className="text-xs text-muted-foreground">
                Pratique pour comparer rapidement une recette riche, légère ou adaptée à la semaine de Jules et de la famille.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Ingrédients */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Ingrédients</CardTitle>
            {recette.portions && (
              <CardDescription>Pour {recette.portions} portions</CardDescription>
            )}
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {recette.ingredients.map((ing, i) => (
                <li key={ing.id ?? i} className="flex items-center gap-2 text-sm">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                  <span className="flex-1">
                    {ing.quantite && (
                      <span className="font-medium">
                        {ing.quantite}
                        {ing.unite ? ` ${ing.unite}` : ""}{" "}
                      </span>
                    )}
                    {ing.nom}
                  </span>
                  {ing.quantite && ing.unite && (
                    <ConvertisseurInline
                      valeurInitiale={ing.quantite}
                      uniteInitiale={ing.unite}
                    />
                  )}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Instructions avec sélecteur de mode cuisson */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">Instructions</CardTitle>
                {tempsTotal > 0 && modeCuisson === "standard" && (
                  <CardDescription>Temps total : {formaterDuree(tempsTotal)}</CardDescription>
                )}
              </div>
              {modeCuisson !== "standard" && editRobot !== modeCuisson && recette.versions_robots?.some((v) => v.type_version === modeCuisson && v.instructions_modifiees) && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => {
                    const versionExistante = recette.versions_robots?.find((v) => v.type_version === modeCuisson);
                    setRobotForm({
                      robot: modeCuisson as "cookeo" | "monsieur_cuisine" | "airfryer",
                      instructions_modifiees: versionExistante?.instructions_modifiees ?? "",
                      modifications_resume: versionExistante?.modifications_resume ?? [],
                    });
                    setEditRobot(modeCuisson);
                  }}
                >
                  <Pencil className="h-3.5 w-3.5" />
                </Button>
              )}
            </div>
            {/* Sélecteur de mode cuisson */}
            <div className="flex flex-wrap gap-1.5 pt-2">
              {([
                { key: "standard" as const, label: "🍳 Standard", always: true },
                { key: "cookeo" as const, label: "🍲 Cookeo", always: false },
                { key: "airfryer" as const, label: "🍟 Air Fryer", always: false },
                { key: "monsieur_cuisine" as const, label: "🤖 Monsieur Cuisine", always: false },
              ]).map(({ key, label, always }) => {
                const compatKey = `compatible_${key}` as keyof typeof recette;
                const compatible = always || !!recette[compatKey];
                const hasVersion = always || recette.versions_robots?.some((v) => v.type_version === key);
                if (!always && !compatible && !hasVersion) return null;
                return (
                  <button
                    key={key}
                    onClick={() => { setModeCuisson(key); setEditRobot(null); }}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      modeCuisson === key
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                    }`}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          </CardHeader>
          <CardContent>
            {modeCuisson === "standard" ? (
              /* ── Instructions standard ── */
              recette.etapes && recette.etapes.length > 0 ? (
              <ol className="space-y-3">
                {recette.etapes.map((etape, i) => (
                  <li key={etape.id ?? i} className="flex gap-3 text-sm">
                    <span className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-primary/10 text-primary font-semibold text-xs">
                      {etape.ordre}
                    </span>
                    <div className="flex-1 pt-0.5">
                      {etape.titre && (
                        <p className="font-medium mb-0.5">{etape.titre}</p>
                      )}
                      <p className="text-muted-foreground whitespace-pre-wrap">{etape.description}</p>
                      {etape.duree && (
                        <p className="text-xs text-muted-foreground mt-1">{etape.duree} min</p>
                      )}
                    </div>
                  </li>
                ))}
              </ol>
            ) : recette.instructions ? (
              <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
                {recette.instructions}
              </div>
            ) : (
              <div className="flex flex-col items-start gap-3">
                <p className="text-sm text-muted-foreground">
                  Aucune instruction renseignée
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => enrichirInstructions()}
                  disabled={enEnrichissement}
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  {enEnrichissement ? "Génération en cours…" : "Générer via l'IA"}
                </Button>
              </div>
            )
            ) : (
              /* ── Instructions robot ── */
              (() => {
                const version = recette.versions_robots?.find((v) => v.type_version === modeCuisson);
                const robotLabels: Record<string, string> = { cookeo: "Cookeo", monsieur_cuisine: "Monsieur Cuisine", airfryer: "Air Fryer" };
                const nomRobot = robotLabels[modeCuisson] ?? modeCuisson;

                if (editRobot === modeCuisson) {
                  return (
                    <div className="space-y-3">
                      <div>
                        <p className="text-xs font-medium mb-1 text-muted-foreground">Résumé des adaptations (séparées par virgules)</p>
                        <Input
                          value={robotForm.modifications_resume?.join(", ") ?? ""}
                          onChange={(e) =>
                            setRobotForm((f) => ({
                              ...f,
                              modifications_resume: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                            }))
                          }
                          placeholder="cuisson 15 min, mode mijoter…"
                        />
                      </div>
                      <div>
                        <p className="text-xs font-medium mb-1 text-muted-foreground">Instructions {nomRobot}</p>
                        <Textarea
                          value={robotForm.instructions_modifiees ?? ""}
                          onChange={(e) => setRobotForm((f) => ({ ...f, instructions_modifiees: e.target.value }))}
                          rows={8}
                          placeholder={`Instructions pour ${nomRobot}…`}
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => sauvegarderRobot(robotForm as AdaptationRobotManuelle)} disabled={enSauvegardeRobot}>
                          <Check className="h-3 w-3 mr-1" />
                          {enSauvegardeRobot ? "Sauvegarde…" : "Sauvegarder"}
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => setEditRobot(null)}>
                          <X className="h-3 w-3 mr-1" />
                          Annuler
                        </Button>
                      </div>
                    </div>
                  );
                }

                if (version?.instructions_modifiees) {
                  return (
                    <div className="space-y-3">
                      {!!version.modifications_resume?.length && (
                        <div className="flex flex-wrap gap-1.5">
                          {version.modifications_resume.map((m) => (
                            <Badge key={m} variant="secondary" className="text-xs">{m}</Badge>
                          ))}
                        </div>
                      )}
                      <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
                        {version.instructions_modifiees}
                      </div>
                    </div>
                  );
                }

                return (
                  <div className="flex flex-col items-center gap-3 py-6 text-center">
                    <p className="text-sm text-muted-foreground">
                      Aucune instruction {nomRobot} pour cette recette
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => genererRobot(modeCuisson as "cookeo" | "monsieur_cuisine" | "airfryer")}
                        disabled={enGenerationRobot}
                      >
                        <Sparkles className="h-4 w-4 mr-2" />
                        {enGenerationRobot ? "Génération en cours…" : "Générer via l'IA"}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setRobotForm({
                            robot: modeCuisson as "cookeo" | "monsieur_cuisine" | "airfryer",
                            instructions_modifiees: "",
                            modifications_resume: [],
                          });
                          setEditRobot(modeCuisson);
                        }}
                      >
                        <Pencil className="h-4 w-4 mr-2" />
                        Saisir manuellement
                      </Button>
                    </div>
                  </div>
                );
              })()
            )}
          </CardContent>
        </Card>
      </div>

      <style>{`
        @media print {
          .prose {
            max-width: 100% !important;
          }
          .print\:hidden {
            display: none !important;
          }
        }
      `}</style>

      {/* Dialog — Générer instructions pour un robot */}
      <Dialog open={dialogRobotOuvert} onOpenChange={setDialogRobotOuvert}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Générer des instructions robot</DialogTitle>
          </DialogHeader>
          <div className="py-3">
            <p className="text-sm text-muted-foreground mb-3">
              Choisissez le robot de cuisine pour adapter cette recette.
            </p>
            <Select
              value={robotSelectionne}
              onValueChange={(v) => setRobotSelectionne(v as typeof robotSelectionne)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="cookeo">🍲 Cookeo</SelectItem>
                <SelectItem value="monsieur_cuisine">🤖 Monsieur Cuisine</SelectItem>
                <SelectItem value="airfryer">🍟 Air Fryer</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDialogRobotOuvert(false)}>
              Annuler
            </Button>
            <Button onClick={() => genererRobot(robotSelectionne)} disabled={enGenerationRobot}>
              <Sparkles className="h-4 w-4 mr-2" />
              {enGenerationRobot ? "Génération..." : "Générer"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// ─── Composant : Carte Adaptation Jules ────────────────────────
interface CarteAdaptationJulesProps {
  version: VersionRecette;
}

function CarteAdaptationJules({ version }: CarteAdaptationJulesProps) {
  return (
    <Card className="border-emerald-200/70 bg-emerald-50/30 dark:border-emerald-800/50 dark:bg-emerald-950/10">
      <CardHeader className="pb-2">
        <CardTitle className="text-base flex items-center gap-2">
          <Baby className="h-4 w-4 text-emerald-600" />
          Version Jules
          <span className="ml-auto text-xs font-normal text-muted-foreground">Générée par l'IA</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        {!!version.modifications_resume?.length && (
          <ul className="list-disc pl-4 space-y-0.5">
            {version.modifications_resume.map((a) => <li key={a}>{a}</li>)}
          </ul>
        )}
        {version.instructions_modifiees && (
          <p className="text-muted-foreground whitespace-pre-line">{version.instructions_modifiees}</p>
        )}
        {version.notes_bebe && (
          <p className="text-xs text-emerald-800 dark:text-emerald-300 bg-emerald-100 dark:bg-emerald-900/40 rounded p-2">
            {version.notes_bebe}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
