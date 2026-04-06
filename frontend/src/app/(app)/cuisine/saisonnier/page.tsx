"use client";

import Link from "next/link";
import { CalendarDays, Leaf, Sparkles, ChefHat } from "lucide-react";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { SkeletonPage } from "@/composants/ui/skeleton-page";
import { EtatVide } from "@/composants/ui/etat-vide";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirCalendrierSaisonnier } from "@/bibliotheque/api/recettes";

const COULEURS_CATEGORIES: Record<string, string> = {
  legume: "bg-green-100 text-green-800 border-green-200",
  fruit: "bg-orange-100 text-orange-800 border-orange-200",
  aromate: "bg-emerald-100 text-emerald-800 border-emerald-200",
  produit_mer: "bg-blue-100 text-blue-800 border-blue-200",
  champignon: "bg-amber-100 text-amber-800 border-amber-200",
};

export default function PageCalendrierSaisonnier() {
  const { data, isLoading } = utiliserRequete(
    ["calendrier-saisonnier"],
    obtenirCalendrierSaisonnier
  );

  if (isLoading) {
    return <SkeletonPage lignes={10} />;
  }

  if (!data) {
    return (
      <EtatVide
        titre="Calendrier indisponible"
        description="Impossible de charger les produits de saison pour le moment."
      />
    );
  }

  const pairesDuMoment = data.paires_saison.filter(
    (paire) => paire.saison === data.saison_courante
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Calendrier saisonnier</h1>
          <p className="text-muted-foreground">
            Fruits, légumes, aromates et produits de la mer au meilleur moment.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="gap-1">
            <Leaf className="h-3.5 w-3.5" />
            Saison actuelle : {data.saison_courante}
          </Badge>
          <Button asChild variant="outline" size="sm">
            <Link href="/cuisine/recettes">
              <ChefHat className="mr-2 h-4 w-4" />
              Voir les recettes
            </Link>
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CalendarDays className="h-5 w-5" />
            Vue mensuelle
          </CardTitle>
          <CardDescription>
            Le mois en cours est mis en avant pour faciliter la planification des repas.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {data.calendrier.map((mois) => {
              const estActuel = mois.mois === data.mois_courant;
              return (
                <div
                  key={mois.mois}
                  className={`rounded-lg border p-4 ${estActuel ? "border-primary bg-primary/5" : "bg-background"}`}
                >
                  <div className="mb-3 flex items-center justify-between">
                    <h3 className="font-semibold">{mois.nom}</h3>
                    {estActuel ? <Badge>En cours</Badge> : null}
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {mois.ingredients.slice(0, 12).map((ingredient) => (
                      <span
                        key={`${mois.mois}-${ingredient.nom}`}
                        className={`rounded-full border px-2 py-1 text-xs ${COULEURS_CATEGORIES[ingredient.categorie] ?? "bg-muted text-foreground"}`}
                      >
                        {ingredient.nom}
                      </span>
                    ))}
                    {mois.ingredients.length > 12 ? (
                      <span className="rounded-full border px-2 py-1 text-xs text-muted-foreground">
                        +{mois.ingredients.length - 12} autres
                      </span>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            Idées de saison
          </CardTitle>
          <CardDescription>
            Associations classiques pour cuisiner avec les produits du moment.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2">
            {pairesDuMoment.map((paire) => (
              <div key={paire.description} className="rounded-lg border p-3">
                <p className="font-medium">{paire.description}</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  {paire.ingredients.join(" • ")}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
