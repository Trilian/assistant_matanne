// ═══════════════════════════════════════════════════════════
// Modifier recette — Page édition
// ═══════════════════════════════════════════════════════════

"use client";

import { use } from "react";
import { useEffect } from "react";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirRecette } from "@/bibliotheque/api/recettes";
import { FormulaireRecette } from "@/composants/cuisine/formulaire-recette";
import { utiliserStoreUI } from "@/magasins/store-ui";

export default function PageModifierRecette({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { definirTitrePage } = utiliserStoreUI();
  const { data: recette, isLoading } = utiliserRequete(
    ["recette", id],
    () => obtenirRecette(Number(id))
  );

  useEffect(() => {
    if (recette?.nom) definirTitrePage(`Modifier — ${recette.nom}`);
    return () => definirTitrePage(null);
  }, [recette?.nom, definirTitrePage]);

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
