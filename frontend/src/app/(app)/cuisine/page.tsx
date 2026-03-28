// ═══════════════════════════════════════════════════════════
// Hub Cuisine — Cockpit avec stats temps réel
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
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
import { obtenirDashboardCuisine } from "@/bibliotheque/api/tableau-bord";

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
  const { data: dashboard } = utiliserRequete(
    ["dashboard-cuisine"],
    obtenirDashboardCuisine
  );

  const nbRepas = dashboard?.repas_aujourd_hui?.length ?? 0;
  const scoreAntiGaspi = dashboard?.score_anti_gaspillage ?? 100;
  const repasJules = dashboard?.repas_jules_aujourd_hui ?? [];
  const repasConsommes = dashboard?.repas_consommes_semaine ?? 0;
  const repasSemaine = dashboard?.repas_semaine_count ?? 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🍽️ Cuisine</h1>
        <p className="text-muted-foreground">
          Ton cockpit cuisine — planning, courses, stocks
        </p>
      </div>

      {/* Cockpit KPIs */}
      {dashboard && (
        <div className="grid gap-3 grid-cols-2 lg:grid-cols-4">
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
        </div>
      )}

      {/* Suivi semaine + Jules */}
      {dashboard && (
        <div className="grid gap-4 sm:grid-cols-2">
          {/* Progression semaine */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Progression de la semaine
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between text-sm mb-2">
                <span>
                  {repasConsommes} / {repasSemaine} repas consommés
                </span>
                <span className="font-semibold">
                  {repasSemaine > 0
                    ? Math.round((repasConsommes / repasSemaine) * 100)
                    : 0}
                  %
                </span>
              </div>
              <Progress
                value={
                  repasSemaine > 0
                    ? (repasConsommes / repasSemaine) * 100
                    : 0
                }
                className="h-2"
              />
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
        </div>
      )}

      {/* Sections navigation */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SECTIONS.map(({ titre, description, chemin, Icone, couleur, bgCouleur }) => {
          const estBatchCooking = chemin === "/cuisine/batch-cooking";

          return (
            <Link key={chemin} href={chemin}>
              <Card className="hover:bg-accent/50 transition-colors h-full">
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
            </Link>
          );
        })}
      </div>
    </div>
  );
}
