"use client";

import { useEffect, useState } from "react";
import {
  Calendar,
  Check,
  ExternalLink,
  Loader2,
  Puzzle,
  RefreshCw,
  ShieldCheck,
  ShoppingCart,
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
      <SectionExtensionChrome />
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
                Synchronisation bidirectionnelle complète du planning repas et activités
                avec Google Calendar
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

function SectionExtensionChrome() {
  const [extensionDisponible, setExtensionDisponible] = useState(false);
  const [navigateurCompatible, setNavigateurCompatible] = useState(true);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const detecterStatut = () => {
      setExtensionDisponible(document.documentElement.dataset.assistantMatanneDriveBridge === "ready");
      const agent = window.navigator.userAgent.toLowerCase();
      setNavigateurCompatible(agent.includes("chrome") || agent.includes("edg"));
    };

    const handleBridgeReady = () => {
      setExtensionDisponible(true);
      detecterStatut();
    };

    detecterStatut();
    window.addEventListener("assistant-matanne-drive-bridge-ready", handleBridgeReady);

    return () => {
      window.removeEventListener("assistant-matanne-drive-bridge-ready", handleBridgeReady);
    };
  }, []);

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <Puzzle className="mt-0.5 h-6 w-6 text-emerald-600" />
            <div>
              <CardTitle>Extension Chrome Carrefour Drive</CardTitle>
              <CardDescription>
                Active l’ajout en 1 clic au panier Carrefour Drive depuis la liste de courses et garde les correspondances produit → Drive.
              </CardDescription>
            </div>
          </div>
          <Badge variant={extensionDisponible ? "default" : "secondary"}>
            {extensionDisponible ? "Bridge détecté" : "À installer"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-lg border bg-muted/30 p-3">
            <p className="font-medium">Source</p>
            <p className="mt-1 text-muted-foreground">
              Dossier repo <code>extension-chrome/</code>
            </p>
          </div>
          <div className="rounded-lg border bg-muted/30 p-3">
            <p className="font-medium">Navigateur</p>
            <p className="mt-1 text-muted-foreground">
              {navigateurCompatible ? "Chrome / Edge détecté" : "Utilisez Chrome ou Edge pour l’installation"}
            </p>
          </div>
          <div className="rounded-lg border bg-muted/30 p-3">
            <p className="font-medium">Usage</p>
            <p className="mt-1 text-muted-foreground">
              Disponible dans <code>Cuisine → Courses</code>
            </p>
          </div>
        </div>

        <div className="rounded-lg border border-dashed bg-muted/20 p-4">
          <p className="font-medium">Installation rapide</p>
          <ol className="mt-2 list-decimal space-y-1 pl-5 text-muted-foreground">
            <li>Ouvrez <code>chrome://extensions</code> puis activez le mode développeur.</li>
            <li>Chargez le dossier local <code>extension-chrome/</code>.</li>
            <li>Ouvrez <code>Cuisine → Courses</code> et utilisez le bouton <strong>Ajouter au Drive</strong>.</li>
          </ol>
        </div>

        <div className="rounded-lg border border-emerald-200 bg-emerald-50/60 p-4 dark:border-emerald-900 dark:bg-emerald-950/20">
          <div className="flex items-start gap-2">
            <ShieldCheck className="mt-0.5 h-4 w-4 text-emerald-700" />
            <div>
              <p className="font-medium">Sécurité minimale</p>
              <p className="text-muted-foreground">
                L’extension ne stocke pas de secret permanent : elle réutilise le token déjà présent dans l’application au moment d’une action utilisateur explicite.
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={() => window.open("chrome://extensions", "_blank") }>
            <ExternalLink className="mr-2 h-4 w-4" />
            Ouvrir Chrome Extensions
          </Button>
          <Button variant="outline" size="sm" onClick={() => window.open("https://www.carrefour.fr/courses-en-ligne", "_blank", "noopener,noreferrer") }>
            <ShoppingCart className="mr-2 h-4 w-4" />
            Ouvrir Carrefour Drive
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
