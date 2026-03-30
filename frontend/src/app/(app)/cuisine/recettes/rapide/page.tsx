// ═══════════════════════════════════════════════════════════
// Rapide Recette — Page création simplifiée (4.4)
// ═══════════════════════════════════════════════════════════
// Formulaire minimal : juste nom + photo
// Les détails (ingrédients, temps) sont générés par l'IA à partir de la photo
// ═══════════════════════════════════════════════════════════

import { FormulaireRecette } from "@/composants/cuisine/formulaire-recette";

export default function PageRapideRecette() {
  return <FormulaireRecette modeSimple={true} />;
}
