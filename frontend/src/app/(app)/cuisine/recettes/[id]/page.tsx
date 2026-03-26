// ═══════════════════════════════════════════════════════════
// Recette — Détail d'une recette
// ═══════════════════════════════════════════════════════════

"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Clock,
  Users,
  ChefHat,
  Edit,
  Trash2,
  Star,
  Heart,
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
import { Separator } from "@/composants/ui/separator";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import { obtenirRecette, supprimerRecette } from "@/bibliotheque/api/recettes";
import { ConvertisseurInline } from "@/composants/cuisine/convertisseur-inline";
import { toast } from "sonner";

export default function PageDetailRecette({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const invalider = utiliserInvalidation();

  const { data: recette, isLoading } = utiliserRequete(
    ["recette", id],
    () => obtenirRecette(Number(id))
  );

  const { mutate: supprimer, isPending: enSuppression } = utiliserMutation(
    (_: void) => supprimerRecette(Number(id)),
    {
      onSuccess: () => {
        invalider(["recettes"]);
        toast.success("Recette supprimée");
        router.push("/cuisine/recettes");
      },
      onError: () => toast.error("Erreur lors de la suppression"),
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

  return (
    <div className="space-y-6">
      {/* Navigation */}
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/cuisine/recettes">
            <ArrowLeft className="mr-1 h-4 w-4" />
            Recettes
          </Link>
        </Button>
      </div>

      {/* En-tête */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
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
          </div>
        </div>
        <div className="flex gap-2 shrink-0">
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
        {recette.note_moyenne != null && (
          <Card>
            <CardContent className="flex items-center gap-2 py-3">
              <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
              <div>
                <p className="text-sm font-medium">
                  {recette.note_moyenne.toFixed(1)}
                </p>
                <p className="text-xs text-muted-foreground">Note</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

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
            {recette.instructions ? (
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
    </div>
  );
}
