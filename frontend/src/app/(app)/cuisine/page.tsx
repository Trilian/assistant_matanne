// ═══════════════════════════════════════════════════════════
// Hub Cuisine
// ═══════════════════════════════════════════════════════════

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
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

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
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🍽️ Cuisine</h1>
        <p className="text-muted-foreground">
          Recettes, planning repas, courses et inventaire
        </p>
      </div>

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
