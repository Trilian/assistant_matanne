"use client";

import { useState } from "react";
import { BarChart3, PlusCircle } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import { comparerScenariosHabitat, creerScenarioHabitat } from "@/bibliotheque/api/habitat";

export default function ScenariosHabitatPage() {
  const [nom, setNom] = useState("");
  const [description, setDescription] = useState("");

  const { data: scenarios, refetch } = utiliserRequete(
    ["habitat", "scenarios", "comparaison"],
    comparerScenariosHabitat
  );

  const { mutate, isPending } = utiliserMutation(creerScenarioHabitat, {
    onSuccess: () => {
      setNom("");
      setDescription("");
      refetch();
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Scenarios Habitat</h1>
        <p className="text-muted-foreground">Comparer objectivement les options de logement.</p>
      </div>

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
