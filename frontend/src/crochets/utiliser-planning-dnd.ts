import { useCallback, useState } from "react";
import { toast } from "sonner";
import { type DragEndEvent, type DragStartEvent } from "@dnd-kit/core";
import { definirRepas, supprimerRepas } from "@/bibliotheque/api/planning";
import { utiliserInvalidation } from "@/crochets/utiliser-api";
import type { RepasPlanning, TypeRepas } from "@/types/planning";
import type { ObjetDonnees } from "@/types/commun";

type UtiliserPlanningDndParams = {
  repasPlanning?: RepasPlanning[];
  identifiantPresencePlanning: string;
  diffuserPlanning: (message: ObjetDonnees) => void;
};

export function utiliserPlanningDnd({
  repasPlanning,
  identifiantPresencePlanning,
  diffuserPlanning,
}: UtiliserPlanningDndParams) {
  const [repasGlisse, setRepasGlisse] = useState<RepasPlanning | null>(null);
  const invalider = utiliserInvalidation();

  const deplacerRepas = useCallback(
    async (dateCible: string, typeCible: TypeRepas, repasSource?: RepasPlanning | null) => {
      const repasActif = repasSource ?? repasGlisse;
      if (!repasActif) return;

      const dateSource = (repasActif.date_repas || repasActif.date || "").split("T")[0];
      if (dateSource === dateCible && repasActif.type_repas === typeCible) {
        setRepasGlisse(null);
        return;
      }

      try {
        await definirRepas({
          date: dateCible,
          type_repas: typeCible,
          recette_id: repasActif.recette_id,
          notes: repasActif.notes ?? repasActif.recette_nom,
          portions: repasActif.portions,
        });

        await supprimerRepas(repasActif.id);
        invalider(["planning"]);
        diffuserPlanning({
          action: "slot_swapped",
          data: {
            repas_id: repasActif.id,
            date_source: dateSource,
            type_source: repasActif.type_repas,
            date_cible: dateCible,
            type_cible: typeCible,
          },
          user_id: identifiantPresencePlanning,
        });
        toast.success("Repas déplacé");
      } catch {
        toast.error("Impossible de déplacer ce repas");
      } finally {
        setRepasGlisse(null);
      }
    },
    [diffuserPlanning, identifiantPresencePlanning, invalider, repasGlisse]
  );

  const handleDragStart = useCallback(
    (event: DragStartEvent) => {
      const repasId = Number(String(event.active.id).replace("repas::", ""));
      const repas = repasPlanning?.find((item) => item.id === repasId) ?? null;
      setRepasGlisse(repas);
    },
    [repasPlanning]
  );

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;
      const repasId = Number(String(active.id).replace("repas::", ""));
      const repas = repasPlanning?.find((item) => item.id === repasId) ?? repasGlisse;

      if (!over || !repas) {
        setRepasGlisse(null);
        return;
      }

      const [prefixe, dateCible, typeCible] = String(over.id).split("::");
      if (prefixe !== "case" || !dateCible || !typeCible) {
        setRepasGlisse(null);
        return;
      }

      void deplacerRepas(dateCible, typeCible as TypeRepas, repas);
    },
    [deplacerRepas, repasPlanning, repasGlisse]
  );

  return {
    repasGlisse,
    setRepasGlisse,
    handleDragStart,
    handleDragEnd,
  };
}
