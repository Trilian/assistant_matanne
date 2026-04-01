"use client";

import { useState } from "react";
import { DatabaseZap, Loader2, Trash2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { obtenirStatsCache, purgerCache, viderCache } from "@/bibliotheque/api/admin";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function PageAdminCache() {
  const [pattern, setPattern] = useState("*");
  const [actionEnCours, setActionEnCours] = useState(false);
  const [retour, setRetour] = useState("");

  const { data, isLoading, refetch } = utiliserRequete(["admin", "cache", "stats"], obtenirStatsCache);

  const purge = async () => {
    setActionEnCours(true);
    setRetour("");
    try {
      const result = await purgerCache(pattern || "*");
      setRetour(result.message);
      await refetch();
    } catch {
      setRetour("Echec purge cache.");
    } finally {
      setActionEnCours(false);
    }
  };

  const clearAll = async () => {
    setActionEnCours(true);
    setRetour("");
    try {
      const result = await viderCache();
      setRetour(result.message);
      await refetch();
    } catch {
      setRetour("Echec vidage cache.");
    } finally {
      setActionEnCours(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <DatabaseZap className="h-6 w-6" />
          Cache Admin
        </h1>
        <p className="text-muted-foreground">Statistiques et purge selective/global du cache multi-niveaux.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Statistiques</CardTitle>
          <CardDescription>Snapshot courant du backend cache.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <pre className="text-xs bg-muted rounded p-3 overflow-auto max-h-80">{JSON.stringify(data ?? {}, null, 2)}</pre>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Purge</CardTitle>
          <CardDescription>Pattern type recettes_* ou * pour tout.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 max-w-md">
          <div className="space-y-1">
            <Label htmlFor="pattern-cache-admin">Pattern</Label>
            <Input id="pattern-cache-admin" value={pattern} onChange={(e) => setPattern(e.target.value)} />
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => void purge()} disabled={actionEnCours}>
              {actionEnCours ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Trash2 className="mr-2 h-4 w-4" />}
              Purger pattern
            </Button>
            <Button variant="destructive" onClick={() => void clearAll()} disabled={actionEnCours}>
              Vider tout
            </Button>
          </div>
          {retour && <p className="text-sm text-muted-foreground">{retour}</p>}
        </CardContent>
      </Card>
    </div>
  );
}
