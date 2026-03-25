// ═══════════════════════════════════════════════════════════
// Hub Maison — Briefing contextuel quotidien
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
  AlertTriangle,
  CheckCircle2,
  Clock,
  CloudRain,
  Bell,
} from "lucide-react";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import {
  statsHubMaison,
  obtenirBriefingMaison,
  envoyerRappelsMaison,
} from "@/bibliotheque/api/maison";
import type { AlerteMaison, TacheJourMaison } from "@/types/maison";

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

function niveauVariant(niveau: string): "destructive" | "secondary" | "outline" {
  if (niveau === "CRITIQUE" || niveau === "HAUTE") return "destructive";
  if (niveau === "MOYENNE") return "secondary";
  return "outline";
}

function CarteAlerte({ alerte }: { alerte: AlerteMaison }) {
  const content = (
    <div className="flex items-start gap-2 py-2">
      <AlertTriangle className={`h-4 w-4 mt-0.5 shrink-0 ${alerte.niveau === "CRITIQUE" || alerte.niveau === "HAUTE" ? "text-destructive" : "text-amber-500"}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium leading-tight">{alerte.titre}</p>
        <p className="text-xs text-muted-foreground mt-0.5">{alerte.message}</p>
      </div>
      <Badge variant={niveauVariant(alerte.niveau)} className="text-xs shrink-0">{alerte.niveau}</Badge>
    </div>
  );

  if (alerte.action_url) {
    return <Link href={alerte.action_url}>{content}</Link>;
  }
  return content;
}

function CarteTache({ tache }: { tache: TacheJourMaison }) {
  return (
    <div className="flex items-center gap-2 py-1.5">
      {tache.fait
        ? <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
        : <Clock className="h-4 w-4 text-muted-foreground shrink-0" />
      }
      <span className={`text-sm flex-1 ${tache.fait ? "line-through text-muted-foreground" : ""}`}>
        {tache.nom}
      </span>
      {tache.duree_estimee_min && (
        <span className="text-xs text-muted-foreground">{tache.duree_estimee_min} min</span>
      )}
    </div>
  );
}

export default function PageMaison() {
  const { data: stats } = utiliserRequete(["maison", "hub", "stats"], statsHubMaison);
  const { data: briefing } = utiliserRequete(["maison", "briefing"], obtenirBriefingMaison);

  const { mutate: envoyerRappels, isPending: envoi } = utiliserMutation(
    envoyerRappelsMaison
  );

  const alertesCritiques = briefing?.alertes.filter(
    (a) => a.niveau === "CRITIQUE" || a.niveau === "HAUTE"
  ) ?? [];
  const alertesNormales = briefing?.alertes.filter(
    (a) => a.niveau !== "CRITIQUE" && a.niveau !== "HAUTE"
  ) ?? [];
  const tachesRestantes = briefing?.taches_jour_detail.filter((t) => !t.fait) ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🏡 Maison</h1>
          <p className="text-muted-foreground">
            {briefing?.resume ?? "Projets, jardin, entretien, cellier, contrats, garanties et plus"}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => envoyerRappels(undefined)}
          disabled={envoi}
        >
          <Bell className="h-4 w-4 mr-1.5" />
          {envoi ? "Envoi…" : "Rappels push"}
        </Button>
      </div>

      {/* Stats rapides */}
      {stats && (
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-4">
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.projets_en_cours}</p><p className="text-xs text-muted-foreground">Projets en cours</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className={`text-2xl font-bold ${stats.taches_en_retard > 0 ? "text-destructive" : ""}`}>{stats.taches_en_retard}</p><p className="text-xs text-muted-foreground">Tâches en retard</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.depenses_mois.toFixed(0)} €</p><p className="text-xs text-muted-foreground">Dépenses du mois</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className={`text-2xl font-bold ${stats.contrats_a_renouveler > 0 ? "text-amber-500" : ""}`}>{stats.contrats_a_renouveler}</p><p className="text-xs text-muted-foreground">Contrats actifs</p></CardContent></Card>
        </div>
      )}

      {/* Section Aujourd'hui / Alertes (visibles seulement si données) */}
      {briefing && (alertesCritiques.length > 0 || tachesRestantes.length > 0 || briefing.meteo) && (
        <div className="grid gap-4 md:grid-cols-2">

          {/* Tâches du jour */}
          {tachesRestantes.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Aujourd'hui ({tachesRestantes.length} tâche{tachesRestantes.length > 1 ? "s" : ""})
                </CardTitle>
              </CardHeader>
              <CardContent className="divide-y">
                {tachesRestantes.slice(0, 5).map((t, i) => (
                  <CarteTache key={i} tache={t} />
                ))}
                {tachesRestantes.length > 5 && (
                  <p className="text-xs text-muted-foreground pt-2">
                    +{tachesRestantes.length - 5} autres tâches
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Alertes critiques */}
          {alertesCritiques.length > 0 && (
            <Card className="border-destructive/40">
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2 text-destructive">
                  <AlertTriangle className="h-4 w-4" />
                  Alertes urgentes ({alertesCritiques.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="divide-y">
                {alertesCritiques.map((a, i) => (
                  <CarteAlerte key={i} alerte={a} />
                ))}
              </CardContent>
            </Card>
          )}

          {/* Météo impact */}
          {briefing.meteo && (briefing.meteo.impact_jardin || briefing.meteo.alertes_meteo.length > 0) && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <CloudRain className="h-4 w-4" />
                  Météo &amp; jardin
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-1">
                {briefing.meteo.temperature_min !== undefined && (
                  <p className="text-sm">
                    {briefing.meteo.temperature_min}° / {briefing.meteo.temperature_max}° — {briefing.meteo.description}
                  </p>
                )}
                {briefing.meteo.impact_jardin && (
                  <p className="text-sm text-muted-foreground">{briefing.meteo.impact_jardin}</p>
                )}
                {briefing.meteo.alertes_meteo.map((a, i) => (
                  <Badge key={i} variant="secondary" className="text-xs">{a}</Badge>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Alertes normales */}
          {alertesNormales.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-amber-500" />
                  Rappels ({alertesNormales.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="divide-y">
                {alertesNormales.slice(0, 4).map((a, i) => (
                  <CarteAlerte key={i} alerte={a} />
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Grille des modules */}
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
