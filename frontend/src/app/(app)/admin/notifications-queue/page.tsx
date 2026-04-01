"use client";

import { useState } from "react";
import { Bell, Loader2, RefreshCw, Send, Trash2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { listerQueueNotifications, relancerQueueNotifications, supprimerQueueNotifications } from "@/bibliotheque/api/admin";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function PageAdminNotificationsQueue() {
  const [actionEnCours, setActionEnCours] = useState<string | null>(null);
  const [retour, setRetour] = useState("");

  const { data, isLoading, refetch } = utiliserRequete(["admin", "notifications", "queue"], () =>
    listerQueueNotifications({ limit: 50 })
  );

  const relancer = async (userId: string) => {
    setActionEnCours(`retry:${userId}`);
    setRetour("");
    try {
      await relancerQueueNotifications(userId);
      setRetour(`Queue relancee pour ${userId}.`);
      await refetch();
    } catch {
      setRetour(`Echec relance pour ${userId}.`);
    } finally {
      setActionEnCours(null);
    }
  };

  const supprimer = async (userId: string) => {
    setActionEnCours(`delete:${userId}`);
    setRetour("");
    try {
      await supprimerQueueNotifications(userId);
      setRetour(`Queue supprimee pour ${userId}.`);
      await refetch();
    } catch {
      setRetour(`Echec suppression pour ${userId}.`);
    } finally {
      setActionEnCours(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Bell className="h-6 w-6" />
            Queue Notifications
          </h1>
          <p className="text-muted-foreground">Gestion des digests en attente et flush manuel par utilisateur.</p>
        </div>
        <Button variant="outline" onClick={() => void refetch()}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Rafraichir
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Utilisateurs en attente</CardTitle>
          <CardDescription>Total utilisateurs pending: {data?.total_users_pending ?? 0}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
          {(data?.items ?? []).map((item) => (
            <div key={item.user_id} className="rounded border p-3 space-y-2">
              <div className="font-medium">{item.user_id}</div>
              <div className="text-sm text-muted-foreground">taille queue: {item.taille_queue}</div>
              {item.dernier_message && <div className="text-sm">dernier message: {item.dernier_message}</div>}
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => void relancer(item.user_id)}
                  disabled={actionEnCours !== null}
                >
                  {actionEnCours === `retry:${item.user_id}` ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="mr-2 h-4 w-4" />
                  )}
                  Flush
                </Button>
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={() => void supprimer(item.user_id)}
                  disabled={actionEnCours !== null}
                >
                  {actionEnCours === `delete:${item.user_id}` ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Trash2 className="mr-2 h-4 w-4" />
                  )}
                  Vider
                </Button>
              </div>
            </div>
          ))}
          {retour && <p className="text-sm text-muted-foreground">{retour}</p>}
        </CardContent>
      </Card>
    </div>
  );
}
