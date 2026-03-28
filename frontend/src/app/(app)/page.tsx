// ═══════════════════════════════════════════════════════════
// Tableau de bord — Page d'accueil
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ChefHat,
  ShoppingCart,
  CalendarDays,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  Zap,
  Euro,
  Bell,
  Settings2,
} from "lucide-react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import {
  obtenirBilanMensuel,
  obtenirAlertesContextuelles,
  obtenirConfigDashboard,
  obtenirPointsFamille,
  obtenirTableauBord,
  sauvegarderConfigDashboard,
} from "@/bibliotheque/api/tableau-bord";
import { statsDepensesMaison } from "@/bibliotheque/api/maison";
import { evaluerRappels, type RappelItem } from "@/bibliotheque/api/push";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import { clientApi } from "@/bibliotheque/api/client";

const WIDGETS_DEFAUT = {
  metriques: true,
  actions_rapides: true,
  lecture_ia: true,
  rappels: true,
  depenses: true,
  bilan_mensuel: true,
  meteo: true,
  histoire_famille: true,
  alertes_contextuelles: true,
  points_famille: true,
};

type ClesWidget = keyof typeof WIDGETS_DEFAUT;

type MeteoWidget = {
  ville: string;
  temperature: number;
  description: string;
  humidite: number;
  vent: number;
};

type HistoireFamille = {
  date: string;
  total: number;
  items: Array<{
    id: string;
    type: string;
    titre: string;
    description?: string;
    annees_depuis: number;
  }>;
};

export default function PageAccueil() {
  const { utilisateur } = utiliserAuth();
  const { data, isLoading } = utiliserRequete(["tableau-bord"], obtenirTableauBord);
  const { data: statsDepenses } = utiliserRequete(["depenses", "stats"], statsDepensesMaison);
  const { data: rappelsData } = utiliserRequete(["rappels"], evaluerRappels);
  const { data: bilanMensuel } = utiliserRequete(["bilan-mensuel"], obtenirBilanMensuel);
  const { data: configDashboard } = utiliserRequete(["dashboard", "config"], obtenirConfigDashboard);
  const { data: histoireFamille } = utiliserRequete(
    ["famille", "aujourd-hui-histoire"],
    async () => {
      const { data } = await clientApi.get<HistoireFamille>("/famille/aujourd-hui-histoire");
      return data;
    }
  );
  const { data: alertesContextuelles } = utiliserRequete(
    ["dashboard", "alertes-contextuelles"],
    obtenirAlertesContextuelles
  );
  const { data: pointsFamille } = utiliserRequete(
    ["dashboard", "points-famille"],
    obtenirPointsFamille
  );

  const [widgetsStockes, setWidgetsStockes] = utiliserStockageLocal("dashboard-widgets", WIDGETS_DEFAUT);
  const [configOuverte, setConfigOuverte] = utiliserStockageLocal("dashboard-config-open", false);
  const [widgets, setWidgets] = useState(WIDGETS_DEFAUT);
  const [meteo, setMeteo] = useState<MeteoWidget | null>(null);

  const configFusionnee = useMemo(
    () => ({
      ...WIDGETS_DEFAUT,
      ...widgetsStockes,
      ...(configDashboard?.config_dashboard ?? {}),
    }),
    [configDashboard?.config_dashboard, widgetsStockes]
  );

  const { mutate: sauvegarderWidgets } = utiliserMutation(
    (config: Record<string, boolean>) => sauvegarderConfigDashboard(config),
    {
      onError: () => {
        // Fallback localStorage conservé si l'API dashboard échoue.
      },
    }
  );

  useEffect(() => {
    setWidgets(configFusionnee);
  }, [configFusionnee]);

  useEffect(() => {
    let annule = false;

    async function chargerMeteo() {
      try {
        const res = await fetch("https://wttr.in/Paris?format=j1");
        if (!res.ok) return;
        const json = await res.json();
        const actuel = json.current_condition?.[0];
        if (!actuel || annule) return;
        setMeteo({
          ville: json.nearest_area?.[0]?.areaName?.[0]?.value ?? "Paris",
          temperature: Number(actuel.temp_C ?? 0),
          description: actuel.weatherDesc?.[0]?.value ?? "",
          humidite: Number(actuel.humidity ?? 0),
          vent: Number(actuel.windspeedKmph ?? 0),
        });
      } catch {
        if (!annule) setMeteo(null);
      }
    }

    chargerMeteo();
    return () => {
      annule = true;
    };
  }, []);

  function basculerWidget(cle: ClesWidget) {
    const prochain = { ...widgets, [cle]: !widgets[cle] };
    setWidgets(prochain);
    setWidgetsStockes(prochain);
    sauvegarderWidgets(prochain);
  }

  return (
    <div className="space-y-6">
      {/* Salutation */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Bonjour {utilisateur?.nom ?? ""} 👋
          </h1>
          <p className="text-muted-foreground">
            Voici le résumé de votre journée
          </p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setConfigOuverte((v: boolean) => !v)}
          title="Personnaliser le tableau de bord"
          aria-label="Personnaliser le tableau de bord"
        >
          <Settings2 className="h-5 w-5" />
        </Button>
      </div>

      {/* Panneau personnalisation */}
      {configOuverte && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Settings2 className="h-4 w-4" />
              Personnaliser le tableau de bord
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2">
              {(Object.keys(WIDGETS_DEFAUT) as ClesWidget[]).map((cle) => (
                <label key={cle} className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={widgets[cle]}
                    onChange={() => basculerWidget(cle)}
                    className="rounded"
                  />
                  <span className="capitalize">{cle.replace(/_/g, " ")}</span>
                </label>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {widgets.meteo && meteo && (
        <Card className="border-blue-300/50 bg-blue-50/50 dark:border-blue-800/40 dark:bg-blue-950/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Météo rapide</CardTitle>
            <CardDescription>{meteo.ville}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="text-3xl font-bold">{meteo.temperature}°C</p>
                <p className="text-sm text-muted-foreground">{meteo.description}</p>
              </div>
              <div className="text-right text-xs text-muted-foreground">
                <p>💧 {meteo.humidite}%</p>
                <p>💨 {meteo.vent} km/h</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {widgets.histoire_famille && histoireFamille && histoireFamille.total > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Aujourd&apos;hui dans notre histoire</CardTitle>
            <CardDescription>
              {histoireFamille.total} souvenir(s) pour cette date
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {histoireFamille.items.slice(0, 3).map((item) => (
              <div key={item.id} className="rounded-md border px-3 py-2">
                <p className="text-sm font-medium">{item.titre}</p>
                <p className="text-xs text-muted-foreground">
                  Il y a {item.annees_depuis} an(s)
                </p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {widgets.alertes_contextuelles && alertesContextuelles && alertesContextuelles.total > 0 && (
        <Card className="border-amber-300/60 bg-amber-50/50 dark:border-amber-900/40 dark:bg-amber-950/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Alertes contextuelles</CardTitle>
            <CardDescription>Actions recommandées sur les 48 prochaines heures</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {alertesContextuelles.items.map((alerte) => (
              <div key={`${alerte.type}-${alerte.module}`} className="rounded-md border bg-background/70 px-3 py-2">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-medium">{alerte.titre}</p>
                  <span className="text-[11px] uppercase text-muted-foreground">{alerte.module}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">{alerte.message}</p>
                <p className="text-xs mt-1">Action: {alerte.action}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {widgets.points_famille && pointsFamille && (
        <Card className="border-emerald-300/50 bg-emerald-50/50 dark:border-emerald-900/40 dark:bg-emerald-950/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Points famille</CardTitle>
            <CardDescription>Gamification sport, alimentation et anti-gaspi</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-end justify-between">
              <div>
                <p className="text-3xl font-bold">{pointsFamille.total_points}</p>
                <p className="text-xs text-muted-foreground">points cumulés</p>
              </div>
              <div className="text-right text-xs text-muted-foreground space-y-1">
                <p>Sport: {pointsFamille.sport}</p>
                <p>Alimentation: {pointsFamille.alimentation}</p>
                <p>Anti-gaspi: {pointsFamille.anti_gaspi}</p>
              </div>
            </div>
            {!!pointsFamille.badges.length && (
              <div className="flex flex-wrap gap-2 text-xs">
                {pointsFamille.badges.map((badge) => (
                  <span key={badge} className="rounded-full border px-2 py-1">{badge}</span>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Cartes métriques */}
      {widgets.metriques && (
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        <CarteMetrique
          titre="Repas aujourd'hui"
          valeur={data?.repas_aujourd_hui.length ?? 0}
          icone={<ChefHat className="h-4 w-4" />}
          lien="/cuisine/planning"
          chargement={isLoading}
        />
        <CarteMetrique
          titre="Articles à acheter"
          valeur={data?.articles_courses_restants ?? 0}
          icone={<ShoppingCart className="h-4 w-4" />}
          lien="/cuisine/courses"
          chargement={isLoading}
        />
        <CarteMetrique
          titre="Activités semaine"
          valeur={data?.activites_semaine ?? 0}
          icone={<CalendarDays className="h-4 w-4" />}
          lien="/planning"
          chargement={isLoading}
        />
        <CarteMetrique
          titre="Alertes entretien"
          valeur={data?.taches_entretien_urgentes ?? 0}
          icone={<AlertTriangle className="h-4 w-4" />}
          lien="/maison/entretien"
          chargement={isLoading}
          alerte={(data?.taches_entretien_urgentes ?? 0) > 0}
        />
      </div>
      )}

      {/* Actions rapides */}
      {widgets.actions_rapides && (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Actions rapides</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 grid-cols-2 sm:grid-cols-4">
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <Link href="/cuisine/recettes/nouveau">
                <ChefHat className="h-5 w-5" />
                <span className="text-xs">Nouvelle recette</span>
              </Link>
            </Button>
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <Link href="/cuisine/courses">
                <ShoppingCart className="h-5 w-5" />
                <span className="text-xs">Liste courses</span>
              </Link>
            </Button>
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <Link href="/cuisine/planning">
                <CalendarDays className="h-5 w-5" />
                <span className="text-xs">Planning repas</span>
              </Link>
            </Button>
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <Link href="/outils/chat-ia">
                <Sparkles className="h-5 w-5" />
                <span className="text-xs">Chat IA</span>
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
      )}

      {/* Suggestion dîner IA */}
      {widgets.lecture_ia && data?.suggestion_diner && (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Suggestion du soir
            </CardTitle>
            <CardDescription>{data.suggestion_diner}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" size="sm" asChild>
              <Link href="/cuisine/recettes" className="flex items-center gap-1">
                Voir les recettes <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Rappels intelligents */}
      {widgets.rappels && rappelsData && rappelsData.total > 0 && (
        <Card className="border-orange-500/30 bg-orange-50/50 dark:bg-orange-950/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Bell className="h-5 w-5 text-orange-500" />
              Rappels ({rappelsData.total})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {rappelsData.rappels.slice(0, 4).map((rappel, i) => (
              <RappelCard key={i} rappel={rappel} />
            ))}
            {rappelsData.total > 4 && (
              <p className="text-xs text-muted-foreground pt-1">
                + {rappelsData.total - 4} autre(s) rappel(s)
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Aperçu financier */}
      {widgets.depenses && statsDepenses && (
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <Euro className="h-5 w-5" />
                Dépenses du mois
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {statsDepenses.total_mois?.toFixed(0) ?? "0"} €
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                {statsDepenses.delta_mois_precedent != null && (
                  <span className={statsDepenses.delta_mois_precedent > 0 ? "text-destructive" : "text-green-600"}>
                    {statsDepenses.delta_mois_precedent > 0 ? "+" : ""}
                    {statsDepenses.delta_mois_precedent.toFixed(0)} € vs mois précédent
                  </span>
                )}
              </p>
              {statsDepenses.par_categorie && (
                <div className="mt-3 space-y-1">
                  {Object.entries(statsDepenses.par_categorie as Record<string, number>)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 3)
                    .map(([cat, montant]) => (
                      <div key={cat} className="flex justify-between text-sm">
                        <span className="text-muted-foreground capitalize">{cat}</span>
                        <span className="font-medium">{montant.toFixed(0)} €</span>
                      </div>
                    ))}
                </div>
              )}
              <Button variant="ghost" size="sm" asChild className="mt-2 -ml-2">
                <Link href="/maison/depenses" className="flex items-center gap-1">
                  Détails <ArrowRight className="h-3 w-3" />
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Budget annuel
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {statsDepenses.total_annee?.toFixed(0) ?? "0"} €
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                Moyenne mensuelle : {statsDepenses.moyenne_mensuelle?.toFixed(0) ?? "0"} €/mois
              </p>
              <Button variant="ghost" size="sm" asChild className="mt-2 -ml-2">
                <Link href="/maison/depenses" className="flex items-center gap-1">
                  Voir tout <ArrowRight className="h-3 w-3" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Bilan mensuel IA */}
      {widgets.bilan_mensuel && bilanMensuel?.synthese_ia && (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Bilan du mois
            </CardTitle>
            <CardDescription>
              {bilanMensuel.donnees.depenses.total.toFixed(0)} € dépensés ·{" "}
              {bilanMensuel.donnees.repas.total_planifies} repas planifiés ·{" "}
              {bilanMensuel.donnees.activites.total} activité(s)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-foreground/80 whitespace-pre-line">
              {bilanMensuel.synthese_ia}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function CarteMetrique({
  titre,
  valeur,
  icone,
  lien,
  chargement,
  alerte,
}: {
  titre: string;
  valeur: number;
  icone: React.ReactNode;
  lien: string;
  chargement: boolean;
  alerte?: boolean;
}) {
  return (
    <Link href={lien}>
      <Card className={alerte ? "border-destructive/50" : "hover:bg-accent/50 transition-colors"}>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {titre}
          </CardTitle>
          {icone}
        </CardHeader>
        <CardContent>
          {chargement ? (
            <Skeleton className="h-8 w-16" />
          ) : (
            <p className={`text-2xl font-bold ${alerte ? "text-destructive" : ""}`}>
              {valeur}
            </p>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}

const PRIORITE_COULEURS: Record<string, string> = {
  urgente: "text-red-600 dark:text-red-400",
  haute: "text-orange-600 dark:text-orange-400",
  normale: "text-yellow-600 dark:text-yellow-400",
  basse: "text-muted-foreground",
};

function RappelCard({ rappel }: { rappel: RappelItem }) {
  const couleur = PRIORITE_COULEURS[rappel.priorite] ?? PRIORITE_COULEURS.normale;
  const contenu = (
    <div className="flex items-start gap-2 rounded-md p-2 hover:bg-accent/50 transition-colors">
      <AlertTriangle className={`h-4 w-4 mt-0.5 shrink-0 ${couleur}`} />
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${couleur}`}>{rappel.titre}</p>
        <p className="text-xs text-muted-foreground line-clamp-2">{rappel.description}</p>
      </div>
    </div>
  );

  if (rappel.lien) {
    return <Link href={rappel.lien}>{contenu}</Link>;
  }
  return contenu;
}
