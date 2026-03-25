// ═══════════════════════════════════════════════════════════
// Formulaire Recette — Composant partagé création/édition
// ═══════════════════════════════════════════════════════════

"use client";

import { useRouter } from "next/navigation";
import { useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Plus, Trash2, Loader2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { schemaRecette, type DonneesRecette } from "@/bibliotheque/validateurs";
import { utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import { creerRecette, modifierRecette } from "@/bibliotheque/api/recettes";
import type { Recette } from "@/types/recettes";

interface PropsFormulaireRecette {
  recetteExistante?: Recette;
}

export function FormulaireRecette({ recetteExistante }: PropsFormulaireRecette) {
  const router = useRouter();
  const invalider = utiliserInvalidation();
  const estEdition = !!recetteExistante;

  const {
    register,
    handleSubmit,
    control,
    setValue,
    watch,
    formState: { errors },
  } = useForm<DonneesRecette>({
    resolver: zodResolver(schemaRecette) as never,
    defaultValues: recetteExistante
      ? {
          nom: recetteExistante.nom,
          description: recetteExistante.description ?? "",
          instructions: recetteExistante.instructions ?? "",
          temps_preparation: recetteExistante.temps_preparation ?? undefined,
          temps_cuisson: recetteExistante.temps_cuisson ?? undefined,
          portions: recetteExistante.portions ?? undefined,
          difficulte: recetteExistante.difficulte ?? undefined,
          categorie: recetteExistante.categorie ?? "",
          ingredients: recetteExistante.ingredients.map((ing) => ({
            nom: ing.nom,
            quantite: ing.quantite ?? undefined,
            unite: ing.unite ?? "",
          })),
        }
      : {
          nom: "",
          ingredients: [{ nom: "", quantite: undefined, unite: "" }],
        },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "ingredients",
  });

  const { mutate: sauvegarder, isPending } = utiliserMutation(
    (donnees: DonneesRecette) =>
      estEdition
        ? modifierRecette(recetteExistante!.id, donnees)
        : creerRecette(donnees),
    {
      onSuccess: (recette) => {
        invalider(["recettes"]);
        router.push(`/cuisine/recettes/${recette.id}`);
      },
    }
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/cuisine/recettes">
            <ArrowLeft className="mr-1 h-4 w-4" />
            Recettes
          </Link>
        </Button>
      </div>

      <h1 className="text-2xl font-bold tracking-tight">
        {estEdition ? "✏️ Modifier la recette" : "➕ Nouvelle recette"}
      </h1>

      <form
        onSubmit={handleSubmit((data) => sauvegarder(data))}
        className="space-y-6"
      >
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Infos principales */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-lg">Informations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="nom">Nom *</Label>
                <Input id="nom" {...register("nom")} placeholder="Ex: Gratin dauphinois" />
                {errors.nom && (
                  <p className="text-sm text-destructive">{errors.nom.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <textarea
                  id="description"
                  {...register("description")}
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  placeholder="Description courte de la recette..."
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="instructions">Instructions</Label>
                <textarea
                  id="instructions"
                  {...register("instructions")}
                  className="flex min-h-[160px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  placeholder="Étape par étape..."
                />
              </div>
            </CardContent>
          </Card>

          {/* Métadonnées */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Détails</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="temps_preparation">Préparation (min)</Label>
                  <Input
                    id="temps_preparation"
                    type="number"
                    min={0}
                    {...register("temps_preparation")}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="temps_cuisson">Cuisson (min)</Label>
                  <Input
                    id="temps_cuisson"
                    type="number"
                    min={0}
                    {...register("temps_cuisson")}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="portions">Portions</Label>
                <Input
                  id="portions"
                  type="number"
                  min={1}
                  {...register("portions")}
                />
              </div>

              <div className="space-y-2">
                <Label>Difficulté</Label>
                <Select
                  value={watch("difficulte") ?? ""}
                  onValueChange={(val) =>
                    setValue("difficulte", val as DonneesRecette["difficulte"])
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="facile">Facile</SelectItem>
                    <SelectItem value="moyen">Moyen</SelectItem>
                    <SelectItem value="difficile">Difficile</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="categorie">Catégorie</Label>
                <Select
                  value={watch("categorie") ?? ""}
                  onValueChange={(val) => setValue("categorie", val)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner" />
                  </SelectTrigger>
                  <SelectContent>
                    {[
                      "Entrée",
                      "Plat",
                      "Dessert",
                      "Accompagnement",
                      "Boisson",
                      "Petit-déjeuner",
                      "Goûter",
                      "Snack",
                    ].map((c) => (
                      <SelectItem key={c} value={c}>
                        {c}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Ingrédients */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Ingrédients</CardTitle>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => append({ nom: "", quantite: undefined, unite: "" })}
            >
              <Plus className="mr-1 h-4 w-4" />
              Ajouter
            </Button>
          </CardHeader>
          <CardContent>
            {errors.ingredients?.root && (
              <p className="text-sm text-destructive mb-3">
                {errors.ingredients.root.message}
              </p>
            )}
            <div className="space-y-3">
              {fields.map((field, index) => (
                <div key={field.id} className="flex items-center gap-2">
                  <Input
                    {...register(`ingredients.${index}.nom`)}
                    placeholder="Ingrédient"
                    className="flex-1"
                  />
                  <Input
                    {...register(`ingredients.${index}.quantite`)}
                    type="number"
                    min={0}
                    step="any"
                    placeholder="Qté"
                    className="w-20"
                  />
                  <Input
                    {...register(`ingredients.${index}.unite`)}
                    placeholder="Unité"
                    className="w-20"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => fields.length > 1 && remove(index)}
                    disabled={fields.length <= 1}
                    aria-label="Retirer l'ingrédient"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" asChild>
            <Link href="/cuisine/recettes">Annuler</Link>
          </Button>
          <Button type="submit" disabled={isPending}>
            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {estEdition ? "Enregistrer" : "Créer la recette"}
          </Button>
        </div>
      </form>
    </div>
  );
}
