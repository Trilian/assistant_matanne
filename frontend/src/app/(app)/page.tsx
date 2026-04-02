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
  Heart,
  Leaf,
} from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { Progress } from "@/composants/ui/progress";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import {
  obtenirBilanMensuel,
  obtenirAlertesContextuelles,
  obtenirConfigDashboard,
  enregistrerActionWidgetDashboard,
  obtenirPointsFamille,
  obtenirScoreEcologique,
  obtenirScoreBienEtre,
  obtenirTableauBord,
  sauvegarderConfigDashboard,
} from "@/bibliotheque/api/tableau-bord";
import { obtenirAnomaliesBudget } from "@/bibliotheque/api/famille";
import {
  modifierTacheEntretien,
  obtenirTachesJourMaison,
  statsDepensesMaison,
} from "@/bibliotheque/api/maison";
import { evaluerRappels, type RappelItem } from "@/bibliotheque/api/push";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import { clientApi } from "@/bibliotheque/api/client";
import { SwipeableItem } from "@/composants/swipeable-item";
import { toast } from "sonner";
import { genererPlanningSemaine } from "@/bibliotheque/api/planning";
import { genererCoursesDepuisPlanning } from "@/bibliotheque/api/courses";
import {
  GrilleDashboardDnd,
  WidgetSortable,
} from "@/composants/dashboard/grille-dashboard-dnd";
import { CompteurAnime } from "@/composants/dashboard/compteur-anime";
import { Sparkline } from "@/composants/dashboard/sparkline";
import { ComparateurTemporel } from "@/composants/dashboard/comparateur-temporel";
import { obtenirScoreFamilleHebdo } from "@/bibliotheque/api/avance";

const WIDGETS_DEFAUT = {
  metriques: true,
  actions_rapides: true,
  lecture_ia: true,
  rappels: true,
  depenses: true,
  alerte_budget: true,
  checklist_jour: true,
  bilan_mensuel: true,
  meteo: true,
  histoire_famille: true,
  alertes_contextuelles: true,
  points_famille: true,
  score_bienetre: true,
  score_ecologique: true,
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
  const router = useRouter();
  const searchParams = useSearchParams();
  const { utilisateur } = utiliserAuth();
  const { data, isLoading } = utiliserRequete(["tableau-bord"], obtenirTableauBord);
  const { data: statsDepenses } = utiliserRequete(["depenses", "stats"], statsDepensesMaison);
  const { data: rappelsData } = utiliserRequete(["rappels"], evaluerRappels);
  const { data: tachesJour, refetch: rechargerTachesJour } = utiliserRequete(
    ["maison", "taches-jour", "dashboard"],
    obtenirTachesJourMaison
  );
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
  const { data: scoreBienEtre } = utiliserRequete(
    ["dashboard", "score-bienetre"],
    obtenirScoreBienEtre
  );
  const { data: scoreEcologique } = utiliserRequete(
    ["dashboard", "score-ecologique"],
    obtenirScoreEcologique
  );
  const { data: scoreFamilleHebdo } = utiliserRequete(
    ["dashboard", "score-famille-hebdo", "avance"],
    obtenirScoreFamilleHebdo,
    { staleTime: 10 * 60 * 1000 }
  );
  const { data: anomaliesBudget } = utiliserRequete(
    ["famille", "budget", "anomalies"],
    obtenirAnomaliesBudget
  );

  const alertesBudget = (anomaliesBudget?.anomalies ?? []).filter(
    (anomalie) => anomalie.severite === "danger" || anomalie.severite === "warning"
  );

  const [widgetsStockes, setWidgetsStockes] = utiliserStockageLocal("dashboard-widgets", WIDGETS_DEFAUT);
  const [configOuverte, setConfigOuverte] = utiliserStockageLocal("dashboard-config-open", false);
  const [widgets, setWidgets] = useState(WIDGETS_DEFAUT);
  const [meteo, setMeteo] = useState<MeteoWidget | null>(null);
  const [actionPushTraitee, setActionPushTraitee] = useState(false);

  const ORDRE_WIDGETS_DEFAUT = Object.keys(WIDGETS_DEFAUT);
  const [ordreWidgets, setOrdreWidgets] = utiliserStockageLocal<string[]>(
    "dashboard-widgets-ordre",
    ORDRE_WIDGETS_DEFAUT
  );

  function obtenirLundiCourant(): string {
    const now = new Date();
    const jour = now.getDay();
    const diff = jour === 0 ? -6 : 1 - jour;
    const lundi = new Date(now);
    lundi.setDate(now.getDate() + diff);
    return lundi.toISOString().split("T")[0];
  }

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

  const { mutate: tracerActionWidgetDashboard } = utiliserMutation(
    enregistrerActionWidgetDashboard,
    {
      onError: () => {
        // Le tracking ne doit jamais bloquer l'interaction utilisateur.
      },
    }
  );

  const { mutate: basculerTacheDashboard, isPending: basculeTacheEnCours } =
    utiliserMutation(
      async ({ idSource, fait }: { idSource: number; fait: boolean }) =>
        modifierTacheEntretien(idSource, { fait }),
      {
        onSuccess: () => {
          void rechargerTachesJour();
        },
        onError: () => {
          toast.error("Impossible de mettre à jour la tâche");
        },
      }
    );

  const { mutateAsync: ajouterArticleCoursesDirect, isPending: ajoutRappelEnCours } = utiliserMutation(
    async (nomArticle: string) => {
      const { data: listesData } = await clientApi.get<{
        items?: Array<{ id: number; nom: string }>;
      }>("/courses", {
        params: { page: 1, page_size: 1, active_only: true },
      });

      let listeId = listesData.items?.[0]?.id;

      if (!listeId) {
        const { data: nouvelleListe } = await clientApi.post<{ id?: number }>("/courses", {
          nom: "Rappels stock bas",
        });
        listeId = nouvelleListe.id;
      }

      if (!listeId) {
        throw new Error("Impossible de récupérer une liste de courses");
      }

      await clientApi.post(`/courses/${listeId}/items`, {
        nom: nomArticle,
        quantite: 1,
        categorie: "A racheter",
      });
    },
    {
      onSuccess: () => {
        toast.success("Article ajouté à la liste de courses");
      },
      onError: () => {
        toast.error("Impossible d'ajouter l'article depuis le rappel");
      },
    }
  );

  const { mutate: ajouterDepuisRappel } = utiliserMutation(
    async (rappel: RappelItem) => {
      const nomArticle = extraireArticleDepuisRappel(rappel);
      if (!nomArticle) {
        throw new Error("Article introuvable dans le rappel");
      }
      await ajouterArticleCoursesDirect(nomArticle);
    },
    {
      onError: () => {
        toast.error("Impossible d'ajouter l'article depuis le rappel");
      },
    }
  );

  const { mutate: planifierSemaine, isPending: planificationSemaineEnCours } = utiliserMutation(
    async () => {
      const lundi = obtenirLundiCourant();
      await genererPlanningSemaine({ date_debut: lundi, nb_jours: 7 });
      const courses = await genererCoursesDepuisPlanning(lundi, {
        soustraireStock: true,
        nomListe: "Courses de la semaine",
      });
      return courses.total_articles;
    },
    {
      onSuccess: (totalArticles) => {
        toast.success(`Semaine planifiée : ${totalArticles} article(s) de courses généré(s)`);
        router.push("/cuisine/ma-semaine");
      },
      onError: () => {
        toast.error("Impossible de planifier la semaine automatiquement");
      },
    }
  );

  const tachesChecklist = (tachesJour ?? []).slice(0, 5);

  useEffect(() => {
    if (actionPushTraitee) {
      return;
    }

    const action = searchParams.get("action");
    if (action !== "add-stock") {
      return;
    }

    const article = searchParams.get("article");
    if (!article) {
      setActionPushTraitee(true);
      router.replace("/");
      return;
    }

    void ajouterArticleCoursesDirect(article);
    setActionPushTraitee(true);
    router.replace("/");
  }, [actionPushTraitee, ajouterArticleCoursesDirect, router, searchParams]);

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
    tracerActionWidgetDashboard({
      widget_id: cle,
      action: prochain[cle] ? "afficher" : "masquer",
      donnees: { visible: prochain[cle] },
    });
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
            <CardDescription>Glissez les widgets pour réorganiser, cochez/décochez pour afficher/masquer.</CardDescription>
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

      <ComparateurTemporel />

      <GrilleDashboardDnd
        ordre={ordreWidgets}
        onOrdreChange={(nouvelOrdre) => {
          setOrdreWidgets(nouvelOrdre);
          tracerActionWidgetDashboard({
            widget_id: "dashboard",
            action: "reordonner_widgets",
            donnees: { ordre: nouvelOrdre },
          });
        }}
      >

      {widgets.meteo && meteo && (
        <WidgetSortable id="meteo">
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
        </WidgetSortable>
      )}

      {widgets.histoire_famille && histoireFamille && histoireFamille.total > 0 && (
        <WidgetSortable id="histoire_famille">
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
        </WidgetSortable>
      )}

      {widgets.alertes_contextuelles && alertesContextuelles && alertesContextuelles.total > 0 && (
        <WidgetSortable id="alertes_contextuelles">
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
        </WidgetSortable>
      )}

      {widgets.alerte_budget && alertesBudget.length > 0 && (
        <WidgetSortable id="alerte_budget">
        <Card className="border-red-300/60 bg-red-50/50 dark:border-red-900/40 dark:bg-red-950/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              Alerte budget
            </CardTitle>
            <CardDescription>
              {alertesBudget.length} dépassement(s) ou dérive(s) détecté(s)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {alertesBudget.slice(0, 3).map((anomalie, index) => (
              <div
                key={`${anomalie.categorie}-${anomalie.type}-${index}`}
                className="rounded-md border bg-background/70 px-3 py-2"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-medium capitalize">{anomalie.categorie}</p>
                  <span className="text-[11px] uppercase text-muted-foreground">
                    {anomalie.severite}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">{anomalie.description}</p>
                <p className="text-xs mt-1">
                  Ecart: {anomalie.ecart_pourcent > 0 ? "+" : ""}
                  {Math.round(anomalie.ecart_pourcent)}%
                </p>
              </div>
            ))}
            <Button variant="ghost" size="sm" asChild className="-ml-2">
              <Link href="/famille/budget" className="flex items-center gap-1">
                Ouvrir budget <ArrowRight className="h-3 w-3" />
              </Link>
            </Button>
          </CardContent>
        </Card>
        </WidgetSortable>
      )}

      {widgets.points_famille && pointsFamille && (
        <WidgetSortable id="points_famille">
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
        </WidgetSortable>
      )}

      {widgets.score_bienetre && scoreBienEtre && (
        <WidgetSortable id="score_bienetre">
        <Card className="border-purple-300/50 bg-purple-50/50 dark:border-purple-900/40 dark:bg-purple-950/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Heart className="h-4 w-4 text-purple-500" />
              Score bien-être
            </CardTitle>
            <CardDescription>
              Semaine du {new Date(scoreBienEtre.periode.debut).toLocaleDateString("fr-FR")} ·{" "}
              {scoreBienEtre.trend_semaine_precedente >= 0 ? "+" : ""}
              {Math.round(scoreBienEtre.trend_semaine_precedente)} pts vs semaine précédente
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-end justify-between">
              <div>
                <p className="text-4xl font-bold text-purple-600 dark:text-purple-400">
                  {scoreBienEtre.score_global}
                  <span className="text-lg text-muted-foreground">/100</span>
                </p>
              </div>
              <div className="text-right text-xs text-muted-foreground space-y-1">
                <p>🥗 Diversité: {scoreBienEtre.diversite_alimentaire}%</p>
                <p>🏷️ Nutri-score: {scoreBienEtre.score_nutri}%</p>
                <p>🏃 Sport: {scoreBienEtre.activites_sport}%</p>
              </div>
            </div>
            <Progress
              value={Math.min(100, scoreBienEtre.score_global)}
              className="mt-3 h-2"
            />
            {scoreFamilleHebdo && (
              <div className="mt-3 rounded-md border border-purple-200/70 bg-background/70 p-2 text-xs">
                <p className="font-medium">Score famille hebdo: {Math.round(scoreFamilleHebdo.score_global)}/100</p>
                <p className="text-muted-foreground">{scoreFamilleHebdo.recommandations[0] ?? "Aucune recommandation."}</p>
              </div>
            )}
          </CardContent>
        </Card>
        </WidgetSortable>
      )}

      {widgets.score_ecologique && scoreEcologique && (
        <WidgetSortable id="score_ecologique">
        <Card className="border-lime-300/50 bg-lime-50/60 dark:border-lime-900/40 dark:bg-lime-950/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Leaf className="h-4 w-4 text-lime-600" />
              Score ecologique
            </CardTitle>
            <CardDescription>
              Niveau {scoreEcologique.niveau} · cuisine {scoreEcologique.modules.cuisine.score}/100 · maison {scoreEcologique.modules.maison.score}/100
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="text-4xl font-bold text-lime-700 dark:text-lime-400">
                  {scoreEcologique.score_global}
                  <span className="text-lg text-muted-foreground">/100</span>
                </p>
                <p className="text-xs text-muted-foreground">
                  {scoreEcologique.modules.maison.economie_mensuelle_estimee.toFixed(0)} € d'economies mensuelles estimees
                </p>
              </div>
              <div className="text-right text-xs text-muted-foreground space-y-1">
                <p>♻️ Anti-gaspi: {scoreEcologique.modules.cuisine.anti_gaspillage}</p>
                <p>⚡ Energie: {scoreEcologique.modules.maison.energie}</p>
                <p>🌿 Eco-actions: {scoreEcologique.modules.maison.eco_actions}</p>
              </div>
            </div>
            <div className="space-y-1">
              {scoreEcologique.leviers_prioritaires.slice(0, 2).map((levier) => (
                <p key={levier} className="text-xs text-muted-foreground">
                  • {levier}
                </p>
              ))}
            </div>
          </CardContent>
        </Card>
        </WidgetSortable>
      )}

      {/* Cartes métriques */}
      {widgets.metriques && (
      <WidgetSortable id="metriques">
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
      </WidgetSortable>
      )}

      {/* Actions rapides */}
      {widgets.actions_rapides && (
      <WidgetSortable id="actions_rapides">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Actions rapides</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* Actions principales */}
          <div className="grid gap-2 grid-cols-2 sm:grid-cols-4">
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <button
                type="button"
                onClick={() => planifierSemaine(undefined)}
                disabled={planificationSemaineEnCours}
              >
                {planificationSemaineEnCours ? (
                  <LoaderCard />
                ) : (
                  <>
                    <CalendarDays className="h-5 w-5" />
                    <span className="text-xs">Planifier ma semaine</span>
                  </>
                )}
              </button>
            </Button>
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <Link href="/cuisine/courses">
                <ShoppingCart className="h-5 w-5" />
                <span className="text-xs">Courses du jour</span>
              </Link>
            </Button>
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <Link href="/maison/entretien">
                <AlertTriangle className="h-5 w-5" />
                <span className="text-xs">Tâche du jour</span>
              </Link>
            </Button>
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <Link href="/focus">
                <Zap className="h-5 w-5" />
                <span className="text-xs">Mode focus</span>
              </Link>
            </Button>
          </div>

          {/* Actions secondaires pour flux rapide */}
          <div className="grid gap-2 grid-cols-2 sm:grid-cols-4 pt-2 border-t">
            <Button variant="ghost" asChild className="h-auto py-2 flex-col gap-1 text-xs">
              <Link href="/cuisine/recettes">
                <ChefHat className="h-4 w-4" />
                <span className="text-xs">Ajouter recette</span>
              </Link>
            </Button>
            <Button variant="ghost" asChild className="h-auto py-2 flex-col gap-1 text-xs">
              <Link href="/cuisine/courses">
                <ShoppingCart className="h-4 w-4" />
                <span className="text-xs">Ajouter course</span>
              </Link>
            </Button>
            <Button variant="ghost" asChild className="h-auto py-2 flex-col gap-1 text-xs">
              <Link href="/maison/entretien">
                <AlertTriangle className="h-4 w-4" />
                <span className="text-xs">Nouvelle tâche</span>
              </Link>
            </Button>
            <Button variant="ghost" asChild className="h-auto py-2 flex-col gap-1 text-xs">
              <Link href="/famille/budget">
                <Euro className="h-4 w-4" />
                <span className="text-xs">Budget</span>
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
      </WidgetSortable>
      )}

      {/* Suggestion dîner IA */}
      {widgets.lecture_ia && data?.suggestion_diner && (
        <WidgetSortable id="lecture_ia">
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
        </WidgetSortable>
      )}

      {/* Rappels intelligents */}
      {widgets.rappels && rappelsData && rappelsData.total > 0 && (
        <WidgetSortable id="rappels">
        <Card className="border-orange-500/30 bg-orange-50/50 dark:bg-orange-950/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Bell className="h-5 w-5 text-orange-500" />
              Rappels ({rappelsData.total})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {rappelsData.rappels.slice(0, 4).map((rappel, i) => (
              <RappelCard
                key={`${rappel.type}-${rappel.titre}-${i}`}
                rappel={rappel}
                enAjout={ajoutRappelEnCours}
                onAjouterCourses={() => ajouterDepuisRappel(rappel)}
              />
            ))}
            {rappelsData.total > 4 && (
              <p className="text-xs text-muted-foreground pt-1">
                + {rappelsData.total - 4} autre(s) rappel(s)
              </p>
            )}
          </CardContent>
        </Card>
        </WidgetSortable>
      )}

      {/* Checklist du jour */}
      {widgets.checklist_jour && (
        <WidgetSortable id="checklist_jour">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Checklist du jour</CardTitle>
            <CardDescription>
              Swipe droite (mobile) ou clic pour valider une tâche directement.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {tachesChecklist.length === 0 ? (
              <p className="text-sm text-muted-foreground">Aucune tâche du jour.</p>
            ) : (
              tachesChecklist.map((tache) => {
                const nom = tache.nom;
                const idSource = tache.id_source;
                const fait = tache.fait;

                const contenu = (
                  <div className="rounded-md border bg-background px-3 py-2 flex items-center justify-between gap-3">
                    <div>
                      <p className={`text-sm font-medium ${fait ? "line-through text-muted-foreground" : ""}`}>
                        {nom}
                      </p>
                      {tache.categorie && (
                        <p className="text-xs text-muted-foreground">{tache.categorie}</p>
                      )}
                    </div>
                    <Button
                      size="sm"
                      variant={fait ? "outline" : "default"}
                      disabled={!idSource || basculeTacheEnCours}
                      onClick={() => {
                        if (!idSource) return;
                        basculerTacheDashboard({ idSource, fait: !fait });
                        tracerActionWidgetDashboard({
                          widget_id: "checklist_jour",
                          action: !fait ? "valider_tache" : "annuler_tache",
                          donnees: { id_source: idSource, fait: !fait, nom },
                        });
                      }}
                    >
                      {fait ? "Annuler" : "Valider"}
                    </Button>
                  </div>
                );

                if (!idSource || fait) {
                  return <div key={`${nom}-${idSource ?? 0}`}>{contenu}</div>;
                }

                return (
                  <SwipeableItem
                    key={`${nom}-${idSource}`}
                    labelDroit="Valider"
                    onSwipeRight={() => {
                      basculerTacheDashboard({ idSource, fait: true });
                      tracerActionWidgetDashboard({
                        widget_id: "checklist_jour",
                        action: "valider_tache_swipe",
                        donnees: { id_source: idSource, fait: true, nom },
                      });
                    }}
                    desactiverGauche
                  >
                    {contenu}
                  </SwipeableItem>
                );
              })
            )}
            <Button variant="ghost" size="sm" asChild className="-ml-2">
              <Link href="/maison/entretien" className="flex items-center gap-1">
                Voir toutes les tâches <ArrowRight className="h-3 w-3" />
              </Link>
            </Button>
          </CardContent>
        </Card>
        </WidgetSortable>
      )}

      {/* Aperçu financier */}
      {widgets.depenses && statsDepenses && (
        <WidgetSortable id="depenses">
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
        </WidgetSortable>
      )}

      {/* Bilan mensuel IA */}
      {widgets.bilan_mensuel && bilanMensuel?.synthese_ia && (
        <WidgetSortable id="bilan_mensuel">
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
        </WidgetSortable>
      )}

      </GrilleDashboardDnd>
    </div>
  );
}

function LoaderCard() {
  return (
    <>
      <Sparkles className="h-5 w-5 animate-pulse" />
      <span className="text-xs">Génération...</span>
    </>
  );
}

function CarteMetrique({
  titre,
  valeur,
  icone,
  lien,
  chargement,
  alerte,
  sparkline,
}: {
  titre: string;
  valeur: number;
  icone: React.ReactNode;
  lien: string;
  chargement: boolean;
  alerte?: boolean;
  sparkline?: number[];
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
            <div className="flex items-end justify-between gap-2">
              <p className={`text-2xl font-bold ${alerte ? "text-destructive" : ""}`}>
                <CompteurAnime valeur={valeur} />
              </p>
              {sparkline && sparkline.length >= 2 && (
                <Sparkline
                  donnees={sparkline}
                  couleur={alerte ? "hsl(0, 72%, 51%)" : "hsl(210, 70%, 50%)"}
                  couleurNegatif="hsl(0, 72%, 51%)"
                />
              )}
            </div>
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

function extraireArticleDepuisRappel(rappel: RappelItem): string | null {
  if (rappel.type !== "inventaire") {
    return null;
  }
  const titre = rappel.titre || "";
  const separateur = titre.indexOf(":");
  if (separateur >= 0) {
    const extrait = titre.slice(separateur + 1).trim();
    return extrait || null;
  }
  return null;
}

function RappelCard({
  rappel,
  onAjouterCourses,
  enAjout,
}: {
  rappel: RappelItem;
  onAjouterCourses?: () => void;
  enAjout?: boolean;
}) {
  const couleur = PRIORITE_COULEURS[rappel.priorite] ?? PRIORITE_COULEURS.normale;
  return (
    <div className="rounded-md p-2 hover:bg-accent/50 transition-colors space-y-2">
      <div className="flex items-start gap-2">
      <AlertTriangle className={`h-4 w-4 mt-0.5 shrink-0 ${couleur}`} />
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${couleur}`}>{rappel.titre}</p>
        <p className="text-xs text-muted-foreground line-clamp-2">{rappel.description}</p>
      </div>
      </div>
      <div className="flex items-center gap-2 pl-6">
        {rappel.lien && (
          <Button size="sm" variant="outline" asChild>
            <Link href={rappel.lien}>Ouvrir</Link>
          </Button>
        )}
        {rappel.type === "inventaire" && onAjouterCourses && (
          <Button
            size="sm"
            variant="secondary"
            disabled={enAjout}
            onClick={onAjouterCourses}
          >
            Ajouter aux courses
          </Button>
        )}
      </div>
    </div>
  );
}
