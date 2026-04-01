"use client";

import { useMemo, useState } from "react";
import { Flag, Loader2, Save } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Switch } from "@/composants/ui/switch";
import { Label } from "@/composants/ui/label";
import { basculerModeMaintenance, lireFeatureFlags, sauvegarderFeatureFlags } from "@/bibliotheque/api/admin";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function PageAdminFeatureFlags() {
  const [flagsLocaux, setFlagsLocaux] = useState<Record<string, boolean>>({});
  const [sauvegardeEnCours, setSauvegardeEnCours] = useState(false);
  const [retour, setRetour] = useState("");

  const { data, isLoading, refetch } = utiliserRequete(["admin", "feature-flags"], lireFeatureFlags);

  const flags = useMemo(() => {
    if (Object.keys(flagsLocaux).length > 0) {
      return flagsLocaux;
    }
    return data?.flags ?? {};
  }, [data?.flags, flagsLocaux]);

  const toggle = (key: string, value: boolean) => {
    setFlagsLocaux((prev) => ({ ...prev, [key]: value }));
  };

  const sauvegarder = async () => {
    setSauvegardeEnCours(true);
    setRetour("");
    try {
      await sauvegarderFeatureFlags(flags);
      setRetour("Feature flags sauvegardes.");
      await refetch();
    } catch {
      setRetour("Echec de sauvegarde.");
    } finally {
      setSauvegardeEnCours(false);
    }
  };

  const maintenance = async (enabled: boolean) => {
    try {
      await basculerModeMaintenance(enabled);
      setFlagsLocaux((prev) => ({ ...prev, "admin.maintenance_mode": enabled }));
      setRetour(`Mode maintenance ${enabled ? "active" : "desactive"}.`);
    } catch {
      setRetour("Impossible de basculer le mode maintenance.");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Flag className="h-6 w-6" />
          Feature Flags
        </h1>
        <p className="text-muted-foreground">Activation/desactivation runtime des modules admin.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Flags disponibles</CardTitle>
          <CardDescription>{data?.total ?? 0} flags charges.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
          {Object.entries(flags).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between rounded border p-3">
              <Label htmlFor={key} className="text-sm">{key}</Label>
              <Switch id={key} checked={Boolean(value)} onCheckedChange={(checked) => toggle(key, checked)} />
            </div>
          ))}
          <div className="flex gap-2">
            <Button onClick={sauvegarder} disabled={sauvegardeEnCours}>
              {sauvegardeEnCours ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
              Sauvegarder
            </Button>
            <Button
              variant="outline"
              onClick={() => void maintenance(!Boolean(flags["admin.maintenance_mode"]))}
            >
              Basculer maintenance
            </Button>
          </div>
          {retour && <p className="text-sm text-muted-foreground">{retour}</p>}
        </CardContent>
      </Card>
    </div>
  );
}
