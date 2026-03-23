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
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirTableauBord } from "@/bibliotheque/api/tableau-bord";

const SECTIONS = [
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
  const { data: dashboard } = utiliserRequete(["tableau-bord"], obtenirTableauBord);

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
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{dashboard.repas_aujourd_hui?.length ?? 0}</p><p className="text-xs text-muted-foreground">Repas aujourd'hui</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{dashboard.articles_courses_restants ?? 0}</p><p className="text-xs text-muted-foreground">Articles à acheter</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{dashboard.alertes_inventaire ?? 0}</p><p className="text-xs text-muted-foreground">Alertes inventaire</p></CardContent></Card>
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
                    <CardDescription className="text-sm">
                      {description}
                    </CardDescription>
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
