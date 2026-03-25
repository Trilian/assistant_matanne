"use client";

import { useState } from "react";
import {
  Calendar,
  Check,
  ExternalLink,
  Loader2,
  RefreshCw,
  Unlink,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import {
  obtenirUrlAuthGoogle,
  synchroniserGoogle,
  statutGoogle,
  deconnecterGoogle,
} from "@/bibliotheque/api/calendriers";
import { toast } from "sonner";

export default function IntegrationsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🔗 Intégrations</h1>
        <p className="text-muted-foreground">
          Connectez vos services externes
        </p>
      </div>
      <SectionGoogleCalendar />
    </div>
  );
}

function SectionGoogleCalendar() {
  const [syncing, setSyncing] = useState(false);
  const invalider = utiliserInvalidation();

  const { data: statut, isLoading } = utiliserRequete(
    ["google-calendar", "status"],
    statutGoogle
  );

  const connecterMutation = utiliserMutation(
    async () => {
      const { auth_url } = await obtenirUrlAuthGoogle();
      window.location.href = auth_url;
    },
    {
      onError: () => toast.error("Impossible de générer l'URL de connexion Google"),
    }
  );

  const deconnecterMutation = utiliserMutation(deconnecterGoogle, {
    onSuccess: () => {
      invalider(["google-calendar"]);
      toast.success("Google Calendar déconnecté");
    },
    onError: () => toast.error("Erreur lors de la déconnexion"),
  });

  const handleSync = async () => {
    setSyncing(true);
    try {
      const result = await synchroniserGoogle();
      toast.success(
        `Sync terminée : ${result.events_imported} importés, ${result.events_exported} exportés`
      );
      invalider(["google-calendar"]);
    } catch {
      toast.error("Erreur lors de la synchronisation");
    } finally {
      setSyncing(false);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Calendar className="h-6 w-6 text-blue-500" />
            <div>
              <CardTitle>Google Calendar</CardTitle>
              <CardDescription>
                Synchronisez votre planning repas et activités avec Google
                Calendar
              </CardDescription>
            </div>
          </div>
          <Badge variant={statut?.connected ? "default" : "secondary"}>
            {statut?.connected ? (
              <>
                <Check className="mr-1 h-3 w-3" />
                Connecté
              </>
            ) : (
              "Non connecté"
            )}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {statut?.connected ? (
          <>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Calendrier :</span>{" "}
                {statut.nom}
              </div>
              <div>
                <span className="text-muted-foreground">Direction :</span>{" "}
                {statut.sync_direction}
              </div>
              <div>
                <span className="text-muted-foreground">Dernière sync :</span>{" "}
                {statut.last_sync
                  ? new Date(statut.last_sync).toLocaleString("fr-FR")
                  : "Jamais"}
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSync}
                disabled={syncing}
              >
                {syncing ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="mr-2 h-4 w-4" />
                )}
                Synchroniser maintenant
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => deconnecterMutation.mutate(undefined)}
                disabled={deconnecterMutation.isPending}
              >
                <Unlink className="mr-2 h-4 w-4" />
                Déconnecter
              </Button>
            </div>
          </>
        ) : (
          <Button
            onClick={() => connecterMutation.mutate(undefined)}
            disabled={connecterMutation.isPending}
          >
            {connecterMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <ExternalLink className="mr-2 h-4 w-4" />
            )}
            Connecter Google Calendar
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
