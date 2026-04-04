"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  ChefHat,
  Clock,
  Pause,
  Play,
  RefreshCw,
  ShoppingCart,
  UtensilsCrossed,
} from "lucide-react";

import { listerListesCourses, obtenirListeCourses } from "@/bibliotheque/api/courses";
import { obtenirPlanningSemaine } from "@/bibliotheque/api/planning";
import { obtenirRecette } from "@/bibliotheque/api/recettes";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Skeleton } from "@/composants/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { utiliserRequete } from "@/crochets/utiliser-api";
import type { RepasPlanning } from "@/types/planning";

const HEURES_REPAS: Record<string, number> = {
  petit_dejeuner: 8,
  dejeuner: 12,
  gouter: 16,
  diner: 19,
};

function obtenirLundiCourant(): string {
  const maintenant = new Date();
  const jour = maintenant.getDay();
  const diff = jour === 0 ? -6 : 1 - jour;
  const lundi = new Date(maintenant);
  lundi.setDate(maintenant.getDate() + diff);
  return lundi.toISOString().slice(0, 10);
}

function horodatageRepas(repas: RepasPlanning): number {
  const dateIso = (repas.date_repas || repas.date || "").slice(0, 10);
  if (!dateIso) {
    return Number.MAX_SAFE_INTEGER;
  }

  const heure = HEURES_REPAS[repas.type_repas] ?? 12;
  return new Date(`${dateIso}T${String(heure).padStart(2, "0")}:00:00`).getTime();
}

function trouverProchainRepas(repas: RepasPlanning[]): RepasPlanning | null {
  const tries = [...repas].sort((a, b) => horodatageRepas(a) - horodatageRepas(b));
  const maintenant = Date.now();
  return tries.find((item) => horodatageRepas(item) >= maintenant - 2 * 60 * 60 * 1000) ?? tries[0] ?? null;
}

function libelleTypeRepas(type: RepasPlanning["type_repas"] | undefined): string {
  switch (type) {
    case "petit_dejeuner":
      return "Petit-déjeuner";
    case "dejeuner":
      return "Déjeuner";
    case "gouter":
      return "Goûter";
    case "diner":
      return "Dîner";
    default:
      return "Repas";
  }
}

export default function PageTabletteCuisine() {
  const [layout, setLayout] = useState<"split" | "focus">("split");
  const [actif, setActif] = useState(false);
  const [tempsRestant, setTempsRestant] = useState(30 * 60);
  const [ingredientsCoches, setIngredientsCoches] = useState<Record<string, boolean>>({});
  const [articlesCoches, setArticlesCoches] = useState<Record<string, boolean>>({});
  const lundiCourant = useMemo(() => obtenirLundiCourant(), []);

  const {
    data: planning,
    isLoading: chargementPlanning,
    refetch: rechargerPlanning,
  } = utiliserRequete(["planning", "tablette", lundiCourant], () => obtenirPlanningSemaine(lundiCourant));

  const repasCourant = useMemo(() => trouverProchainRepas(planning?.repas ?? []), [planning?.repas]);

  const { data: recette, isLoading: chargementRecette } = utiliserRequete(
    ["recettes", "tablette", String(repasCourant?.recette_id ?? "aucune")],
    () => obtenirRecette(repasCourant!.recette_id!),
    { enabled: Boolean(repasCourant?.recette_id) }
  );

  const { data: listes } = utiliserRequete(["courses", "tablette", "listes"], listerListesCourses, {
    staleTime: 60 * 1000,
  });

  const listeActiveId = useMemo(() => {
    const source = listes ?? [];
    return source.find((liste) => liste.etat !== "terminee")?.id ?? source[0]?.id ?? null;
  }, [listes]);

  const { data: listeActive } = utiliserRequete(
    ["courses", "tablette", String(listeActiveId ?? "aucune")],
    () => obtenirListeCourses(listeActiveId!),
    { enabled: listeActiveId !== null }
  );

  const totalMinutes = (recette?.temps_preparation ?? 0) + (recette?.temps_cuisson ?? 0);
  const dureeInitiale = Math.max(5, totalMinutes || 30) * 60;

  useEffect(() => {
    setTempsRestant(dureeInitiale);
    setActif(false);
  }, [dureeInitiale, recette?.id, repasCourant?.id]);

  useEffect(() => {
    setIngredientsCoches({});
  }, [recette?.id, repasCourant?.id]);

  useEffect(() => {
    setArticlesCoches({});
  }, [listeActive?.id]);

  useEffect(() => {
    if (!actif || tempsRestant <= 0) {
      return;
    }

    const intervalle = window.setInterval(() => {
      setTempsRestant((precedent) => precedent - 1);
    }, 1000);

    return () => window.clearInterval(intervalle);
  }, [actif, tempsRestant]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const cible = event.target as HTMLElement | null;
      if (cible?.tagName === "INPUT" || cible?.tagName === "TEXTAREA") {
        return;
      }

      if (event.code === "Space") {
        event.preventDefault();
        setActif((precedent) => !precedent);
      }

      if (event.key.toLowerCase() === "l") {
        setLayout((precedent) => (precedent === "split" ? "focus" : "split"));
      }

      if (event.key.toLowerCase() === "r") {
        setTempsRestant(dureeInitiale);
        setActif(false);
      }

      if (event.key === "Escape") {
        window.location.href = "/cuisine";
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [dureeInitiale]);

  const minutes = Math.floor(Math.max(0, tempsRestant) / 60);
  const secondes = Math.max(0, tempsRestant) % 60;

  const etapes = useMemo(() => {
    const source = recette?.instructions?.split(/\r?\n+/).map((ligne) => ligne.trim()).filter(Boolean);
    if (source?.length) {
      return source;
    }
    if (repasCourant?.notes) {
      return repasCourant.notes.split(/\r?\n+/).map((ligne) => ligne.trim()).filter(Boolean);
    }
    return [
      "Préparez les ingrédients et placez-les à portée de main.",
      "Lancez le minuteur et suivez les étapes de cuisson.",
      "Servez dès que la texture et l'assaisonnement sont prêts.",
    ];
  }, [recette?.instructions, repasCourant?.notes]);

  const presetsTimer = useMemo(
    () =>
      Array.from(new Set([5, 10, 15, recette?.temps_preparation ?? 0, recette?.temps_cuisson ?? 0, totalMinutes || 30].filter((valeur) => valeur >= 5))).sort(
        (a, b) => a - b
      ),
    [recette?.temps_cuisson, recette?.temps_preparation, totalMinutes]
  );

  const ingredients = recette?.ingredients ?? [];
  const articlesRestants = (listeActive?.articles ?? []).filter((article) => !article.est_coche).slice(0, 8);
  const titreRecette = recette?.nom ?? repasCourant?.recette_nom ?? repasCourant?.notes ?? "Aucun repas planifié";
  const imageRecette = recette?.image_url ?? `https://picsum.photos/seed/${encodeURIComponent(titreRecette)}/900/500`;
  const badgeTypeRepas = libelleTypeRepas(repasCourant?.type_repas);
  const dateRepas = repasCourant
    ? new Date((repasCourant.date_repas || repasCourant.date || "").slice(0, 10)).toLocaleDateString("fr-FR", {
        weekday: "long",
        day: "numeric",
        month: "long",
      })
    : null;

  const resumeTempsReel = repasCourant
    ? `${badgeTypeRepas} ${dateRepas ?? "du jour"} · ${ingredients.length} ingrédient(s) · ${articlesRestants.length} course(s) restante(s)`
    : "Aucun repas planifié. Utilisez le planning pour préparer la semaine.";

  const panneauRecette = (
    <Card className="overflow-hidden border-orange-200/70 dark:border-orange-900/50 dark:bg-slate-950/70">
      <div className="relative h-44 bg-gradient-to-br from-orange-100 via-amber-50 to-white dark:from-orange-950 dark:via-slate-950 dark:to-slate-900">
        <img
          src={imageRecette}
          alt={`Illustration du plat ${titreRecette}`}
          className="h-full w-full object-cover opacity-80"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-slate-900/30 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 p-4 text-white">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <Badge className="bg-white/90 text-slate-900 hover:bg-white">{badgeTypeRepas}</Badge>
            {dateRepas ? <Badge variant="secondary">{dateRepas}</Badge> : null}
          </div>
          <h2 className="text-2xl font-semibold lg:text-3xl">{titreRecette}</h2>
          {repasCourant?.plat_jules ? (
            <p className="mt-1 text-sm text-orange-100">Version Jules : {repasCourant.plat_jules}</p>
          ) : null}
        </div>
      </div>

      <CardContent className="space-y-5 p-5">
        {chargementPlanning || chargementRecette ? (
          <div className="space-y-3">
            <Skeleton className="h-5 w-2/3" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
        ) : (
          <>
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-xl border bg-muted/40 p-3">
                <p className="text-xs uppercase text-muted-foreground">Temps total</p>
                <p className="mt-1 text-lg font-semibold">{totalMinutes || 30} min</p>
              </div>
              <div className="rounded-xl border bg-muted/40 p-3">
                <p className="text-xs uppercase text-muted-foreground">Préparation</p>
                <p className="mt-1 text-lg font-semibold">{recette?.temps_preparation ?? 0} min</p>
              </div>
              <div className="rounded-xl border bg-muted/40 p-3">
                <p className="text-xs uppercase text-muted-foreground">Portions</p>
                <p className="mt-1 text-lg font-semibold">{recette?.portions ?? repasCourant?.portions ?? 4}</p>
              </div>
            </div>

            <div>
              <p className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                <UtensilsCrossed className="h-4 w-4" />
                Ingrédients à préparer
              </p>
              <div className="space-y-2">
                {ingredients.length > 0 ? (
                  ingredients.map((ingredient, index) => {
                    const cle = `${ingredient.nom}-${index}`;
                    return (
                      <label
                        key={cle}
                        htmlFor={`ingredient-${index}`}
                        className="flex items-center gap-3 rounded-xl border px-3 py-2 text-base hover:bg-muted/40"
                      >
                        <input
                          id={`ingredient-${index}`}
                          type="checkbox"
                          checked={Boolean(ingredientsCoches[cle])}
                          onChange={() =>
                            setIngredientsCoches((precedent) => ({
                              ...precedent,
                              [cle]: !precedent[cle],
                            }))
                          }
                          className="h-5 w-5"
                          aria-label={`Ingrédient prêt : ${ingredient.nom}`}
                        />
                        <span>
                          {ingredient.quantite ?? ""} {ingredient.unite ?? ""} {ingredient.nom}
                        </span>
                      </label>
                    );
                  })
                ) : (
                  <p className="rounded-xl border border-dashed px-3 py-4 text-sm text-muted-foreground">
                    Aucun détail ingrédient n'est encore disponible pour ce repas.
                  </p>
                )}
              </div>
            </div>

            <div>
              <p className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                <ChefHat className="h-4 w-4" />
                Étapes clés
              </p>
              <ol className="space-y-2">
                {etapes.map((etape, index) => (
                  <li key={`${index}-${etape}`} className="flex gap-3 rounded-xl border px-3 py-3 text-base">
                    <span className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-orange-100 font-semibold text-orange-700 dark:bg-orange-950/50 dark:text-orange-200">
                      {index + 1}
                    </span>
                    <span>{etape}</span>
                  </li>
                ))}
              </ol>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );

  const panneauMinuteur = (
    <Card className="border-orange-200/70 dark:border-orange-900/50 dark:bg-slate-950/70">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-xl">
          <Clock className="h-5 w-5 text-orange-600" />
          Minuteur cuisine
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <p className="text-sm text-muted-foreground" aria-live="polite" aria-atomic="true">
          {resumeTempsReel}
        </p>

        <div className="rounded-2xl border bg-gradient-to-br from-orange-50 to-white p-5 text-center dark:from-orange-950/20 dark:to-slate-950">
          <div className="text-6xl font-bold tabular-nums text-orange-600 dark:text-orange-300 lg:text-7xl">
            {String(minutes).padStart(2, "0")}:{String(secondes).padStart(2, "0")}
          </div>
          <p className="mt-2 text-sm text-muted-foreground">
            Raccourcis clavier : <span className="font-mono">Espace</span> pause/démarre · <span className="font-mono">R</span> reset · <span className="font-mono">L</span> change l’affichage
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {presetsTimer.map((minutesPreset) => (
            <Button
              key={minutesPreset}
              type="button"
              variant="outline"
              onClick={() => {
                setTempsRestant(minutesPreset * 60);
                setActif(false);
              }}
            >
              {minutesPreset} min
            </Button>
          ))}
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <Button size="lg" className="text-base" onClick={() => setActif((precedent) => !precedent)}>
            {actif ? <Pause className="mr-2 h-5 w-5" /> : <Play className="mr-2 h-5 w-5" />}
            {actif ? "Pause" : "Démarrer"}
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="text-base"
            onClick={() => {
              setTempsRestant(dureeInitiale);
              setActif(false);
            }}
          >
            Réinitialiser
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  const panneauCourses = (
    <Card className="border-orange-200/70 dark:border-orange-900/50 dark:bg-slate-950/70">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-xl">
          <ShoppingCart className="h-5 w-5 text-orange-600" />
          Courses à proximité
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground">
          {listeActive ? `Liste active : ${listeActive.nom}` : "Aucune liste active trouvée."}
        </p>
        <div className="space-y-2">
          {articlesRestants.length > 0 ? (
            articlesRestants.map((article) => {
              const cle = String(article.id);
              return (
                <label
                  key={article.id}
                  htmlFor={`course-${article.id}`}
                  className="flex items-center gap-3 rounded-xl border px-3 py-3 text-base hover:bg-muted/40"
                >
                  <input
                    id={`course-${article.id}`}
                    type="checkbox"
                    checked={Boolean(articlesCoches[cle])}
                    onChange={() =>
                      setArticlesCoches((precedent) => ({
                        ...precedent,
                        [cle]: !precedent[cle],
                      }))
                    }
                    className="h-5 w-5"
                    aria-label={`Article récupéré : ${article.nom}`}
                  />
                  <div className="flex-1">
                    <p className="font-medium">{article.nom}</p>
                    <p className="text-sm text-muted-foreground">
                      {article.quantite ?? 1} {article.unite ?? ""} · {article.categorie ?? "À classer"}
                    </p>
                  </div>
                </label>
              );
            })
          ) : (
            <p className="rounded-xl border border-dashed px-3 py-4 text-sm text-muted-foreground">
              Rien à acheter pour le moment — la liste est déjà vide ou finalisée.
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="fixed inset-0 flex flex-col bg-gradient-to-br from-orange-50 via-background to-background text-foreground dark:from-slate-950 dark:via-slate-950 dark:to-black">
      <div className="border-b bg-orange-600/95 px-5 py-3 text-white backdrop-blur">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="flex items-center gap-2 text-2xl font-bold">
              <ChefHat className="h-6 w-6" />
              Mode cuisine tablette
            </h1>
            <p className="text-sm text-orange-50/90">Vue épurée pour suivre le prochain repas, le minuteur et la liste de courses sans quitter le plan de travail.</p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="ghost"
              className="text-white hover:bg-orange-700"
              onClick={() => setLayout((precedent) => (precedent === "split" ? "focus" : "split"))}
            >
              {layout === "split" ? "Plein écran" : "Vue scindée"}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="text-white hover:bg-orange-700"
              onClick={() => void rechargerPlanning()}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Actualiser
            </Button>
            <Button asChild size="sm" variant="ghost" className="text-white hover:bg-orange-700">
              <Link href="/cuisine/planning">Planning</Link>
            </Button>
            <Button asChild size="sm" variant="ghost" className="text-white hover:bg-orange-700">
              <Link href="/cuisine">Fermer</Link>
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4 lg:p-6">
        {!repasCourant && !chargementPlanning ? (
          <Card className="mx-auto max-w-2xl border-dashed">
            <CardContent className="flex flex-col items-center gap-4 py-12 text-center">
              <ChefHat className="h-12 w-12 text-muted-foreground" />
              <div>
                <p className="text-lg font-semibold">Aucun repas planifié</p>
                <p className="text-sm text-muted-foreground">Commencez par générer ou compléter le planning hebdomadaire.</p>
              </div>
              <Button asChild>
                <Link href="/cuisine/planning">Ouvrir le planning</Link>
              </Button>
            </CardContent>
          </Card>
        ) : layout === "split" ? (
          <div className="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
            {panneauRecette}
            <div className="space-y-6">
              {panneauMinuteur}
              {panneauCourses}
            </div>
          </div>
        ) : (
          <Tabs defaultValue="recette" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="recette">Recette</TabsTrigger>
              <TabsTrigger value="minuteur">Minuteur</TabsTrigger>
              <TabsTrigger value="courses">Courses</TabsTrigger>
            </TabsList>
            <TabsContent value="recette">{panneauRecette}</TabsContent>
            <TabsContent value="minuteur">{panneauMinuteur}</TabsContent>
            <TabsContent value="courses">{panneauCourses}</TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  );
}
