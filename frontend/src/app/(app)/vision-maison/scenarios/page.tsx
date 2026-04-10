"use client";

import { useEffect, useState } from "react";
import { BarChart3, PlusCircle } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/composants/ui/button";
import { EntetePageHabitat } from "@/composants/habitat/entete-page-habitat";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import { comparerScenariosHabitat, creerScenarioHabitat } from "@/bibliotheque/api/habitat";
import { utiliserBrouillonAuto } from "@/crochets/utiliser-brouillon-auto";
import { utiliserRaccourcisPage } from "@/crochets/utiliser-raccourcis-page";

export default function ScenariosHabitatPage() {
  const [nom, setNom] = useState("");
  const [description, setDescription] = useState("");
  const { valeurInitiale: brouillonInitial, effacerBrouillon } = utiliserBrouillonAuto({
    cle: "draft:habitat:scenario",
    valeur: { nom, description },
    actif: true,
  });

  useEffect(() => {
    if (!brouillonInitial) {
      return;
    }

    setNom((prev) => prev || brouillonInitial.nom || "");
    setDescription((prev) => prev || brouillonInitial.description || "");
  }, [brouillonInitial]);

  const { data: scenarios, refetch } = utiliserRequete(
    ["habitat", "scenarios", "comparaison"],
    comparerScenariosHabitat
  );

  const { mutate, isPending } = utiliserMutation(creerScenarioHabitat, {
    onSuccess: () => {
      setNom("");
      setDescription("");
      effacerBrouillon();
      toast.success("Scénario créé");
      refetch();
    },
  });

  utiliserRaccourcisPage([
    {
      touche: "n",
      action: () => {
        setNom("");
        setDescription("");
      },
    },
    {
      touche: "s",
      action: () => {
        if (!isPending && nom.trim().length > 0) {
          mutate({ nom, description, statut: "brouillon" });
        }
      },
    },
  ]);

  return (
    <div className="space-y-6">
      <EntetePageHabitat
        badge="H1-H2 • Decision"
        titre="Scénarios"
        description="Comparer objectivement les options logement et garder un arbitrage lisible entre budget, surface cible et confort familial." 
        stats={[
          { label: "Scenarios", valeur: `${scenarios?.length ?? 0}` },
          { label: "Meilleur score", valeur: scenarios?.[0]?.score_global ? `${scenarios[0].score_global.toFixed(1)} / 100` : "-" },
        ]}
      />

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base"><PlusCircle className="h-4 w-4" /> Nouveau scenario</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-1">
            <Label htmlFor="nom-scenario">Nom</Label>
            <Input
              id="nom-scenario"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              placeholder="Ex: Demenager vers maison 4 chambres"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="desc-scenario">Description</Label>
            <Input
              id="desc-scenario"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Contexte, contraintes, hypothese"
            />
          </div>
          <Button
            onClick={() => mutate({ nom, description, statut: "brouillon" })}
            disabled={isPending || nom.trim().length === 0}
          >
            {isPending ? "Creation..." : "Creer"}
          </Button>
          {(nom.trim().length > 0 || description.trim().length > 0) && (
            <p className="text-xs text-muted-foreground">
              Brouillon enregistré automatiquement. Raccourcis: N pour réinitialiser, S pour enregistrer.
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base"><BarChart3 className="h-4 w-4" /> Classement</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {(scenarios ?? []).map((scenario) => (
            <div key={scenario.id} className="rounded-md border p-3 flex items-center justify-between">
              <div>
                <p className="font-medium">{scenario.nom}</p>
                <p className="text-xs text-muted-foreground">
                  {scenario.nb_chambres ?? "?"} chambres · {scenario.surface_finale_m2 ?? "?"} m2
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold">{(scenario.score_global ?? 0).toFixed(1)} / 100</p>
                <p className="text-xs text-muted-foreground">{scenario.budget_estime ?? "?"} EUR</p>
              </div>
            </div>
          ))}
          {(scenarios ?? []).length === 0 && (
            <p className="text-sm text-muted-foreground">Aucun scenario pour le moment.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
