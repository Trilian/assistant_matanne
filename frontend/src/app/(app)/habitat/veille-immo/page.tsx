"use client";

import { listerAnnoncesHabitat } from "@/bibliotheque/api/habitat";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function VeilleImmoHabitatPage() {
  const { data } = utiliserRequete(["habitat", "annonces"], listerAnnoncesHabitat);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Veille Immo</h1>
        <p className="text-muted-foreground">Suivi des annonces agregees et score de pertinence.</p>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Annonces</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {(data ?? []).map((annonce) => (
            <a key={annonce.id} href={annonce.url_source} target="_blank" rel="noreferrer" className="block rounded-md border p-3 hover:bg-accent/40 transition-colors">
              <p className="font-medium">{annonce.titre ?? "Annonce sans titre"}</p>
              <p className="text-xs text-muted-foreground">
                {annonce.source} · {annonce.ville ?? "Ville inconnue"} · {annonce.prix ?? "?"} EUR · score {(annonce.score_pertinence ?? 0).toFixed(2)}
              </p>
            </a>
          ))}
          {(data ?? []).length === 0 && <p className="text-sm text-muted-foreground">Aucune annonce disponible.</p>}
        </CardContent>
      </Card>
    </div>
  );
}
