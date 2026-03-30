// ═══════════════════════════════════════════════════════════
// Recettes — Marmiton-style cards + kitchen appliance filters
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Plus,
  Search,
  Clock,
  ChefHat,
  Filter,
  Heart,
  CalendarDays,
  Users,
  UtensilsCrossed,
  Flame,
  Wind,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Card, CardContent } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete, utiliserMutationAvecInvalidation } from "@/crochets/utiliser-api";
import { utiliserDelai } from "@/crochets/utiliser-delai";
import {
  listerRecettes,
  listerRecettesSemaine,
  planifierRecetteSemaine,
  deplanifierRecetteSemaine,
} from "@/bibliotheque/api/recettes";
import { DialogueImportRecette } from "@/composants/cuisine/dialogue-import-recette";
import type { Recette } from "@/types/recettes";

const CATEGORIES = [
  "Toutes",
  "Entrée",
  "Plat",
  "Dessert",
  "Accompagnement",
  "Boisson",
  "Petit-déjeuner",
  "Goûter",
  "Snack",
];

const APPAREILS = [
  { cle: "cookeo" as const, label: "Cookeo", icone: Flame },
  { cle: "monsieur_cuisine" as const, label: "Mr Cuisine", icone: UtensilsCrossed },
  { cle: "airfryer" as const, label: "Air Fryer", icone: Wind },
] as const;

type CleAppareil = (typeof APPAREILS)[number]["cle"];

function tempsTotal(r: Recette): number {
  return (r.temps_preparation ?? 0) + (r.temps_cuisson ?? 0);
}

function ApplianceBadges({ recette }: { recette: Recette }) {
  const appareils = [];
  if (recette.compatible_cookeo) appareils.push({ label: "Cookeo", icone: Flame });
  if (recette.compatible_monsieur_cuisine) appareils.push({ label: "Mr Cuisine", icone: UtensilsCrossed });
  if (recette.compatible_airfryer) appareils.push({ label: "Air Fryer", icone: Wind });
  if (appareils.length === 0) return null;
  return (
    <div className="flex gap-1 mt-1">
      {appareils.map((a) => {
        const Ic = a.icone;
        return (
          <Badge key={a.label} variant="outline" className="text-[10px] gap-0.5 px-1 py-0">
            <Ic className="h-2.5 w-2.5" />
            {a.label}
          </Badge>
        );
      })}
    </div>
  );
}

export default function PageRecettes() {
  const [recherche, setRecherche] = useState("");
  const [categorie, setCategorie] = useState("Toutes");
  const [page, setPage] = useState(1);
  const [filtresAppareils, setFiltresAppareils] = useState<Set<CleAppareil>>(new Set());
  const rechercheDelayee = utiliserDelai(recherche, 300);

  const { data, isLoading } = utiliserRequete(
    ["recettes", String(page), rechercheDelayee, categorie],
    () => listerRecettes(page, 20, rechercheDelayee || undefined)
  );

  const { data: planifiees } = utiliserRequete(
    ["recettes", "semaine"],
    listerRecettesSemaine
  );
  const idsPlanifies = new Set((planifiees ?? []).map((r) => r.id));

  const mutationPlanifier = utiliserMutationAvecInvalidation(
    (id: number) => planifierRecetteSemaine(id),
    [["recettes", "semaine"]],
    { onSuccess: () => toast.success("Recette ajoutée au menu de la semaine") }
  );

  const mutationDeplanifier = utiliserMutationAvecInvalidation(
    (id: number) => deplanifierRecetteSemaine(id),
    [["recettes", "semaine"]],
    { onSuccess: () => toast.success("Recette retirée du menu de la semaine") }
  );

  const recettes = data?.items ?? [];
  const totalPages = data?.pages_totales ?? 1;

  // Filtrage client par appareil
  const recettesFiltrees = filtresAppareils.size === 0
    ? recettes
    : recettes.filter((r) => {
        for (const f of filtresAppareils) {
          if (f === "cookeo" && !r.compatible_cookeo) return false;
          if (f === "monsieur_cuisine" && !r.compatible_monsieur_cuisine) return false;
          if (f === "airfryer" && !r.compatible_airfryer) return false;
        }
        return true;
      });

  const toggleAppareil = (cle: CleAppareil) => {
    setFiltresAppareils((prev) => {
      const next = new Set(prev);
      if (next.has(cle)) next.delete(cle);
      else next.add(cle);
      return next;
    });
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📖 Recettes</h1>
          <p className="text-muted-foreground">
            {data?.total ?? 0} recettes dans votre collection
          </p>
        </div>
        <div className="flex gap-2">
          <DialogueImportRecette />
          <Button asChild>
            <Link href="/cuisine/recettes/nouveau">
              <Plus className="mr-2 h-4 w-4" />
              Nouvelle recette
            </Link>
          </Button>
        </div>
      </div>

      {/* Barre de recherche + filtres */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher une recette..."
            value={recherche}
            onChange={(e) => {
              setRecherche(e.target.value);
              setPage(1);
            }}
            className="pl-10"
          />
        </div>
        <Select
          value={categorie}
          onValueChange={(val) => {
            setCategorie(val);
            setPage(1);
          }}
        >
          <SelectTrigger className="w-full sm:w-[180px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {CATEGORIES.map((cat) => (
              <SelectItem key={cat} value={cat}>
                {cat}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Filtres appareils */}
      <div className="flex flex-wrap gap-2">
        {APPAREILS.map((ap) => {
          const Ic = ap.icone;
          const actif = filtresAppareils.has(ap.cle);
          return (
            <Button
              key={ap.cle}
              variant={actif ? "default" : "outline"}
              size="sm"
              onClick={() => toggleAppareil(ap.cle)}
              className="gap-1.5"
            >
              <Ic className="h-4 w-4" />
              {ap.label}
            </Button>
          );
        })}
      </div>

      {/* Grille de recettes */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <Skeleton className="h-40 w-full rounded-t-xl" />
              <CardContent className="pt-3 space-y-2">
                <Skeleton className="h-5 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : recettesFiltrees.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <ChefHat className="h-12 w-12 text-muted-foreground" />
            <div className="text-center">
              <p className="font-medium">Aucune recette trouvée</p>
              <p className="text-sm text-muted-foreground">
                {recherche
                  ? "Essayez avec d'autres termes de recherche"
                  : "Commencez par ajouter votre première recette"}
              </p>
            </div>
            {!recherche && (
              <Button asChild>
                <Link href="/cuisine/recettes/nouveau">
                  <Plus className="mr-2 h-4 w-4" />
                  Créer une recette
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {recettesFiltrees.map((recette) => (
            <div key={recette.id} className="relative group">
              <Link href={`/cuisine/recettes/${recette.id}`}>
                <Card className="overflow-hidden hover:shadow-lg transition-shadow h-full">
                  {/* Photo placeholder */}
                  <div className="relative h-40 bg-gradient-to-br from-orange-100 to-amber-50 dark:from-orange-950 dark:to-amber-950 flex items-center justify-center">
                    {recette.image_url ? (
                      <img
                        src={recette.image_url}
                        alt={recette.nom}
                        className="object-cover w-full h-full"
                      />
                    ) : (
                      <ChefHat className="h-12 w-12 text-orange-300 dark:text-orange-700" />
                    )}
                    {/* Actions overlay */}
                    <div className="absolute top-2 right-2 flex gap-1">
                      {recette.est_favori && (
                        <div className="rounded-full bg-white/80 dark:bg-black/50 p-1">
                          <Heart className="h-4 w-4 text-red-500 fill-red-500" />
                        </div>
                      )}
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          if (idsPlanifies.has(recette.id)) {
                            mutationDeplanifier.mutate(recette.id);
                          } else {
                            mutationPlanifier.mutate(recette.id);
                          }
                        }}
                        title={
                          idsPlanifies.has(recette.id)
                            ? "Retirer du menu de la semaine"
                            : "Ajouter au menu de la semaine"
                        }
                        className="rounded-full bg-white/80 dark:bg-black/50 p-1 hover:bg-white dark:hover:bg-black/70 transition-colors"
                      >
                        <CalendarDays
                          className={`h-4 w-4 ${
                            idsPlanifies.has(recette.id)
                              ? "text-blue-500"
                              : "text-muted-foreground"
                          }`}
                        />
                      </button>
                    </div>
                    {/* Catégorie badge */}
                    {recette.categorie && (
                      <Badge className="absolute bottom-2 left-2 bg-white/90 text-foreground dark:bg-black/70 dark:text-white text-xs">
                        {recette.categorie}
                      </Badge>
                    )}
                  </div>

                  <CardContent className="pt-3 pb-3 space-y-2">
                    <h3 className="font-semibold text-sm line-clamp-1">
                      {recette.nom}
                    </h3>
                    {recette.description && (
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {recette.description}
                      </p>
                    )}

                    {recette.jours_depuis_derniere_cuisson != null && (
                      <div>
                        <Badge variant="outline" className="text-[10px]">
                          Dernière fois il y a {recette.jours_depuis_derniere_cuisson}j
                        </Badge>
                      </div>
                    )}

                    {/* Métadonnées */}
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      {tempsTotal(recette) > 0 && (
                        <span className="flex items-center gap-0.5">
                          <Clock className="h-3 w-3" />
                          {tempsTotal(recette)} min
                        </span>
                      )}
                      {recette.portions && (
                        <span className="flex items-center gap-0.5">
                          <Users className="h-3 w-3" />
                          {recette.portions}
                        </span>
                      )}

                      {recette.difficulte && (
                        <Badge
                          variant={
                            recette.difficulte === "facile"
                              ? "outline"
                              : recette.difficulte === "moyen"
                                ? "secondary"
                                : "destructive"
                          }
                          className="text-[10px] px-1 py-0"
                        >
                          {recette.difficulte}
                        </Badge>
                      )}
                    </div>

                    {/* Appareils compatibles */}
                    <ApplianceBadges recette={recette} />
                  </CardContent>
                </Card>
              </Link>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Précédent
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} / {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Suivant
          </Button>
        </div>
      )}
    </div>
  );
}
