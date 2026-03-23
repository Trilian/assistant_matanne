// ═══════════════════════════════════════════════════════════
// Hub Jeux
// ═══════════════════════════════════════════════════════════

import Link from "next/link";
import { Trophy, Ticket, Star } from "lucide-react";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const SECTIONS = [
  { titre: "Paris sportifs", description: "Suivi des paris", chemin: "/jeux/paris", Icone: Trophy },
  { titre: "Loto", description: "Tirages Loto", chemin: "/jeux/loto", Icone: Ticket },
  { titre: "Euromillions", description: "Tirages Euromillions", chemin: "/jeux/euromillions", Icone: Star },
];

export default function PageJeux() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🎮 Jeux</h1>
        <p className="text-muted-foreground">
          Paris sportifs et tirages
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
