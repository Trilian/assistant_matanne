// ═══════════════════════════════════════════════════════════
// Travaux — Projets · Entretien · Artisans (fusionnés en tabs)
// Page travaux maison
// ═══════════════════════════════════════════════════════════

"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Hammer, SprayCan, Wrench } from "lucide-react";

import { BandeauIA } from "@/composants/maison/bandeau-ia";
import { OngletArtisans } from "@/composants/maison/travaux/onglet-artisans";
import { OngletEntretien } from "@/composants/maison/travaux/onglet-entretien";
import { OngletProjets } from "@/composants/maison/travaux/onglet-projets";
import { Skeleton } from "@/composants/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";

// ─── Page principale ──────────────────────────────────────────
function ContenuTravaux() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = searchParams.get("tab") ?? "projets";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🔧 Travaux</h1>
        <p className="text-muted-foreground">Projets, entretien et artisans</p>
      </div>

      <BandeauIA section="travaux" />

      <Tabs value={tab} onValueChange={(val) => router.replace(`?tab=${val}`)}>
        <TabsList>
          <TabsTrigger value="projets"><Hammer className="h-4 w-4 mr-1.5" />Projets</TabsTrigger>
          <TabsTrigger value="entretien"><SprayCan className="h-4 w-4 mr-1.5" />Entretien</TabsTrigger>
          <TabsTrigger value="artisans"><Wrench className="h-4 w-4 mr-1.5" />Artisans</TabsTrigger>
        </TabsList>
        <TabsContent value="projets" className="mt-4"><OngletProjets /></TabsContent>
        <TabsContent value="entretien" className="mt-4"><OngletEntretien /></TabsContent>
        <TabsContent value="artisans" className="mt-4"><OngletArtisans /></TabsContent>
      </Tabs>
    </div>
  );
}

export default function PageTravaux() {
  return (
    <Suspense fallback={<div className="space-y-4"><Skeleton className="h-8 w-48" /><Skeleton className="h-10 w-64" /><Skeleton className="h-64" /></div>}>
      <ContenuTravaux />
    </Suspense>
  );
}
