"use client";

import Link from "next/link";
import { ArrowRight, Bot, Heart, NotebookText } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";

const REDISTRIBUTION = [
  {
    titre: "Mode Pilote Automatique",
    description: "La configuration du pilotage IA est maintenant centralisée dans Outils.",
    href: "/outils",
    label: "Aller vers Outils",
    Icone: Bot,
  },
  {
    titre: "Score Famille Hebdo",
    description: "Le score est intégré directement dans le Dashboard pour le suivi quotidien.",
    href: "/",
    label: "Aller vers Dashboard",
    Icone: Heart,
  },
  {
    titre: "Journal Familial",
    description: "Le résumé familial automatique est maintenant visible dans le hub Famille.",
    href: "/famille",
    label: "Aller vers Famille",
    Icone: NotebookText,
  },
];

export default function PageAvance() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Fonctionnalités Avancées</h1>
        <p className="text-muted-foreground">
          Cette page sert désormais de hub de transition vers les modules métier.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {REDISTRIBUTION.map(({ titre, description, href, label, Icone }) => (
          <Card key={href}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Icone className="h-4 w-4" />
                {titre}
              </CardTitle>
              <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild className="w-full" variant="outline">
                <Link href={href}>
                  {label}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}