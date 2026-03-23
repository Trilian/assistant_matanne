// ═══════════════════════════════════════════════════════════
// Hub Maison — avec stats en temps réel
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import {
  Hammer,
  Sprout,
  SprayCan,
  Receipt,
  Banknote,
  Zap,
  Package,
  Wine,
  Wrench,
  FileText,
  ShieldCheck,
  ClipboardCheck,
  Leaf,
} from "lucide-react";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { statsHubMaison } from "@/bibliotheque/api/maison";

const SECTIONS = [
  { titre: "Projets", description: "Travaux et améliorations", chemin: "/maison/projets", Icone: Hammer, statKey: "projets_en_cours" as const },
  { titre: "Jardin", description: "Plantes et calendrier semis", chemin: "/maison/jardin", Icone: Sprout, statKey: null },
  { titre: "Entretien", description: "Tâches ménagères et appareils", chemin: "/maison/entretien", Icone: SprayCan, statKey: "taches_en_retard" as const },
  { titre: "Charges", description: "Factures et abonnements", chemin: "/maison/charges", Icone: Receipt, statKey: null },
  { titre: "Dépenses", description: "Suivi des dépenses maison", chemin: "/maison/depenses", Icone: Banknote, statKey: "depenses_mois" as const },
  { titre: "Énergie", description: "Consommation énergétique", chemin: "/maison/energie", Icone: Zap, statKey: null },
  { titre: "Stocks", description: "Stocks non-alimentaires", chemin: "/maison/stocks", Icone: Package, statKey: "stocks_en_alerte" as const },
  { titre: "Cellier", description: "Cave et garde-manger", chemin: "/maison/cellier", Icone: Wine, statKey: null },
  { titre: "Artisans", description: "Carnet d'adresses et interventions", chemin: "/maison/artisans", Icone: Wrench, statKey: null },
  { titre: "Contrats", description: "Assurances, énergie, abonnements", chemin: "/maison/contrats", Icone: FileText, statKey: "contrats_a_renouveler" as const },
  { titre: "Garanties", description: "Appareils et SAV", chemin: "/maison/garanties", Icone: ShieldCheck, statKey: "garanties_expirant" as const },
  { titre: "Diagnostics", description: "Diagnostics immobiliers", chemin: "/maison/diagnostics", Icone: ClipboardCheck, statKey: "diagnostics_expirant" as const },
  { titre: "Éco-Tips", description: "Actions écologiques", chemin: "/maison/eco-tips", Icone: Leaf, statKey: null },
];

type StatsKeys = "projets_en_cours" | "taches_en_retard" | "depenses_mois" | "stocks_en_alerte" | "contrats_a_renouveler" | "garanties_expirant" | "diagnostics_expirant";

function formatStat(key: StatsKeys, val: number): string {
  if (key === "depenses_mois") return `${val.toFixed(0)} €`;
  return String(val);
}

function labelStat(key: StatsKeys): string {
  const map: Record<StatsKeys, string> = {
    projets_en_cours: "en cours",
    taches_en_retard: "en retard",
    depenses_mois: "ce mois",
    stocks_en_alerte: "alertes",
    contrats_a_renouveler: "à renouveler",
    garanties_expirant: "expirent bientôt",
    diagnostics_expirant: "à renouveler",
  };
  return map[key] ?? "";
}

export default function PageMaison() {
  const { data: stats } = utiliserRequete(["maison", "hub", "stats"], statsHubMaison);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🏡 Maison</h1>
        <p className="text-muted-foreground">
          Projets, jardin, entretien, cellier, contrats, garanties et plus
        </p>
      </div>

      {/* Stats rapides */}
      {stats && (
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-4">
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.projets_en_cours}</p><p className="text-xs text-muted-foreground">Projets en cours</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold text-destructive">{stats.taches_en_retard}</p><p className="text-xs text-muted-foreground">Tâches en retard</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.depenses_mois.toFixed(0)} €</p><p className="text-xs text-muted-foreground">Dépenses du mois</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.contrats_a_renouveler}</p><p className="text-xs text-muted-foreground">Contrats actifs</p></CardContent></Card>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SECTIONS.map(({ titre, description, chemin, Icone, statKey }) => (
          <Link key={chemin} href={chemin}>
            <Card className="hover:bg-accent/50 transition-colors h-full">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-primary/10 p-2">
                    <Icone className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">{titre}</CardTitle>
                      {stats && statKey && (stats as unknown as Record<string, number>)[statKey] > 0 && (
                        <Badge variant={statKey.includes("retard") || statKey.includes("alerte") || statKey.includes("renouveler") ? "destructive" : "secondary"} className="text-xs">
                          {formatStat(statKey, (stats as unknown as Record<string, number>)[statKey])} {labelStat(statKey)}
                        </Badge>
                      )}
                    </div>
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
