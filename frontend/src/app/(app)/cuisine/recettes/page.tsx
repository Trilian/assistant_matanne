// ═══════════════════════════════════════════════════════════
// Recettes — Liste avec recherche, filtres et pagination
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Plus,
  Search,
  Clock,
  ChefHat,
  Star,
  Filter,
  Heart,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { utiliserRequete } from "@/hooks/utiliser-api";
import { utiliserDelai } from "@/hooks/utiliser-delai";
import { listerRecettes } from "@/lib/api/recettes";

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

const DIFFICULTES = [
  { valeur: "toutes", label: "Toutes" },
  { valeur: "facile", label: "Facile" },
  { valeur: "moyen", label: "Moyen" },
  { valeur: "difficile", label: "Difficile" },
];

export default function PageRecettes() {
  const [recherche, setRecherche] = useState("");
  const [categorie, setCategorie] = useState("Toutes");
  const [page, setPage] = useState(1);
  const rechercheDelayee = utiliserDelai(recherche, 300);

  const { data, isLoading } = utiliserRequete(
    ["recettes", String(page), rechercheDelayee, categorie],
    () => listerRecettes(page, 20, rechercheDelayee || undefined)
  );

  const recettes = data?.items ?? [];
  const totalPages = data?.pages_totales ?? 1;

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
        <Button asChild>
          <Link href="/cuisine/recettes/nouveau">
            <Plus className="mr-2 h-4 w-4" />
            Nouvelle recette
          </Link>
        </Button>
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

      {/* Grille de recettes */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-5 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : recettes.length === 0 ? (
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
          {recettes.map((recette) => (
            <Link key={recette.id} href={`/cuisine/recettes/${recette.id}`}>
              <Card className="hover:bg-accent/50 transition-colors h-full">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-base line-clamp-1">
                      {recette.nom}
                    </CardTitle>
                    {recette.est_favori && (
                      <Heart className="h-4 w-4 text-red-500 fill-red-500 shrink-0" />
                    )}
                  </div>
                  {recette.description && (
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {recette.description}
                    </p>
                  )}
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {recette.categorie && (
                      <Badge variant="secondary">{recette.categorie}</Badge>
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
                      >
                        {recette.difficulte}
                      </Badge>
                    )}
                  </div>
                  <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
                    {(recette.temps_preparation || recette.temps_cuisson) && (
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {(recette.temps_preparation ?? 0) +
                          (recette.temps_cuisson ?? 0)}{" "}
                        min
                      </span>
                    )}
                    {recette.portions && (
                      <span>{recette.portions} portions</span>
                    )}
                    {recette.note_moyenne && (
                      <span className="flex items-center gap-1">
                        <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                        {recette.note_moyenne.toFixed(1)}
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
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
