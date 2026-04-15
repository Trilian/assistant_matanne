"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { cn } from "@/bibliotheque/utils";
import type { RepasPlanning, TypeRepas } from "@/types/planning";

const COULEUR_TYPE: Record<TypeRepas, string> = {
  petit_dejeuner: "bg-amber-200 text-amber-950 dark:bg-amber-900/50 dark:text-amber-100",
  dejeuner:       "bg-emerald-200 text-emerald-950 dark:bg-emerald-900/50 dark:text-emerald-100",
  gouter:         "bg-pink-200 text-pink-950 dark:bg-pink-900/50 dark:text-pink-100",
  diner:          "bg-indigo-200 text-indigo-950 dark:bg-indigo-900/50 dark:text-indigo-100",
};

const BORDURE_TYPE: Record<TypeRepas, string> = {
  petit_dejeuner: "border-l-[3px] border-amber-500",
  dejeuner:       "border-l-[3px] border-emerald-600",
  gouter:         "border-l-[3px] border-pink-500",
  diner:          "border-l-[3px] border-indigo-500",
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
  viande:   "bg-rose-200 text-rose-950 dark:bg-rose-900/50 dark:text-rose-100",
  poisson:  "bg-cyan-200 text-cyan-950 dark:bg-cyan-900/50 dark:text-cyan-100",
  vegetal:  "bg-lime-200 text-lime-950 dark:bg-lime-900/50 dark:text-lime-100",
  feculent: "bg-yellow-200 text-yellow-950 dark:bg-yellow-900/50 dark:text-yellow-100",
  autre:    "bg-slate-200 text-slate-700 dark:bg-slate-700/40 dark:text-slate-300",
};

const BORDURE_CATEGORIE: Record<CategorieAlimentaire, string> = {
  viande:   "border-l-[3px] border-rose-500",
  poisson:  "border-l-[3px] border-cyan-500",
  vegetal:  "border-l-[3px] border-lime-600",
  feculent: "border-l-[3px] border-yellow-500",
  autre:    "border-l-[3px] border-slate-400",
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
              <div key={date} className="overflow-hidden rounded-lg border p-2.5">
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
                          "relative isolate overflow-hidden rounded-md px-2 py-1.5 text-[11px]",
                          mode === "nutrition" && repas && categorie
                            ? cn(COULEUR_CATEGORIE[categorie], BORDURE_CATEGORIE[categorie])
                            : repas && mode === "repas"
                              ? "text-white"
                              : cn(COULEUR_TYPE[type], BORDURE_TYPE[type])
                        )}
                        title={repas?.recette_nom || repas?.notes || `${LABEL_TYPE[type]} non planifié`}
                      >
                        {repas && vignette && mode === "repas" && (
                          <img
                            src={vignette}
                            alt={`Vignette recette ${repas.recette_nom ?? repas.notes ?? LABEL_TYPE[type]}`}
                            className="absolute inset-0 z-0 h-full w-full object-cover"
                            loading="lazy"
                          />
                        )}

                        {repas && mode === "repas" && (
                          <div className="absolute inset-0 z-[1] bg-gradient-to-t from-black/70 via-black/45 to-black/20" />
                        )}

                        <div className="relative z-[2]">
                          <p className="font-semibold">{LABEL_TYPE[type]}</p>
                          <p className="truncate opacity-90">{repas?.recette_nom || repas?.notes || "Non planifié"}</p>
                          {repas && (type === "dejeuner" || type === "diner") &&
                            (repas.entree || repas.laitage || repas.legumes || repas.dessert) && (
                              <div className="flex flex-wrap gap-x-1.5 gap-y-0.5 mt-0.5">
                                {repas.entree && (
                                  <span className="text-[9px] opacity-75 truncate" title={`Entrée : ${repas.entree}`}>E·{repas.entree}</span>
                                )}
                                {repas.legumes && (
                                  <span className="text-[9px] opacity-75 truncate" title={`Légumes : ${repas.legumes}`}>🥦 {repas.legumes}</span>
                                )}
                                {repas.laitage && (
                                  <span className="text-[9px] opacity-75 truncate" title={`Laitage : ${repas.laitage}`}>🥛 {repas.laitage}</span>
                                )}
                                {repas.dessert && (
                                  <span className="text-[9px] opacity-75 truncate" title={`Dessert : ${repas.dessert}`}>🍮 {repas.dessert}</span>
                                )}
                              </div>
                            )}
                          {repas && type === "gouter" && (repas.gateau_gouter || repas.laitage || repas.fruit_gouter) && (
                            <div className="flex flex-wrap gap-x-1.5 gap-y-0.5 mt-0.5">
                              {repas.gateau_gouter && (
                                <span className="text-[9px] opacity-75 truncate" title={`Céréales/gâteau : ${repas.gateau_gouter}`}>🍪 {repas.gateau_gouter}</span>
                              )}
                              {repas.laitage && (
                                <span className="text-[9px] opacity-75 truncate" title={`Laitage : ${repas.laitage}`}>🥛 {repas.laitage}</span>
                              )}
                              {repas.fruit_gouter && (
                                <span className="text-[9px] opacity-75 truncate" title={`Fruit : ${repas.fruit_gouter}`}>🍎 {repas.fruit_gouter}</span>
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
