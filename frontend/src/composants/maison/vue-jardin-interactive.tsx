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

function obtenirEtatZone(zone: ZoneJardinHabitat): "plante" | "amenagement" | "libre" {
  if ((zone.plantes?.length ?? 0) > 0) return "plante";
  if ((zone.amenagements?.length ?? 0) > 0) return "amenagement";
  return "libre";
}

function couleursZone(zone: ZoneJardinHabitat, active: boolean) {
  const etat = obtenirEtatZone(zone);
  if (etat === "plante") {
    return {
      fill: active ? "rgba(16,185,129,0.48)" : "rgba(16,185,129,0.26)",
      stroke: active ? "rgba(6,95,70,0.95)" : "rgba(6,95,70,0.55)",
      shadow: "rgba(6,95,70,0.18)",
      label: "Planté",
    };
  }
  if (etat === "amenagement") {
    return {
      fill: active ? "rgba(245,158,11,0.44)" : "rgba(245,158,11,0.22)",
      stroke: active ? "rgba(146,64,14,0.95)" : "rgba(146,64,14,0.5)",
      shadow: "rgba(146,64,14,0.15)",
      label: "À aménager",
    };
  }
  return {
    fill: active ? "rgba(148,163,184,0.38)" : "rgba(148,163,184,0.18)",
    stroke: active ? "rgba(51,65,85,0.85)" : "rgba(51,65,85,0.38)",
    shadow: "rgba(51,65,85,0.12)",
    label: "Libre",
  };
}

/** Micro-icône plante SVG pour les zones plantées */
function IcoPlante({ x, y }: { x: number; y: number }) {
  return (
    <g transform={`translate(${x},${y}) scale(0.018)`} className="pointer-events-none" style={{ animation: "croissancePlante 1.2s ease-out both" }}>
      <path d="M12 22V12M12 12C12 12 8 8 4 10C4 10 6 16 12 12ZM12 12C12 12 16 8 20 10C20 10 18 16 12 12Z" stroke="rgba(6,95,70,0.8)" strokeWidth="1.5" strokeLinecap="round" fill="none" />
    </g>
  );
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
    () => zones.find((z) => z.id === selectionId) ?? zones[0] ?? null,
    [selectionId, zones]
  );

  if (!zones.length) return null;

  return (
    <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <MapPinned className="h-4 w-4 text-emerald-600" />
            Vue jardin 2.5D interactive
          </CardTitle>
          <CardDescription>
            Vue isométrique avec animations de croissance. Cliquez sur une zone pour voir les détails.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-3 flex flex-wrap gap-2">
            <Badge variant="secondary" className="bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-200">Planté</Badge>
            <Badge variant="secondary" className="bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-200">À aménager</Badge>
            <Badge variant="secondary" className="bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-200">Libre</Badge>
          </div>

          {/* Conteneur 2.5D avec perspective isométrique via CSS */}
          <div
            className="overflow-hidden rounded-2xl border"
            style={{
              background: "radial-gradient(circle at top, #f4fff1, #d6ecd0)",
            }}
          >
            <div
              style={{
                transform: "perspective(600px) rotateX(28deg) rotateZ(-2deg) scale(1.04)",
                transformOrigin: "50% 30%",
                transition: "transform 0.4s ease",
              }}
            >
              <svg
                viewBox="0 0 100 100"
                className="h-[300px] w-full"
                preserveAspectRatio="none"
                style={{ display: "block" }}
              >
                {/* Grille isométrique de fond */}
                <defs>
                  <pattern id="grille-jardin" width="10" height="10" patternUnits="userSpaceOnUse">
                    <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(6,95,70,0.08)" strokeWidth="0.3" />
                  </pattern>
                  <style>{`
                    @keyframes croissancePlante {
                      from { opacity: 0; transform: scaleY(0); }
                      to   { opacity: 1; transform: scaleY(1); }
                    }
                    @keyframes pulsePlante {
                      0%, 100% { opacity: 0.7; }
                      50%       { opacity: 1; }
                    }
                    .zone-plante { animation: pulsePlante 3s ease-in-out infinite; }
                    .zone-selectionnee { filter: drop-shadow(0 2px 4px rgba(0,0,0,0.25)); }
                  `}</style>
                </defs>
                <rect width="100" height="100" fill="url(#grille-jardin)" />

                {zones.map((zone) => {
                  const left = clampPosition(zone.position_x, 10);
                  const top = clampPosition(zone.position_y, 10);
                  const width = Math.max(14, Math.min(34, Number(zone.largeur ?? 18)));
                  const height = Math.max(12, Math.min(30, Number(zone.longueur ?? 16)));
                  const active = zone.id === zoneActive?.id;
                  const etat = obtenirEtatZone(zone);
                  const palette = couleursZone(zone, active);

                  return (
                    <g
                      key={zone.id}
                      onClick={() => setSelectionId(zone.id)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setSelectionId(zone.id); }
                      }}
                      className={`cursor-pointer${active ? " zone-selectionnee" : ""}${etat === "plante" ? " zone-plante" : ""}`}
                      role="button"
                      tabIndex={0}
                      aria-label={`Zone ${zone.nom}`}
                      aria-pressed={active}
                    >
                      {/* Ombre 2.5D (décalée vers le bas) */}
                      <rect
                        x={left + 1.2}
                        y={top + 1.8}
                        width={width}
                        height={height}
                        rx="4"
                        fill={palette.shadow}
                        className="pointer-events-none"
                      />
                      {/* Zone principale */}
                      <rect
                        x={left}
                        y={top}
                        width={width}
                        height={height}
                        rx="4"
                        fill={palette.fill}
                        stroke={palette.stroke}
                        strokeWidth={active ? 0.9 : 0.4}
                      />
                      {/* Libellés */}
                      <text x={left + 2} y={top + 5} style={{ fontSize: "3.2px", fontWeight: 600, fill: "rgba(5,46,22,0.9)" }}>
                        {zone.nom}
                      </text>
                      <text x={left + 2} y={top + 9} style={{ fontSize: "2.5px", fill: "rgba(5,46,22,0.65)" }}>
                        {palette.label}
                      </text>
                      {/* Icône plante animée pour les zones plantées */}
                      {etat === "plante" && (
                        <IcoPlante x={left + width - 6} y={top + height - 7} />
                      )}
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>

          {resume && (
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-muted-foreground">
              <span>{resume.zones} zones</span>
              <span>{Math.round(resume.surface_totale_m2)} m²</span>
              <span>{Math.round(resume.budget_estime).toLocaleString("fr-FR")} € estimés</span>
            </div>
          )}
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
                <Badge variant="secondary">{couleursZone(zoneActive, true).label}</Badge>
                {zoneActive.surface_m2 ? <Badge variant="secondary">{Math.round(zoneActive.surface_m2)} m²</Badge> : null}
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
