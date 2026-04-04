"use client";

import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, Bot, CloudSun, Download, Heart, Lightbulb, NotebookText, Plane } from "lucide-react";
import {
  configurerModeVacances,
  obtenirInsightsQuotidiens,
  obtenirMeteoContextuelle,
  obtenirModeVacances,
  obtenirRapportMensuelPdf,
  telechargerPdfBase64,
} from "@/bibliotheque/api/avance";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Switch } from "@/composants/ui/switch";

const REDISTRIBUTION = [
  {
    titre: "Mode Pilote Automatique",
    description: "La configuration du pilotage IA est maintenant centralisée dans Outils.",
    href: "/outils",
    label: "Aller vers Outils",
    Icone: Bot,
  },
  {
    titre: "Score Famille Hebdo",
    description: "Le score est intégré directement dans le Dashboard pour le suivi quotidien.",
    href: "/",
    label: "Aller vers Dashboard",
    Icone: Heart,
  },
  {
    titre: "Journal Familial",
    description: "Le résumé familial automatique est maintenant visible dans le hub Famille.",
    href: "/famille",
    label: "Aller vers Famille",
    Icone: NotebookText,
  },
];

export default function PageAvance() {
  const queryClient = useQueryClient();

  const modeVacancesQuery = useQuery({
    queryKey: ["avance", "mode-vacances"],
    queryFn: obtenirModeVacances,
  });

  const insightsQuery = useQuery({
    queryKey: ["avance", "insights-quotidiens"],
    queryFn: () => obtenirInsightsQuotidiens(2),
  });

  const meteoQuery = useQuery({
    queryKey: ["avance", "meteo-contextuelle"],
    queryFn: obtenirMeteoContextuelle,
  });

  const mutModeVacances = useMutation({
    mutationFn: configurerModeVacances,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["avance", "mode-vacances"] });
    },
  });

  const mutTelechargerRapport = useMutation({
    mutationFn: () => obtenirRapportMensuelPdf(),
    onSuccess: (data) => {
      if (data?.contenu_base64 && data?.filename) {
        telechargerPdfBase64(data.contenu_base64, data.filename);
      }
    },
  });

  const modeVacances = modeVacancesQuery.data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Fonctionnalités Avancées</h1>
        <p className="text-muted-foreground">
          Cette page sert désormais de hub de transition vers les modules métier.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {REDISTRIBUTION.map(({ titre, description, href, label, Icone }) => (
          <Card key={href}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Icone className="h-4 w-4" />
                {titre}
              </CardTitle>
              <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild className="w-full" variant="outline">
                <Link href={href}>
                  {label}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Plane className="h-4 w-4" />
              Mode Vacances
            </CardTitle>
            <CardDescription>Toggle rapide du mode vacances (courses compactes, entretien suspendu).</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Activer</span>
              <Switch
                checked={Boolean(modeVacances?.actif)}
                disabled={modeVacancesQuery.isLoading || mutModeVacances.isPending}
                onCheckedChange={(actif) =>
                  mutModeVacances.mutate({
                    actif,
                    checklist_voyage_auto: modeVacances?.checklist_voyage_auto ?? true,
                  })
                }
              />
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={modeVacances?.actif ? "default" : "secondary"}>
                {modeVacances?.actif ? "Actif" : "Inactif"}
              </Badge>
              {modeVacances?.checklist_voyage_auto ? <Badge variant="outline">Checklist auto</Badge> : null}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Lightbulb className="h-4 w-4" />
              Insights Quotidiens
            </CardTitle>
            <CardDescription>1-2 insights IA proactifs du jour.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {insightsQuery.data?.insights?.length ? (
              insightsQuery.data.insights.map((insight, index) => (
                <div key={`${insight.titre}-${index}`} className="rounded-md border p-2">
                  <p className="text-sm font-medium">{insight.titre}</p>
                  <p className="text-xs text-muted-foreground">{insight.message}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">Aucun insight disponible.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <CloudSun className="h-4 w-4" />
              Météo Contextuelle
            </CardTitle>
            <CardDescription>Impacts météo cross-module du jour.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm text-muted-foreground">
              {meteoQuery.data?.ville ?? "Ville"} · {meteoQuery.data?.saison ?? "Saison"}
              {meteoQuery.data?.temperature != null ? ` · ${meteoQuery.data.temperature}°C` : ""}
            </p>
            <p className="text-sm">{meteoQuery.data?.description ?? "Données météo indisponibles"}</p>
            <div className="flex flex-wrap gap-2">
              {meteoQuery.data?.modules?.slice(0, 4).map((m) => (
                <Badge key={m.module} variant="outline">
                  {m.module}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Rapport Mensuel Unifié (PDF)</CardTitle>
          <CardDescription>Téléchargement immédiat du rapport consolidé, avec envoi automatique par email en début de mois.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={() => mutTelechargerRapport.mutate()}
            disabled={mutTelechargerRapport.isPending}
            variant="default"
          >
            <Download className="mr-2 h-4 w-4" />
            Télécharger le rapport
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}