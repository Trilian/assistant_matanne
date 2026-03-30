"use client";

import { useState } from "react";
import {
  listerZonesJardinHabitat,
  modifierZoneJardinHabitat,
  obtenirResumeJardinHabitat,
} from "@/bibliotheque/api/habitat";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import { utiliserMutationAvecInvalidation, utiliserRequete } from "@/crochets/utiliser-api";
import type { ZoneJardinHabitat } from "@/types/habitat";

const POSITION_CLASSES = [
  "0", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60", "65", "70", "75", "80", "85", "90", "95",
].map((value) => ({
  left: `left-[${value}%]`,
  top: `top-[${value}%]`,
  width: `w-[${value}%]`,
  height: `h-[${value}%]`,
}));

function classePourValeur(value: number | undefined, axis: "left" | "top" | "width" | "height") {
  const numeric = typeof value === "number" ? value : 0;
  const index = Math.max(0, Math.min(POSITION_CLASSES.length - 1, Math.round(numeric / 5)));
  return POSITION_CLASSES[index][axis];
}

export default function JardinHabitatPage() {
  const { data: zones } = utiliserRequete(["habitat", "jardin", "zones"], () => listerZonesJardinHabitat());
  const { data: resume } = utiliserRequete(["habitat", "jardin", "resume"], () => obtenirResumeJardinHabitat());
  const [selection, setSelection] = useState<ZoneJardinHabitat | null>(null);
  const zoneActive = selection ?? zones?.[0] ?? null;

  const patchMutation = utiliserMutationAvecInvalidation(
    ({ zoneId, payload }: { zoneId: number; payload: Partial<ZoneJardinHabitat> }) =>
      modifierZoneJardinHabitat(zoneId, payload),
    [["habitat", "jardin", "zones"], ["habitat", "jardin", "resume"], ["habitat", "hub"]]
  );

  function updateSelection(key: keyof ZoneJardinHabitat, value: string) {
    setSelection((current) => {
      const base = current ?? zoneActive;
      return base ? { ...base, [key]: Number(value) || 0 } : base;
    });
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Jardin Habitat</h1>
        <p className="text-muted-foreground">Canvas paysager léger avec zones persistées et budget agrégé.</p>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Canvas paysager</CardTitle>
            <CardDescription>Les positions viennent des coordonnées enregistrées dans Habitat.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative h-[420px] overflow-hidden rounded-xl border bg-[linear-gradient(180deg,#f6fff6_0%,#ebf7ef_100%)]">
              {(zones ?? []).map((zone) => (
                <button
                  key={zone.id}
                  type="button"
                  onClick={() => setSelection(zone)}
                  className={`absolute rounded-xl border border-emerald-700/30 bg-emerald-500/20 text-left shadow-sm transition hover:bg-emerald-500/30 ${classePourValeur(zone.position_x ?? 5, "left")} ${classePourValeur(zone.position_y ?? 5, "top")} ${classePourValeur(zone.largeur ?? 18, "width")} ${classePourValeur(zone.longueur ?? 16, "height")}`}
                >
                  <span className="block p-2 text-xs font-medium text-emerald-950">{zone.nom}</span>
                </button>
              ))}
              {(zones ?? []).length === 0 && (
                <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                  Aucune zone jardin disponible.
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Edition de zone</CardTitle>
            <CardDescription>
              {resume ? `${resume.zones} zone(s) · ${resume.surface_totale_m2} m2 · ${resume.budget_estime} EUR` : "Sélectionne une zone à ajuster."}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {zoneActive ? (
              <>
                <div>
                  <p className="font-medium">{zoneActive?.nom}</p>
                  <p className="text-xs text-muted-foreground">{zoneActive?.type_zone ?? "type libre"}</p>
                </div>
                <div className="grid gap-3 grid-cols-2">
                  <Input value={String(zoneActive?.position_x ?? 0)} onChange={(event) => updateSelection("position_x", event.target.value)} />
                  <Input value={String(zoneActive?.position_y ?? 0)} onChange={(event) => updateSelection("position_y", event.target.value)} />
                  <Input value={String(zoneActive?.largeur ?? 0)} onChange={(event) => updateSelection("largeur", event.target.value)} />
                  <Input value={String(zoneActive?.longueur ?? 0)} onChange={(event) => updateSelection("longueur", event.target.value)} />
                </div>
                <Button
                  disabled={patchMutation.isPending}
                  onClick={() =>
                    zoneActive && patchMutation.mutate({
                      zoneId: zoneActive.id,
                      payload: {
                        position_x: zoneActive.position_x,
                        position_y: zoneActive.position_y,
                        largeur: zoneActive.largeur,
                        longueur: zoneActive.longueur,
                      },
                    })
                  }
                >
                  {patchMutation.isPending ? "Enregistrement..." : "Enregistrer le canvas"}
                </Button>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">Aucune zone sélectionnée.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}