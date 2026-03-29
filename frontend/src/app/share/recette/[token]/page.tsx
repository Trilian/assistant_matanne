"use client";

import { use, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Skeleton } from "@/composants/ui/skeleton";

interface RecettePublique {
  id: number;
  nom: string;
  description?: string;
  temps_preparation?: number;
  temps_cuisson?: number;
  portions?: number;
  categorie?: string;
  ingredients?: Array<{ nom: string; quantite?: number; unite?: string }>;
  instructions?: string;
}

export default function PageRecettePartagee({ params }: { params: Promise<{ token: string }> }) {
  const { token } = use(params);
  const [recette, setRecette] = useState<RecettePublique | null>(null);
  const [erreur, setErreur] = useState<string | null>(null);
  const [chargement, setChargement] = useState(true);

  useEffect(() => {
    async function charger() {
      setChargement(true);
      setErreur(null);
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiBase}/share/recette/${encodeURIComponent(token)}`);
        if (!res.ok) {
          throw new Error("Lien invalide ou expiré");
        }
        const data = (await res.json()) as RecettePublique;
        setRecette(data);
      } catch (e) {
        setErreur(e instanceof Error ? e.message : "Erreur de chargement");
      } finally {
        setChargement(false);
      }
    }

    charger();
  }, [token]);

  if (chargement) {
    return (
      <div className="mx-auto max-w-3xl p-6 space-y-4">
        <Skeleton className="h-8 w-72" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (erreur || !recette) {
    return (
      <div className="mx-auto max-w-2xl p-6">
        <Card>
          <CardHeader>
            <CardTitle>Recette indisponible</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{erreur ?? "Cette recette n'est plus accessible."}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl p-6 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>{recette.nom}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {recette.description && <p className="text-sm text-muted-foreground">{recette.description}</p>}
          <div className="text-sm text-muted-foreground">
            {recette.portions ? `Portions: ${recette.portions}` : ""}
            {recette.temps_preparation ? ` · Préparation: ${recette.temps_preparation} min` : ""}
            {recette.temps_cuisson ? ` · Cuisson: ${recette.temps_cuisson} min` : ""}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Ingrédients</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc pl-5 space-y-1 text-sm">
            {(recette.ingredients ?? []).map((ing, idx) => (
              <li key={`${ing.nom}-${idx}`}>
                {ing.quantite ? `${ing.quantite}${ing.unite ? ` ${ing.unite}` : ""} ` : ""}
                {ing.nom}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Instructions</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="whitespace-pre-wrap text-sm font-sans">{recette.instructions || "Aucune instruction"}</pre>
        </CardContent>
      </Card>
    </div>
  );
}
