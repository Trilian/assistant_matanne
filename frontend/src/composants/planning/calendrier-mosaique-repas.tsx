"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { cn } from "@/bibliotheque/utils";
import type { RepasPlanning, TypeRepas } from "@/types/planning";

const COULEUR_TYPE: Record<TypeRepas, string> = {
  petit_dejeuner: "bg-amber-100 text-amber-900 dark:bg-amber-950/30 dark:text-amber-100",
  dejeuner: "bg-emerald-100 text-emerald-900 dark:bg-emerald-950/30 dark:text-emerald-100",
  gouter: "bg-fuchsia-100 text-fuchsia-900 dark:bg-fuchsia-950/30 dark:text-fuchsia-100",
  diner: "bg-blue-100 text-blue-900 dark:bg-blue-950/30 dark:text-blue-100",
};

const LABEL_TYPE: Record<TypeRepas, string> = {
  petit_dejeuner: "Petit-dej",
  dejeuner: "Dejeuner",
  gouter: "Gouter",
  diner: "Diner",
};

const TYPES: TypeRepas[] = ["petit_dejeuner", "dejeuner", "gouter", "diner"];

// ── Mode nutritionnel : colorisation par catégorie alimentaire ──

type CategorieAlimentaire = "viande" | "poisson" | "vegetal" | "feculent" | "autre";

const COULEUR_CATEGORIE: Record<CategorieAlimentaire, string> = {
  viande: "bg-red-200 text-red-900 dark:bg-red-950/40 dark:text-red-200",
  poisson: "bg-blue-200 text-blue-900 dark:bg-blue-950/40 dark:text-blue-200",
  vegetal: "bg-green-200 text-green-900 dark:bg-green-950/40 dark:text-green-200",
  feculent: "bg-orange-200 text-orange-900 dark:bg-orange-950/40 dark:text-orange-200",
  autre: "bg-slate-100 text-slate-700 dark:bg-slate-800/40 dark:text-slate-300",
};

const LABEL_CATEGORIE: Record<CategorieAlimentaire, string> = {
  viande: "🥩 Viande",
  poisson: "🐟 Poisson",
  vegetal: "🥗 Végétal",
  feculent: "🍝 Féculent",
  autre: "🍽️ Autre",
};

const MOTS_CLES_CATEGORIE: Record<CategorieAlimentaire, readonly string[]> = {
  viande: ["poulet", "boeuf", "bœuf", "porc", "veau", "agneau", "canard", "dinde", "lapin", "steak", "roti", "rôti", "saucisse", "jambon", "blanquette", "bourguignon", "coq", "viande", "grillade", "brochette", "côtelette", "filet mignon", "magret"],
  poisson: ["saumon", "thon", "cabillaud", "colin", "crevette", "poisson", "truite", "sardine", "moule", "fruits de mer", "coquillage", "bar", "sole", "dorade", "anchois", "lieu", "merlu", "lotte", "gambas", "homard"],
  vegetal: ["salade", "légume", "végé", "vegan", "tofu", "lentille", "pois chiche", "haricot", "soupe", "velouté", "ratatouille", "buddha bowl", "falafel", "houmous", "courgette", "aubergine", "brocoli", "épinard", "chou"],
  feculent: ["pâte", "pasta", "riz", "pomme de terre", "frite", "gratin", "lasagne", "risotto", "gnocchi", "semoule", "quinoa", "boulgour", "pizza", "tarte", "quiche", "crêpe", "galette", "ravioli", "tagliatelle", "spaghetti"],
  autre: [],
};

function detecterCategorie(nom: string | undefined | null): CategorieAlimentaire {
  if (!nom) return "autre";
  const nomLower = nom.toLowerCase();
  for (const [categorie, motsCles] of Object.entries(MOTS_CLES_CATEGORIE) as [CategorieAlimentaire, readonly string[]][]) {
    if (motsCles.some((mot) => nomLower.includes(mot))) {
      return categorie;
    }
  }
  return "autre";
}

type ModeVue = "repas" | "nutrition";

interface CalendrierMosaiqueRepasProps {
  dates: string[];
  repasParJour: Record<string, RepasPlanning[]>;
}

function trouverRepasParType(repasJour: RepasPlanning[], type: TypeRepas): RepasPlanning | undefined {
  return repasJour.find((repas) => repas.type_repas === type);
}

function getVignetteRepas(repas: RepasPlanning | undefined): string {
  if (!repas) {
    return "";
  }

  const seed = `${repas.recette_id ?? "sans-id"}-${repas.recette_nom ?? repas.notes ?? "repas"}`;
  return `https://picsum.photos/seed/${encodeURIComponent(seed)}/420/260`;
}

export function CalendrierMosaiqueRepas({ dates, repasParJour }: CalendrierMosaiqueRepasProps) {
  const [mode, setMode] = useState<ModeVue>("repas");

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Calendrier mosaïque des repas</CardTitle>
          <div className="flex items-center gap-1 rounded-lg border p-0.5">
            <button
              onClick={() => setMode("repas")}
              className={cn(
                "rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
                mode === "repas" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
              )}
            >
              Par repas
            </button>
            <button
              onClick={() => setMode("nutrition")}
              className={cn(
                "rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
                mode === "nutrition" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
              )}
            >
              Équilibre
            </button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {mode === "nutrition" && (
          <div className="flex flex-wrap gap-2">
            {(Object.entries(LABEL_CATEGORIE) as [CategorieAlimentaire, string][]).map(([cat, label]) => (
              <span key={cat} className={cn("inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium", COULEUR_CATEGORIE[cat])}>
                {label}
              </span>
            ))}
          </div>
        )}
        <div className="grid gap-3 grid-cols-2 md:grid-cols-4 xl:grid-cols-7">
          {dates.map((date) => {
            const repasJour = repasParJour[date] ?? [];
            return (
              <div key={date} className="rounded-lg border p-2.5">
                <p className="mb-2 text-xs font-semibold text-muted-foreground">
                  {new Date(date).toLocaleDateString("fr-FR", {
                    weekday: "short",
                    day: "numeric",
                    month: "short",
                  })}
                </p>
                <div className="space-y-1.5">
                  {TYPES.map((type) => {
                    const repas = trouverRepasParType(repasJour, type);
                    const vignette = mode === "repas" ? getVignetteRepas(repas) : "";
                    const categorie = mode === "nutrition" ? detecterCategorie(repas?.recette_nom ?? repas?.notes) : null;

                    return (
                      <div
                        key={`${date}-${type}`}
                        className={cn(
                          "relative overflow-hidden rounded-md px-2 py-1.5 text-[11px]",
                          mode === "nutrition" && repas && categorie
                            ? COULEUR_CATEGORIE[categorie]
                            : repas && mode === "repas"
                              ? "text-white"
                              : COULEUR_TYPE[type]
                        )}
                        title={repas?.recette_nom || repas?.notes || `${LABEL_TYPE[type]} non planifié`}
                      >
                        {repas && vignette && mode === "repas" && (
                          <img
                            src={vignette}
                            alt={`Vignette recette ${repas.recette_nom ?? repas.notes ?? LABEL_TYPE[type]}`}
                            className="absolute inset-0 h-full w-full object-cover"
                            loading="lazy"
                          />
                        )}

                        {repas && mode === "repas" && (
                          <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/45 to-black/20" />
                        )}

                        <div className="relative">
                          <p className="font-semibold">{LABEL_TYPE[type]}</p>
                          <p className="truncate opacity-90">{repas?.recette_nom || repas?.notes || "Non planifié"}</p>
                          {repas && (type === "dejeuner" || type === "diner") &&
                            (repas.entree || repas.laitage || repas.dessert) && (
                              <div className="flex flex-wrap gap-x-1.5 gap-y-0.5 mt-0.5">
                                {repas.entree && (
                                  <span className="text-[9px] opacity-75 truncate max-w-[60px]">E·{repas.entree}</span>
                                )}
                                {repas.laitage && (
                                  <span className="text-[9px] opacity-75 truncate max-w-[60px]">🥛 {repas.laitage}</span>
                                )}
                                {repas.dessert && (
                                  <span className="text-[9px] opacity-75 truncate max-w-[60px]">🍮 {repas.dessert}</span>
                                )}
                              </div>
                            )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
