"use client";

import { Bot, Download, Flame, Sparkles, Trophy } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Switch } from "@/composants/ui/switch";
import { utiliserInvalidation, utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import {
  configurerModePiloteAuto,
  obtenirJournalFamilialAuto,
  obtenirJournalFamilialPdf,
  obtenirModePiloteAuto,
  obtenirRapportMensuelPdf,
  obtenirScoreFamilleHebdo,
  obtenirSuggestionRepasGarmin,
  telechargerPdfBase64,
} from "@/bibliotheque/api/innovations";
import { toast } from "sonner";

export default function PageInnovations() {
  const invalider = utiliserInvalidation();
  const { data: modePilote } = utiliserRequete(["innovations", "mode-pilote"], obtenirModePiloteAuto);
  const { data: scoreFamille } = utiliserRequete(["innovations", "score-famille"], obtenirScoreFamilleHebdo);
  const { data: journal } = utiliserRequete(["innovations", "journal-familial"], obtenirJournalFamilialAuto);
  const { data: repasGarmin } = utiliserRequete(["innovations", "garmin-repas"], obtenirSuggestionRepasGarmin);

  const { mutate: basculerModePilote, isPending: basculeEnCours } = utiliserMutation(
    (actif: boolean) =>
      configurerModePiloteAuto({
        actif,
        niveau_autonomie: actif ? modePilote?.niveau_autonomie ?? "validation_requise" : "off",
      }),
    {
      onSuccess: (data) => {
        invalider(["innovations", "mode-pilote"]);
        toast.success(data.actif ? "Mode pilote active" : "Mode pilote desactive");
      },
      onError: () => {
        toast.error("Impossible de mettre a jour le mode pilote");
      },
    }
  );

  const { mutate: telechargerJournal, isPending: telechargementJournal } = utiliserMutation(
    () => obtenirJournalFamilialPdf(),
    {
      onSuccess: (data) => {
        telechargerPdfBase64(data.contenu_base64, data.filename);
        toast.success("PDF du journal téléchargé");
      },
    }
  );

  const { mutate: telechargerRapport, isPending: telechargementRapport } = utiliserMutation(
    () => obtenirRapportMensuelPdf(),
    {
      onSuccess: (data) => {
        telechargerPdfBase64(data.contenu_base64, data.filename);
        toast.success("Rapport mensuel téléchargé");
      },
    }
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Innovations</h1>
        <p className="text-muted-foreground">Phase E: pilote auto, score famille, journal et rapports intelligents.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              Mode Pilote Automatique
            </CardTitle>
            <CardDescription>Niveau: {modePilote?.niveau_autonomie ?? "-"}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between rounded-md border p-2">
              <p className="text-sm">Activer le pilotage IA</p>
              <Switch
                checked={Boolean(modePilote?.actif)}
                disabled={basculeEnCours}
                onCheckedChange={(actif) => basculerModePilote(actif)}
              />
            </div>
            {(modePilote?.actions ?? []).length === 0 ? (
              <p className="text-sm text-muted-foreground">Aucune action proposée pour le moment.</p>
            ) : (
              modePilote?.actions.map((a) => (
                <div key={`${a.module}-${a.action}`} className="rounded-md border p-2">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium">{a.module} · {a.action}</p>
                    <Badge variant="outline">{a.statut}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">{a.details}</p>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5" />
              Score Famille Hebdo
            </CardTitle>
            <CardDescription>
              Score global: <span className="font-semibold">{scoreFamille?.score_global ?? 0}/100</span>
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {(scoreFamille?.dimensions ?? []).map((d) => (
              <div key={d.nom} className="flex items-center justify-between rounded-md border p-2 text-sm">
                <span>{d.nom}</span>
                <span className="font-medium">{d.score.toFixed(1)}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Flame className="h-5 w-5" />
            Adaptation Repas selon Garmin
          </CardTitle>
          <CardDescription>Proposition automatique selon la depense energetique recente.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="font-medium">{repasGarmin?.recette_suggeree ?? "Suggestion indisponible"}</p>
          <p className="text-sm text-muted-foreground">{repasGarmin?.raison ?? ""}</p>
          {(repasGarmin?.alternatives ?? []).length > 0 && (
            <div className="flex flex-wrap gap-2">
              {repasGarmin?.alternatives.map((alt) => (
                <Badge key={alt} variant="outline">
                  {alt}
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            Journal Familial Automatique
          </CardTitle>
          <CardDescription>{journal?.semaine_reference ?? "-"}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="font-medium">{journal?.titre ?? "Journal familial"}</p>
          <p className="text-sm text-muted-foreground">{journal?.resume ?? ""}</p>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" onClick={() => telechargerJournal()} disabled={telechargementJournal}>
              <Download className="mr-2 h-4 w-4" /> PDF Journal
            </Button>
            <Button onClick={() => telechargerRapport()} disabled={telechargementRapport}>
              <Download className="mr-2 h-4 w-4" /> PDF Rapport mensuel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
