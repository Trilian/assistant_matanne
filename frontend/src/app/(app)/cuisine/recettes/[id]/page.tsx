// ═══════════════════════════════════════════════════════════
// Recette — Détail d'une recette
// ═══════════════════════════════════════════════════════════

"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  CalendarDays,
  Clock,
  Users,
  ChefHat,
  Edit,
  Trash2,
  Heart,
  Printer,
  Baby,
  ShoppingCart,
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
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import { exporterRecettePdf, genererVersionJules, obtenirRecette, supprimerRecette } from "@/bibliotheque/api/recettes";
import { obtenirScoreEcologiqueRecette } from "@/bibliotheque/api/ia-avancee";
import { ConvertisseurInline } from "@/composants/cuisine/convertisseur-inline";
import { BadgeEcoscore } from "@/composants/cuisine/badge-ecoscore";
import { RadarNutritionFamille } from "@/composants/graphiques/radar-nutrition-famille";
import { toast } from "sonner";
import { useEffect } from "react";
import { utiliserStoreUI } from "@/magasins/store-ui";

export default function PageDetailRecette({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const invalider = utiliserInvalidation();
  const { definirTitrePage } = utiliserStoreUI();
  const [versionJules, setVersionJules] = useState<Awaited<ReturnType<typeof genererVersionJules>> | null>(null);

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
      onSuccess: (data) => {
        setVersionJules(data);
        toast.success("Version Jules générée");
      },
      onError: () => toast.error("Impossible de générer la version Jules"),
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
            {enVersionJules ? "Génération..." : "Version Jules"}
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

      {versionJules && (
        <Card className="border-emerald-200 bg-emerald-50/60 dark:border-emerald-900 dark:bg-emerald-950/20 print:hidden">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Baby className="h-4 w-4" />
              Version Jules
            </CardTitle>
            <CardDescription>{versionJules.nom}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            {!!versionJules.adaptations?.length && (
              <div>
                <p className="font-medium mb-1">Adaptations</p>
                <ul className="list-disc pl-4 space-y-1">
                  {versionJules.adaptations.map((adaptation) => (
                    <li key={adaptation}>{adaptation}</li>
                  ))}
                </ul>
              </div>
            )}
            {!!versionJules.ingredients?.length && (
              <div>
                <p className="font-medium mb-1">Ingrédients adaptés</p>
                <ul className="list-disc pl-4 space-y-1">
                  {versionJules.ingredients.map((ingredient) => (
                    <li key={ingredient}>{ingredient}</li>
                  ))}
                </ul>
              </div>
            )}
            <p className="text-muted-foreground whitespace-pre-line">{versionJules.instructions}</p>
          </CardContent>
        </Card>
      )}

      {/* Métriques */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {recette.temps_preparation != null && (
          <Card>
            <CardContent className="flex items-center gap-2 py-3">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">
                  {recette.temps_preparation} min
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
                  {recette.temps_cuisson} min
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

        {/* Instructions */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">Instructions</CardTitle>
            {tempsTotal > 0 && (
              <CardDescription>Temps total : {tempsTotal} min</CardDescription>
            )}
          </CardHeader>
          <CardContent>
            {recette.etapes && recette.etapes.length > 0 ? (
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
              <p className="text-sm text-muted-foreground">
                Aucune instruction renseignée
              </p>
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
    </div>
  );
}
