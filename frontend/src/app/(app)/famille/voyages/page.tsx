"use client";

import { useState } from "react";
import { Plane, Sparkles } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/composants/ui/select";
import { utiliserMutation, utiliserRequete, utiliserInvalidation } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import { toast } from "sonner";

type ResumeVoyage = {
  id: number;
  titre: string;
  destination: string;
  date_depart: string;
  jours_restants?: number | null;
  preparation_pct: number;
  budget_restant?: number | null;
};

export default function PageVoyages() {
  const invalider = utiliserInvalidation();
  const [destination, setDestination] = useState("");
  const [typeSejour, setTypeSejour] = useState("mer_ete");
  const [nbJours, setNbJours] = useState("5");

  const { data: voyages } = utiliserRequete(["voyages"], async () => {
    const { data } = await clientApi.get<{ items: ResumeVoyage[] }>("/famille/voyages");
    return data.items;
  });

  const { mutate: planifier, isPending } = utiliserMutation(
    async () => {
      const { data } = await clientApi.post("/famille/voyages/planifier-ia", {
        destination: destination.trim(),
        type_sejour: typeSejour,
        nb_jours: Number(nbJours || 5),
      });
      return data as { suggestions: string[] };
    },
    {
      onSuccess: (data) => {
        invalider(["voyages"]);
        toast.success("Voyage planifié");
        if (data.suggestions?.length) {
          toast.message(data.suggestions[0]);
        }
        setDestination("");
      },
      onError: () => toast.error("Impossible de planifier le voyage"),
    }
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Mode Voyage</h1>
        <p className="text-muted-foreground">Séjours, checklists intelligentes et préparation assistée.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_1.1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              Planifier un séjour
            </CardTitle>
            <CardDescription>Crée un voyage et prépare automatiquement les checklists adaptées.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Destination</Label>
              <Input value={destination} onChange={(e) => setDestination(e.target.value)} placeholder="Ex: Bretagne, Chamonix..." />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Type de séjour</Label>
                <Select value={typeSejour} onValueChange={setTypeSejour}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mer_ete">Mer été</SelectItem>
                    <SelectItem value="mer_hiver">Mer hiver</SelectItem>
                    <SelectItem value="montagne_ete">Montagne été</SelectItem>
                    <SelectItem value="montagne_hiver">Montagne hiver</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Durée</Label>
                <Input value={nbJours} onChange={(e) => setNbJours(e.target.value)} type="number" min="1" />
              </div>
            </div>
            <Button onClick={() => planifier()} disabled={isPending || !destination.trim()}>
              <Plane className="mr-2 h-4 w-4" />
              {isPending ? "Planification..." : "Planifier avec l'IA"}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Voyages à venir</CardTitle>
            <CardDescription>Résumé de préparation et budget restant.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {voyages?.length ? voyages.map((voyage) => (
              <div key={voyage.id} className="rounded-lg border p-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-medium">{voyage.titre}</p>
                    <p className="text-sm text-muted-foreground">{voyage.destination}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {voyage.jours_restants ?? "-"} j
                  </span>
                </div>
                <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                  <span>Préparation: {voyage.preparation_pct}%</span>
                  <span>Budget restant: {voyage.budget_restant ?? 0} €</span>
                </div>
              </div>
            )) : (
              <p className="text-sm text-muted-foreground">Aucun voyage planifié.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}