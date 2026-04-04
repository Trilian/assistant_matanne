"use client";

import { useEffect, useRef, useState } from "react";
import { Workflow, Play } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { utiliserMutation, utiliserRequete, utiliserInvalidation } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import { toast } from "sonner";

type Automation = {
  id: number;
  nom: string;
  declencheur: { type: string; seuil?: number };
  action: { type: string; quantite?: number };
  active: boolean;
};

export default function PageAutomations() {
  const invalider = utiliserInvalidation();
  const [nom, setNom] = useState("");
  const initialisationAutoFaite = useRef(false);

  const { data: automations } = utiliserRequete(["automations"], async () => {
    const { data } = await clientApi.get<{ items: Automation[] }>("/automations");
    return data.items;
  });

  const { mutate: initialiser } = utiliserMutation(
    async () => {
      await clientApi.post<{ total: number }>("/automations/init")
    },
    {
      onSuccess: () => {
        invalider(["automations"])
      },
      onError: () => {
        initialisationAutoFaite.current = true
      },
    }
  )

  useEffect(() => {
    if (automations === undefined || initialisationAutoFaite.current) {
      return
    }
    if (automations.length === 0) {
      initialisationAutoFaite.current = true
      initialiser(undefined)
    }
  }, [automations, initialiser])

  const { mutate: creer, isPending } = utiliserMutation(
    async () => {
      await clientApi.post("/automations", {
        nom: nom.trim(),
        declencheur: { type: "stock_bas", seuil: 2 },
        action: { type: "ajouter_courses", quantite: 1 },
        active: true,
      });
    },
    {
      onSuccess: () => {
        invalider(["automations"]);
        setNom("");
        toast.success("Automation créée");
      },
      onError: () => toast.error("Impossible de créer l'automation"),
    }
  );

  const { mutate: simuler } = utiliserMutation(
    async (id: number) => {
      const { data } = await clientApi.post<{ resume: string }>(`/automations/${id}/simuler`);
      return data;
    },
    {
      onSuccess: (data) => toast.message(data.resume),
      onError: () => toast.error("Simulation impossible"),
    }
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Automations</h1>
        <p className="text-muted-foreground">Règles simples “si → alors” pour alléger les tâches répétitives.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Workflow className="h-5 w-5" />
              Nouvelle automation
            </CardTitle>
            <CardDescription>Version initiale stockée dans les préférences utilisateur.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Nom</Label>
              <Input value={nom} onChange={(e) => setNom(e.target.value)} placeholder="Ex: Lait bas -> courses" />
            </div>
            <p className="text-sm text-muted-foreground">
              Déclencheur par défaut: stock bas. Action par défaut: ajout à la liste de courses.
            </p>
            <Button onClick={() => creer(undefined)} disabled={isPending || !nom.trim()}>
              Créer l'automation
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Règles actives</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {automations?.length ? automations.map((automation) => (
              <div key={automation.id} className="rounded-lg border p-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-medium">{automation.nom}</p>
                    <p className="text-sm text-muted-foreground">
                      Si {automation.declencheur.type} alors {automation.action.type}
                    </p>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => simuler(automation.id)}>
                    <Play className="mr-1 h-4 w-4" />
                    Simuler
                  </Button>
                </div>
              </div>
            )) : (
              <p className="text-sm text-muted-foreground">Aucune automation configurée.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}