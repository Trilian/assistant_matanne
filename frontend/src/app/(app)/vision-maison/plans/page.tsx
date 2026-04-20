"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import dynamic from "next/dynamic";
import { Box, Sparkles } from "lucide-react";
import {
  analyserPlanHabitat,
  historiquePlanHabitat,
  listerPiecesHabitat,
  listerPlansHabitat,
  obtenirConfiguration3DHabitat,
  sauvegarderConfiguration3DHabitat,
} from "@/bibliotheque/api/habitat";
import { EntetePageHabitat } from "@/composants/habitat/entete-page-habitat";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { Textarea } from "@/composants/ui/textarea";
import { utiliserMutation, utiliserMutationAvecInvalidation, utiliserRequete } from "@/crochets/utiliser-api";
import type { PlanHabitatConfiguration3DServeur } from "@/types/habitat";

const Plan3DHabitat = dynamic(() => import("@/composants/habitat/plan-3d-habitat"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[420px] items-center justify-center rounded-xl border text-sm text-muted-foreground">
      Chargement de la vue 3D...
    </div>
  ),
});

export default function PlansHabitatPage() {
  const [planSelectionne, setPlanSelectionne] = useState<number | null>(null);
  const [afficherComparaisonIA, setAfficherComparaisonIA] = useState(false);
  const [prompt, setPrompt] = useState("Optimiser la circulation, les rangements et le cout travaux.");
  const { data: plans } = utiliserRequete(["habitat", "plans"], listerPlansHabitat);
  const planActif = (plans ?? []).find((plan) => plan.id === planSelectionne) ?? (plans ?? [])[0] ?? null;
  const { data: historique } = utiliserRequete(
    ["habitat", "plans", String(planActif?.id ?? "aucun"), "historique"],
    () => historiquePlanHabitat(planActif?.id ?? 0),
    { enabled: Boolean(planActif?.id) }
  );
  const { data: piecesPlanActif } = utiliserRequete(
    ["habitat", "plans", String(planActif?.id ?? "aucun"), "pieces"],
    () => listerPiecesHabitat(planActif?.id ?? 0),
    { enabled: Boolean(planActif?.id) }
  );
  const { data: configuration3D } = utiliserRequete(
    ["habitat", "plans", String(planActif?.id ?? "aucun"), "configuration-3d"],
    () => obtenirConfiguration3DHabitat(planActif?.id ?? 0),
    { enabled: Boolean(planActif?.id) }
  );

  const analyseMutation = utiliserMutationAvecInvalidation(
    ({ planId, generer_image }: { planId: number; generer_image: boolean }) =>
      analyserPlanHabitat(planId, { prompt_utilisateur: prompt, generer_image }),
    [["habitat", "plans"], ["habitat", "plans", String(planActif?.id ?? "aucun"), "historique"]]
  );
  const sauvegardeConfigurationMutation = utiliserMutation(
    ({ planId, payload }: { planId: number; payload: Omit<PlanHabitatConfiguration3DServeur, "plan_id"> }) =>
      sauvegarderConfiguration3DHabitat(planId, payload)
  );

  const piecesVarianteIA = useMemo(
    () =>
      (analyseMutation.data?.analyse.suggestions_pieces ?? []).map((suggestion, index) => ({
        id: -(index + 1),
        plan_id: planActif?.id ?? 0,
        nom: suggestion.nom,
        type_piece: suggestion.type_piece,
        surface_m2: suggestion.surface_m2,
      })),
    [analyseMutation.data?.analyse.suggestions_pieces, planActif?.id]
  );

  return (
    <div className="space-y-6">
      <EntetePageHabitat
        badge="H6 • Plans IA"
        titre="Plans"
        description="Analyse des plans, lecture des risques et memorisation des variantes pour converger vers un schema exploitable avant travaux ou amenagement." 
        stats={[
          { label: "Plans", valeur: `${plans?.length ?? 0}` },
          { label: "Historique", valeur: `${historique?.length ?? 0}` },
          { label: "Plan actif", valeur: planActif?.nom ?? "-" },
        ]}
      />

      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Plans enregistres</CardTitle>
            <CardDescription>Sélectionne un plan puis déclenche une analyse.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {(plans ?? []).map((plan) => {
              const actif = planActif?.id === plan.id;
              return (
                <button
                  key={plan.id}
                  type="button"
                  onClick={() => setPlanSelectionne(plan.id)}
                  className={`w-full rounded-xl border p-3 text-left transition-colors ${actif ? "border-emerald-500 bg-emerald-50" : "hover:bg-accent/40"}`}
                >
                  <p className="font-medium">{plan.nom}</p>
                  <p className="text-xs text-muted-foreground">
                    {plan.type_plan} · v{plan.version} · {plan.surface_totale_m2 ?? "?"} m2
                  </p>
                  {plan.suggestions_ia && plan.suggestions_ia.length > 0 && (
                    <p className="mt-2 text-xs text-muted-foreground">
                      {plan.suggestions_ia.length} suggestion(s) IA déjà stockée(s)
                    </p>
                  )}
                </button>
              );
            })}
            {(plans ?? []).length === 0 && <p className="text-sm text-muted-foreground">Aucun plan disponible.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Analyse IA</CardTitle>
            <CardDescription>Mistral pour le diagnostic + visualisation 3D instantanee du plan actif.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Tabs defaultValue="analyse" className="w-full">
              <TabsList variant="line" className="w-full justify-start">
                <TabsTrigger value="analyse" className="gap-1.5">
                  <Sparkles className="h-4 w-4" /> Analyse IA
                </TabsTrigger>
                <TabsTrigger value="visualisation" className="gap-1.5">
                  <Box className="h-4 w-4" /> Vue 3D
                </TabsTrigger>
              </TabsList>

              <TabsContent value="analyse" className="space-y-4 pt-3">
                <Textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} rows={4} />
                <div className="flex gap-2">
                  <Button
                    disabled={!planActif || analyseMutation.isPending}
                    onClick={() => planActif && analyseMutation.mutate({ planId: planActif.id, generer_image: false })}
                  >
                    {analyseMutation.isPending ? "Analyse..." : "Analyser"}
                  </Button>
                  <Button
                    variant="outline"
                    disabled={!planActif || analyseMutation.isPending}
                    onClick={() => planActif && analyseMutation.mutate({ planId: planActif.id, generer_image: true })}
                  >
                    Analyse + image
                  </Button>
                </div>

                {analyseMutation.data && (
                  <div className="rounded-xl border p-4">
                    <p className="font-medium">{analyseMutation.data.analyse.resume}</p>
                    <div className="mt-3 grid gap-3 md:grid-cols-2">
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Points forts</p>
                        <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                          {analyseMutation.data.analyse.points_forts.map((item) => <li key={item}>• {item}</li>)}
                        </ul>
                      </div>
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Risques</p>
                        <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                          {analyseMutation.data.analyse.risques.map((item) => <li key={item}>• {item}</li>)}
                        </ul>
                      </div>
                    </div>
                    {analyseMutation.data.image?.image_base64 && (
                      <Image
                        src={analyseMutation.data.image.image_base64}
                        alt="Variante visuelle du plan"
                        width={1200}
                        height={800}
                        unoptimized
                        className="mt-4 rounded-xl border"
                      />
                    )}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="visualisation" className="space-y-3 pt-3">
                {!planActif ? (
                  <div className="flex h-[420px] items-center justify-center rounded-xl border border-dashed text-sm text-muted-foreground">
                    Selectionnez un plan pour ouvrir la visualisation 3D.
                  </div>
                ) : (
                  <>
                    {piecesVarianteIA.length > 0 && (
                      <div className="flex items-center gap-2 rounded-lg border px-3 py-2 text-xs text-muted-foreground">
                        <span>{piecesVarianteIA.length} piece(s) proposee(s) par l'analyse IA.</span>
                        <Button
                          type="button"
                          size="sm"
                          variant={afficherComparaisonIA ? "default" : "outline"}
                          onClick={() => setAfficherComparaisonIA((precedent) => !precedent)}
                        >
                          {afficherComparaisonIA ? "Masquer comparaison" : "Comparer avec variante IA"}
                        </Button>
                      </div>
                    )}
                    <Plan3DHabitat
                      pieces={piecesPlanActif ?? []}
                      nomPlan={planActif.nom}
                      planId={planActif.id}
                      piecesVariante={piecesVarianteIA}
                      afficherComparaison={afficherComparaisonIA}
                      configurationServeur={configuration3D ?? null}
                      sauvegardeServeurEnCours={sauvegardeConfigurationMutation.isPending}
                      onSauvegarderConfigurationServeur={async (payload) => {
                        await sauvegardeConfigurationMutation.mutateAsync({
                          planId: planActif.id,
                          payload,
                        });
                      }}
                    />
                  </>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Historique des variantes</CardTitle>
          <CardDescription>Demandes IA et analyses précédentes pour le plan sélectionné.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {(historique ?? []).map((item) => (
            <div key={item.id} className="rounded-xl border p-4">
              <p className="font-medium">{item.prompt_utilisateur}</p>
              <p className="mt-1 text-sm text-muted-foreground">{item.analyse_ia.resume}</p>
            </div>
          ))}
          {(historique ?? []).length === 0 && <p className="text-sm text-muted-foreground">Aucun historique IA pour ce plan.</p>}
        </CardContent>
      </Card>
    </div>
  );
}