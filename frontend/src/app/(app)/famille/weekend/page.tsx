// ═══════════════════════════════════════════════════════════
// Weekend — Idées et planning du week-end
// ═══════════════════════════════════════════════════════════

"use client";

import {
  Palmtree,
  MapPin,
  Calendar,
  Sparkles,
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
import { utiliserRequete } from "@/hooks/utiliser-api";
import { listerActivites } from "@/lib/api/famille";

export default function PageWeekend() {
  // Charger les activités de type sortie/weekend
  const { data: activites, isLoading } = utiliserRequete(
    ["famille", "weekend"],
    () => listerActivites("sortie")
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🌴 Weekend</h1>
        <p className="text-muted-foreground">
          Idées et planification des week-ends
        </p>
      </div>

      {/* Prochain weekend */}
      <Card className="border-primary/30 bg-primary/5">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Ce week-end
          </CardTitle>
          <CardDescription>
            Activités prévues pour le prochain week-end
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 2 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !activites?.length ? (
            <p className="text-sm text-muted-foreground">
              Rien de prévu — planifiez quelque chose !
            </p>
          ) : (
            <div className="space-y-2">
              {activites.slice(0, 5).map((a) => (
                <div
                  key={a.id}
                  className="flex items-center justify-between rounded-md px-3 py-2 hover:bg-accent transition-colors"
                >
                  <div>
                    <p className="text-sm font-medium">{a.titre}</p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(a.date).toLocaleDateString("fr-FR", {
                          weekday: "short",
                          day: "numeric",
                          month: "short",
                        })}
                      </span>
                      {a.lieu && (
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {a.lieu}
                        </span>
                      )}
                    </div>
                  </div>
                  <Badge variant="outline" className="text-xs capitalize">
                    {a.type}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Idées catégories */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Catégories d&apos;idées</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { label: "Nature & Parcs", emoji: "🌿" },
            { label: "Musées & Culture", emoji: "🎨" },
            { label: "Sport & Aventure", emoji: "⛰️" },
            { label: "Gastronomie", emoji: "🍽️" },
            { label: "Jeux & Détente", emoji: "🎲" },
            { label: "Famille & Amis", emoji: "👨‍👩‍👦" },
          ].map(({ label, emoji }) => (
            <Card
              key={label}
              className="hover:bg-accent/50 cursor-pointer transition-colors"
            >
              <CardContent className="flex items-center gap-3 py-4">
                <span className="text-2xl">{emoji}</span>
                <span className="text-sm font-medium">{label}</span>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
