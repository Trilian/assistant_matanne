// ═══════════════════════════════════════════════════════════
// Hub Cuisine — Cockpit avec stats temps réel
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  BookOpen,
  CalendarCheck,
  ShoppingCart,
  Thermometer,
  CookingPot,
  Baby,
  Leaf,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Flame,
  RefreshCw,
  Star,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Progress } from "@/composants/ui/progress";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { useQuery } from "@tanstack/react-query";
import { clientApi } from "@/bibliotheque/api/client";
import { obtenirDashboardCuisine } from "@/bibliotheque/api/tableau-bord";
import { CarteNotificationsModule } from "@/composants/disposition/carte-notifications-module";
import { CarteActionsAdminModule } from "@/composants/disposition/carte-actions-admin-module";
import { ItemAnime, SectionReveal } from "@/composants/ui/motion-utils";
import { LienTransition } from "@/composants/ui/lien-transition";
import { DialogueFeedbackSemaine } from "@/composants/cuisine/dialogue-feedback-semaine";
import { Button } from "@/composants/ui/button";

const SECTIONS = [
  {
    titre: "Ma Semaine",
    description: "Planning repas & nutrition",
    chemin: "/cuisine/ma-semaine",
    Icone: CalendarCheck,
    couleur: "text-blue-600",
    bgCouleur: "bg-blue-500/10",
  },
  {
    titre: "Recettes",
    description: "Bibliothèque & import",
    chemin: "/cuisine/recettes",
    Icone: BookOpen,
    couleur: "text-amber-600",
    bgCouleur: "bg-amber-500/10",
  },
  {
    titre: "Courses",
    description: "Listes & suggestions",
    chemin: "/cuisine/courses",
    Icone: ShoppingCart,
    couleur: "text-green-600",
    bgCouleur: "bg-green-500/10",
  },
  {
    titre: "Frigo & Stock",
    description: "Inventaire, QR codes & alertes",
    chemin: "/cuisine/inventaire",
    Icone: Thermometer,
    couleur: "text-cyan-600",
    bgCouleur: "bg-cyan-500/10",
  },
  {
    titre: "Batch Cooking",
    description: "Sessions de cuisine en lot",
    chemin: "/cuisine/batch-cooking",
    Icone: CookingPot,
    couleur: "text-orange-600",
    bgCouleur: "bg-orange-500/10",
  },
];

export default function PageCuisine() {
  const [feedbackOuvert, setFeedbackOuvert] = useState(false);

  const { data: dashboard } = utiliserRequete(
    ["dashboard-cuisine"],
    obtenirDashboardCuisine
  );

  // G1 — Recette express depuis stock
  const {
    data: recettesStock,
    isFetching: chargementStock,
    refetch: rechercherRecettesStock,
  } = useQuery({
    queryKey: ["suggestions-depuis-stock"],
    queryFn: async () => {
      const { data } = await clientApi.get("/suggestions/depuis-stock", {
        params: { max_resultats: 3, temps_max_min: 45 },
      });
      return data as { suggestions: { nom: string; description: string; raison: string; temps_preparation: number; temps_cuisson: number }[]; nb_ingredients_stock: number };
    },
    enabled: false,
    staleTime: 30 * 60 * 1000,
  });

  const nbRepas = dashboard?.repas_aujourd_hui?.length ?? 0;
  const scoreAntiGaspi = dashboard?.score_anti_gaspillage ?? 100;
  const repasJules = dashboard?.repas_jules_aujourd_hui ?? [];
  const repasSemaine = dashboard?.repas_semaine_count ?? 0;
  const repasConsommes = Math.min(
    repasSemaine,
    Number((dashboard as { repas_consommes_count?: number } | undefined)?.repas_consommes_count ?? Math.max(nbRepas + 1, Math.round(repasSemaine * 0.4)))
  );
  const progressionSemaine = repasSemaine > 0 ? Math.round((repasConsommes / repasSemaine) * 100) : 0;

  return (
    <div className="space-y-6">
      <SectionReveal>
        <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🍽️ Cuisine</h1>
          <p className="text-muted-foreground">
            Ton cockpit cuisine — planning, courses, stocks
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => setFeedbackOuvert(true)}>
          <Star className="h-4 w-4 mr-1.5 text-yellow-500" />
          Feedback semaine
        </Button>
        </div>
      </SectionReveal>

      <SectionReveal delay={0.03}>
        <CarteNotificationsModule moduleKey="cuisine" moduleLabel="Cuisine" />
      </SectionReveal>

      <SectionReveal delay={0.06}>
        <CarteActionsAdminModule
        moduleLabel="Cuisine"
        description="Relance rapide des automations cuisine et accès au cockpit admin du module."
        jobs={[
          {
            id: "briefing_matinal_ia",
            label: "Briefing matinal IA",
            hint: "Synthèse Telegram du matin",
          },
          {
            id: "resume_hebdo",
            label: "Résumé hebdo",
            hint: "Bilan famille/cuisine de la semaine",
          },
          {
            id: "resume_hebdo_ia",
            label: "Résumé hebdo IA",
            hint: "Version enrichie par IA",
          },
        ]}
      />
      </SectionReveal>

      {/* Cockpit KPIs */}
      {dashboard && (
        <SectionReveal delay={0.09} className="grid gap-3 grid-cols-2 lg:grid-cols-4">
          {/* Repas aujourd'hui */}
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">
                    Repas aujourd&apos;hui
                  </p>
                  <p className="text-2xl font-bold">{nbRepas}</p>
                </div>
                <CalendarCheck className="h-8 w-8 text-blue-500 opacity-80" />
              </div>
              {nbRepas > 0 && (
                <div className="mt-2 text-xs text-muted-foreground">
                  {dashboard.repas_aujourd_hui
                    .map(
                      (r) =>
                        `${r.type_repas === "diner" ? "🌙" : "☀️"} ${r.recette_nom || "?"}`
                    )
                    .join(" · ")}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Articles à acheter */}
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">
                    Articles à acheter
                  </p>
                  <p className="text-2xl font-bold">
                    {dashboard.articles_courses_restants}
                  </p>
                </div>
                <ShoppingCart className="h-8 w-8 text-green-500 opacity-80" />
              </div>
            </CardContent>
          </Card>

          {/* Score anti-gaspillage */}
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">
                    Anti-gaspillage
                  </p>
                  <p className="text-2xl font-bold">{scoreAntiGaspi}%</p>
                </div>
                {scoreAntiGaspi >= 80 ? (
                  <Leaf className="h-8 w-8 text-green-500 opacity-80" />
                ) : (
                  <AlertTriangle className="h-8 w-8 text-amber-500 opacity-80" />
                )}
              </div>
              <Progress
                value={scoreAntiGaspi}
                className="mt-2 h-1.5"
              />
            </CardContent>
          </Card>

          {/* Alertes inventaire */}
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground">
                    Alertes stock
                  </p>
                  <p className="text-2xl font-bold">
                    {dashboard.alertes_inventaire}
                  </p>
                </div>
                {dashboard.alertes_inventaire === 0 ? (
                  <CheckCircle2 className="h-8 w-8 text-green-500 opacity-80" />
                ) : (
                  <AlertTriangle className="h-8 w-8 text-red-500 opacity-80" />
                )}
              </div>
            </CardContent>
          </Card>
        </SectionReveal>
      )}

      {/* Suivi semaine + Jules */}
      {dashboard && (
        <SectionReveal delay={0.12} className="grid gap-4 sm:grid-cols-2">
          {/* Progression semaine */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Progression de la semaine
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span>
                  {repasConsommes} / {repasSemaine} repas consommés
                </span>
                <span className="font-semibold text-primary">{progressionSemaine}%</span>
              </div>
              <Progress value={progressionSemaine} className="h-1.5" />
              <p className="text-xs text-muted-foreground mt-2">
                {dashboard.nb_recettes} recettes en bibliothèque
                {dashboard.batch_en_cours && " · 🍳 Batch en cours"}
              </p>
            </CardContent>
          </Card>

          {/* Repas Jules */}
          {repasJules.length > 0 && (
            <Card className="border-pink-200 dark:border-pink-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Baby className="h-4 w-4 text-pink-500" />
                  Menu Jules aujourd&apos;hui
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {repasJules.map((r, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-2 text-sm"
                    >
                      <span>
                        {r.type_repas === "diner" ? "🌙" : "☀️"}
                      </span>
                      <span className="font-medium">
                        {r.plat_jules || "Non défini"}
                      </span>
                      {r.adaptation_auto && (
                        <span className="text-xs bg-pink-100 text-pink-700 dark:bg-pink-900 dark:text-pink-300 px-1.5 rounded">
                          Auto
                        </span>
                      )}
                    </div>
                  ))}
                  {repasJules.some((r) => r.notes_jules) && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {repasJules.find((r) => r.notes_jules)?.notes_jules}
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </SectionReveal>
      )}

      {/* G1 — Recette express depuis stock */}
      <SectionReveal delay={0.14}>
        <Card className="border-orange-200 dark:border-orange-800">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Flame className="h-4 w-4 text-orange-500" />
                Qu&apos;est-ce qu&apos;on cuisine ce soir ?
              </CardTitle>
              <button
                type="button"
                onClick={() => void rechercherRecettesStock()}
                disabled={chargementStock}
                className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full bg-orange-500 hover:bg-orange-600 text-white font-medium transition-colors disabled:opacity-60"
              >
                {chargementStock ? (
                  <RefreshCw className="h-3 w-3 animate-spin" />
                ) : (
                  <Flame className="h-3 w-3" />
                )}
                {chargementStock ? "Recherche…" : "Idées depuis mon stock"}
              </button>
            </div>
          </CardHeader>
          {recettesStock && (
            <CardContent>
              {recettesStock.suggestions.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Aucune recette trouvée avec le stock actuel ({recettesStock.nb_ingredients_stock} ingrédients).
                </p>
              ) : (
                <div className="grid gap-2 sm:grid-cols-3">
                  {recettesStock.suggestions.map((s, i) => (
                    <div key={i} className="rounded-lg border p-3 text-sm space-y-1">
                      <p className="font-semibold">{s.nom}</p>
                      <p className="text-xs text-muted-foreground line-clamp-2">{s.description}</p>
                      <p className="text-xs text-orange-600 dark:text-orange-400">⏱ {(s.temps_preparation ?? 0) + (s.temps_cuisson ?? 0)} min</p>
                      {s.raison && (
                        <p className="text-xs text-muted-foreground italic">💡 {s.raison}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          )}
        </Card>
      </SectionReveal>

      {/* Sections navigation */}
      <SectionReveal delay={0.16} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SECTIONS.map(({ titre, description, chemin, Icone, couleur, bgCouleur }, index) => {
          const estBatchCooking = chemin === "/cuisine/batch-cooking";

          return (
            <ItemAnime key={chemin} index={index}>
              <LienTransition href={chemin}>
                <Card className="h-full transition-all hover:-translate-y-0.5 hover:bg-accent/50 hover:shadow-md">
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className={`rounded-lg ${bgCouleur} p-2`}>
                        <Icone className={`h-5 w-5 ${couleur}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-base">{titre}</CardTitle>
                        <CardDescription className="text-sm">
                          {description}
                        </CardDescription>
                      </div>
                      {estBatchCooking && dashboard?.batch_en_cours && (
                        <span className="shrink-0 rounded-full bg-orange-500/10 px-2 py-0.5 text-xs font-semibold text-orange-600">
                          En cours
                        </span>
                      )}
                    </div>
                  </CardHeader>
                </Card>
              </LienTransition>
            </ItemAnime>
          );
        })}
      </SectionReveal>

      <DialogueFeedbackSemaine ouvert={feedbackOuvert} onFermer={() => setFeedbackOuvert(false)} />
    </div>
  );
}
