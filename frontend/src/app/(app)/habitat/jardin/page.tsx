"use client";

import { useState } from "react";
import {
  listerZonesJardinHabitat,
  modifierZoneJardinHabitat,
  obtenirResumeJardinHabitat,
} from "@/bibliotheque/api/habitat";
import { EntetePageHabitat } from "@/composants/habitat/entete-page-habitat";
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
      <EntetePageHabitat
        badge="H8 • Paysagisme"
        titre="Jardin Habitat"
        description="Pilotage des zones exterieures, lecture surfacique et budget d'amenagement dans le meme flux que les plans Habitat." 
        stats={[
          { label: "Zones", valeur: `${resume?.zones ?? zones?.length ?? 0}` },
          { label: "Surface", valeur: `${Math.round(resume?.surface_totale_m2 ?? 0)} m2` },
          { label: "Budget", valeur: `${Math.round(resume?.budget_estime ?? 0).toLocaleString("fr-FR")} EUR` },
        ]}
      />

      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Canvas paysager 2.5D</CardTitle>
            <CardDescription>Vue isométrique légère pour lire les volumes des zones de jardin.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative h-[420px] overflow-hidden rounded-xl border bg-[radial-gradient(circle_at_20%_10%,#f8fff6_0%,#e7f5e9_52%,#d9ead9_100%)] [perspective:1200px]">
              <div className="absolute inset-0 [transform:rotateX(58deg)_rotateZ(-42deg)_scale(1.04)] [transform-origin:center_58%]">
                {(zones ?? []).map((zone) => {
                  const left = classePourValeur(zone.position_x ?? 10, "left");
                  const top = classePourValeur(zone.position_y ?? 10, "top");
                  const width = classePourValeur(zone.largeur ?? 18, "width");
                  const height = classePourValeur(zone.longueur ?? 16, "height");
                  const active = zone.id === zoneActive?.id;

                  return (
                    <button
                      key={zone.id}
                      type="button"
                      onClick={() => setSelection(zone)}
                      className={`absolute z-20 text-left transition-transform hover:scale-[1.02] focus-visible:outline-none ${left} ${top} ${width} ${height}`}
                    >
                      <span
                        className={`absolute inset-0 rounded-lg border ${active ? "border-emerald-900/70" : "border-emerald-700/35"} ${active ? "bg-emerald-500/50" : "bg-emerald-400/30"}`}
                      />
                      <span
                        className={`absolute left-[4%] top-[100%] h-[16%] w-[96%] origin-top-left skew-x-[-40deg] rounded-b-md ${active ? "bg-emerald-900/45" : "bg-emerald-900/30"}`}
                      />
                      <span
                        className={`absolute left-[100%] top-[4%] h-[96%] w-[14%] origin-top-left skew-y-[-40deg] rounded-r-md ${active ? "bg-emerald-800/45" : "bg-emerald-800/30"}`}
                      />
                      <span className="relative z-30 block p-2 text-xs font-semibold text-emerald-950 drop-shadow-sm">
                        {zone.nom}
                      </span>
                    </button>
                  );
                })}
              </div>
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