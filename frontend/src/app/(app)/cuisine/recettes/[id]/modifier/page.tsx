// ═══════════════════════════════════════════════════════════
// Modifier recette — Page édition
// ═══════════════════════════════════════════════════════════

"use client";

import { use } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirRecette } from "@/bibliotheque/api/recettes";
import { FormulaireRecette } from "@/composants/cuisine/formulaire-recette";

export default function PageModifierRecette({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: recette, isLoading } = utiliserRequete(
    ["recette", id],
    () => obtenirRecette(Number(id))
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-[400px] w-full" />
      </div>
    );
  }

  if (!recette) return <p>Recette non trouvée</p>;

  return <FormulaireRecette recetteExistante={recette} />;
}
