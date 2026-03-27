// ═══════════════════════════════════════════════════════════
// Hub Cuisine — avec stats en temps réel
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import {
  BookOpen,
  CalendarDays,
  ShoppingCart,
  Package,
  CookingPot,
  Leaf,
  CalendarCheck,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirDashboardCuisine } from "@/bibliotheque/api/tableau-bord";

const SECTIONS = [
  {
    titre: "Ma Semaine",
    description: "Assistant planning + courses en 4 étapes",
    chemin: "/cuisine/ma-semaine",
    Icone: CalendarCheck,
  },
  {
    titre: "Recettes",
    description: "Gérer et rechercher vos recettes",
    chemin: "/cuisine/recettes",
    Icone: BookOpen,
  },
  {
    titre: "Planning repas",
    description: "Planifier les repas de la semaine",
    chemin: "/cuisine/planning",
    Icone: CalendarDays,
  },
  {
    titre: "Courses",
    description: "Listes de courses et achats",
    chemin: "/cuisine/courses",
    Icone: ShoppingCart,
  },
  {
    titre: "Inventaire",
    description: "Stock alimentaire et alertes",
    chemin: "/cuisine/inventaire",
    Icone: Package,
  },
  {
    titre: "Batch Cooking",
    description: "Sessions de cuisine en lot",
    chemin: "/cuisine/batch-cooking",
    Icone: CookingPot,
  },
  {
    titre: "Anti-Gaspillage",
    description: "Score et recettes rescue",
    chemin: "/cuisine/anti-gaspillage",
    Icone: Leaf,
  },
];

export default function PageCuisine() {
  const { data: dashboard } = utiliserRequete(["dashboard-cuisine"], obtenirDashboardCuisine);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🍽️ Cuisine</h1>
        <p className="text-muted-foreground">
          Recettes, planning repas, courses et inventaire
        </p>
      </div>

      {/* Stats rapides */}
      {dashboard && (
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-3">
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{dashboard.repas_aujourd_hui.length}</p><p className="text-xs text-muted-foreground">Repas aujourd'hui</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{dashboard.articles_courses_restants}</p><p className="text-xs text-muted-foreground">Articles à acheter</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{dashboard.alertes_inventaire}</p><p className="text-xs text-muted-foreground">Alertes inventaire</p></CardContent></Card>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SECTIONS.map(({ titre, description, chemin, Icone }) => {
          const estMaSemaine = chemin === "/cuisine/ma-semaine";
          const estBatchCooking = chemin === "/cuisine/batch-cooking";
          const nbRepasAujourdhui = dashboard?.repas_aujourd_hui?.length ?? 0;
          const nbRepasHebdo = dashboard?.repas_semaine_count;

          return (
            <Link key={chemin} href={chemin}>
              <Card className="hover:bg-accent/50 transition-colors h-full">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-primary/10 p-2">
                      <Icone className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-base">{titre}</CardTitle>
                      <CardDescription className="text-sm">
                        {description}
                      </CardDescription>
                    </div>
                    {estMaSemaine && nbRepasAujourdhui > 0 && (
                      <span className="shrink-0 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
                        {nbRepasAujourdhui} repas
                      </span>
                    )}
                    {estBatchCooking && dashboard?.batch_en_cours && (
                      <span className="shrink-0 rounded-full bg-orange-500/10 px-2 py-0.5 text-xs font-semibold text-orange-600">
                        En cours
                      </span>
                    )}
                  </div>
                  {estMaSemaine && dashboard && (
                    <div className="mt-2 flex gap-3 text-xs text-muted-foreground">
                      <span>
                        📅 Aujourd&apos;hui : <strong>{nbRepasAujourdhui}</strong> repas prévus
                      </span>
                      {typeof nbRepasHebdo === "number" && (
                        <span>
                          · Semaine : <strong>{nbRepasHebdo}</strong>
                        </span>
                      )}
                    </div>
                  )}
                </CardHeader>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
