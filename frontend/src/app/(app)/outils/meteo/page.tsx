"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Skeleton } from "@/composants/ui/skeleton";

interface DonneesMeteo {
  ville: string;
  temperature: number;
  description: string;
  humidite: number;
  vent: number;
  icone: string;
}

const ICONES_METEO: Record<string, string> = {
  Clear: "☀️",
  Clouds: "☁️",
  Rain: "🌧️",
  Drizzle: "🌦️",
  Thunderstorm: "⛈️",
  Snow: "🌨️",
  Mist: "🌫️",
  Fog: "🌫️",
};

export default function MeteoPage() {
  const [ville, setVille] = useState("Paris");
  const [meteo, setMeteo] = useState<DonneesMeteo | null>(null);
  const [chargement, setChargement] = useState(false);
  const [erreur, setErreur] = useState("");

  async function rechercherMeteo(nomVille: string) {
    if (!nomVille.trim()) return;
    setChargement(true);
    setErreur("");
    try {
      const res = await fetch(
        `https://wttr.in/${encodeURIComponent(nomVille)}?format=j1`
      );
      if (!res.ok) throw new Error("Ville introuvable");
      const data = await res.json();
      const actuel = data.current_condition?.[0];
      if (!actuel) throw new Error("Données indisponibles");

      setMeteo({
        ville: data.nearest_area?.[0]?.areaName?.[0]?.value ?? nomVille,
        temperature: Number(actuel.temp_C),
        description: actuel.weatherDesc?.[0]?.value ?? "",
        humidite: Number(actuel.humidity),
        vent: Number(actuel.windspeedKmph),
        icone:
          ICONES_METEO[actuel.weatherCode >= 200 && actuel.weatherCode < 300 ? "Thunderstorm" : "Clear"] ??
          "🌤️",
      });
    } catch {
      setErreur("Impossible de récupérer la météo. Vérifiez le nom de la ville.");
      setMeteo(null);
    } finally {
      setChargement(false);
    }
  }

  useEffect(() => {
    rechercherMeteo("Paris");
  }, []);

  function gererRecherche(e: React.FormEvent) {
    e.preventDefault();
    rechercherMeteo(ville);
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">🌤️ Météo</h1>

      <form onSubmit={gererRecherche} className="flex gap-2 max-w-md">
        <Input
          value={ville}
          onChange={(e) => setVille(e.target.value)}
          placeholder="Entrez une ville…"
        />
        <Button type="submit" disabled={chargement}>
          Rechercher
        </Button>
      </form>

      {chargement && <Skeleton className="h-48 max-w-md rounded-xl" />}

      {erreur && (
        <p className="text-destructive text-sm">{erreur}</p>
      )}

      {meteo && !chargement && (
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="text-4xl">{meteo.icone}</span>
              <span>{meteo.ville}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-bold">{meteo.temperature}°C</span>
                <span className="text-muted-foreground">{meteo.description}</span>
              </div>
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="text-center p-3 rounded-lg bg-muted">
                  <p className="text-2xl font-semibold">💧 {meteo.humidite}%</p>
                  <p className="text-xs text-muted-foreground">Humidité</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-muted">
                  <p className="text-2xl font-semibold">💨 {meteo.vent} km/h</p>
                  <p className="text-xs text-muted-foreground">Vent</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
