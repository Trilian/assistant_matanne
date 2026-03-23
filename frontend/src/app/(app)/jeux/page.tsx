// ═══════════════════════════════════════════════════════════
// Hub Jeux — avec stats en temps réel
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import { Trophy, Ticket, Star } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirStatsParis } from "@/bibliotheque/api/jeux";

const SECTIONS = [
  { titre: "Paris sportifs", description: "Suivi des paris", chemin: "/jeux/paris", Icone: Trophy },
  { titre: "Loto", description: "Tirages Loto", chemin: "/jeux/loto", Icone: Ticket },
  { titre: "Euromillions", description: "Tirages Euromillions", chemin: "/jeux/euromillions", Icone: Star },
];

export default function PageJeux() {
  const { data: stats } = utiliserRequete(["jeux", "stats-paris"], obtenirStatsParis);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🎮 Jeux</h1>
        <p className="text-muted-foreground">
          Paris sportifs et tirages
        </p>
      </div>

      {/* Stats rapides */}
      {stats && (
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-3">
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.total_paris ?? 0}</p><p className="text-xs text-muted-foreground">Total paris</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.benefice?.toFixed(0) ?? "—"} €</p><p className="text-xs text-muted-foreground">Bénéfice</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.taux_reussite?.toFixed(0) ?? "—"}%</p><p className="text-xs text-muted-foreground">Taux de réussite</p></CardContent></Card>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SECTIONS.map(({ titre, description, chemin, Icone }) => (
          <Link key={chemin} href={chemin}>
            <Card className="hover:bg-accent/50 transition-colors h-full">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-primary/10 p-2">
                    <Icone className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-base">{titre}</CardTitle>
                    <CardDescription className="text-sm">{description}</CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
