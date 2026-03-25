// ═══════════════════════════════════════════════════════════
// Page Ménage — Planning, tâches du jour, guides
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Checkbox } from "@/composants/ui/checkbox";
import {
  obtenirTachesJourMaison,
  obtenirPlanningSemaine,
  consulterGuide,
  type PlanningSemaine,
  type FicheTache,
} from "@/bibliotheque/api/maison";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { utiliserStoreMaison } from "@/magasins/store-maison";
import { TimerAppareil } from "@/composants/maison/timer-appareil";
import { DrawerFicheTache } from "@/composants/maison/drawer-fiche-tache";

const JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"] as const;
type JourSemaine = (typeof JOURS)[number];

const COULEUR_DIFF: Record<string, string> = {
  facile: "bg-green-100 text-green-800",
  moyen: "bg-yellow-100 text-yellow-800",
  difficile: "bg-red-100 text-red-800",
};

// ─── Composant tâche du jour ─────────────────────────────────────────────────

function TacheJourItem({
  tache,
  fait,
  onToggle,
  onVoirFiche,
}: {
  tache: { nom: string; categorie?: string; duree_estimee_min?: number; id?: string };
  fait: boolean;
  onToggle: (id: string) => void;
  onVoirFiche: () => void;
}) {
  const id = tache.id ?? tache.nom;
  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg border transition-opacity ${fait ? "opacity-50" : ""}`}>
      <Checkbox
        checked={fait}
        onCheckedChange={() => onToggle(String(id))}
        id={`tache-${id}`}
      />
      <label htmlFor={`tache-${id}`} className="flex-1 cursor-pointer">
        <p className={`text-sm font-medium ${fait ? "line-through text-muted-foreground" : ""}`}>
          {tache.nom}
        </p>
        <div className="flex items-center gap-2 mt-0.5">
          {tache.categorie && (
            <span className="text-xs text-muted-foreground capitalize">{tache.categorie}</span>
          )}
          {tache.duree_estimee_min && (
            <span className="text-xs text-muted-foreground">⏱ {tache.duree_estimee_min} min</span>
          )}
        </div>
      </label>
      <Button variant="ghost" size="sm" className="text-muted-foreground h-7 text-xs" onClick={onVoirFiche}>
        Guide
      </Button>
    </div>
  );
}

// ─── Composant planning semaine ──────────────────────────────────────────────

function ColonneJour({
  jour,
  taches,
  onVoirFiche,
}: {
  jour: string;
  taches: FicheTache[];
  onVoirFiche: (tache: FicheTache) => void;
}) {
  const total = taches.reduce((acc, t) => acc + (t.duree_estimee_min ?? 0), 0);
  return (
    <div className="min-w-[140px]">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs font-semibold capitalize text-muted-foreground">{jour}</p>
        {total > 0 && <span className="text-xs text-muted-foreground">{total}min</span>}
      </div>
      <div className="space-y-2">
        {taches.length === 0 ? (
          <p className="text-xs text-muted-foreground italic">Rien de prévu</p>
        ) : (
          taches.map((t, i) => (
            <button
              key={i}
              onClick={() => onVoirFiche(t)}
              className="w-full text-left rounded-md border bg-card hover:bg-accent transition-colors p-2 group"
            >
              <p className="text-xs font-medium line-clamp-2">{t.nom}</p>
              <div className="flex items-center gap-1 mt-1">
                {t.difficulte && (
                  <span className={`text-[10px] px-1 rounded ${COULEUR_DIFF[t.difficulte] ?? "bg-muted"}`}>
                    {t.difficulte}
                  </span>
                )}
                {t.duree_estimee_min && (
                  <span className="text-[10px] text-muted-foreground">{t.duree_estimee_min}m</span>
                )}
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}

// ─── Guide lessive ─────────────────────────────────────────────────────────

const TACHES_LESSIVE = [
  { id: "vin_rouge", label: "Tache de vin rouge" },
  { id: "graisse", label: "Tache de graisse" },
  { id: "herbe", label: "Tache d'herbe" },
  { id: "sang", label: "Tache de sang" },
  { id: "cafe", label: "Tache de café" },
  { id: "moisissure", label: "Tache de moisissure" },
  { id: "transpiration", label: "Auréole de transpiration" },
];

function GuideLessive() {
  const [tacheSelectee, setTacheSelectee] = useState<string | null>(null);
  const [tissu, setTissu] = useState("");

  const { data, isLoading } = utiliserRequete(
    ["guide-lessive", tacheSelectee ?? "", tissu],
    () =>
      consulterGuide({
        type_guide: "lessive",
        tache: tacheSelectee ?? undefined,
        tissu: tissu || undefined,
      }),
    { enabled: !!tacheSelectee }
  );

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-sm">Quelle tache ?</h3>

      {/* Sélection de la tache */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {TACHES_LESSIVE.map((t) => (
          <button
            key={t.id}
            onClick={() => setTacheSelectee(t.id)}
            className={`text-left rounded-lg border p-3 text-sm transition-colors ${
              tacheSelectee === t.id
                ? "border-primary bg-primary/5 font-medium"
                : "hover:bg-accent"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Optionnel : tissu */}
      {tacheSelectee && (
        <div className="flex items-center gap-3">
          <label className="text-sm text-muted-foreground">Tissu (optionnel) :</label>
          <select
            value={tissu}
            onChange={(e) => setTissu(e.target.value)}
            className="text-sm border rounded-md px-2 py-1 bg-background"
          >
            <option value="">Tous tissus</option>
            <option value="coton">Coton</option>
            <option value="laine">Laine</option>
            <option value="soie">Soie</option>
            <option value="synthetique">Synthétique</option>
            <option value="lin">Lin</option>
          </select>
        </div>
      )}

      {/* Résultat */}
      {isLoading && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
          Chargement du guide...
        </div>
      )}

      {data && tacheSelectee && !isLoading && (
        <Card>
          <CardContent className="pt-4 space-y-4">
            {/* Étapes */}
            {Array.isArray((data as Record<string, unknown>).etapes) && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">Étapes</p>
                <ol className="space-y-2">
                  {((data as Record<string, unknown>).etapes as string[]).map((e: string, i: number) => (
                    <li key={i} className="flex gap-2 text-sm">
                      <span className="font-bold text-primary">{i + 1}.</span>
                      {e}
                    </li>
                  ))}
                </ol>
              </div>
            )}
            {/* Produits */}
            {Array.isArray((data as Record<string, unknown>).produits) && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">Produits</p>
                <div className="flex flex-wrap gap-2">
                  {((data as Record<string, unknown>).produits as string[]).map((p: string) => (
                    <Badge key={p} variant="secondary">🧴 {p}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// ─── Timer section ────────────────────────────────────────────────────────────

function SectionTimers() {
  const APPAREILS = [
    { id: "lave_linge", nom: "Lave-linge", dureeMin: 90, action: "Étendre le linge" },
    { id: "lave_vaisselle", nom: "Lave-vaisselle", dureeMin: 60, action: "Vider le lave-vaisselle" },
    { id: "seche_linge", nom: "Sèche-linge", dureeMin: 60, action: "Plier le linge" },
  ];

  return (
    <div className="space-y-2">
      <h3 className="font-semibold text-sm">Timers appareils</h3>
      <div className="grid gap-3">
        {APPAREILS.map((a) => (
          <div key={a.id} className="flex items-center justify-between rounded-lg border p-3">
            <span className="text-sm font-medium">{a.nom}</span>
            <TimerAppareil
              appareil={a.id}
              dureeMin={a.dureeMin}
              actionPost={a.action}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Page principale ─────────────────────────────────────────────────────────

export default function MenagePage() {
  const { tachesTerminees, basculerTache } = utiliserStoreMaison();
  const [ficheOuverte, setFicheOuverte] = useState<{
    typeTache: string;
    nomTache: string;
  } | null>(null);

  // Tâches du jour
  const { data: tachesJour, isLoading: chargTaches } = utiliserRequete(
    ["taches-jour-maison"],
    obtenirTachesJourMaison
  );

  // Planning de la semaine
  const { data: planning, isLoading: chargPlanning } = utiliserRequete(
    ["planning-semaine-menage"],
    obtenirPlanningSemaine
  );

  const tachesArray = Array.isArray(tachesJour)
    ? tachesJour
    : (tachesJour as { items?: unknown[] } | undefined)?.items ?? [];

  const tachesTermineesAujourdHui = tachesArray.filter((t: { id?: string; nom?: string }) =>
    tachesTerminees.includes(String(t.id ?? t.nom))
  ).length;

  return (
    <div className="space-y-6 p-4 max-w-5xl mx-auto">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Ménage</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Planning, tâches et guides pratiques
          </p>
        </div>
        {tachesArray.length > 0 && (
          <Badge variant="outline" className="text-sm">
            {tachesTermineesAujourdHui}/{tachesArray.length} faites
          </Badge>
        )}
      </div>

      <Tabs defaultValue="aujourd-hui">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="aujourd-hui">Aujourd&apos;hui</TabsTrigger>
          <TabsTrigger value="semaine">Semaine</TabsTrigger>
          <TabsTrigger value="guides">Guides</TabsTrigger>
        </TabsList>

        {/* ── Onglet Aujourd'hui ─────────────────────────────────── */}
        <TabsContent value="aujourd-hui" className="space-y-6 mt-4">
          {/* Tâches du jour */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Tâches du jour</CardTitle>
            </CardHeader>
            <CardContent>
              {chargTaches && (
                <p className="text-sm text-muted-foreground">Chargement...</p>
              )}
              {!chargTaches && tachesArray.length === 0 && (
                <p className="text-sm text-muted-foreground italic">
                  Aucune tâche prévue aujourd&apos;hui 🎉
                </p>
              )}
              <div className="space-y-2">
                {(tachesArray as Array<{ nom: string; categorie?: string; duree_estimee_min?: number; id?: string }>).map((t, i) => (
                  <TacheJourItem
                    key={t.id ?? i}
                    tache={t}
                    fait={tachesTerminees.includes(String(t.id ?? t.nom))}
                    onToggle={basculerTache}
                    onVoirFiche={() =>
                      setFicheOuverte({ typeTache: t.categorie ?? "menage", nomTache: t.nom })
                    }
                  />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Timers */}
          <Card>
            <CardContent className="pt-4">
              <SectionTimers />
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Onglet Semaine ─────────────────────────────────────── */}
        <TabsContent value="semaine" className="mt-4">
          {chargPlanning && <p className="text-sm text-muted-foreground">Chargement...</p>}
          {planning && (
            <div className="overflow-x-auto">
              <div className="flex gap-3 min-w-max pb-2">
                {JOURS.map((jour) => (
                  <ColonneJour
                    key={jour}
                    jour={jour}
                    taches={planning[jour as JourSemaine] ?? []}
                    onVoirFiche={(t) =>
                      setFicheOuverte({
                        typeTache: t.type_tache ?? "menage",
                        nomTache: t.nom,
                      })
                    }
                  />
                ))}
              </div>
            </div>
          )}
          {!chargPlanning && !planning && (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-sm text-muted-foreground">
                  Aucun planning disponible. Configurez vos routines pour générer un planning automatique.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* ── Onglet Guides ──────────────────────────────────────── */}
        <TabsContent value="guides" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Guide des taches</CardTitle>
            </CardHeader>
            <CardContent>
              <GuideLessive />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Drawer fiche tâche */}
      {ficheOuverte && (
        <DrawerFicheTache
          ouvert
          onFermer={() => setFicheOuverte(null)}
          typeTache={ficheOuverte.typeTache}
          nomTache={ficheOuverte.nomTache}
        />
      )}
    </div>
  );
}
