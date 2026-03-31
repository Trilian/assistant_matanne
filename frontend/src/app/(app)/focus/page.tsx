"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Bell, CalendarCheck, CloudSun, ListTodo, UtensilsCrossed } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirTableauBord } from "@/bibliotheque/api/tableau-bord";
import { obtenirBriefingMaison } from "@/bibliotheque/api/maison";
import { evaluerRappelsFamille } from "@/bibliotheque/api/famille";

type MeteoWidget = {
  ville: string;
  temperature: number;
  description: string;
};

export default function FocusPage() {
  const { data: dashboard } = utiliserRequete(["focus", "dashboard"], obtenirTableauBord);
  const { data: briefingMaison } = utiliserRequete(["focus", "maison"], obtenirBriefingMaison);
  const { data: rappelsFamille } = utiliserRequete(["focus", "rappels"], evaluerRappelsFamille);

  const [meteo, setMeteo] = useState<MeteoWidget | null>(null);

  useEffect(() => {
    let annule = false;
    async function chargerMeteo() {
      try {
        const res = await fetch("https://wttr.in/Paris?format=j1");
        if (!res.ok) return;
        const json = await res.json();
        const actuel = json.current_condition?.[0];
        if (!actuel || annule) return;
        setMeteo({
          ville: json.nearest_area?.[0]?.areaName?.[0]?.value ?? "Paris",
          temperature: Number(actuel.temp_C ?? 0),
          description: actuel.weatherDesc?.[0]?.value ?? "",
        });
      } catch {
        if (!annule) setMeteo(null);
      }
    }
    chargerMeteo();
    return () => {
      annule = true;
    };
  }, []);

  const repas = dashboard?.repas_aujourd_hui ?? [];
  const tachesMaison = (briefingMaison?.taches_jour_detail ?? []).filter((t) => !t.fait).slice(0, 4);
  const rappelsUrgents = (rappelsFamille?.rappels ?? []).filter(
    (r) => r.priorite === "danger" || r.priorite === "warning"
  ).slice(0, 4);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Mode focus</h1>
        <p className="text-muted-foreground">
          L&apos;essentiel du jour sur un seul ecran: meteo, repas, taches et rappels.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <CloudSun className="h-4 w-4" /> Meteo
            </CardTitle>
            {meteo && <CardDescription>{meteo.ville}</CardDescription>}
          </CardHeader>
          <CardContent>
            {meteo ? (
              <div>
                <p className="text-2xl font-bold">{meteo.temperature}°C</p>
                <p className="text-sm text-muted-foreground">{meteo.description}</p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Meteo indisponible.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <UtensilsCrossed className="h-4 w-4" /> Repas du jour
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {repas.length === 0 ? (
              <p className="text-sm text-muted-foreground">Aucun repas planifie aujourd&apos;hui.</p>
            ) : (
              repas.map((item, idx) => (
                <div key={`${item.type_repas}-${idx}`} className="rounded-md border px-3 py-2 text-sm">
                  <span className="font-medium capitalize">{item.type_repas}</span>
                  <span className="text-muted-foreground"> - {item.recette_nom ?? "A definir"}</span>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <ListTodo className="h-4 w-4" /> Taches du jour
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {tachesMaison.length === 0 ? (
              <p className="text-sm text-muted-foreground">Rien d&apos;urgent cote maison.</p>
            ) : (
              tachesMaison.map((tache) => (
                <div key={`${tache.nom}-${tache.id_source ?? 0}`} className="rounded-md border px-3 py-2 text-sm">
                  <p className="font-medium">{tache.nom}</p>
                  {tache.categorie && <p className="text-xs text-muted-foreground">{tache.categorie}</p>}
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Bell className="h-4 w-4" /> Rappels
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {rappelsUrgents.length === 0 ? (
              <p className="text-sm text-muted-foreground">Aucun rappel urgent.</p>
            ) : (
              rappelsUrgents.map((rappel, idx) => (
                <div key={`${rappel.type}-${idx}`} className="rounded-md border px-3 py-2 text-sm">
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-medium">{rappel.type}</p>
                    <Badge variant={rappel.priorite === "danger" ? "destructive" : "secondary"}>
                      {rappel.priorite}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">{rappel.message}</p>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button asChild>
          <Link href="/cuisine/ma-semaine">
            <CalendarCheck className="h-4 w-4 mr-2" /> Planifier ma semaine
          </Link>
        </Button>
        <Button variant="outline" asChild>
          <Link href="/famille/timeline">Ouvrir timeline famille</Link>
        </Button>
        <Button variant="outline" asChild>
          <Link href="/maison/travaux">Voir projets maison</Link>
        </Button>
      </div>
    </div>
  );
}
