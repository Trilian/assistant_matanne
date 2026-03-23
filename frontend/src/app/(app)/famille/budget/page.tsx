// ═══════════════════════════════════════════════════════════
// Budget Famille — Dépenses et statistiques
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Wallet,
  TrendingUp,
  Filter,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import dynamic from "next/dynamic";
import { utiliserRequete } from "@/hooks/utiliser-api";
import { listerDepenses, obtenirStatsBudget } from "@/lib/api/famille";

const CamembertBudget = dynamic(
  () => import("@/composants/graphiques/camembert-budget").then((m) => m.CamembertBudget),
  { ssr: false }
);

const CATEGORIES_BUDGET = [
  "tous",
  "alimentation",
  "logement",
  "transport",
  "loisirs",
  "sante",
  "education",
  "vetements",
  "autre",
];

export default function PageBudget() {
  const [categorieFiltre, setCategorieFiltre] = useState("tous");

  const { data: stats, isLoading: chargementStats } = utiliserRequete(
    ["famille", "budget", "stats"],
    obtenirStatsBudget
  );

  const { data: depenses, isLoading: chargementDepenses } = utiliserRequete(
    ["famille", "budget", "depenses", categorieFiltre],
    () =>
      listerDepenses(
        categorieFiltre !== "tous" ? categorieFiltre : undefined
      )
  );

  const totalMois = stats?.total_mois ?? 0;
  const parCategorie = stats?.par_categorie ?? {};
  const categoriesTriees = Object.entries(parCategorie).sort(
    ([, a], [, b]) => b - a
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">💰 Budget</h1>
        <p className="text-muted-foreground">
          Suivi des dépenses familiales
        </p>
      </div>

      {/* Résumé mensuel */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Wallet className="h-8 w-8 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Total du mois</p>
                {chargementStats ? (
                  <Skeleton className="h-8 w-24" />
                ) : (
                  <p className="text-2xl font-bold">
                    {totalMois.toFixed(2)} €
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="sm:col-span-1 lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Répartition par catégorie
            </CardTitle>
          </CardHeader>
          <CardContent>
            {chargementStats ? (
              <Skeleton className="h-16 w-full" />
            ) : categoriesTriees.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Aucune donnée ce mois
              </p>
            ) : (
              <CamembertBudget
                donnees={categoriesTriees.map(([nom, montant]) => ({ nom, montant }))}
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Liste dépenses */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Dépenses</h2>
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <Select value={categorieFiltre} onValueChange={setCategorieFiltre}>
              <SelectTrigger className="w-[160px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES_BUDGET.map((c) => (
                  <SelectItem key={c} value={c}>
                    {c === "tous"
                      ? "Toutes"
                      : c.charAt(0).toUpperCase() + c.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {chargementDepenses ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-14 w-full" />
            ))}
          </div>
        ) : !depenses?.length ? (
          <Card>
            <CardContent className="py-8 text-center text-sm text-muted-foreground">
              Aucune dépense trouvée
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="p-0">
              <div className="divide-y">
                {depenses.map((d) => (
                  <div
                    key={d.id}
                    className="flex items-center justify-between px-4 py-3 hover:bg-accent/50 transition-colors"
                  >
                    <div>
                      <p className="text-sm font-medium">{d.libelle}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <Badge
                          variant="outline"
                          className="text-xs capitalize"
                        >
                          {d.categorie}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {new Date(d.date).toLocaleDateString("fr-FR")}
                        </span>
                      </div>
                    </div>
                    <span className="text-sm font-semibold tabular-nums">
                      {d.montant.toFixed(2)} €
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
