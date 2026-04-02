"use client";

import { useMemo, useState } from "react";
import { CalendarDays, Download, Filter, Home, Baby, Users, Trophy } from "lucide-react";

import { clientApi } from "@/bibliotheque/api/client";
import { TimelineInteractive } from "@/composants/famille/timeline-interactive";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";

interface ItemTimeline {
  id: string;
  categorie: "jules" | "maison" | "famille" | "jeux";
  date: string;
  titre: string;
  description?: string | null;
  meta?: Record<string, unknown>;
}

const CATEGORIES = ["toutes", "jules", "maison", "famille", "jeux"] as const;
type CategorieFiltre = (typeof CATEGORIES)[number];

function iconeCategorie(categorie: ItemTimeline["categorie"]) {
  if (categorie === "jules") return <Baby className="h-4 w-4" />;
  if (categorie === "maison") return <Home className="h-4 w-4" />;
  if (categorie === "famille") return <Users className="h-4 w-4" />;
  return <Trophy className="h-4 w-4" />;
}

function couleurBadge(categorie: ItemTimeline["categorie"]) {
  if (categorie === "jules") return "bg-blue-100 text-blue-800";
  if (categorie === "maison") return "bg-emerald-100 text-emerald-800";
  if (categorie === "famille") return "bg-amber-100 text-amber-800";
  return "bg-rose-100 text-rose-800";
}

export default function TimelineFamillePage() {
  const [filtre, setFiltre] = useState<CategorieFiltre>("toutes");

  const { data, isLoading } = utiliserRequete(
    ["famille", "timeline", filtre],
    async (): Promise<{ items: ItemTimeline[]; total: number }> => {
      const params = new URLSearchParams();
      if (filtre !== "toutes") params.set("categorie", filtre);
      const { data } = await clientApi.get(`/famille/timeline?${params}`);
      return data;
    }
  );

  const items = useMemo(() => data?.items ?? [], [data]);

  const exporterPDF = () => {
    window.print();
  };

  return (
    <div className="space-y-6 pb-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <CalendarDays className="h-6 w-6" />
            Timeline vie familiale
          </h1>
          <p className="text-muted-foreground">
            Jalons Jules, voyages et événements famille, projets maison, jardinage et moments jeux marquants.
          </p>
        </div>
        <Button variant="outline" onClick={exporterPDF}>
          <Download className="mr-2 h-4 w-4" />
          Export PDF
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filtrer par catégorie
          </CardTitle>
          <CardDescription>
            {isLoading ? "Chargement..." : `${data?.total ?? 0} événement(s)`}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => (
            <Button
              key={cat}
              size="sm"
              variant={filtre === cat ? "default" : "outline"}
              onClick={() => setFiltre(cat)}
            >
              {cat === "toutes" ? "Toutes" : cat}
            </Button>
          ))}
        </CardContent>
      </Card>

      {items.length > 0 ? (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Vue chronologique</CardTitle>
            <CardDescription>
              Lecture condensée des jalons et événements de la famille sur une frise zoomable.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TimelineInteractive items={items} />
          </CardContent>
        </Card>
      ) : null}

      <div className="relative ml-2 border-l pl-6 sm:ml-4 sm:pl-8">
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Chargement de la timeline…</p>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">Aucun événement à afficher.</p>
        ) : (
          <div className="space-y-6">
            {items.map((item) => (
              <div key={item.id} className="relative">
                <span className="absolute -left-[2.35rem] top-1 inline-flex h-7 w-7 items-center justify-center rounded-full border bg-background sm:-left-[2.9rem]">
                  {iconeCategorie(item.categorie)}
                </span>
                <Card>
                  <CardHeader className="pb-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge className={couleurBadge(item.categorie)}>{item.categorie}</Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(item.date).toLocaleDateString("fr-FR")}
                      </span>
                    </div>
                    <CardTitle className="text-base">{item.titre}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {item.description ? (
                      <p className="text-sm text-muted-foreground whitespace-pre-line">{item.description}</p>
                    ) : null}
                    {item.meta && Object.keys(item.meta).length > 0 ? (
                      <pre className="text-xs bg-muted rounded-md p-2 overflow-x-auto">
                        {JSON.stringify(item.meta, null, 2)}
                      </pre>
                    ) : null}
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
