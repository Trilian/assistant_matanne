// ═══════════════════════════════════════════════════════════
// Hook utiliserDialogCrud — Gestion état dialog CRUD
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";

/**
 * Hook générique pour gérer l'état dialog + mode édition d'un CRUD.
 *
 * Remplace le boilerplate répété dans chaque page :
 * - `const [dialogOuvert, setDialogOuvert] = useState(false)`
 * - `const [enEdition, setEnEdition] = useState<T | null>(null)`
 * - Fonctions `ouvrirCreation`, `ouvrirEdition`, `fermerDialog`
 *
 * @example
 * ```tsx
 * const formVide = { nom: "", description: "" };
 * const [form, setForm] = useState(formVide);
 *
 * const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
 *   utiliserDialogCrud<MonType>({
 *     onOuvrirCreation: () => setForm(formVide),
 *     onOuvrirEdition: (item) => setForm({ nom: item.nom, description: item.description ?? "" }),
 *   });
 * ```
 */
export function utiliserDialogCrud<T>(options?: {
  /** Appelé lors de l'ouverture en mode création — typiquement pour réinitialiser le form */
  onOuvrirCreation?: () => void;
  /** Appelé lors de l'ouverture en mode édition — typiquement pour pré-remplir le form */
  onOuvrirEdition?: (item: T) => void;
  /** Appelé à la fermeture — nettoyage supplémentaire si besoin */
  onFermer?: () => void;
}) {
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [enEdition, setEnEdition] = useState<T | null>(null);

  const ouvrirCreation = () => {
    setEnEdition(null);
    setDialogOuvert(true);
    options?.onOuvrirCreation?.();
  };

  const ouvrirEdition = (item: T) => {
    setEnEdition(item);
    setDialogOuvert(true);
    options?.onOuvrirEdition?.(item);
  };

  const fermerDialog = () => {
    setDialogOuvert(false);
    setEnEdition(null);
    options?.onFermer?.();
  };

  return {
    dialogOuvert,
    setDialogOuvert,
    enEdition,
    /** Vrai si on est en mode édition (enEdition !== null) */
    estEnEdition: enEdition !== null,
    ouvrirCreation,
    ouvrirEdition,
    fermerDialog,
  };
}
