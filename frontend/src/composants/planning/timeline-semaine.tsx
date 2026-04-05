"use client";

import { Home, Sparkles, Utensils, Users } from "lucide-react";
import { Badge } from "@/composants/ui/badge";
import { Card, CardContent } from "@/composants/ui/card";
import type { RepasPlanning, TypeRepas } from "@/types/planning";

const LABELS_REPAS: Record<TypeRepas, string> = {
  petit_dejeuner: "🌅 Petit-déjeuner",
  dejeuner: "☀️ Déjeuner",
  gouter: "🍰 Goûter",
  diner: "🌙 Dîner",
};

const JOURS_SEMAINE = [
  "Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi",
];

type ActiviteTimeline = {
  id: number;
  date: string | null;
  titre: string;
  type: string | null;
};

type TacheMaisonTimeline = {
  nom: string;
  categorie: string | null;
  duree_estimee_min: number | null;
};

type EvenementTimeline = {
  cle: string;
  date: string;
  ordre: number;
  module: "repas" | "activite" | "maison";
  titre: string;
  sousTitre: string;
  badge?: string;
};

interface TimelineSemaineProps {
  repas: RepasPlanning[];
  activites?: ActiviteTimeline[];
  tachesMaison?: TacheMaisonTimeline[];
}

export function TimelineSemaine({ repas, activites = [], tachesMaison = [] }: TimelineSemaineProps) {
  const repasOrdre: TypeRepas[] = ["petit_dejeuner", "dejeuner", "gouter", "diner"];
  const aujourdHui = new Date().toISOString().split("T")[0];

  const evenements: EvenementTimeline[] = [
    ...repas.map((item) => ({
      cle: `repas-${item.id}`,
      date: (item.date ?? item.date_repas ?? "").split("T")[0],
      ordre: repasOrdre.indexOf(item.type_repas),
      module: "repas" as const,
      titre: item.recette_nom || item.notes || "Repas planifié",
      sousTitre: LABELS_REPAS[item.type_repas] ?? item.type_repas,
      badge: item.portions ? `${item.portions} pers.` : undefined,
    })),
    ...activites
      .filter((item) => item.date)
      .map((item) => ({
        cle: `activite-${item.id}`,
        date: (item.date ?? aujourdHui).split("T")[0],
        ordre: 10,
        module: "activite" as const,
        titre: item.titre,
        sousTitre: item.type ?? "Activité famille",
      })),
    ...tachesMaison.map((item, index) => ({
      cle: `maison-${index}-${item.nom}`,
      date: aujourdHui,
      ordre: 20 + index,
      module: "maison" as const,
      titre: item.nom,
      sousTitre: item.categorie ?? "Tâche maison",
      badge: item.duree_estimee_min ? `~${item.duree_estimee_min} min` : undefined,
    })),
  ].sort((a, b) => {
    const dateCompare = a.date.localeCompare(b.date);
    if (dateCompare !== 0) return dateCompare;
    return a.ordre - b.ordre;
  });

  const parDate: Record<string, EvenementTimeline[]> = {};
  for (const evenement of evenements) {
    if (!parDate[evenement.date]) parDate[evenement.date] = [];
    parDate[evenement.date].push(evenement);
  }

  const iconeParModule = {
    repas: <Utensils className="h-4 w-4 shrink-0 text-orange-500" />,
    activite: <Users className="h-4 w-4 shrink-0 text-blue-500" />,
    maison: <Home className="h-4 w-4 shrink-0 text-emerald-500" />,
  };

  const badgeModule = {
    repas: "Repas",
    activite: "Famille",
    maison: "Maison",
  };

  return (
    <div className="relative space-y-6">
      <div className="absolute bottom-0 left-4 top-0 w-0.5 bg-border" />

      {Object.entries(parDate).map(([dateStr, evenementsDate]) => {
        const d = new Date(dateStr);
        const jourNom = JOURS_SEMAINE[d.getDay()];
        const estAujourdhui = dateStr === aujourdHui;

        return (
          <div key={dateStr} className="relative pl-10">
            <div
              className={`absolute left-2.5 top-1 h-3 w-3 rounded-full border-2 ${
                estAujourdhui
                  ? "border-primary bg-primary"
                  : "border-muted-foreground bg-background"
              }`}
            />

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <h2 className={`text-sm font-semibold ${estAujourdhui ? "text-primary" : ""}`}>
                  {jourNom}
                </h2>
                <span className="text-xs text-muted-foreground">
                  {d.toLocaleDateString("fr-FR", {
                    day: "numeric",
                    month: "long",
                  })}
                </span>
                {estAujourdhui && (
                  <Badge variant="default" className="text-xs">
                    Aujourd&apos;hui
                  </Badge>
                )}
              </div>

              <div className="space-y-2">
                {evenementsDate.map((item) => (
                  <Card key={item.cle} className="ml-2">
                    <CardContent className="flex items-center gap-3 py-3">
                      {iconeParModule[item.module]}
                      <div className="min-w-0 flex-1">
                        <div className="mb-1 flex items-center gap-2">
                          <Badge variant="outline" className="text-[10px]">
                            {badgeModule[item.module]}
                          </Badge>
                          <p className="text-xs text-muted-foreground">{item.sousTitre}</p>
                        </div>
                        <p className="truncate text-sm font-medium">{item.titre}</p>
                      </div>
                      {item.badge && (
                        <Badge variant="secondary" className="shrink-0 text-xs">
                          {item.badge}
                        </Badge>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        );
      })}

      {evenements.length === 0 && (
        <div className="flex items-center gap-2 rounded-lg border border-dashed p-4 text-sm text-muted-foreground">
          <Sparkles className="h-4 w-4" />
          Rien de planifié pour le moment sur la semaine.
        </div>
      )}
    </div>
  );
}
