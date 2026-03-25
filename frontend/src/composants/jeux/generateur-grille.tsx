"use client";

import { useState } from "react";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { AlertTriangle } from "lucide-react";
import { utiliserMutation } from "@/crochets/utiliser-api";
import type { GrilleGeneree } from "@/types/jeux";

type Strategie = "statistique" | "aleatoire" | "ia";

interface GenerateurGrilleProps {
  typeJeu: "loto" | "euromillions";
  genererFn: (strategie: Strategie, sauvegarder: boolean) => Promise<GrilleGeneree>;
  labelSpecial?: string;
  couleurSpecial?: string;
}

export function GenerateurGrille({
  typeJeu,
  genererFn,
  labelSpecial = typeJeu === "loto" ? "N° Chance" : "Étoiles",
  couleurSpecial = typeJeu === "loto" ? "bg-yellow-500" : "bg-yellow-500",
}: GenerateurGrilleProps) {
  const [strategie, setStrategie] = useState<Strategie>("statistique");
  const [grille, setGrille] = useState<GrilleGeneree | null>(null);

  const mutation = utiliserMutation(
    (s: Strategie) => genererFn(s, false),
    { onSuccess: (data) => setGrille(data) }
  );

  const strategies: { value: Strategie; label: string; emoji: string }[] = [
    { value: "statistique", label: "Statistique", emoji: "📊" },
    { value: "aleatoire", label: "Aléatoire", emoji: "🎲" },
    { value: "ia", label: "IA", emoji: "🤖" },
  ];

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Générateur de grilles</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Toggle stratégie */}
        <div className="flex gap-2">
          {strategies.map((s) => (
            <Button
              key={s.value}
              size="sm"
              variant={strategie === s.value ? "default" : "outline"}
              onClick={() => setStrategie(s.value)}
            >
              {s.emoji} {s.label}
            </Button>
          ))}
        </div>

        <Button
          onClick={() => mutation.mutate(strategie)}
          disabled={mutation.isPending}
          className="w-full"
        >
          {mutation.isPending ? "Génération…" : `Générer une grille (${strategie})`}
        </Button>

        {mutation.isPending && <Skeleton className="h-16 w-full" />}

        {grille && (
          <div className="space-y-3">
            {/* Numéros principaux */}
            <div>
              <p className="text-sm text-muted-foreground mb-2">Numéros</p>
              <div className="flex gap-2">
                {grille.numeros.map((n, i) => (
                  <span
                    key={i}
                    className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground text-lg font-bold"
                  >
                    {n}
                  </span>
                ))}
              </div>
            </div>

            {/* Spéciaux (chance ou étoiles) */}
            {grille.special.length > 0 && (
              <div>
                <p className="text-sm text-muted-foreground mb-2">{labelSpecial}</p>
                <div className="flex gap-2">
                  {grille.special.map((n, i) => (
                    <span
                      key={i}
                      className={`inline-flex h-12 w-12 items-center justify-center rounded-full ${couleurSpecial} text-white text-lg font-bold`}
                    >
                      {n}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <Badge variant="secondary">{grille.strategie}</Badge>

            {/* Analyse IA */}
            {grille.analyse_ia && (
              <div className="bg-muted p-3 rounded-lg space-y-1 text-sm">
                <p className="font-semibold">🤖 Analyse IA</p>
                <p>{grille.analyse_ia}</p>
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  Le jeu comporte des risques. Jouez de manière responsable.
                </p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
