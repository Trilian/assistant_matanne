"use client";

import { useMemo, useState } from "react";
import { Bot, Loader2, Play } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { executerActionService, listerActionsServices } from "@/bibliotheque/api/admin";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function PageAdminAutomations() {
  const [actionEnCours, setActionEnCours] = useState<string | null>(null);
  const [retour, setRetour] = useState<string>("");

  const { data, isLoading } = utiliserRequete(["admin", "actions-services"], listerActionsServices);

  const actionsAutomations = useMemo(
    () => (data?.items ?? []).filter((item) => item.id.startsWith("automations.")),
    [data?.items]
  );

  const executer = async (actionId: string, dryRun: boolean) => {
    setActionEnCours(actionId + String(dryRun));
    setRetour("");
    try {
      const result = await executerActionService(actionId, { dry_run: dryRun });
      setRetour(`Action ${actionId} executee (${dryRun ? "dry-run" : "reel"}).`);
      if (result.status !== "ok") {
        setRetour(`Action ${actionId} terminee avec statut: ${result.status}`);
      }
    } catch {
      setRetour(`Echec de l'action ${actionId}.`);
    } finally {
      setActionEnCours(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Bot className="h-6 w-6" />
          Automations Admin
        </h1>
        <p className="text-muted-foreground">Execution manuelle des regles d'automation exposees par le backend.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Actions disponibles</CardTitle>
          <CardDescription>Filtre sur les actions de type automations.*</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
          {actionsAutomations.map((action) => (
            <div key={action.id} className="rounded border p-3 space-y-2">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <div className="font-medium">{action.description}</div>
                  <div className="text-xs text-muted-foreground">{action.service}</div>
                </div>
                <Badge variant="secondary">{action.id}</Badge>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => void executer(action.id, true)}
                  disabled={actionEnCours !== null}
                >
                  {actionEnCours === action.id + "true" ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="mr-2 h-4 w-4" />
                  )}
                  Dry-run
                </Button>
                <Button
                  size="sm"
                  onClick={() => void executer(action.id, false)}
                  disabled={actionEnCours !== null}
                >
                  {actionEnCours === action.id + "false" ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="mr-2 h-4 w-4" />
                  )}
                  Executer
                </Button>
              </div>
            </div>
          ))}
          {actionsAutomations.length === 0 && !isLoading && (
            <p className="text-sm text-muted-foreground">Aucune action automation detectee.</p>
          )}
          {retour && <p className="text-sm text-muted-foreground">{retour}</p>}
        </CardContent>
      </Card>
    </div>
  );
}
