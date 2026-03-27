// Page Équipements — stub (Phase 2)
// Tabs: Inventaire | Garanties | Domotique

"use client";

import { Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Boxes, ShieldCheck, Wifi, ChevronDown } from "lucide-react";
import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Skeleton } from "@/composants/ui/skeleton";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/composants/ui/collapsible";
import { BandeauIA } from "@/composants/maison/bandeau-ia";
import { BoutonAchat } from "@/composants/bouton-achat";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerGaranties, alertesGaranties, obtenirAstucesDomotique } from "@/bibliotheque/api/maison";

function OngletInventaire() {
  return (
    <Card>
      <CardContent className="py-10 text-center text-muted-foreground">
        <Boxes className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p className="font-medium">Inventaire des équipements</p>
        <p className="text-xs mt-1">Fonctionnalité à venir prochainement</p>
      </CardContent>
    </Card>
  );
}

function OngletGaranties() {
  const { data: garanties, isLoading } = utiliserRequete(["maison", "garanties"], () => listerGaranties());
  const { data: alertes } = utiliserRequete(["maison", "garanties", "alertes"], () => alertesGaranties(90));

  if (isLoading) return <Skeleton className="h-48" />;

  return (
    <div className="space-y-3">
      {alertes?.length > 0 && (
        <Card className="border-amber-300">
          <CardContent className="py-3">
            <p className="text-sm font-medium text-amber-700">{alertes.length} garantie(s) expirant dans 90 jours</p>
          </CardContent>
        </Card>
      )}
      {!garanties?.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><ShieldCheck className="h-8 w-8 mx-auto mb-2 opacity-50" />Aucune garantie</CardContent></Card>
      ) : (
        <div className="space-y-2">
          {garanties.map((g: { id: number; nom: string; date_fin?: string; fournisseur?: string }) => (
            <Card key={g.id}>
              <CardContent className="py-3">
                <p className="text-sm font-medium">{g.nom}</p>
                <p className="text-xs text-muted-foreground">{g.fournisseur ?? "—"}{g.date_fin ? ` · exp. ${new Date(g.date_fin).toLocaleDateString("fr-FR")}` : ""}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function OngletDomotique() {
  const { data: catalogue, isLoading } = utiliserRequete(["maison", "domotique"], () => obtenirAstucesDomotique());
  const [expanded, setExpanded] = useState<string | null>(null);

  if (isLoading) return <Skeleton className="h-48" />;

  const categories = catalogue ? Object.entries(catalogue) : [];

  return (
    <div className="space-y-3">
      {!categories.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><Wifi className="h-8 w-8 mx-auto mb-2 opacity-50" />Aucune astuce domotique</CardContent></Card>
      ) : (
        categories.map(([cat, astuces]) => (
          <Collapsible key={cat} open={expanded === cat} onOpenChange={(o) => setExpanded(o ? cat : null)}>
            <Card>
              <CollapsibleTrigger asChild>
                <CardHeader className="pb-2 cursor-pointer hover:bg-muted/30 transition-colors rounded-t-lg">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm flex items-center gap-1.5">
                      <Wifi className="h-4 w-4 text-blue-500" />{cat}
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <BoutonAchat article={{ nom: cat }} taille="xs" />
                      <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${expanded === cat ? "rotate-180" : ""}`} />
                    </div>
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <CardContent className="pt-0 pb-3">
                  {Array.isArray(astuces) && astuces.map((a: string | { titre?: string; description?: string }, i: number) => (
                    <p key={i} className="text-xs text-muted-foreground py-0.5">• {typeof a === "string" ? a : (a.titre ?? a.description ?? JSON.stringify(a))}</p>
                  ))}
                </CardContent>
              </CollapsibleContent>
            </Card>
          </Collapsible>
        ))
      )}
    </div>
  );
}

function ContenuEquipements() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = searchParams.get("tab") ?? "inventaire";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📦 Équipements</h1>
        <p className="text-muted-foreground">Inventaire, garanties et domotique</p>
      </div>

      <BandeauIA section="equipements" />

      <Tabs value={tab} onValueChange={(val) => router.replace(`?tab=${val}`)}>
        <TabsList>
          <TabsTrigger value="inventaire"><Boxes className="h-4 w-4 mr-1.5" />Inventaire</TabsTrigger>
          <TabsTrigger value="garanties"><ShieldCheck className="h-4 w-4 mr-1.5" />Garanties</TabsTrigger>
          <TabsTrigger value="domotique"><Wifi className="h-4 w-4 mr-1.5" />Domotique</TabsTrigger>
        </TabsList>
        <TabsContent value="inventaire" className="mt-4"><OngletInventaire /></TabsContent>
        <TabsContent value="garanties" className="mt-4"><OngletGaranties /></TabsContent>
        <TabsContent value="domotique" className="mt-4"><OngletDomotique /></TabsContent>
      </Tabs>
    </div>
  );
}

export default function PageEquipements() {
  return (
    <Suspense fallback={<div className="space-y-4"><Skeleton className="h-8 w-40" /><Skeleton className="h-10 w-64" /><Skeleton className="h-48" /></div>}>
      <ContenuEquipements />
    </Suspense>
  );
}
