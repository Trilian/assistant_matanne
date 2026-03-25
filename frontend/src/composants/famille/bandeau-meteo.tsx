"use client";

import type { MeteoActuelle } from "@/types/famille";

interface Props {
  meteo: MeteoActuelle;
}

export function BandeauMeteo({ meteo }: Props) {
  const tempMin = meteo.temperature_min?.toFixed(0) ?? "—";
  const tempMax = meteo.temperature_max?.toFixed(0) ?? "—";

  return (
    <div className="flex items-center gap-3 rounded-lg bg-gradient-to-r from-blue-50 to-sky-50 dark:from-blue-950/30 dark:to-sky-950/30 px-4 py-3">
      <span className="text-2xl">{meteo.emoji || "🌤️"}</span>
      <div className="flex-1">
        <p className="font-medium text-sm">
          {tempMin}° / {tempMax}°
          <span className="text-muted-foreground ml-2">{meteo.condition}</span>
        </p>
        {meteo.precipitation_mm != null && meteo.precipitation_mm > 0 && (
          <p className="text-xs text-muted-foreground">
            🌧️ {meteo.precipitation_mm.toFixed(1)} mm prévus
          </p>
        )}
      </div>
      {meteo.vent_km_h != null && meteo.vent_km_h > 30 && (
        <span className="text-xs text-muted-foreground">
          💨 {meteo.vent_km_h.toFixed(0)} km/h
        </span>
      )}
    </div>
  );
}
