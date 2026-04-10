"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import {
  genererSuggestionsDecoHabitat,
  listerProjetsDecoHabitat,
  synchroniserDepenseDecoHabitat,
} from "@/bibliotheque/api/habitat";
import { EntetePageHabitat } from "@/composants/habitat/entete-page-habitat";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import { Textarea } from "@/composants/ui/textarea";
import { utiliserMutationAvecInvalidation, utiliserRequete } from "@/crochets/utiliser-api";

export default function DecoHabitatPage() {
  const [brief, setBrief] = useState("Ambiance chaleureuse, rangements intégrés, matières durables.");
  const [montant, setMontant] = useState("250");
  const { data: projets } = utiliserRequete(["habitat", "deco"], listerProjetsDecoHabitat);
  const projetActif = projets?.[0] ?? null;

  const conceptMutation = utiliserMutationAvecInvalidation(
    ({ projetId, generer_image }: { projetId: number; generer_image: boolean }) =>
      genererSuggestionsDecoHabitat(projetId, { brief, generer_image }),
    [["habitat", "deco"], ["habitat", "hub"]]
  );

  const budgetMutation = utiliserMutationAvecInvalidation(
    ({ projetId }: { projetId: number }) =>
      synchroniserDepenseDecoHabitat(projetId, {
        montant: Number(montant) || 0,
        note: "Synchronisation habitat -> maison",
      }),
    [["habitat", "deco"], ["habitat", "hub"]]
  );

  const consommation = useMemo(() => {
    return (projets ?? []).reduce(
      (acc, projet) => {
        acc.prevu += projet.budget_prevu ?? 0;
        acc.depense += projet.budget_depense ?? 0;
        return acc;
      },
      { prevu: 0, depense: 0 }
    );
  }, [projets]);

  return (
    <div className="space-y-6">
      <EntetePageHabitat
        badge="H7-H9 • Deco & budget"
        titre="Deco"
        description="Concepts IA par piece, visuels de projection et synchronisation des depenses avec Maison pour garder une lecture budgetaire coherente." 
        stats={[
          { label: "Projets", valeur: `${projets?.length ?? 0}` },
          { label: "Prevu", valeur: `${Math.round(consommation.prevu).toLocaleString("fr-FR")} EUR` },
          { label: "Depense", valeur: `${Math.round(consommation.depense).toLocaleString("fr-FR")} EUR` },
        ]}
      />

      <div className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Portefeuille deco</CardTitle>
            <CardDescription>
              {consommation.depense.toFixed(0)} / {consommation.prevu.toFixed(0)} EUR engages.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {(projets ?? []).map((projet) => (
              <div key={projet.id} className="rounded-xl border p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium">{projet.nom_piece}</p>
                    <p className="text-xs text-muted-foreground">
                      {projet.style ?? "style non defini"} · {projet.budget_prevu ?? "?"} EUR prevus
                    </p>
                  </div>
                  <Badge variant="outline">{projet.statut}</Badge>
                </div>
                {projet.palette_couleurs && projet.palette_couleurs.length > 0 && (
                  <div className="mt-3 flex gap-2">
                    {projet.palette_couleurs.map((couleur) => (
                      <Badge key={couleur} variant="secondary">{couleur}</Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Assistant deco</CardTitle>
            <CardDescription>Génère un concept détaillé, puis pousse la dépense dans Maison.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea value={brief} onChange={(event) => setBrief(event.target.value)} rows={4} />
            <div className="flex flex-wrap gap-2">
              <Button
                disabled={!projetActif || conceptMutation.isPending}
                onClick={() => projetActif && conceptMutation.mutate({ projetId: projetActif.id, generer_image: false })}
              >
                {conceptMutation.isPending ? "Generation..." : "Generer concept"}
              </Button>
              <Button
                variant="outline"
                disabled={!projetActif || conceptMutation.isPending}
                onClick={() => projetActif && conceptMutation.mutate({ projetId: projetActif.id, generer_image: true })}
              >
                Concept + image
              </Button>
            </div>

            {conceptMutation.data && (
              <div className="rounded-xl border p-4">
                <p className="font-medium">{conceptMutation.data.concept.resume}</p>
                <p className="mt-3 text-xs font-medium uppercase tracking-wide text-muted-foreground">Achats prioritaires</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {conceptMutation.data.concept.achats_prioritaires.map((item) => (
                    <Badge key={item} variant="secondary">{item}</Badge>
                  ))}
                </div>
                {conceptMutation.data.image?.image_base64 && (
                  <Image
                    src={conceptMutation.data.image.image_base64}
                    alt="Concept deco"
                    width={1200}
                    height={800}
                    unoptimized
                    className="mt-4 rounded-xl border"
                  />
                )}
              </div>
            )}

            <div className="rounded-xl border p-4">
              <p className="mb-3 text-sm font-medium">Synchronisation budget</p>
              <div className="flex gap-2">
                <Input value={montant} onChange={(event) => setMontant(event.target.value)} inputMode="decimal" className="w-32" />
                <Button
                  variant="outline"
                  disabled={!projetActif || budgetMutation.isPending}
                  onClick={() => projetActif && budgetMutation.mutate({ projetId: projetActif.id })}
                >
                  {budgetMutation.isPending ? "Sync..." : "Pousser vers Maison"}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}