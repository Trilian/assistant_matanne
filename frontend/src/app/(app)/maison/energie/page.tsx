// ═══════════════════════════════════════════════════════════
// Énergie — Consommation énergétique
// ═══════════════════════════════════════════════════════════

"use client";

import { Zap, Droplets, Flame, Gauge } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

// Page placeholder — pas d'endpoint backend dédié encore
const COMPTEURS = [
  {
    nom: "Électricité",
    icone: Zap,
    unite: "kWh",
    couleur: "text-yellow-500",
    description: "Consommation électrique",
  },
  {
    nom: "Eau",
    icone: Droplets,
    unite: "m³",
    couleur: "text-blue-500",
    description: "Consommation eau froide/chaude",
  },
  {
    nom: "Gaz",
    icone: Flame,
    unite: "m³",
    couleur: "text-orange-500",
    description: "Consommation gaz naturel",
  },
];

export default function PageEnergie() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">⚡ Énergie</h1>
        <p className="text-muted-foreground">
          Suivi de la consommation énergétique du foyer
        </p>
      </div>

      {/* Compteurs */}
      <div className="grid gap-4 sm:grid-cols-3">
        {COMPTEURS.map((c) => {
          const Icone = c.icone;
          return (
            <Card key={c.nom}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Icone className={`h-5 w-5 ${c.couleur}`} />
                  {c.nom}
                </CardTitle>
                <CardDescription className="text-xs">
                  {c.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">— {c.unite}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Aucun relevé enregistré
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Graphiques placeholder */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Gauge className="h-5 w-5" />
            Évolution mensuelle
          </CardTitle>
          <CardDescription>
            Graphiques de consommation — Recharts à intégrer
          </CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-10 text-muted-foreground">
          <div className="text-center">
            <Zap className="h-10 w-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm">Saisissez vos relevés pour voir l&apos;évolution</p>
            <p className="text-xs mt-1">
              Endpoint API énergie à venir
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
