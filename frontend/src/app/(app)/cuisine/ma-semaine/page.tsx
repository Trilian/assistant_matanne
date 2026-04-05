// ═══════════════════════════════════════════════════════════
// Ma Semaine — Wizard Planning + Inventaire + Courses
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  Calendar,
  Package,
  ShoppingCart,
  CheckCircle2,
  ChevronRight,
  ChevronLeft,
  Sparkles,
  AlertCircle,
  Loader2,
  CookingPot,
  Baby,
  Flame,
  UtensilsCrossed,
  Wind,
  Copy,
} from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Progress } from "@/composants/ui/progress";
import { Skeleton } from "@/composants/ui/skeleton";
import { FriseFluxCuisine } from "@/composants/cuisine/frise-flux-cuisine";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  obtenirPlanningSemaine,
  genererPlanningSemaine,
  obtenirNutritionHebdo,
  copierPlanning,
} from "@/bibliotheque/api/planning";
import { listerInventaire, obtenirAlertes } from "@/bibliotheque/api/inventaire";
import { genererCoursesDepuisPlanning } from "@/bibliotheque/api/courses";
import { genererSessionDepuisPlanning } from "@/bibliotheque/api/batch-cooking";
import { toast } from "sonner";
import type { RepasPlanning } from "@/types/planning";

const ETAPES = [
  {
    id: "planning",
    titre: "📅 Planning de la semaine",
    description: "Consultez ou générez votre planning hebdomadaire",
    icone: Calendar,
  },
  {
    id: "inventaire",
    titre: "📦 État du stock",
    description: "Vérifiez ce que vous avez déjà",
    icone: Package,
  },
  {
    id: "courses",
    titre: "🛒 Liste de courses",
    description: "Générez votre liste en fonction du planning",
    icone: ShoppingCart,
  },
  {
    id: "recap",
    titre: "✅ Récapitulatif",
    description: "Vue d'ensemble et actions rapides",
    icone: CheckCircle2,
  },
];

function getLundiDeSemaine(offset = 0): string {
  const now = new Date();
  const jour = now.getDay();
  const diff = jour === 0 ? -6 : 1 - jour;
  const lundi = new Date(now);
  lundi.setDate(now.getDate() + diff + offset * 7);
  return lundi.toISOString().split("T")[0];
}

function ApplianceIcons({ repas }: { repas: RepasPlanning }) {
  const icons = [];
  if (repas.compatible_cookeo) icons.push({ key: "cookeo", label: "Cookeo", Ic: Flame });
  if (repas.compatible_monsieur_cuisine) icons.push({ key: "mc", label: "Mr Cuisine", Ic: UtensilsCrossed });
  if (repas.compatible_airfryer) icons.push({ key: "af", label: "Air Fryer", Ic: Wind });
  if (icons.length === 0) return null;
  return (
    <div className="flex gap-0.5">
      {icons.map(({ key, label, Ic }) => (
        <span key={key} title={label} className="text-muted-foreground">
          <Ic className="h-3 w-3" />
        </span>
      ))}
    </div>
  );
}

function JulesRow({ repas }: { repas: RepasPlanning }) {
  if (!repas.plat_jules && !repas.notes_jules) return null;
  return (
    <div className="flex items-start gap-2 ml-4 mt-1 text-xs">
      <Baby className="h-3.5 w-3.5 text-purple-500 shrink-0 mt-0.5" />
      <div className="min-w-0">
        <span className="font-medium text-purple-700 dark:text-purple-300">
          Jules :
        </span>{" "}
        <span className="text-muted-foreground">{repas.plat_jules ?? repas.notes_jules}</span>
        {repas.adaptation_auto && (
          <Badge variant="outline" className="ml-1 text-[9px] px-1 py-0 border-purple-300 text-purple-600 dark:text-purple-400">
            auto
          </Badge>
        )}
      </div>
    </div>
  );
}

const TYPE_REPAS_LABEL: Record<string, string> = {
  petit_dejeuner: "🌅 Petit-déj",
  dejeuner: "🍽️ Déjeuner",
  gouter: "🍪 Goûter",
  diner: "🌙 Dîner",
};

export default function MaSemainePage() {
  const router = useRouter();
  const [etapeActuelle, setEtapeActuelle] = useState(0);
  const [dateDebut] = useState(getLundiDeSemaine(0));
  const [coursesGenereesId, setCoursesGenereesId] = useState<number | null>(null);
  const [batchSessionId, setBatchSessionId] = useState<number | null>(null);

  const invalider = utiliserInvalidation();

  // Requêtes
  const { data: planning, isLoading: loadingPlanning, refetch: rechercherPlanning } = utiliserRequete(
    ["planning", dateDebut],
    () => obtenirPlanningSemaine(dateDebut),
    { enabled: etapeActuelle >= 0 }
  );

  const { data: inventaire, isLoading: loadingInventaire } = utiliserRequete(
    ["inventaire"],
    () => listerInventaire(),
    { enabled: etapeActuelle >= 1 }
  );

  const { data: alertes } = utiliserRequete(
    ["inventaire-alertes"],
    () => obtenirAlertes(),
    { enabled: etapeActuelle >= 1 }
  );

  const { data: nutrition } = utiliserRequete(
    ["nutrition-hebdo", dateDebut],
    () => obtenirNutritionHebdo(dateDebut),
    { enabled: etapeActuelle >= 0 && !!planning }
  );

  // Mutations
  const { mutate: genererPlanning, isPending: enGenerationPlanning } = utiliserMutation(
    () => genererPlanningSemaine({ date_debut: dateDebut, nb_jours: 7 }),
    {
      onSuccess: () => {
        rechercherPlanning();
        toast.success("Planning généré par l'IA !");
      },
      onError: () => toast.error("Erreur lors de la génération du planning"),
    }
  );

  const { mutate: genererCourses, isPending: enGenerationCourses } = utiliserMutation(
    () => genererCoursesDepuisPlanning(dateDebut),
    {
      onSuccess: (result) => {
        setCoursesGenereesId(result.liste_id);
        toast.success(`${result.total_articles} articles ajoutés à la liste !`);
      },
      onError: () => toast.error("Erreur lors de la génération des courses"),
    }
  );

  const { mutate: genererBatch, isPending: enGenerationBatch } = utiliserMutation(
    () => {
      if (!planning) throw new Error("Pas de planning");
      if (!planning.planning_id) {
        throw new Error("Planning sans identifiant. Générez d'abord un planning persistant.");
      }
      const dimanche = new Date(dateDebut);
      dimanche.setDate(dimanche.getDate() + 6);
      return genererSessionDepuisPlanning({
        planning_id: planning.planning_id,
        date_session: dimanche.toISOString().split("T")[0],
      });
    },
    {
      onSuccess: (result) => {
        setBatchSessionId(result.session_id);
        toast.success(`Session batch créée avec ${result.nb_recettes} recettes !`);
      },
      onError: () => toast.error("Erreur lors de la création de la session batch"),
    }
  );

  const { mutate: copier, isPending: enCopie } = utiliserMutation(
    (semaineCible: string) => {
      if (!planning?.planning_id) throw new Error("Pas de planning à copier");
      return copierPlanning(planning.planning_id, semaineCible);
    },
    {
      onSuccess: (result) => {
        toast.success(result.message);
        invalider(["planning"]);
      },
      onError: () => toast.error("Erreur lors de la copie du planning"),
    }
  );

  // Calculs
  const nbRepas = planning?.repas?.length ?? 0;
  const articlesEnStock = inventaire?.length ?? 0;
  const alertesCount = alertes?.length ?? 0;
  const progression = ((etapeActuelle + 1) / ETAPES.length) * 100;

  // Regrouper les repas par jour pour l'affichage
  const repasParJour = useMemo(() => {
    const repas = planning?.repas ?? [];
    const parJour: Record<string, RepasPlanning[]> = {};
    for (const r of repas) {
      const jour = r.date_repas ?? r.date ?? "";
      (parJour[jour] ??= []).push(r);
    }
    return Object.entries(parJour).sort(([a], [b]) => a.localeCompare(b));
  }, [planning?.repas]);

  const peutAvancer = useMemo(() => {
    if (etapeActuelle === 0) return nbRepas > 0;
    if (etapeActuelle === 1) return true; // Inventaire optionnel
    if (etapeActuelle === 2) return true; // Courses optionnelles
    return true;
  }, [etapeActuelle, nbRepas]);

  const etapesFrise = useMemo(
    () => [
      {
        ...ETAPES[0],
        resume: nbRepas > 0 ? `${nbRepas} repas planifiés` : "Planning à générer",
        meta: planning?.planning_id
          ? `Semaine du ${new Date(dateDebut).toLocaleDateString("fr-FR")}`
          : "L'IA peut proposer une semaine complète en un clic",
      },
      {
        ...ETAPES[1],
        resume: `${articlesEnStock} articles disponibles`,
        meta:
          alertesCount > 0
            ? `${alertesCount} alerte${alertesCount > 1 ? "s" : ""} stock à vérifier`
            : "Stock stable, pas de rupture signalée",
        alerte: alertesCount > 0,
      },
      {
        ...ETAPES[2],
        resume: coursesGenereesId ? `Liste #${coursesGenereesId} prête` : "Liste de courses à générer",
        meta: coursesGenereesId
          ? "Les achats peuvent être cochés au fil de l'eau"
          : "Les articles seront calculés directement depuis les repas",
      },
      {
        ...ETAPES[3],
        resume: batchSessionId ? `Batch #${batchSessionId} créé` : "Récapitulatif et préparation",
        meta: nutrition
          ? `≈ ${Math.round(nutrition.moyenne_calories_par_jour)} kcal / jour`
          : "Synthèse nutritionnelle disponible en fin de parcours",
      },
    ],
    [
      alertesCount,
      articlesEnStock,
      batchSessionId,
      coursesGenereesId,
      dateDebut,
      nbRepas,
      nutrition,
      planning?.planning_id,
    ]
  );

  const allerEtapeSuivante = () => {
    if (etapeActuelle < ETAPES.length - 1 && peutAvancer) {
      setEtapeActuelle(etapeActuelle + 1);
    }
  };

  const allerEtapePrecedente = () => {
    if (etapeActuelle > 0) {
      setEtapeActuelle(etapeActuelle - 1);
    }
  };

  const etape = ETAPES[etapeActuelle];
  const IconeEtape = etape.icone;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          🗓️ Ma Semaine
        </h1>
        <p className="text-muted-foreground">
          Planifiez votre semaine en 4 étapes simples
        </p>
      </div>

      <FriseFluxCuisine
        etapes={etapesFrise}
        etapeActive={etapeActuelle}
        progression={progression}
        onSelectionEtape={setEtapeActuelle}
      />

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium">
            Étape {etapeActuelle + 1} sur {ETAPES.length}
          </span>
          <span className="text-muted-foreground">{Math.round(progression)}%</span>
        </div>
        <Progress value={progression} className="h-2" />
      </div>

      {/* Stepper Navigation */}
      <div className="flex items-center justify-between">
        {ETAPES.map((e, idx) => {
          const Icone = e.icone;
          const estActif = idx === etapeActuelle;
          const estComplete = idx < etapeActuelle;
          return (
            <div
              key={e.id}
              className="flex flex-col items-center gap-2 flex-1"
            >
              <button
                onClick={() => setEtapeActuelle(idx)}
                title={e.titre}
                className={`rounded-full p-3 transition-colors ${
                  estActif
                    ? "bg-primary text-primary-foreground"
                    : estComplete
                      ? "bg-green-600 text-white"
                      : "bg-muted text-muted-foreground"
                }`}
              >
                <Icone className="h-5 w-5" />
              </button>
              <span
                className={`text-xs text-center ${
                  estActif ? "font-medium" : "text-muted-foreground"
                }`}
              >
                {e.titre.replace(/^.+ /, "")}
              </span>
            </div>
          );
        })}
      </div>

      {/* Contenu de l'étape */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <IconeEtape className="h-6 w-6 text-primary" />
            <div>
              <CardTitle>{etape.titre}</CardTitle>
              <CardDescription>{etape.description}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Étape 1 : Planning */}
          {etapeActuelle === 0 && (
            <>
              {loadingPlanning ? (
                <div className="space-y-2">
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-20 w-full" />
                </div>
              ) : nbRepas > 0 ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">
                        ✅ Planning du {new Date(dateDebut).toLocaleDateString("fr-FR", {
                          day: "numeric",
                          month: "long",
                        })}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {nbRepas} repas planifiés
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={enCopie || !planning?.planning_id}
                        onClick={() => {
                          const lundi = new Date(dateDebut);
                          lundi.setDate(lundi.getDate() + 7);
                          const cible = lundi.toISOString().split("T")[0];
                          copier(cible);
                        }}
                      >
                        <Copy className="h-3.5 w-3.5 mr-1" />
                        {enCopie ? "Copie…" : "Copier semaine +1"}
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => router.push("/cuisine/planning")}>
                        Modifier
                      </Button>
                    </div>
                  </div>
                  {nutrition && (
                    <div className="grid grid-cols-3 gap-2 text-sm">
                      <div className="rounded-lg border p-2">
                        <p className="text-muted-foreground">Calories moy.</p>
                        <p className="font-medium">{Math.round(nutrition.moyenne_calories_par_jour)} kcal</p>
                      </div>
                      <div className="rounded-lg border p-2">
                        <p className="text-muted-foreground">Protéines</p>
                        <p className="font-medium">{Math.round(nutrition.totaux.proteines)}g</p>
                      </div>
                      <div className="rounded-lg border p-2">
                        <p className="text-muted-foreground">Équilibre</p>
                        <Badge
                          variant={
                            ((nutrition.nb_repas_total - nutrition.nb_repas_sans_donnees) /
                              Math.max(1, nutrition.nb_repas_total)) *
                              100 >
                            70
                              ? "default"
                              : "secondary"
                          }
                        >
                          {Math.round(
                            ((nutrition.nb_repas_total - nutrition.nb_repas_sans_donnees) /
                              Math.max(1, nutrition.nb_repas_total)) *
                              100
                          )}
                          %
                        </Badge>
                      </div>
                    </div>
                  )}

                  {/* Liste des repas par jour */}
                  <div className="space-y-3 max-h-80 overflow-y-auto">
                    {repasParJour.map(([jour, repasJour]) => (
                      <div key={jour} className="space-y-1">
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                          {new Date(jour).toLocaleDateString("fr-FR", {
                            weekday: "long",
                            day: "numeric",
                            month: "short",
                          })}
                        </p>
                        {repasJour.map((r) => (
                          <div key={r.id}>
                            <div className="flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-accent/50 transition-colors">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-1.5">
                                  <span className="text-xs text-muted-foreground">
                                    {TYPE_REPAS_LABEL[r.type_repas] ?? r.type_repas}
                                  </span>
                                  <span className="text-sm font-medium truncate">
                                    {r.recette_nom ?? r.notes ?? "—"}
                                  </span>
                                </div>
                              </div>
                              <ApplianceIcons repas={r} />
                            </div>
                            <JulesRow repas={r} />
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 space-y-4">
                  <AlertCircle className="h-12 w-12 mx-auto text-muted-foreground" />
                  <div>
                    <p className="font-medium">Aucun planning pour cette semaine</p>
                    <p className="text-sm text-muted-foreground">
                      Générez un planning avec l'IA ou créez-le manuellement
                    </p>
                  </div>
                  <div className="flex gap-2 justify-center">
                    <Button
                      onClick={() => genererPlanning(undefined)}
                      disabled={enGenerationPlanning}
                    >
                      {enGenerationPlanning ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <Sparkles className="mr-2 h-4 w-4" />
                      )}
                      Générer avec l'IA
                    </Button>
                    <Button variant="outline" onClick={() => router.push("/cuisine/planning")}>
                      Créer manuellement
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}

          {/* Étape 2 : Inventaire */}
          {etapeActuelle === 1 && (
            <>
              {loadingInventaire ? (
                <Skeleton className="h-40 w-full" />
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="rounded-lg border p-4">
                      <p className="text-sm text-muted-foreground">Articles en stock</p>
                      <p className="text-2xl font-bold">{articlesEnStock}</p>
                    </div>
                    <div className="rounded-lg border p-4">
                      <p className="text-sm text-muted-foreground">Alertes</p>
                      <p className="text-2xl font-bold text-orange-600">{alertesCount}</p>
                    </div>
                  </div>
                  {alertesCount > 0 && alertes && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium">⚠️ Alertes :</p>
                      <div className="space-y-1 max-h-32 overflow-y-auto">
                        {alertes.slice(0, 5).map((a) => (
                          <div
                            key={a.id}
                            className="flex items-center justify-between text-sm rounded-md bg-orange-50 dark:bg-orange-950 px-2 py-1"
                          >
                            <span>{a.nom}</span>
                            <Badge variant="outline" className="text-xs">
                              {a.est_bas ? "Stock bas" : "Périmé"}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  <Button variant="outline" className="w-full" onClick={() => router.push("/cuisine/inventaire")}>
                    Gérer l'inventaire
                  </Button>
                </div>
              )}
            </>
          )}

          {/* Étape 3 : Courses */}
          {etapeActuelle === 2 && (
            <div className="space-y-4">
              {coursesGenereesId ? (
                <div className="text-center py-6 space-y-4">
                  <CheckCircle2 className="h-12 w-12 mx-auto text-green-600" />
                  <div>
                    <p className="font-medium">Liste de courses générée !</p>
                    <p className="text-sm text-muted-foreground">
                      Les articles manquants ont été ajoutés à votre liste
                    </p>
                  </div>
                  <Button onClick={() => router.push("/cuisine/courses")}>
                    Voir la liste
                  </Button>
                </div>
              ) : (
                <div className="text-center py-6 space-y-4">
                  <ShoppingCart className="h-12 w-12 mx-auto text-muted-foreground" />
                  <div>
                    <p className="font-medium">Générer la liste de courses</p>
                    <p className="text-sm text-muted-foreground">
                      Basée sur votre planning et votre stock actuel
                    </p>
                  </div>
                  <Button
                    onClick={() => genererCourses(undefined)}
                    disabled={enGenerationCourses || nbRepas === 0}
                  >
                    {enGenerationCourses ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <ShoppingCart className="mr-2 h-4 w-4" />
                    )}
                    Générer les courses
                  </Button>
                </div>
              )}
            </div>
          )}

          {/* Étape 4 : Récapitulatif */}
          {etapeActuelle === 3 && (
            <div className="space-y-6">
              <div className="grid gap-4">
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div className="flex items-center gap-3">
                    <Calendar className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Planning</p>
                      <p className="text-sm text-muted-foreground">{nbRepas} repas</p>
                    </div>
                  </div>
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div className="flex items-center gap-3">
                    <Package className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Inventaire</p>
                      <p className="text-sm text-muted-foreground">
                        {articlesEnStock} articles{alertesCount > 0 && `, ${alertesCount} alertes`}
                      </p>
                    </div>
                  </div>
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div className="flex items-center gap-3">
                    <ShoppingCart className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Courses</p>
                      <p className="text-sm text-muted-foreground">
                        {coursesGenereesId ? "Liste générée" : "Non générées"}
                      </p>
                    </div>
                  </div>
                  {coursesGenereesId ? (
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium">Actions supplémentaires :</p>
                <div className="grid gap-2">
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => genererBatch(undefined)}
                    disabled={enGenerationBatch || !planning}
                  >
                    {enGenerationBatch ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <CookingPot className="mr-2 h-4 w-4" />
                    )}
                    Créer une session batch cooking
                  </Button>
                  {batchSessionId && (
                    <Button
                      variant="outline"
                      onClick={() => router.push(`/cuisine/batch-cooking/${batchSessionId}`)}
                    >
                      Voir la session batch
                    </Button>
                  )}
                </div>
              </div>

              <div className="pt-4 border-t">
                <Button className="w-full" onClick={() => router.push("/")}>
                  Terminer et retourner au dashboard
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      {etapeActuelle < 3 && (
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={allerEtapePrecedente}
            disabled={etapeActuelle === 0}
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            Précédent
          </Button>
          <Button
            onClick={allerEtapeSuivante}
            disabled={!peutAvancer}
          >
            Suivant
            <ChevronRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
