"use client";

import { useMemo, useState } from "react";
import { Baby, CalendarDays, Home, Trophy, Users } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Slider } from "@/composants/ui/slider";
import { cn } from "@/bibliotheque/utils";

export interface EvenementTimelineInteractive {
  id: string;
  categorie: "jules" | "maison" | "famille" | "jeux";
  date: string;
  titre: string;
  description?: string | null;
}

const CONFIG_CATEGORIE = {
  jules: {
    couleur: "#2563eb",
    fond: "bg-blue-100 text-blue-900",
    icone: Baby,
    ligne: 0,
  },
  maison: {
    couleur: "#059669",
    fond: "bg-emerald-100 text-emerald-900",
    icone: Home,
    ligne: 1,
  },
  famille: {
    couleur: "#d97706",
    fond: "bg-amber-100 text-amber-900",
    icone: Users,
    ligne: 2,
  },
  jeux: {
    couleur: "#db2777",
    fond: "bg-pink-100 text-pink-900",
    icone: Trophy,
    ligne: 3,
  },
} as const;

function normaliserDate(date: string): Date {
  const valeur = new Date(date);
  valeur.setHours(0, 0, 0, 0);
  return valeur;
}

function differenceJours(a: Date, b: Date): number {
  return Math.round((b.getTime() - a.getTime()) / 86_400_000);
}

export function TimelineInteractive({
  items,
}: {
  items: EvenementTimelineInteractive[];
}) {
  const [zoom, setZoom] = useState([2]);
  const [selectionId, setSelectionId] = useState<string | null>(items[0]?.id ?? null);
  const [mode, setMode] = useState<"horizontale" | "verticale">("horizontale");
  const [categoriesVisibles, setCategoriesVisibles] = useState<Array<EvenementTimelineInteractive["categorie"]>>([
    "jules",
    "maison",
    "famille",
    "jeux",
  ]);

  const itemsFiltres = useMemo(
    () => items.filter((item) => categoriesVisibles.includes(item.categorie)),
    [categoriesVisibles, items]
  );

  const itemsTries = useMemo(
    () => [...itemsFiltres].sort((a, b) => a.date.localeCompare(b.date)),
    [itemsFiltres]
  );

  const bornes = useMemo(() => {
    if (!itemsTries.length) {
      const aujourdHui = new Date();
      return { debut: aujourdHui, fin: aujourdHui, totalJours: 1 };
    }

    const debut = normaliserDate(itemsTries[0].date);
    const fin = normaliserDate(itemsTries[itemsTries.length - 1].date);
    return {
      debut,
      fin,
      totalJours: Math.max(1, differenceJours(debut, fin)),
    };
  }, [itemsTries]);

  const largeurParJour = 22 + zoom[0] * 18;
  const hauteurParEvenement = 54 + zoom[0] * 14;
  const largeurCanvas = Math.max(720, bornes.totalJours * largeurParJour + 160);
  const hauteurCanvasVerticale = Math.max(360, itemsTries.length * hauteurParEvenement + 60);
  const selection = itemsTries.find((item) => item.id === selectionId) ?? itemsTries[0] ?? null;

  const marqueursMois = useMemo(() => {
    const marqueurs: Array<{ cle: string; label: string; x: number }> = [];
    const courant = new Date(bornes.debut);
    courant.setDate(1);

    while (courant <= bornes.fin) {
      const x = differenceJours(bornes.debut, courant) * largeurParJour + 80;
      marqueurs.push({
        cle: courant.toISOString(),
        label: courant.toLocaleDateString("fr-FR", { month: "short", year: "numeric" }),
        x,
      });
      courant.setMonth(courant.getMonth() + 1);
    }

    return marqueurs;
  }, [bornes.debut, bornes.fin, largeurParJour]);

  if (!itemsTries.length) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm font-medium">Frise interactive</p>
          <p className="text-xs text-muted-foreground">
            Zoomez pour resserrer les périodes et cliquez un point pour lire le détail.
          </p>
        </div>
        <div className="flex items-center gap-3 lg:w-[280px]">
          <span className="text-xs text-muted-foreground">Vue large</span>
          <Slider value={zoom} min={0} max={4} step={1} onValueChange={setZoom} />
          <span className="text-xs text-muted-foreground">Zoom</span>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Button size="sm" variant={mode === "horizontale" ? "default" : "outline"} onClick={() => setMode("horizontale")}>
          Frise
        </Button>
        <Button size="sm" variant={mode === "verticale" ? "default" : "outline"} onClick={() => setMode("verticale")}>
          Timeline verticale
        </Button>
        {(["jules", "maison", "famille", "jeux"] as const).map((categorie) => {
          const active = categoriesVisibles.includes(categorie);
          return (
            <Button
              key={categorie}
              size="sm"
              variant={active ? "secondary" : "outline"}
              onClick={() => {
                setCategoriesVisibles((current) => {
                  if (current.includes(categorie)) {
                    const suivant = current.filter((item) => item !== categorie);
                    return suivant.length ? suivant : current;
                  }
                  return [...current, categorie];
                });
              }}
              className="capitalize"
            >
              {categorie}
            </Button>
          );
        })}
      </div>

      {mode === "horizontale" ? (
        <div className="overflow-x-auto rounded-xl border bg-muted/20">
          <svg width={largeurCanvas} height="320" className="block min-w-full">
            <line x1="80" x2={largeurCanvas - 32} y1="148" y2="148" stroke="hsl(var(--border))" strokeWidth="1" />

            {marqueursMois.map((marqueur) => (
              <g key={marqueur.cle} transform={`translate(${marqueur.x} 18)`}>
                <line x1="0" x2="0" y1="0" y2="12" stroke="hsl(var(--border))" strokeWidth="1" />
                <text x="0" y="28" className="fill-muted-foreground text-[11px]">
                  {marqueur.label}
                </text>
              </g>
            ))}

            {Object.entries(CONFIG_CATEGORIE).map(([cle, config]) => (
              <g key={cle} transform={`translate(12 ${100 + config.ligne * 44})`}>
                <text x="0" y="0" className="fill-muted-foreground text-[12px] capitalize">
                  {cle}
                </text>
              </g>
            ))}

            {itemsTries.map((item) => {
              const config = CONFIG_CATEGORIE[item.categorie];
              const x = differenceJours(bornes.debut, normaliserDate(item.date)) * largeurParJour + 80;
              const y = 96 + config.ligne * 44;
              const estSelectionne = item.id === selection?.id;

              return (
                <g
                  key={item.id}
                  transform={`translate(${x} ${y})`}
                  className="cursor-pointer"
                  onClick={() => setSelectionId(item.id)}
                >
                  <circle
                    cx="0"
                    cy="0"
                    r={estSelectionne ? 22 : 18}
                    fill="hsl(var(--background))"
                    stroke={config.couleur}
                    strokeWidth={estSelectionne ? 3 : 2}
                  />
                  <text x="0" y="4" textAnchor="middle" fill={config.couleur} className="text-[12px] font-semibold">
                    {item.categorie === "jules" ? "J" : item.categorie === "maison" ? "M" : item.categorie === "famille" ? "F" : "G"}
                  </text>
                  <text x="0" y="34" textAnchor="middle" className="fill-foreground text-[11px] font-medium">
                    {item.titre.length > 18 ? `${item.titre.slice(0, 18)}…` : item.titre}
                  </text>
                  <text x="0" y="50" textAnchor="middle" className="fill-muted-foreground text-[10px]">
                    {new Date(item.date).toLocaleDateString("fr-FR", { day: "numeric", month: "short" })}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      ) : (
        <div className="overflow-auto rounded-xl border bg-muted/20 p-3">
          <svg width="100%" height={hauteurCanvasVerticale} className="block min-w-[320px]">
            <line x1="130" x2="130" y1="20" y2={hauteurCanvasVerticale - 20} stroke="hsl(var(--border))" strokeWidth="2" />
            {itemsTries.map((item, index) => {
              const y = 34 + index * hauteurParEvenement;
              const config = CONFIG_CATEGORIE[item.categorie];
              return (
                <g key={item.id} className="cursor-pointer" onClick={() => setSelectionId(item.id)}>
                  <text x="8" y={y + 4} className="fill-muted-foreground text-[11px]">
                    {new Date(item.date).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" })}
                  </text>
                  <circle cx="130" cy={y} r={item.id === selection?.id ? 11 : 8} fill="hsl(var(--background))" stroke={config.couleur} strokeWidth={item.id === selection?.id ? 3 : 2} />
                  <text x="150" y={y + 4} className="fill-foreground text-[12px] font-medium">
                    {item.titre}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      )}

      {selection ? (
        <Card>
          <CardHeader className="pb-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className={cn("rounded-full px-2 py-1 text-xs font-medium capitalize", CONFIG_CATEGORIE[selection.categorie].fond)}>
                {selection.categorie}
              </span>
              <CardDescription className="flex items-center gap-1">
                <CalendarDays className="h-3.5 w-3.5" />
                {new Date(selection.date).toLocaleDateString("fr-FR", {
                  weekday: "long",
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                })}
              </CardDescription>
            </div>
            <CardTitle className="text-base">{selection.titre}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {selection.description || "Aucun détail complémentaire pour cet événement."}
            </p>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
