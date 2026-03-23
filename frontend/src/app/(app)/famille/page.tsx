// ═══════════════════════════════════════════════════════════
// Hub Famille — avec stats en temps réel
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import {
  Baby,
  CalendarHeart,
  ListChecks,
  Wallet,
  Palmtree,
  Camera,
  Cake,
  BookUser,
  FileText,
  BookOpenCheck,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirStatsBudget, listerRoutines } from "@/bibliotheque/api/famille";

const SECTIONS = [
  { titre: "Jules", description: "Suivi développement", chemin: "/famille/jules", Icone: Baby },
  { titre: "Activités", description: "Sorties et loisirs", chemin: "/famille/activites", Icone: CalendarHeart },
  { titre: "Routines", description: "Routines quotidiennes", chemin: "/famille/routines", Icone: ListChecks },
  { titre: "Budget", description: "Budget familial", chemin: "/famille/budget", Icone: Wallet },
  { titre: "Weekend", description: "Plans du weekend", chemin: "/famille/weekend", Icone: Palmtree },
  { titre: "Album", description: "Photos de famille", chemin: "/famille/album", Icone: Camera },
  { titre: "Anniversaires", description: "Dates importantes", chemin: "/famille/anniversaires", Icone: Cake },
  { titre: "Contacts", description: "Carnet d'adresses", chemin: "/famille/contacts", Icone: BookUser },
  { titre: "Documents", description: "Documents importants", chemin: "/famille/documents", Icone: FileText },
  { titre: "Journal", description: "Journal familial", chemin: "/famille/journal", Icone: BookOpenCheck },
];

export default function PageFamille() {
  const { data: budget } = utiliserRequete(["famille", "stats-budget"], obtenirStatsBudget);
  const { data: routines } = utiliserRequete(["famille", "routines"], listerRoutines);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">👨‍👩‍👦 Famille</h1>
        <p className="text-muted-foreground">
          Suivi de Jules, activités, routines et vie familiale
        </p>
      </div>

      {/* Stats rapides */}
      {(budget || routines) && (
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-3">
          {budget && (
            <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{budget.total_mois?.toFixed(0) ?? "—"} €</p><p className="text-xs text-muted-foreground">Budget du mois</p></CardContent></Card>
          )}
          {routines && (
            <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{routines.length}</p><p className="text-xs text-muted-foreground">Routines actives</p></CardContent></Card>
          )}
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
