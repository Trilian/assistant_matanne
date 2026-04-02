// ═══════════════════════════════════════════════════════════
// Hub Maison — Briefing contextuel quotidien
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Hammer,
  Sprout,
  SprayCan,
  Banknote,
  Package,
  Wrench,
  FileText,
  ShieldCheck,
  Boxes,
  Layers,
  AlertTriangle,
  CheckCircle2,
  Clock,
  CloudRain,
  Bell,
  Wine,
  Zap,
  Sofa,
  Volume2,
  VolumeX,
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
import { GrilleWidgets } from "@/composants/disposition/grille-widgets";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import {
  statsHubMaison,
  obtenirBriefingMaison,
  envoyerRappelsMaison,
} from "@/bibliotheque/api/maison";
import type { AlerteMaison, TacheJourMaison } from "@/types/maison";
import { BandeauIA } from "@/composants/maison/bandeau-ia";
import { CarteConseil, estDismissed } from "@/composants/maison/carte-conseil";
import { obtenirConseilsIA } from "@/bibliotheque/api/maison";
import { CarteNotificationsModule } from "@/composants/disposition/carte-notifications-module";
import { utiliserSyntheseVocale } from "@/crochets/utiliser-synthese-vocale";

// Sections consolidées — 9 modules
const SECTIONS: Array<{ id: string; titre: string; description: string; chemin: string; Icone: typeof Hammer; statKey: StatsKeys | null }> = [
  { id: "visualisation", titre: "Visualisation", description: "Plan 2D/3D de la maison", chemin: "/maison/visualisation", Icone: Layers, statKey: null },
  { id: "menage", titre: "Ménage", description: "Planning et guides ménage", chemin: "/maison/menage", Icone: SprayCan, statKey: null },
  { id: "jardin", titre: "Jardin", description: "Plantes, semis et éco-gestes", chemin: "/maison/jardin", Icone: Sprout, statKey: null },
  { id: "travaux", titre: "Travaux", description: "Projets, entretien et artisans", chemin: "/maison/travaux", Icone: Hammer, statKey: "projets_en_cours" as const },
  { id: "equipements", titre: "Équipements", description: "Inventaire et domotique", chemin: "/maison/equipements", Icone: Boxes, statKey: null },
  { id: "finances", titre: "Finances", description: "Charges, dépenses et énergie", chemin: "/maison/finances", Icone: Banknote, statKey: "depenses_mois" as const },
  { id: "artisans", titre: "Artisans", description: "Carnet de pros et interventions", chemin: "/maison/artisans", Icone: Wrench, statKey: null },
  { id: "diagnostics", titre: "Diagnostics", description: "DPE, amiante, plomb", chemin: "/maison/diagnostics", Icone: ShieldCheck, statKey: "diagnostics_expirant" as const },
  { id: "provisions", titre: "Provisions", description: "Stocks et cellier", chemin: "/maison/provisions", Icone: Package, statKey: "stocks_en_alerte" as const },
  { id: "meubles", titre: "Meubles", description: "Wishlist et achats mobilier", chemin: "/maison/meubles", Icone: Sofa, statKey: null },
  { id: "documents", titre: "Documents", description: "Factures et diagnostics", chemin: "/maison/documents", Icone: FileText, statKey: "diagnostics_expirant" as const },
];

type StatsKeys = "projets_en_cours" | "taches_en_retard" | "depenses_mois" | "stocks_en_alerte" | "diagnostics_expirant";

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
  const { data: conseilsIA } = utiliserRequete(
    ["maison", "conseils-ia"],
    obtenirConseilsIA,
    { staleTime: 2 * 60 * 60 * 1000 }
  );

  const [, setDismisses] = useState(0); // incrémenté pour forcer un re-render après dismiss
  const { estSupporte, enLecture, lire, arreter } = utiliserSyntheseVocale();

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

  const resumeVocal = briefing
    ? `${briefing.resume}. Vous avez ${tachesRestantes.length} taches a faire aujourd'hui et ${alertesCritiques.length} alertes urgentes.`
    : "Le briefing maison n'est pas encore disponible.";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🏡 Maison</h1>
          <p className="text-muted-foreground">
            {briefing?.resume ?? "Projets, jardin, entretien, cellier et plus"}
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

      {estSupporte && (
        <div className="flex items-center gap-2">
          <Button type="button" variant="outline" size="sm" onClick={() => lire(resumeVocal)}>
            <Volume2 className="h-4 w-4 mr-1.5" />
            Lire le briefing
          </Button>
          {enLecture && (
            <Button type="button" variant="ghost" size="sm" onClick={arreter}>
              <VolumeX className="h-4 w-4 mr-1.5" />
              Arrêter
            </Button>
          )}
        </div>
      )}

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Fonctionnalités Avancées</CardTitle>
          <CardDescription>Accès rapide aux nouveautés différenciantes.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-2 md:grid-cols-3">
          <Button asChild variant="outline" size="sm">
            <Link href="/outils">Mode pilote (Outils)</Link>
          </Button>
          <Button asChild variant="outline" size="sm">
            <Link href="/maison/visualisation">Vue jardin 2D/3D</Link>
          </Button>
          <Button asChild variant="outline" size="sm">
            <Link href="/">Score famille (Dashboard)</Link>
          </Button>
        </CardContent>
      </Card>

      <CarteNotificationsModule moduleKey="maison" moduleLabel="Maison" />

      {/* Bandeau IA */}
      <BandeauIA section="general" />

      {/* Stats rapides */}
      {stats && (
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-4">
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.projets_en_cours}</p><p className="text-xs text-muted-foreground">Projets en cours</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className={`text-2xl font-bold ${stats.taches_en_retard > 0 ? "text-destructive" : ""}`}>{stats.taches_en_retard}</p><p className="text-xs text-muted-foreground">Tâches en retard</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.depenses_mois.toFixed(0)} €</p><p className="text-xs text-muted-foreground">Dépenses du mois</p></CardContent></Card>
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

      {/* Jardin — tâches saisonnières */}
      {briefing?.jardin && briefing.jardin.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Sprout className="h-4 w-4 text-green-600" />
              Jardin — à faire ce mois
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              {briefing.jardin.map((item, i) => (
                <li key={i} className="text-sm flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-500 shrink-0" />
                  <span className="flex-1">{item.nom}</span>
                  {item.urgence && <Badge variant="outline" className="text-xs">{item.urgence}</Badge>}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Cellier — alertes péremption */}
      {briefing?.cellier_alertes && briefing.cellier_alertes.length > 0 && (
        <Card className="border-amber-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Wine className="h-4 w-4 text-amber-600" />
              Cellier — à consommer bientôt
            </CardTitle>
          </CardHeader>
          <CardContent className="divide-y">
            {briefing.cellier_alertes.slice(0, 5).map((item, i) => (
              <div key={i} className="flex items-center justify-between py-1.5">
                <span className="text-sm">{item.nom}</span>
                <Badge variant={item.jours_restants <= 3 ? "destructive" : "secondary"} className="text-xs">
                  J-{item.jours_restants}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Énergie — anomalies de consommation */}
      {briefing?.energie_anomalies && briefing.energie_anomalies.length > 0 && (
        <Card className="border-blue-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Zap className="h-4 w-4 text-blue-600" />
              Énergie — anomalies détectées
            </CardTitle>
          </CardHeader>
          <CardContent className="divide-y">
            {briefing.energie_anomalies.slice(0, 3).map((item, i) => (
              <div key={i} className="flex items-start gap-2 py-1.5">
                <AlertTriangle className="h-4 w-4 text-amber-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{item.type}</p>
                  <p className="text-sm">{item.message}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Conseils IA hub */}
      {conseilsIA && conseilsIA.filter(c => !estDismissed(c)).length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold flex items-center gap-2">
              <span>💡</span> Conseils du moment
            </h2>
          </div>
          <div className="grid gap-2 sm:grid-cols-2">
            {conseilsIA
              .filter(c => !estDismissed(c))
              .slice(0, 4)
              .map((conseil, i) => (
                <CarteConseil
                  key={i}
                  conseil={conseil}
                  onDismiss={() => setDismisses(d => d + 1)}
                />
              ))}
          </div>
        </div>
      )}

      {/* Grille des modules */}
      <GrilleWidgets
        stockageCle="widgets:hub:maison"
        items={SECTIONS}
        classeGrille="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
        titre="Modules"
        renderItem={({ titre, description, chemin, Icone, statKey }) => (
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
                      {stats && statKey && stats[statKey] > 0 && (
                        <Badge variant={statKey.includes("retard") || statKey.includes("alerte") || statKey.includes("renouveler") ? "destructive" : "secondary"} className="text-xs">
                          {formatStat(statKey, stats[statKey])} {labelStat(statKey)}
                        </Badge>
                      )}
                    </div>
                    <CardDescription className="text-sm">{description}</CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>
          </Link>
        )}
      />
    </div>
  );
}
