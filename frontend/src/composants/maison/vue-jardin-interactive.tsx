"use client";

import { useMemo, useState } from "react";
import { Flower2, MapPinned, Sprout } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import type { ResumeJardinHabitat, ZoneJardinHabitat } from "@/types/habitat";

function clampPosition(value: number | undefined, fallback: number) {
  const numeric = Number(value ?? fallback);
  return Math.max(4, Math.min(84, numeric));
}

export function VueJardinInteractive({
  zones,
  resume,
}: {
  zones: ZoneJardinHabitat[];
  resume?: ResumeJardinHabitat | null;
}) {
  const [selectionId, setSelectionId] = useState<number | null>(zones[0]?.id ?? null);

  const zoneActive = useMemo(
    () => zones.find((zone) => zone.id === selectionId) ?? zones[0] ?? null,
    [selectionId, zones]
  );

  if (!zones.length) {
    return null;
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <MapPinned className="h-4 w-4 text-emerald-600" />
            Vue jardin 2D interactive
          </CardTitle>
          <CardDescription>
            Zones cliquables, surface estimée et prochaine lecture visuelle du jardin.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-hidden rounded-2xl border bg-[radial-gradient(circle_at_top,#f4fff1,#e3f5de_58%,#d6ecd0)]">
            <svg viewBox="0 0 100 100" className="h-[320px] w-full" preserveAspectRatio="none">
              {zones.map((zone) => {
                const left = clampPosition(zone.position_x, 10);
                const top = clampPosition(zone.position_y, 10);
                const width = Math.max(14, Math.min(34, Number(zone.largeur ?? 18)));
                const height = Math.max(12, Math.min(30, Number(zone.longueur ?? 16)));
                const active = zone.id === zoneActive?.id;

                return (
                  <g key={zone.id} onClick={() => setSelectionId(zone.id)} className="cursor-pointer">
                    <rect
                      x={left}
                      y={top}
                      width={width}
                      height={height}
                      rx="4"
                      fill={active ? "rgba(16, 185, 129, 0.35)" : "rgba(16, 185, 129, 0.18)"}
                      stroke={active ? "rgba(6, 95, 70, 0.8)" : "rgba(6, 95, 70, 0.35)"}
                      strokeWidth={active ? 0.8 : 0.4}
                    />
                    <text x={left + 2} y={top + 5} className="fill-emerald-950 text-[3.2px] font-semibold">
                      {zone.nom}
                    </text>
                    {zone.type_zone ? (
                      <text x={left + 2} y={top + 9} className="fill-emerald-900 text-[2.5px]">
                        {zone.type_zone}
                      </text>
                    ) : null}
                  </g>
                );
              })}
            </svg>
          </div>
          {resume ? (
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-muted-foreground">
              <span>{resume.zones} zones</span>
              <span>{Math.round(resume.surface_totale_m2)} m2</span>
              <span>{Math.round(resume.budget_estime).toLocaleString("fr-FR")} € estimés</span>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <Flower2 className="h-4 w-4 text-amber-600" />
            Détail de zone
          </CardTitle>
          <CardDescription>
            Lecture rapide de la zone sélectionnée pour décider des prochaines actions.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {zoneActive ? (
            <>
              <div>
                <p className="text-lg font-semibold">{zoneActive.nom}</p>
                <p className="text-sm text-muted-foreground">{zoneActive.type_zone ?? "Type libre"}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                {zoneActive.surface_m2 ? <Badge variant="secondary">{Math.round(zoneActive.surface_m2)} m2</Badge> : null}
                {zoneActive.budget_estime ? <Badge variant="outline">{Math.round(zoneActive.budget_estime)} €</Badge> : null}
                {zoneActive.plantes?.length ? <Badge variant="outline">{zoneActive.plantes.length} plantes</Badge> : null}
              </div>
              {zoneActive.plantes?.length ? (
                <div>
                  <p className="mb-2 text-sm font-medium">Plantes présentes</p>
                  <div className="flex flex-wrap gap-2">
                    {zoneActive.plantes.map((plante) => (
                      <Badge key={plante} variant="secondary" className="gap-1">
                        <Sprout className="h-3 w-3" />
                        {plante}
                      </Badge>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Aucune plante renseignée pour cette zone.</p>
              )}
              {zoneActive.amenagements?.length ? (
                <div>
                  <p className="mb-2 text-sm font-medium">Aménagements</p>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    {zoneActive.amenagements.map((item) => (
                      <li key={item}>• {item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Sélectionnez une zone pour voir le détail.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
