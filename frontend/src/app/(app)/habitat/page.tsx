"use client";

import Link from "next/link";
import { Home, Search, Ruler, Armchair, Trees } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirHubHabitat } from "@/bibliotheque/api/habitat";

const BLOCS = [
  {
    titre: "Scenarios",
    description: "Comparer demenager, agrandir ou rester avec un score multi-criteres.",
    chemin: "/habitat/scenarios",
    Icone: Home,
  },
  {
    titre: "Veille Immo",
    description: "Centraliser les annonces et piloter leur statut.",
    chemin: "/habitat/veille-immo",
    Icone: Search,
  },
  {
    titre: "Plans",
    description: "Importer les plans et structurer les pieces.",
    chemin: "/habitat/plans",
    Icone: Ruler,
  },
  {
    titre: "Deco",
    description: "Suivre les projets deco par piece et par budget.",
    chemin: "/habitat/deco",
    Icone: Armchair,
  },
  {
    titre: "Jardin",
    description: "Organiser les zones paysageres du terrain.",
    chemin: "/habitat/jardin",
    Icone: Trees,
  },
];

export default function HabitatPage() {
  const { data } = utiliserRequete(["habitat", "hub"], obtenirHubHabitat);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Habitat</h1>
        <p className="text-muted-foreground">
          Hub de decision et projection logement: scenarios, immo, plans, deco et paysagisme.
        </p>
      </div>

      {data && (
        <div className="grid gap-3 grid-cols-2 md:grid-cols-5">
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.scenarios}</p><p className="text-xs text-muted-foreground">Scenarios</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.annonces}</p><p className="text-xs text-muted-foreground">Annonces</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.plans}</p><p className="text-xs text-muted-foreground">Plans</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.projets_deco}</p><p className="text-xs text-muted-foreground">Projets deco</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.zones_jardin}</p><p className="text-xs text-muted-foreground">Zones jardin</p></CardContent></Card>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {BLOCS.map(({ titre, description, chemin, Icone }) => (
          <Link key={chemin} href={chemin}>
            <Card className="h-full hover:bg-accent/40 transition-colors">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg"><Icone className="h-4 w-4" /> {titre}</CardTitle>
                <CardDescription>{description}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
