"use client";

import { Bot, History } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Label } from "@/composants/ui/label";
import { Input } from "@/composants/ui/input";
import { Badge } from "@/composants/ui/badge";
import { Switch } from "@/composants/ui/switch";
import { toast } from "sonner";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import {
  obtenirPiloteAutoStatus,
  togglePiloteAuto,
  obtenirActionsPiloteAuto,
} from "@/bibliotheque/api/ia-avancee";
import { clientApi } from "@/bibliotheque/api/client";

async function obtenirModeleIa(): Promise<string> {
  const { data } = await clientApi.get<{ services?: { ia?: { details?: { modele?: string } } } }>("/health");
  return data?.services?.ia?.details?.modele ?? "—";
}

export function OngletIA() {
  const { data: modeleReel = "—" } = utiliserRequete(
    ["ia", "modele"],
    obtenirModeleIa,
    { staleTime: 300_000 }
  );

  const { data: piloteStatus, refetch: rechargerPilote } = utiliserRequete(
    ["pilote-auto", "status"],
    obtenirPiloteAutoStatus,
    { staleTime: 30_000 }
  );

  const { data: actionsRecentes } = utiliserRequete(
    ["pilote-auto", "actions"],
    obtenirActionsPiloteAuto,
    { staleTime: 60_000 }
  );

  const { mutate: basculerPilote, isPending: basculementEnCours } = utiliserMutation(
    (actif: boolean) => togglePiloteAuto(actif),
    {
      onSuccess: () => {
        toast.success(
          piloteStatus?.actif ? "Pilote automatique désactivé" : "Pilote automatique activé"
        );
        void rechargerPilote();
      },
      onError: () => toast.error("Impossible de modifier le pilote automatique"),
    }
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Intelligence Artificielle</CardTitle>
          <CardDescription>Configuration de Mistral AI</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 max-w-md">
          <div className="space-y-2">
            <Label htmlFor="ia-modele">Modèle IA actif</Label>
            <Input
              id="ia-modele"
              value={modeleReel}
              readOnly
              className="bg-muted cursor-default"
            />
            <p className="text-xs text-muted-foreground">
              Défini par <code>MISTRAL_MODEL</code> dans les variables d&apos;environnement serveur.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Pilote Automatique */}
      <Card className="border-sky-300/60 bg-sky-50/50 dark:border-sky-900/50 dark:bg-sky-950/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-sky-600" />
            Mode Pilote Automatique
          </CardTitle>
          <CardDescription>
            L&apos;IA peut exécuter des actions automatiquement selon le niveau choisi
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Activer le pilote automatique</Label>
              <p className="text-xs text-muted-foreground">
                {piloteStatus?.actif
                  ? `Niveau : ${piloteStatus.niveau_autonomie}`
                  : "Désactivé — l'IA ne fait que des suggestions"}
              </p>
            </div>
            <Switch
              checked={piloteStatus?.actif ?? false}
              onCheckedChange={(actif) => basculerPilote(actif)}
              disabled={basculementEnCours}
            />
          </div>

          {/* Actions récentes */}
          {actionsRecentes && actionsRecentes.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium flex items-center gap-1">
                <History className="h-3.5 w-3.5" />
                Actions récentes
              </p>
              <div className="space-y-1.5 max-h-48 overflow-y-auto">
                {actionsRecentes.slice(0, 5).map((action, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between text-xs rounded-md bg-background p-2 border"
                  >
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-[10px]">
                        {action.module}
                      </Badge>
                      <span>{action.action}</span>
                    </div>
                    <Badge
                      variant={action.statut === "succes" ? "default" : "secondary"}
                      className="text-[10px]"
                    >
                      {action.statut}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
