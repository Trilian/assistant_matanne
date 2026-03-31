"use client";

import { useEffect, useState } from "react";
import { Bell, Loader2, Mail, MessageCircle, Save, Smartphone } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Switch } from "@/composants/ui/switch";
import { utiliserInvalidation, utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import { statutPush, souscrirePush, desabonnerPush } from "@/bibliotheque/api/push";
import { demanderPermissionNotificationsJeux } from "@/crochets/utiliser-notifications-jeux";
import { toast } from "sonner";

const CANAUX_DISPONIBLES = [
  { id: "push", label: "Push navigateur", icon: Smartphone },
  { id: "ntfy", label: "Ntfy.sh", icon: Bell },
  { id: "email", label: "Email", icon: Mail },
  { id: "whatsapp", label: "WhatsApp", icon: MessageCircle },
] as const;

const CATEGORIES = [
  {
    id: "rappels" as const,
    label: "Rappels",
    description: "Rappels courses, entretien, médicaments…",
  },
  {
    id: "alertes" as const,
    label: "Alertes critiques",
    description: "Péremptions, garanties, dépassement budget…",
  },
  {
    id: "resumes" as const,
    label: "Résumés",
    description: "Résumé hebdomadaire, rapport mensuel…",
  },
];

function OngletCanauxNotifications() {
  const invalider = utiliserInvalidation();

  const { data: prefs, isLoading } = utiliserRequete(
    ["preferences", "notifications"],
    async () => {
      const { obtenirPreferencesNotifications } = await import("@/bibliotheque/api/preferences");
      return obtenirPreferencesNotifications();
    }
  );

  const { mutate: sauvegarder, isPending } = utiliserMutation(
    async (data: Parameters<typeof import("@/bibliotheque/api/preferences").sauvegarderPreferencesNotifications>[0]) => {
      const { sauvegarderPreferencesNotifications } = await import("@/bibliotheque/api/preferences");
      return sauvegarderPreferencesNotifications(data);
    },
    {
      onSuccess: () => {
        invalider(["preferences", "notifications"]);
        toast.success("Préférences de notification sauvegardées");
      },
      onError: () => toast.error("Erreur lors de la sauvegarde"),
    }
  );

  const [canaux, setCanaux] = useState<Record<string, string[]>>({
    rappels: ["push", "ntfy"],
    alertes: ["push", "ntfy", "email"],
    resumes: ["email"],
  });

  useEffect(() => {
    if (prefs?.canaux_par_categorie) {
      setCanaux({
        rappels: prefs.canaux_par_categorie.rappels ?? ["push", "ntfy"],
        alertes: prefs.canaux_par_categorie.alertes ?? ["push", "ntfy", "email"],
        resumes: prefs.canaux_par_categorie.resumes ?? ["email"],
      });
    }
  }, [prefs]);

  const toggleCanal = (categorie: string, canal: string) => {
    setCanaux((prev) => {
      const actuels = prev[categorie] ?? [];
      const nouveau = actuels.includes(canal)
        ? actuels.filter((c) => c !== canal)
        : [...actuels, canal];
      return { ...prev, [categorie]: nouveau };
    });
  };

  const handleSave = () => {
    sauvegarder({
      canaux_par_categorie: canaux as unknown as Parameters<typeof sauvegarder>[0]["canaux_par_categorie"],
    });
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">Chargement…</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Canaux par catégorie</CardTitle>
        <CardDescription>
          Choisissez les canaux de notification pour chaque type d&apos;alerte.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6 max-w-lg">
        {CATEGORIES.map((cat) => (
          <div key={cat.id} className="space-y-3">
            <div>
              <p className="font-medium text-sm">{cat.label}</p>
              <p className="text-xs text-muted-foreground">{cat.description}</p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {CANAUX_DISPONIBLES.map(({ id, label, icon: Icon }) => {
                const actif = (canaux[cat.id] ?? []).includes(id);
                return (
                  <div
                    key={id}
                    className="flex items-center justify-between rounded-md border px-3 py-2"
                  >
                    <div className="flex items-center gap-2">
                      <Icon className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{label}</span>
                    </div>
                    <Switch
                      checked={actif}
                      onCheckedChange={() => toggleCanal(cat.id, id)}
                      aria-label={`${label} pour ${cat.label}`}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        ))}

        <Button onClick={handleSave} disabled={isPending} className="w-full">
          {isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Save className="mr-2 h-4 w-4" />
          )}
          Sauvegarder les canaux
        </Button>
      </CardContent>
    </Card>
  );
}

export function OngletNotifications() {
  const { data: status, isLoading } = utiliserRequete(
    ["push", "status"],
    statutPush
  );
  const invalider = utiliserInvalidation();

  const { mutate: activer, isPending: enActivation } = utiliserMutation(
    async () => {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY,
      });
      const json = subscription.toJSON();
      return souscrirePush({
        endpoint: json.endpoint!,
        keys: {
          p256dh: json.keys!.p256dh!,
          auth: json.keys!.auth!,
        },
      });
    },
    {
      onSuccess: () => {
        invalider(["push", "status"]);
        toast.success("Notifications activées");
      },
      onError: () => toast.error("Erreur lors de l'activation"),
    }
  );

  const { mutate: desactiver, isPending: enDesactivation } = utiliserMutation(
    async () => {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      if (subscription) {
        await desabonnerPush(subscription.endpoint);
        await subscription.unsubscribe();
      }
    },
    {
      onSuccess: () => {
        invalider(["push", "status"]);
        toast.success("Notifications désactivées");
      },
      onError: () => toast.error("Erreur lors de la désactivation"),
    }
  );

  const pushSupporte = typeof window !== "undefined" && "PushManager" in window;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Notifications Push</CardTitle>
          <CardDescription>
            Recevez des alertes pour les courses, entretien, péremptions, etc.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 max-w-md">
          {!pushSupporte ? (
            <p className="text-sm text-muted-foreground">
              Les notifications push ne sont pas supportées par votre navigateur.
            </p>
          ) : isLoading ? (
            <p className="text-sm text-muted-foreground">Chargement…</p>
          ) : (
            <>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-sm">Notifications</p>
                  <p className="text-xs text-muted-foreground">
                    {status?.has_subscriptions
                      ? `${status.subscription_count} appareil(s) enregistré(s)`
                      : "Aucun appareil enregistré"}
                  </p>
                </div>
                <Badge variant={status?.has_subscriptions ? "default" : "secondary"}>
                  {status?.has_subscriptions ? "Activées" : "Désactivées"}
                </Badge>
              </div>

              {status?.has_subscriptions ? (
                <Button
                  variant="outline"
                  onClick={() => desactiver(undefined)}
                  disabled={enDesactivation}
                >
                  {enDesactivation ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Bell className="mr-2 h-4 w-4" />}
                  Désactiver les notifications
                </Button>
              ) : (
                <Button
                  onClick={() => activer(undefined)}
                  disabled={enActivation}
                >
                  {enActivation ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Bell className="mr-2 h-4 w-4" />}
                  Activer les notifications
                </Button>
              )}

              <div className="border-t pt-4 space-y-3">
                <div>
                  <p className="font-medium text-sm">🎮 Notifications Jeux</p>
                  <p className="text-xs text-muted-foreground">
                    Recevez des alertes pour les résultats de paris et tirages loto
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    try {
                      const granted = await demanderPermissionNotificationsJeux();
                      if (granted) {
                        toast.success("Notifications jeux activées");
                      } else {
                        toast.error("Permission refusée");
                      }
                    } catch {
                      toast.error("Erreur lors de l'activation");
                    }
                  }}
                >
                  <Bell className="mr-2 h-4 w-4" />
                  Activer les notifications jeux
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <OngletCanauxNotifications />
    </div>
  );
}
