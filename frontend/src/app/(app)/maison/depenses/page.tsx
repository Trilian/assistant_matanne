// ═══════════════════════════════════════════════════════════
// Dépenses Maison — Suivi des dépenses
// ═══════════════════════════════════════════════════════════

"use client";

import { Banknote, ShoppingCart, TrendingDown, ArrowUpRight } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

// Page placeholder — pas d'endpoint backend dédié encore
const CATEGORIES_DEPENSES = [
  { nom: "Courses", icone: ShoppingCart, montant: 0, couleur: "text-blue-500" },
  { nom: "Travaux", icone: ArrowUpRight, montant: 0, couleur: "text-orange-500" },
  { nom: "Équipement", icone: Banknote, montant: 0, couleur: "text-purple-500" },
  { nom: "Divers", icone: TrendingDown, montant: 0, couleur: "text-gray-500" },
];

export default function PageDepenses() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">💸 Dépenses</h1>
        <p className="text-muted-foreground">
          Suivi des dépenses maison par catégorie
        </p>
      </div>

      {/* Résumé mensuel placeholder */}
      <Card className="border-primary/30 bg-primary/5">
        <CardContent className="py-4 text-center">
          <p className="text-3xl font-bold">0,00 €</p>
          <p className="text-sm text-muted-foreground">
            Total du mois en cours
          </p>
        </CardContent>
      </Card>

      {/* Catégories */}
      <div className="grid gap-3 sm:grid-cols-2">
        {CATEGORIES_DEPENSES.map((cat) => {
          const Icone = cat.icone;
          return (
            <Card key={cat.nom} className="hover:bg-accent/50 transition-colors">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Icone className={`h-4 w-4 ${cat.couleur}`} />
                  {cat.nom}
                </CardTitle>
                <CardDescription className="text-xs">
                  Ce mois
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-lg font-semibold">
                  {cat.montant.toLocaleString("fr-FR", {
                    style: "currency",
                    currency: "EUR",
                  })}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          <Banknote className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p>Suivi des dépenses détaillé à venir</p>
          <p className="text-xs mt-1">
            Intégration avec le module budget famille en cours
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
