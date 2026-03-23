// ═══════════════════════════════════════════════════════════
// Hub Maison
// ═══════════════════════════════════════════════════════════

import Link from "next/link";
import {
  Hammer,
  Sprout,
  SprayCan,
  Receipt,
  Banknote,
  Zap,
  Package,
} from "lucide-react";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const SECTIONS = [
  { titre: "Projets", description: "Travaux et améliorations", chemin: "/maison/projets", Icone: Hammer },
  { titre: "Jardin", description: "Plantes et calendrier semis", chemin: "/maison/jardin", Icone: Sprout },
  { titre: "Entretien", description: "Tâches ménagères et appareils", chemin: "/maison/entretien", Icone: SprayCan },
  { titre: "Charges", description: "Factures et abonnements", chemin: "/maison/charges", Icone: Receipt },
  { titre: "Dépenses", description: "Suivi des dépenses maison", chemin: "/maison/depenses", Icone: Banknote },
  { titre: "Énergie", description: "Consommation énergétique", chemin: "/maison/energie", Icone: Zap },
  { titre: "Stocks", description: "Stocks non-alimentaires", chemin: "/maison/stocks", Icone: Package },
];

export default function PageMaison() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🏡 Maison</h1>
        <p className="text-muted-foreground">
          Projets, jardin, entretien, charges et dépenses
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
