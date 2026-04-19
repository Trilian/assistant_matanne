// ═══════════════════════════════════════════════════════════
// CarteRepasDraggable — carte déplaçable d'un repas dans la grille
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { GripVertical, RefreshCw, X } from "lucide-react";
import { useDraggable } from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";
import { Button } from "@/composants/ui/button";
import { BadgeNutriscore } from "@/composants/cuisine/badge-nutriscore";
import type { TypeRepas, RepasPlanning } from "@/types/planning";

export function construireIdRepasPlanning(repasId: number): string {
  return `repas::${repasId}`;
}

export function CarteRepasDraggable({
  repas,
  label,
  onRetirer,
  onModifierChamp,
  onRegenerer,
  nomDinerSource,
}: {
  repas: RepasPlanning;
  label: string;
  onRetirer: (repas: RepasPlanning) => void;
  onModifierChamp?: (repasId: number, champ: string, valeur: string) => void;
  onRegenerer?: (repas: RepasPlanning) => void;
  nomDinerSource?: string;
}) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: construireIdRepasPlanning(repas.id),
    data: { repasId: repas.id },
  });
  const carteRef = useRef<HTMLDivElement | null>(null);
  const [champEnEdition, setChampEnEdition] = useState<"legumes" | "feculents" | null>(null);
  const [valeurEdition, setValeurEdition] = useState("");

  const definirRefs = useCallback(
    (node: HTMLDivElement | null) => {
      setNodeRef(node);
      carteRef.current = node;
    },
    [setNodeRef]
  );

  useEffect(() => {
    if (!carteRef.current) {
      return;
    }
    carteRef.current.style.transform = transform ? (CSS.Translate.toString(transform) ?? "") : "";
  }, [transform]);

  return (
    <div
      ref={definirRefs}
      className={`flex items-center justify-between gap-1 rounded-md bg-background/80 ${isDragging ? "opacity-60 shadow-lg ring-2 ring-primary/30" : ""}`}
    >
      <div className="flex items-start gap-1 min-w-0 flex-1">
        <button
          type="button"
          className="rounded p-0.5 text-muted-foreground hover:bg-muted touch-none mt-0.5"
          aria-label={`Déplacer ${repas.recette_nom || repas.notes || label}`}
          {...listeners}
          {...attributes}
        >
          <GripVertical className="h-3 w-3" />
        </button>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1">
            {repas.est_reste && repas.reste_description ? (
              <span className="font-medium text-amber-700 dark:text-amber-300 break-words">
                ♻ {nomDinerSource || repas.recette_nom || repas.notes || "Reste"}{" "}
                <span className="font-normal text-xs text-muted-foreground">
                  (reste du {repas.reste_description})
                </span>
              </span>
            ) : repas.recette_id ? (
              <a
                href={`/cuisine/recettes/${repas.recette_id}`}
                className="font-medium text-foreground break-words hover:underline hover:text-primary transition-colors"
                title={`Voir la recette : ${repas.recette_nom || repas.notes || "—"}`}
                onClick={(e) => e.stopPropagation()}
              >
                {repas.recette_nom || repas.notes || "—"}
              </a>
            ) : (
              <span className="font-medium text-foreground break-words">
                {repas.recette_nom || repas.notes || "—"}
              </span>
            )}
            {repas.nutri_score && <BadgeNutriscore grade={repas.nutri_score} />}
            {repas.genere_par_ia && (
              <span title="Recette générée par l'IA" className="inline-flex items-center text-[11px]">
                🤖
              </span>
            )}
          </div>
          {repas.type_repas === "gouter" &&
            (repas.gateau_gouter || repas.laitage || repas.fruit_gouter) && (
              <div className="flex flex-col gap-y-0.5 mt-0.5">
                {repas.gateau_gouter &&
                  repas.gateau_gouter.toLowerCase() !==
                    (repas.recette_nom || repas.notes || "").toLowerCase() && (
                    <span
                      className="text-[10px] text-muted-foreground break-words"
                      title={`Céréales/gâteau : ${repas.gateau_gouter}`}
                    >
                      🍪 {repas.gateau_gouter}
                    </span>
                  )}
                {repas.laitage && (
                  <span
                    className="text-[10px] text-muted-foreground break-words"
                    title={`Laitage : ${repas.laitage}`}
                  >
                    🥛 {repas.laitage}
                  </span>
                )}
                {repas.fruit_gouter && (
                  <span
                    className="text-[10px] text-muted-foreground break-words"
                    title={`Fruit : ${repas.fruit_gouter}`}
                  >
                    🍎 {repas.fruit_gouter}
                  </span>
                )}
              </div>
            )}
          {(repas.type_repas === "dejeuner" || repas.type_repas === "diner") &&
            !repas.est_reste &&
            (repas.entree ||
              repas.laitage ||
              repas.dessert ||
              repas.legumes ||
              repas.feculents ||
              repas.proteine_accompagnement) && (
              <div className="flex flex-col gap-y-0.5 mt-0.5">
                {repas.entree &&
                  (repas.entree_recette_id ? (
                    <a
                      href={`/cuisine/recettes/${repas.entree_recette_id}`}
                      className="text-[10px] text-muted-foreground hover:underline break-words"
                      title={`Entrée : ${repas.entree}`}
                      onClick={(e) => e.stopPropagation()}
                    >
                      🥗 {repas.entree}
                    </a>
                  ) : (
                    <span
                      className="text-[10px] text-muted-foreground break-words"
                      title={`Entrée : ${repas.entree}`}
                    >
                      🥗 {repas.entree}
                    </span>
                  ))}
                {repas.legumes &&
                  (champEnEdition === "legumes" ? (
                    <form
                      className="flex gap-0.5"
                      onSubmit={(e) => {
                        e.preventDefault();
                        if (valeurEdition.trim() && onModifierChamp) {
                          onModifierChamp(repas.id, "legumes", valeurEdition.trim());
                        }
                        setChampEnEdition(null);
                      }}
                    >
                      <input
                        aria-label="Modifier les légumes"
                        autoFocus
                        className="text-[10px] w-full rounded border px-1 py-0 bg-background"
                        value={valeurEdition}
                        onChange={(e) => setValeurEdition(e.target.value)}
                        onBlur={() => setChampEnEdition(null)}
                        onKeyDown={(e) => e.key === "Escape" && setChampEnEdition(null)}
                      />
                    </form>
                  ) : (
                    <span
                      className="text-[10px] break-words text-muted-foreground cursor-pointer hover:text-primary transition-colors"
                      title={`Légumes : ${repas.legumes} — cliquer pour modifier`}
                      onClick={() => {
                        setChampEnEdition("legumes");
                        setValeurEdition(repas.legumes || "");
                      }}
                    >
                      🥦 {repas.legumes}
                    </span>
                  ))}
                {repas.feculents &&
                  (champEnEdition === "feculents" ? (
                    <form
                      className="flex gap-0.5"
                      onSubmit={(e) => {
                        e.preventDefault();
                        if (valeurEdition.trim() && onModifierChamp) {
                          onModifierChamp(repas.id, "feculents", valeurEdition.trim());
                        }
                        setChampEnEdition(null);
                      }}
                    >
                      <input
                        aria-label="Modifier les féculents"
                        autoFocus
                        className="text-[10px] w-full rounded border px-1 py-0 bg-background"
                        value={valeurEdition}
                        onChange={(e) => setValeurEdition(e.target.value)}
                        onBlur={() => setChampEnEdition(null)}
                        onKeyDown={(e) => e.key === "Escape" && setChampEnEdition(null)}
                      />
                    </form>
                  ) : (
                    <span
                      className="text-[10px] break-words text-muted-foreground cursor-pointer hover:text-primary transition-colors"
                      title={`Féculents : ${repas.feculents} — cliquer pour modifier`}
                      onClick={() => {
                        setChampEnEdition("feculents");
                        setValeurEdition(repas.feculents || "");
                      }}
                    >
                      🍚 {repas.feculents}
                    </span>
                  ))}
                {repas.proteine_accompagnement && (
                  <span
                    className="text-[10px] text-muted-foreground break-words"
                    title={`Protéine : ${repas.proteine_accompagnement}`}
                  >
                    🥩 {repas.proteine_accompagnement}
                  </span>
                )}
                {repas.laitage && (
                  <span
                    className="text-[10px] text-muted-foreground break-words"
                    title={`Laitage : ${repas.laitage}`}
                  >
                    🥛 {repas.laitage}
                  </span>
                )}
                {repas.dessert &&
                  (repas.dessert_recette_id ? (
                    <a
                      href={`/cuisine/recettes/${repas.dessert_recette_id}`}
                      className="text-[10px] text-muted-foreground hover:underline break-words"
                      title={`Dessert : ${repas.dessert}`}
                      onClick={(e) => e.stopPropagation()}
                    >
                      🍮 {repas.dessert}
                    </a>
                  ) : (
                    <span
                      className="text-[10px] text-muted-foreground break-words"
                      title={`Dessert : ${repas.dessert}`}
                    >
                      🍮 {repas.dessert}
                    </span>
                  ))}
              </div>
            )}
        </div>
      </div>
      <div className="flex items-center gap-0.5 shrink-0">
        {onRegenerer && !repas.est_reste && (
          <Button
            variant="ghost"
            size="icon"
            className="h-5 w-5"
            title="Régénérer ce repas avec l'IA"
            onClick={() => onRegenerer(repas)}
          >
            <RefreshCw className="h-3 w-3" />
          </Button>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="h-5 w-5"
          onClick={() => onRetirer(repas)}
          aria-label="Retirer le repas"
        >
          <X className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}
