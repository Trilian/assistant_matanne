"use client";

import { useState } from "react";
import Image from "next/image";
import { analyserPlanHabitat, historiquePlanHabitat, listerPlansHabitat } from "@/bibliotheque/api/habitat";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Textarea } from "@/composants/ui/textarea";
import { utiliserMutationAvecInvalidation, utiliserRequete } from "@/crochets/utiliser-api";

export default function PlansHabitatPage() {
  const [planSelectionne, setPlanSelectionne] = useState<number | null>(null);
  const [prompt, setPrompt] = useState("Optimiser la circulation, les rangements et le cout travaux.");
  const { data: plans } = utiliserRequete(["habitat", "plans"], listerPlansHabitat);
  const planActif = (plans ?? []).find((plan) => plan.id === planSelectionne) ?? (plans ?? [])[0] ?? null;
  const { data: historique } = utiliserRequete(
    ["habitat", "plans", String(planActif?.id ?? "aucun"), "historique"],
    () => historiquePlanHabitat(planActif?.id ?? 0),
    { enabled: Boolean(planActif?.id) }
  );

  const analyseMutation = utiliserMutationAvecInvalidation(
    ({ planId, generer_image }: { planId: number; generer_image: boolean }) =>
      analyserPlanHabitat(planId, { prompt_utilisateur: prompt, generer_image }),
    [["habitat", "plans"], ["habitat", "plans", String(planActif?.id ?? "aucun"), "historique"]]
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Plans</h1>
        <p className="text-muted-foreground">Pipeline IA pour analyser les plans et historiser les variantes.</p>
      </div>

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
            <CardDescription>Mistral pour le diagnostic, Hugging Face en option pour la variante visuelle.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
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