'use client';

import type { GenererPlanningParams } from "@/types/planning";
import { ModalGenerationPlanning } from "@/composants/cuisine/modal-generation-planning";

interface Props {
  ouvert: boolean;
  setModalGenerationOuvert: (v: boolean) => void;
  setModalGenerationInitialPlats: (plats: string[]) => void;
  enGeneration: boolean;
  nbPersonnesInitial: number;
  dateDebut: string;
  modalGenerationInitialPlats: string[];
  repasActuelsSemaine: string[];
  lancerGenerationIA: (params: GenererPlanningParams) => void;
}

export function OverlayModalGenerationPlanning({
  ouvert,
  setModalGenerationOuvert,
  setModalGenerationInitialPlats,
  enGeneration,
  nbPersonnesInitial,
  dateDebut,
  modalGenerationInitialPlats,
  repasActuelsSemaine,
  lancerGenerationIA,
}: Props) {
  return (
    <ModalGenerationPlanning
      ouvert={ouvert}
      onFermer={() => {
        setModalGenerationOuvert(false);
        setModalGenerationInitialPlats([]);
      }}
      enGeneration={enGeneration}
      nbPersonnesInitial={nbPersonnesInitial}
      dateDebut={dateDebut}
      initialPlats={modalGenerationInitialPlats}
      repasActuels={repasActuelsSemaine}
      onGenerer={(params) => {
        setModalGenerationOuvert(false);
        setModalGenerationInitialPlats([]);
        lancerGenerationIA(params);
      }}
    />
  );
}
