// ═══════════════════════════════════════════════════════════
// Bandeau Météo — impact jardin/ménage du jour
// ═══════════════════════════════════════════════════════════

"use client";

import { CloudRain, Sun, Cloud, Snowflake } from "lucide-react";
import { Badge } from "@/composants/ui/badge";
import type { MeteoResumeMaison } from "@/types/maison";

interface BandeauMeteoProps {
  meteo: MeteoResumeMaison;
}

function MeteoIcone({ description }: { description?: string }) {
  const d = (description ?? "").toLowerCase();
  if (d.includes("neige") || d.includes("gel")) return <Snowflake className="h-5 w-5 text-blue-400" />;
  if (d.includes("pluie") || d.includes("averse")) return <CloudRain className="h-5 w-5 text-blue-500" />;
  if (d.includes("nuage") || d.includes("couvert")) return <Cloud className="h-5 w-5 text-gray-400" />;
  return <Sun className="h-5 w-5 text-amber-400" />;
}

export function BandeauMeteo({ meteo }: BandeauMeteoProps) {
  if (!meteo.description && !meteo.impact_jardin && meteo.alertes_meteo.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg border bg-card px-4 py-3">
      <MeteoIcone description={meteo.description} />

      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          {meteo.temperature_min !== undefined && (
            <span className="text-sm font-medium">
              {meteo.temperature_min}° / {meteo.temperature_max}°
            </span>
          )}
          {meteo.description && (
            <span className="text-sm text-muted-foreground">{meteo.description}</span>
          )}
          {meteo.precipitation_mm !== undefined && meteo.precipitation_mm > 0 && (
            <span className="text-xs text-muted-foreground">{meteo.precipitation_mm} mm</span>
          )}
        </div>
        {meteo.impact_jardin && (
          <p className="text-xs text-muted-foreground mt-0.5">{meteo.impact_jardin}</p>
        )}
      </div>

      {meteo.alertes_meteo.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {meteo.alertes_meteo.map((a, i) => (
            <Badge key={i} variant="secondary" className="text-xs">{a}</Badge>
          ))}
        </div>
      )}
    </div>
  );
}
