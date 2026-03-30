"use client";

import Link from "next/link";
import { AlertTriangle, Armchair, Building2, Home, Ruler, Search, Trees, Wallet } from "lucide-react";
import { EntetePageHabitat } from "@/composants/habitat/entete-page-habitat";
import { Badge } from "@/composants/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import { evaluerFraicheurSync, libelleFraicheurSync } from "@/bibliotheque/habitat-fraicheur-sync";
import { obtenirHubHabitat } from "@/bibliotheque/api/habitat";

const BLOCS = [
  {
    titre: "Scenarios",
    description: "Comparer demenager, agrandir ou rester avec un score multi-criteres.",
    chemin: "/habitat/scenarios",
    Icone: Home,
  },
  {
    titre: "Veille Immo",
    description: "Centraliser les annonces et piloter leur statut.",
    chemin: "/habitat/veille-immo",
    Icone: Search,
  },
  {
    titre: "Plans",
    description: "Importer les plans et structurer les pieces.",
    chemin: "/habitat/plans",
    Icone: Ruler,
  },
  {
    titre: "Marche",
    description: "Comparer les prix DVF locaux avant arbitrage ou visite.",
    chemin: "/habitat/marche",
    Icone: Building2,
  },
  {
    titre: "Deco",
    description: "Suivre les projets deco par piece et par budget.",
    chemin: "/habitat/deco",
    Icone: Armchair,
  },
  {
    titre: "Jardin",
    description: "Organiser les zones paysageres du terrain.",
    chemin: "/habitat/jardin",
    Icone: Trees,
  },
];

interface DerniereSyncVeille {
  dateIso: string;
}

export default function HabitatPage() {
  const { data } = utiliserRequete(["habitat", "hub"], obtenirHubHabitat);
  const [derniereSync] = utiliserStockageLocal<DerniereSyncVeille | null>("habitat.veille.derniere-sync", null);
  const etatFraicheur = derniereSync ? evaluerFraicheurSync(derniereSync.dateIso) : null;

  return (
    <div className="space-y-6">
      <EntetePageHabitat
        badge="Module Habitat"
        titre="Habitat"
        description="Hub de decision logement pour cadrer la veille immo, les plans, le marche local, la deco et le jardin dans une meme trajectoire projet."
        stats={data ? [
          { label: "Scenarios", valeur: `${data.scenarios}` },
          { label: "Alertes", valeur: `${data.alertes}` },
          { label: "Plans", valeur: `${data.plans}` },
          { label: "Budget deco", valeur: `${Math.round(data.budget_deco_depense).toLocaleString("fr-FR")} EUR` },
        ] : undefined}
      />

      {data && (
        <div className="grid gap-3 grid-cols-2 md:grid-cols-4 xl:grid-cols-8">
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.scenarios}</p><p className="text-xs text-muted-foreground">Scenarios</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.annonces}</p><p className="text-xs text-muted-foreground">Annonces</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.plans}</p><p className="text-xs text-muted-foreground">Plans</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.projets_deco}</p><p className="text-xs text-muted-foreground">Projets deco</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.zones_jardin}</p><p className="text-xs text-muted-foreground">Zones jardin</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.alertes}</p><p className="text-xs text-muted-foreground">Alertes</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.annonces_a_traiter}</p><p className="text-xs text-muted-foreground">A traiter</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{Math.round((data.budget_deco_depense / Math.max(data.budget_deco_total || 1, 1)) * 100)}%</p><p className="text-xs text-muted-foreground">Budget deco consomme</p></CardContent></Card>
        </div>
      )}

      {data && (
        <div className="grid gap-4 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base"><AlertTriangle className="h-4 w-4" /> Priorites H4-H12</CardTitle>
              <CardDescription>Lecture rapide de la charge Habitat en cours.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <p>{data.alertes} alerte(s) veille a arbitrer.</p>
              <p>{data.annonces_a_traiter} annonce(s) en statut nouveau ou alerte.</p>
              <p>{data.plans} plan(s) exploitables par le pipeline IA.</p>
              <div className="pt-1">
                {!etatFraicheur ? <Badge variant="outline">Derniere sync: aucune</Badge> : null}
                {etatFraicheur === "fresh" ? <Badge variant="secondary">Derniere sync: {libelleFraicheurSync("fresh")}</Badge> : null}
                {etatFraicheur === "warning" ? (
                  <Badge className="border-amber-300 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-200" variant="outline">
                    Derniere sync: {libelleFraicheurSync("warning")}
                  </Badge>
                ) : null}
                {etatFraicheur === "stale" ? (
                  <Badge className="border-red-300 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200" variant="outline">
                    Derniere sync: {libelleFraicheurSync("stale")}
                  </Badge>
                ) : null}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base"><Wallet className="h-4 w-4" /> Budget Habitat</CardTitle>
              <CardDescription>Suivi de la depense deco synchronisee avec Maison.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <p>Total prevu: {data.budget_deco_total.toFixed(0)} EUR</p>
              <p>Depense synchronisee: {data.budget_deco_depense.toFixed(0)} EUR</p>
              <p>Reste theorique: {(data.budget_deco_total - data.budget_deco_depense).toFixed(0)} EUR</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base"><Home className="h-4 w-4" /> Parcours recommande</CardTitle>
              <CardDescription>Synchroniser la veille, analyser les plans, puis arbitrer le budget deco.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <p>1. Veille Immo pour capter les opportunites et la carte.</p>
              <p>2. Plans pour lancer l&apos;analyse IA et l&apos;historique de variantes.</p>
              <p>3. Deco/Jardin pour convertir en decisions budgetees.</p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {BLOCS.map(({ titre, description, chemin, Icone }) => (
          <Link key={chemin} href={chemin}>
            <Card className="h-full transition-all hover:-translate-y-0.5 hover:bg-accent/40">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg"><Icone className="h-4 w-4" /> {titre}</CardTitle>
                <CardDescription>{description}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
