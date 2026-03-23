"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const NUMEROS_PRINCIPAUX = 50;
const ETOILES = 12;

function genererGrilleAleatoire() {
  const nums: number[] = [];
  while (nums.length < 5) {
    const n = Math.floor(Math.random() * NUMEROS_PRINCIPAUX) + 1;
    if (!nums.includes(n)) nums.push(n);
  }
  nums.sort((a, b) => a - b);

  const etoiles: number[] = [];
  while (etoiles.length < 2) {
    const e = Math.floor(Math.random() * ETOILES) + 1;
    if (!etoiles.includes(e)) etoiles.push(e);
  }
  etoiles.sort((a, b) => a - b);

  return { numeros: nums, etoiles };
}

import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function EuromillionsPage() {
  const [grille, setGrille] = useState(genererGrilleAleatoire);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">⭐ Euromillions</h1>

      <Card>
        <CardHeader>
          <CardTitle>Générateur de grille</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <p className="text-sm text-muted-foreground mb-3">
              5 numéros (1-{NUMEROS_PRINCIPAUX})
            </p>
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

          <div>
            <p className="text-sm text-muted-foreground mb-3">
              2 étoiles (1-{ETOILES})
            </p>
            <div className="flex gap-2">
              {grille.etoiles.map((e, i) => (
                <span
                  key={i}
                  className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-yellow-500 text-white text-lg font-bold"
                >
                  ⭐ {e}
                </span>
              ))}
            </div>
          </div>

          <Button onClick={() => setGrille(genererGrilleAleatoire())}>
            🎲 Nouvelle grille
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Informations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="text-center p-4 rounded-lg bg-muted">
              <p className="text-3xl font-bold text-primary">5 + 2</p>
              <p className="text-sm text-muted-foreground mt-1">Numéros à choisir</p>
            </div>
            <div className="text-center p-4 rounded-lg bg-muted">
              <p className="text-3xl font-bold text-primary">1/139M</p>
              <p className="text-sm text-muted-foreground mt-1">Probabilité jackpot</p>
            </div>
            <div className="text-center p-4 rounded-lg bg-muted">
              <p className="text-3xl font-bold text-primary">13</p>
              <p className="text-sm text-muted-foreground mt-1">Rangs de gains</p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Badge>Mardi</Badge>
            <Badge>Vendredi</Badge>
            <Badge variant="outline">2,50 € / grille</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
