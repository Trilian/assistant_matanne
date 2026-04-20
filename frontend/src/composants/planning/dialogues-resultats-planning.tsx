'use client'

import { ResponsiveOverlay } from "@/composants/planning/responsive-overlay";
import {
  ContenuDialogueCoursesPlanning,
  ContenuDialogueBatchPlanning,
  ContenuDialogueModePreparationPlanning,
} from "@/composants/planning/blocs-planning";
import type { GenererCoursesResult } from "@/bibliotheque/api/courses";
import type { GenererSessionDepuisPlanningResult } from "@/types/batch-cooking";

interface DialoguesResultatsPlanningProps {
  coursesDialogue: boolean;
  setCoursesDialogue: (open: boolean) => void;
  coursesResultat: GenererCoursesResult | null;
  batchDialogue: boolean;
  setBatchDialogue: (open: boolean) => void;
  batchResultat: GenererSessionDepuisPlanningResult | null;
  choixModePrepa: boolean;
  setChoixModePrepa: (open: boolean) => void;
  enGenerationBatch: boolean;
  genererBatch: (variables: undefined) => void;
}

export function DialoguesResultatsPlanning({
  coursesDialogue,
  setCoursesDialogue,
  coursesResultat,
  batchDialogue,
  setBatchDialogue,
  batchResultat,
  choixModePrepa,
  setChoixModePrepa,
  enGenerationBatch,
  genererBatch,
}: DialoguesResultatsPlanningProps) {
  return (
    <>
      {/* ─── Dialogue résultat courses ─── */}
      <ResponsiveOverlay
        open={coursesDialogue}
        onOpenChange={setCoursesDialogue}
        title="🛒 Liste de courses générée"
        contentClassName="sm:max-w-md"
      >
        {coursesResultat && (
          <ContenuDialogueCoursesPlanning
            coursesResultat={coursesResultat}
            onFermer={() => setCoursesDialogue(false)}
            onVoirListe={() => {
              setCoursesDialogue(false);
              window.location.href = `/cuisine/courses`;
            }}
          />
        )}
      </ResponsiveOverlay>

      {/* ─── Dialogue résultat batch ─── */}
      <ResponsiveOverlay
        open={batchDialogue}
        onOpenChange={setBatchDialogue}
        title="🍳 Session batch créée"
        contentClassName="sm:max-w-md"
      >
        {batchResultat && (
          <ContenuDialogueBatchPlanning
            batchResultat={batchResultat}
            onFermer={() => setBatchDialogue(false)}
            onVoirSession={() => {
              setBatchDialogue(false);
              window.location.href = `/cuisine/batch-cooking/${batchResultat.session_id}`;
            }}
          />
        )}
      </ResponsiveOverlay>

      {/* ─── Dialog choix mode préparation ─── */}
      <ResponsiveOverlay
        open={choixModePrepa}
        onOpenChange={setChoixModePrepa}
        title="🍳 Mode de préparation"
        contentClassName="sm:max-w-md"
      >
        <ContenuDialogueModePreparationPlanning
          enGenerationBatch={enGenerationBatch}
          onChoisirBatch={() => {
            setChoixModePrepa(false);
            genererBatch(undefined);
          }}
          onChoisirJourParJour={() => {
            setChoixModePrepa(false);
            window.location.href = "/cuisine/ma-semaine";
          }}
        />
      </ResponsiveOverlay>
    </>
  );
}
