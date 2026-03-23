// ═══════════════════════════════════════════════════════════
// Anniversaires — Dates importantes
// ═══════════════════════════════════════════════════════════

"use client";

import { Cake, Gift, Calendar } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

// Données statiques pour démarrer — à connecter au backend plus tard
const ANNIVERSAIRES = [
  { nom: "Jules", date: "2024-08-15", type: "Naissance" },
  { nom: "Mariage", date: "2021-06-12", type: "Anniversaire" },
];

function joursAvant(dateStr: string): number {
  const now = new Date();
  const d = new Date(dateStr);
  // Prochain anniversaire cette année ou l'an prochain
  d.setFullYear(now.getFullYear());
  if (d < now) d.setFullYear(now.getFullYear() + 1);
  return Math.ceil((d.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

export default function PageAnniversaires() {
  const anniversairesTries = [...ANNIVERSAIRES].sort(
    (a, b) => joursAvant(a.date) - joursAvant(b.date)
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🎂 Anniversaires</h1>
        <p className="text-muted-foreground">
          Dates importantes à ne pas oublier
        </p>
      </div>

      {/* Prochain */}
      {anniversairesTries.length > 0 && (
        <Card className="border-primary/30 bg-primary/5">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Gift className="h-5 w-5 text-primary" />
              Prochain anniversaire
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-lg font-semibold">
                  {anniversairesTries[0].nom}
                </p>
                <p className="text-sm text-muted-foreground">
                  {anniversairesTries[0].type}
                </p>
              </div>
              <Badge className="text-sm">
                Dans {joursAvant(anniversairesTries[0].date)} jours
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Liste */}
      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Tous les anniversaires</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {anniversairesTries.map((a) => {
            const jours = joursAvant(a.date);
            return (
              <Card key={a.nom}>
                <CardContent className="flex items-center justify-between py-4">
                  <div className="flex items-center gap-3">
                    <Cake className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">{a.nom}</p>
                      <p className="text-xs text-muted-foreground flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(a.date).toLocaleDateString("fr-FR", {
                          day: "numeric",
                          month: "long",
                        })}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant={jours <= 30 ? "default" : "secondary"}
                    className="text-xs"
                  >
                    {jours}j
                  </Badge>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
