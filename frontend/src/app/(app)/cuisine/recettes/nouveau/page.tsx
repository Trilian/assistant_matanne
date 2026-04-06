// ═══════════════════════════════════════════════════════════
// Nouvelle recette — Page création (mode normal ou rapide)
// ═══════════════════════════════════════════════════════════

"use client";

import { useSearchParams } from "next/navigation";
import { FormulaireRecette } from "@/composants/cuisine/formulaire-recette";

export default function PageNouvelleRecette() {
  const searchParams = useSearchParams();
  const modeSimple = searchParams.get("mode") === "rapide";

  return <FormulaireRecette modeSimple={modeSimple} />;
}
