"use client";

import { useState } from "react";
import { Activity, Loader2, Play, RefreshCw } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Textarea } from "@/composants/ui/textarea";
import { Badge } from "@/composants/ui/badge";
import { declencherEvenementAdmin, lireEvenementsAdmin } from "@/bibliotheque/api/admin";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function PageAdminEvents() {
  const [typeEvenement, setTypeEvenement] = useState("");
  const [source, setSource] = useState("admin");
  const [payloadTexte, setPayloadTexte] = useState("{}");
  const [envoiEnCours, setEnvoiEnCours] = useState(false);
  const [retour, setRetour] = useState<{ ok: boolean; message: string } | null>(null);

  const { data, isLoading, refetch } = utiliserRequete(["admin", "events"], () =>
    lireEvenementsAdmin({ limite: 30 })
  );

  const declencher = async () => {
    setRetour(null);
    setEnvoiEnCours(true);
    try {
      const payload = payloadTexte.trim() ? (JSON.parse(payloadTexte) as Record<string, unknown>) : {};
      const result = await declencherEvenementAdmin({
        type_evenement: typeEvenement,
        source,
        payload,
      });
      setRetour({ ok: true, message: `Evenement emis (${result.handlers_notifies} handlers notifies).` });
      await refetch();
    } catch {
      setRetour({ ok: false, message: "Impossible d'emettre l'evenement. Verifiez le JSON du payload." });
    } finally {
      setEnvoiEnCours(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Activity className="h-6 w-6" />
          Event Bus Admin
        </h1>
        <p className="text-muted-foreground">Visualisation des evenements et trigger manuel pour tests.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Declencher un evenement</CardTitle>
            <CardDescription>Emet un evenement domaine depuis l'interface admin.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-1">
              <Label htmlFor="type_evenement">Type d'evenement</Label>
              <Input
                id="type_evenement"
                placeholder="courses.item_ajoute"
                value={typeEvenement}
                onChange={(e) => setTypeEvenement(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="source_evenement">Source</Label>
              <Input id="source_evenement" value={source} onChange={(e) => setSource(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="payload_evenement">Payload JSON</Label>
              <Textarea
                id="payload_evenement"
                value={payloadTexte}
                onChange={(e) => setPayloadTexte(e.target.value)}
                rows={8}
              />
            </div>
            <Button onClick={declencher} disabled={envoiEnCours || !typeEvenement.trim()}>
              {envoiEnCours ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
              Emettre
            </Button>
            {retour && (
              <p className={`text-sm ${retour.ok ? "text-green-600" : "text-red-600"}`}>{retour.message}</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Historique recent</span>
              <Button variant="outline" size="sm" onClick={() => void refetch()}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Rafraichir
              </Button>
            </CardTitle>
            <CardDescription>Metrices et derniers evenements du bus.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            {data?.metriques && (
              <pre className="text-xs bg-muted rounded p-3 overflow-auto max-h-40">
                {JSON.stringify(data.metriques, null, 2)}
              </pre>
            )}
            <div className="space-y-2 max-h-80 overflow-auto">
              {(data?.items ?? []).map((item) => (
                <div key={item.event_id} className="rounded border p-3 text-sm space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <Badge variant="secondary">{item.type}</Badge>
                    <span className="text-xs text-muted-foreground">{item.timestamp ?? "-"}</span>
                  </div>
                  <div className="text-xs text-muted-foreground">source: {item.source}</div>
                  <pre className="text-xs bg-muted rounded p-2 overflow-auto">{JSON.stringify(item.data, null, 2)}</pre>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
