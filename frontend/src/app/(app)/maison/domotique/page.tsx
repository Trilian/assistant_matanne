// ═══════════════════════════════════════════════════════════
// Page Domotique — Catalogue appareils connectés et astuces
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { obtenirAstucesDomotique, type CategoriesDomotique } from "@/bibliotheque/api/maison";
import { utiliserRequete } from "@/crochets/utiliser-api";

const COULEUR_DIFF: Record<string, string> = {
  facile: "bg-green-100 text-green-800",
  moyen: "bg-yellow-100 text-yellow-800",
  difficile: "bg-red-100 text-red-800",
};

type CategorieItem = CategoriesDomotique["categories"][number];
type AppareilItem = CategorieItem["appareils"][number];

function CarteAppareil({ appareil }: { appareil: AppareilItem }) {
  const [ouvert, setOuvert] = useState(false);

  return (
    <Card className="transition-shadow hover:shadow-md cursor-pointer" onClick={() => setOuvert(!ouvert)}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div>
            <CardTitle className="text-sm font-semibold">{appareil.nom}</CardTitle>
            <div className="flex items-center gap-2 mt-1 flex-wrap">
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                  COULEUR_DIFF[appareil.difficulte_installation] ?? "bg-muted"
                }`}
              >
                Installation {appareil.difficulte_installation}
              </span>
              <span className="text-sm font-bold text-primary">~{appareil.prix_estime}€</span>
            </div>
          </div>
          <span className="text-muted-foreground text-sm">{ouvert ? "▲" : "▼"}</span>
        </div>
      </CardHeader>

      {ouvert && (
        <CardContent className="pt-0 space-y-3">
          {/* Avantages */}
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase mb-1.5">Avantages</p>
            <ul className="space-y-1">
              {appareil.avantages.map((a, i) => (
                <li key={i} className="text-sm flex gap-2">
                  <span className="text-green-500 flex-shrink-0">✓</span>
                  {a}
                </li>
              ))}
            </ul>
          </div>

          {/* Cas d'usage */}
          {appareil.cas_usage?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase mb-1.5">Cas d&apos;usage</p>
              <ul className="space-y-1">
                {appareil.cas_usage.map((c, i) => (
                  <li key={i} className="text-sm flex gap-2">
                    <span className="text-blue-500 flex-shrink-0">→</span>
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Compatibilité */}
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase mb-1.5">Compatible avec</p>
            <div className="flex flex-wrap gap-1">
              {appareil.compatible_avec.map((c) => (
                <Badge key={c} variant="outline" className="text-xs">{c}</Badge>
              ))}
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}

export default function DomotiquePage() {
  const [categorieActive, setCategorieActive] = useState<string | null>(null);

  const { data, isLoading } = utiliserRequete(
    ["domotique-astuces"],
    () => obtenirAstucesDomotique()
  );

  const categories = data?.categories ?? [];
  const conseilsGeneraux = data?.conseils_generaux ?? [];

  const categoriesExposees = categorieActive
    ? categories.filter((c) => c.id === categorieActive)
    : categories;

  return (
    <div className="space-y-6 p-4 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold">Domotique</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Rendre votre maison plus intelligente et économe
        </p>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
          Chargement du catalogue...
        </div>
      )}

      {/* Filtres catégories */}
      {categories.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setCategorieActive(null)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              !categorieActive
                ? "bg-primary text-primary-foreground"
                : "bg-muted hover:bg-muted/80"
            }`}
          >
            Tout
          </button>
          {categories.map((c) => (
            <button
              key={c.id}
              onClick={() => setCategorieActive(c.id === categorieActive ? null : c.id)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                categorieActive === c.id
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted hover:bg-muted/80"
              }`}
            >
              {c.icone} {c.nom}
            </button>
          ))}
        </div>
      )}

      {/* Catégories et appareils */}
      {categoriesExposees.map((categorie) => (
        <section key={categorie.id}>
          <h2 className="text-lg font-semibold mb-3">
            {categorie.icone} {categorie.nom}
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {categorie.appareils.map((appareil) => (
              <CarteAppareil key={appareil.id} appareil={appareil} />
            ))}
          </div>
        </section>
      ))}

      {/* Conseils généraux */}
      {conseilsGeneraux.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-3">💡 Conseils généraux</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {conseilsGeneraux.map((conseil, i) => (
              <Card key={i} className="bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900">
                <CardContent className="pt-4">
                  <p className="font-semibold text-sm text-amber-800 dark:text-amber-200 mb-1">
                    {conseil.titre}
                  </p>
                  <p className="text-sm text-amber-700 dark:text-amber-300">{conseil.detail}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
