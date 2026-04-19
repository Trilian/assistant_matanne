// ═══════════════════════════════════════════════════════════
// Formulaire Recette — Composant partagé création/édition
// ═══════════════════════════════════════════════════════════

"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Plus, Trash2, Loader2, Camera, Sparkles, Baby } from "lucide-react";
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
import { Textarea } from "@/composants/ui/textarea";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/composants/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { schemaRecette, type DonneesRecette } from "@/bibliotheque/validateurs-cuisine";
import { utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import { creerRecette, genererDepuisPhoto, genererVersionJules, modifierRecette, sauvegarderVersionJulesManuelle } from "@/bibliotheque/api/recettes";
import type { Recette } from "@/types/recettes";

interface PropsFormulaireRecette {
  recetteExistante?: Recette;
  modeSimple?: boolean;
}

export function FormulaireRecette({ recetteExistante, modeSimple = false }: PropsFormulaireRecette) {
  const router = useRouter();
  const invalider = utiliserInvalidation();
  const estEdition = !!recetteExistante;
  const inputPhotoRef = useRef<HTMLInputElement | null>(null);

  // État pour l'onglet Jules (édition uniquement)
  const [julesForm, setJulesForm] = useState({
    instructions_modifiees: recetteExistante?.version_jules?.instructions_modifiees ?? "",
    notes_bebe: recetteExistante?.version_jules?.notes_bebe ?? "",
    modifications_resume: (recetteExistante?.version_jules?.modifications_resume ?? []).join(", "),
  });
  const [enRegenerationJules, setEnRegenerationJules] = useState(false);

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
          instructions: recetteExistante.etapes && recetteExistante.etapes.length > 0
            ? recetteExistante.etapes.map((e) => e.description).join("\n")
            : (recetteExistante.instructions ?? ""),
          temps_preparation: recetteExistante.temps_preparation ?? undefined,
          temps_cuisson: recetteExistante.temps_cuisson ?? undefined,
          portions: recetteExistante.portions ?? undefined,
          difficulte: recetteExistante.difficulte ?? undefined,
          categorie: recetteExistante.categorie ?? "",
          compatible_cookeo: recetteExistante.compatible_cookeo ?? false,
          compatible_monsieur_cuisine: recetteExistante.compatible_monsieur_cuisine ?? false,
          compatible_airfryer: recetteExistante.compatible_airfryer ?? false,
          instructions_cookeo: recetteExistante.instructions_cookeo ?? "",
          instructions_monsieur_cuisine: recetteExistante.instructions_monsieur_cuisine ?? "",
          instructions_airfryer: recetteExistante.instructions_airfryer ?? "",
          ingredients: recetteExistante.ingredients.map((ing) => ({
            nom: ing.nom,
            quantite: ing.quantite ?? undefined,
            unite: ing.unite ?? "",
          })),
        }
      : {
          nom: "",
          categorie: "Plat",
          compatible_cookeo: false,
          compatible_monsieur_cuisine: false,
          compatible_airfryer: false,
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
      onSuccess: async (recette) => {
        await _sauvegarderJulesSiRempli(recette.id);
        invalider(["recettes"]);
        invalider(["recette", String(recette.id)]);
        router.push(`/cuisine/recettes/${recette.id}`);
      },
    }
  );

  const { mutate: genererPhoto, isPending: generationPhotoEnCours } = utiliserMutation(
    (file: File) => genererDepuisPhoto(file),
    {
      onSuccess: (recette) => {
        invalider(["recettes"]);
        router.push(`/cuisine/recettes/${recette.id}`);
      },
    }
  );

  // Sauvegarde Jules lors du submit si les champs sont remplis
  async function _sauvegarderJulesSiRempli(recetteId: number) {
    if (!estEdition) return;
    const { instructions_modifiees, notes_bebe, modifications_resume } = julesForm;
    if (!instructions_modifiees && !notes_bebe) return;
    await sauvegarderVersionJulesManuelle(recetteId, {
      instructions_modifiees: instructions_modifiees || undefined,
      notes_bebe: notes_bebe || undefined,
      modifications_resume: modifications_resume
        ? modifications_resume.split(",").map((s) => s.trim()).filter(Boolean)
        : [],
    });
  }

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

      {/* Mode simplifié (4.4) — juste nom + photo */}
      {modeSimple && !estEdition ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Créer rapidement</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <form
              onSubmit={handleSubmit((data) => sauvegarder(data))}
              className="space-y-4"
            >
              <div className="space-y-2">
                <Label htmlFor="nom-simple">Nom de la recette *</Label>
                <Input 
                  id="nom-simple"
                  {...register("nom")} 
                  placeholder="Ex: Gratin dauphinois"
                  className="text-lg"
                />
                {errors.nom && (
                  <p className="text-sm text-destructive">{errors.nom.message}</p>
                )}
              </div>
              
              <div className="border-2 border-dashed rounded-lg p-6 text-center">
                <input
                  ref={inputPhotoRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  aria-label="Choisir une photo pour générer une recette"
                  title="Choisir une photo pour générer une recette"
                  onChange={(event) => {
                    const file = event.target.files?.[0];
                    if (file) genererPhoto(file);
                    event.target.value = "";
                  }}
                />
                <Button
                  type="button"
                  variant="outline"
                  size="lg"
                  disabled={generationPhotoEnCours}
                  onClick={() => inputPhotoRef.current?.click()}
                  className="w-full"
                >
                  <Camera className="mr-2 h-5 w-5" />
                  {generationPhotoEnCours ? "Analyse photo..." : "Ajouter une photo du plat"}
                </Button>
                <p className="text-xs text-muted-foreground mt-2">
                  L'IA générera les détails automatiquement
                </p>
              </div>

              <Button 
                type="submit" 
                size="lg"
                disabled={isPending}
                className="w-full"
              >
                {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Créer
              </Button>
            </form>
          </CardContent>
        </Card>
      ) : (
        <Tabs defaultValue="recette" className="space-y-4">
          {estEdition && (
            <TabsList>
              <TabsTrigger value="recette">🍽️ Recette</TabsTrigger>
              <TabsTrigger value="jules">
                <Baby className="h-3.5 w-3.5 mr-1.5" />
                Version Jules
              </TabsTrigger>
            </TabsList>
          )}

          {!estEdition && (
            <Card>
              <CardContent className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-medium">Générer depuis une photo</p>
                  <p className="text-sm text-muted-foreground">
                    Importez une photo de plat ou de recette et laissez l'IA créer une première version.
                  </p>
                </div>
                <>
                  <input
                    ref={inputPhotoRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    aria-label="Choisir une photo pour générer une recette"
                    title="Choisir une photo pour générer une recette"
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      if (file) genererPhoto(file);
                      event.target.value = "";
                    }}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    disabled={generationPhotoEnCours}
                    onClick={() => inputPhotoRef.current?.click()}
                  >
                    <Camera className="mr-2 h-4 w-4" />
                    {generationPhotoEnCours ? "Analyse photo..." : "Générer depuis une photo"}
                  </Button>
                </>
              </CardContent>
            </Card>
          )}

          <TabsContent value="recette">
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

        {/* Robots de cuisine */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Robots de cuisine</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {([
              { cle: "compatible_cookeo" as const, labelInstr: "instructions_cookeo" as const, label: "Cookeo" },
              { cle: "compatible_monsieur_cuisine" as const, labelInstr: "instructions_monsieur_cuisine" as const, label: "Monsieur Cuisine" },
              { cle: "compatible_airfryer" as const, labelInstr: "instructions_airfryer" as const, label: "Air Fryer" },
            ]).map(({ cle, labelInstr, label }) => (
              <div key={cle} className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-input accent-primary"
                    {...register(cle)}
                  />
                  <span className="text-sm font-medium">{label}</span>
                </label>
                {watch(cle) && (
                  <textarea
                    {...register(labelInstr)}
                    className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    placeholder={`Instructions adaptées pour ${label}\u00a0: températures, durées, accessoires…`}
                  />
                )}
              </div>
            ))}
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
          </TabsContent>

          {estEdition && (
            <TabsContent value="jules" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Baby className="h-4 w-4 text-emerald-600" />
                    Version Jules
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Adaptation de la recette pour Jules (sans sel, sans alcool, texture adaptée).
                    Gérez manuellement ou régénérez via l'IA.
                  </p>
                  <div className="space-y-2">
                    <Label htmlFor="jules-resume">Résumé des adaptations</Label>
                    <input
                      id="jules-resume"
                      className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                      placeholder="sans sel, champignons mixés, sauce à part…"
                      value={julesForm.modifications_resume}
                      onChange={(e) => setJulesForm((f) => ({ ...f, modifications_resume: e.target.value }))}
                    />
                    <p className="text-xs text-muted-foreground">Séparées par des virgules</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="jules-instructions">Instructions adaptées</Label>
                    <Textarea
                      id="jules-instructions"
                      rows={5}
                      placeholder="Instructions simplifiées pour Jules…"
                      value={julesForm.instructions_modifiees}
                      onChange={(e) => setJulesForm((f) => ({ ...f, instructions_modifiees: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="jules-notes">Notes bébé</Label>
                    <Textarea
                      id="jules-notes"
                      rows={2}
                      placeholder="Mixé, sans sel, servir tiède…"
                      value={julesForm.notes_bebe}
                      onChange={(e) => setJulesForm((f) => ({ ...f, notes_bebe: e.target.value }))}
                    />
                  </div>
                  <div className="flex flex-wrap gap-2 pt-1">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      disabled={enRegenerationJules}
                      onClick={async () => {
                        setEnRegenerationJules(true);
                        try {
                          await genererVersionJules(recetteExistante!.id);
                          // Recharger la page pour afficher la nouvelle version
                          router.refresh();
                        } finally {
                          setEnRegenerationJules(false);
                        }
                      }}
                    >
                      <Sparkles className="h-3.5 w-3.5 mr-1.5" />
                      {enRegenerationJules ? "Génération..." : "Régénérer via l'IA"}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      disabled={isPending}
                      onClick={async () => {
                        await _sauvegarderJulesSiRempli(recetteExistante!.id);
                        invalider(["recette", String(recetteExistante!.id)]);
                      }}
                    >
                      Enregistrer les modifications Jules
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          )}
        </Tabs>
        )}
    </div>
  );
}
