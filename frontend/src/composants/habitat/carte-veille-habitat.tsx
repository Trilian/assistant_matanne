"use client";

import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import type { PointCarteHabitat } from "@/types/habitat";

interface CarteVeilleHabitatProps {
  points: PointCarteHabitat[];
}

const CENTRE_FRANCE: [number, number] = [46.603354, 1.888334];

export function CarteVeilleHabitat({ points }: CarteVeilleHabitatProps) {
  const pointsValides = points.filter(
    (point) => typeof point.latitude === "number" && typeof point.longitude === "number"
  );

  const centre: [number, number] = pointsValides.length > 0
    ? [pointsValides[0].latitude as number, pointsValides[0].longitude as number]
    : CENTRE_FRANCE;

  return (
    <MapContainer center={centre} zoom={pointsValides.length > 0 ? 9 : 6} scrollWheelZoom className="h-[420px] w-full rounded-2xl">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {pointsValides.map((point) => {
        const radius = Math.max(8, Math.min(20, 6 + point.nb_annonces * 2));
        const color = point.score_max >= 0.8 ? "#047857" : point.score_max >= 0.65 ? "#0f766e" : "#b45309";
        return (
          <CircleMarker
            key={`${point.ville}-${point.code_postal}`}
            center={[point.latitude as number, point.longitude as number]}
            radius={radius}
            pathOptions={{ color, fillColor: color, fillOpacity: 0.45, weight: 2 }}
          >
            <Popup>
              <div className="space-y-1 text-sm">
                <p className="font-semibold">{point.ville ?? "Ville inconnue"}</p>
                <p>{point.nb_annonces} annonce(s)</p>
                <p>Score max: {(point.score_max ?? 0).toFixed(2)}</p>
                <p>
                  Prix: {typeof point.prix_min === "number" ? `${Math.round(point.prix_min).toLocaleString("fr-FR")} €` : "?"}
                  {typeof point.prix_max === "number" ? ` à ${Math.round(point.prix_max).toLocaleString("fr-FR")} €` : ""}
                </p>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}