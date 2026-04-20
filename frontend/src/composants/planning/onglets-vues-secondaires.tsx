'use client';

import { lazy, Suspense } from "react";
import { Loader2 } from "lucide-react";
import { TabsContent } from "@/composants/ui/tabs";

const ContenuNutritionLazy = lazy(() => import("@/app/(app)/cuisine/nutrition/page"));
const ContenuMaSemaineLazy = lazy(() => import("@/app/(app)/cuisine/ma-semaine/page"));
const ContenuSaisonnierLazy = lazy(() => import("@/app/(app)/cuisine/saisonnier/page"));

const FallbackChargement = () => (
  <div className="flex items-center justify-center py-12">
    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
  </div>
);

export function OngletsVuesSecondaires() {
  return (
    <>
      <TabsContent value="ma-semaine" className="mt-4">
        <Suspense fallback={<FallbackChargement />}>
          <ContenuMaSemaineLazy />
        </Suspense>
      </TabsContent>

      <TabsContent value="nutrition" className="mt-4">
        <Suspense fallback={<FallbackChargement />}>
          <ContenuNutritionLazy />
        </Suspense>
      </TabsContent>

      <TabsContent value="saisonnier" className="mt-4">
        <Suspense fallback={<FallbackChargement />}>
          <ContenuSaisonnierLazy />
        </Suspense>
      </TabsContent>
    </>
  );
}
