// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// Page MÃ©nage â€” Planning, tÃ¢ches du jour, guides, routines
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

"use client";

import { useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Switch } from "@/composants/ui/switch";
import { RefreshCw, Plus, Pencil, Trash2 } from "lucide-react";
import {
  obtenirTachesJourMaison,
  obtenirPlanningMenageSemaine,
  consulterGuide,
  initialiserRoutinesDefaut,
  listerRoutinesMaison,
  creerRoutineMaison,
  modifierRoutineMaison,
  supprimerRoutineMaison,
  type PlanningSemaine,
  type FicheTache,
  type RoutineMaison,
} from "@/bibliotheque/api/maison";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserStoreMaison } from "@/magasins/store-maison";
import { TimerAppareil } from "@/composants/maison/timer-appareil";
import { DrawerFicheTache } from "@/composants/maison/drawer-fiche-tache";
import { DialogueFormulaire } from "@/composants/disposition/dialogue-formulaire";
import { utiliserDialogCrud } from "@/crochets/utiliser-dialog-crud";
import { toast } from "sonner";

const JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"] as const;
type JourSemaine = (typeof JOURS)[number];

const COULEUR_DIFF: Record<string, string> = {
  facile: "bg-green-100 text-green-800",
  moyen: "bg-yellow-100 text-yellow-800",
  difficile: "bg-red-100 text-red-800",
};

const COULEUR_FREQ: Record<string, string> = {
  quotidien: "bg-amber-100 text-amber-800",
  hebdomadaire: "bg-green-100 text-green-800",
  mensuel: "bg-purple-100 text-purple-800",
};

// â”€â”€â”€ Composant tÃ¢che du jour â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
      <input
        type="checkbox"
        checked={fait}
        onChange={() => onToggle(String(id))}
        id={`tache-${id}`}
        className="h-4 w-4 rounded border-border cursor-pointer"
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
            <span className="text-xs text-muted-foreground">â± {tache.duree_estimee_min} min</span>
          )}
        </div>
      </label>
      <Button variant="ghost" size="sm" className="text-muted-foreground h-7 text-xs" onClick={onVoirFiche}>
        Guide
      </Button>
    </div>
  );
}

// â”€â”€â”€ Composant planning semaine â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
          <p className="text-xs text-muted-foreground italic">Rien de prÃ©vu</p>
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

// â”€â”€â”€ Guide lessive â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

const TACHES_LESSIVE = [
  { id: "vin_rouge", label: "Tache de vin rouge" },
  { id: "graisse", label: "Tache de graisse" },
  { id: "herbe", label: "Tache d'herbe" },
  { id: "sang", label: "Tache de sang" },
  { id: "cafe", label: "Tache de cafÃ©" },
  { id: "moisissure", label: "Tache de moisissure" },
  { id: "transpiration", label: "AurÃ©ole de transpiration" },
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

      {/* SÃ©lection de la tache */}
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
            <option value="synthetique">SynthÃ©tique</option>
            <option value="lin">Lin</option>
          </select>
        </div>
      )}

      {/* RÃ©sultat */}
      {isLoading && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
          Chargement du guide...
        </div>
      )}

      {data && tacheSelectee && !isLoading && (
        <Card>
          <CardContent className="pt-4 space-y-4">
            {/* Ã‰tapes */}
            {Array.isArray((data as Record<string, unknown>).etapes) && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">Ã‰tapes</p>
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
                    <Badge key={p} variant="secondary">ðŸ§´ {p}</Badge>
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

// â”€â”€â”€ Timer section â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function SectionTimers() {
  const APPAREILS = [
    { id: "lave_linge", nom: "Lave-linge", dureeMin: 90, action: "Ã‰tendre le linge" },
    { id: "lave_vaisselle", nom: "Lave-vaisselle", dureeMin: 60, action: "Vider le lave-vaisselle" },
    { id: "seche_linge", nom: "SÃ¨che-linge", dureeMin: 60, action: "Plier le linge" },
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

// â”€â”€â”€ Onglet Routines â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function OngletRoutines() {
  const queryClient = useQueryClient();

  const { data: routines, isLoading } = utiliserRequete(
    ["maison", "routines"],
    listerRoutinesMaison
  );

  const dialog = utiliserDialogCrud<RoutineMaison>();

  const creer = utiliserMutation(
    (payload: Omit<RoutineMaison, "id" | "taches_count">) => creerRoutineMaison(payload),
    { onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["maison", "routines"] }); dialog.fermer(); toast.success("Routine crÃ©Ã©e"); } }
  );

  const modifier = utiliserMutation(
    ({ id, ...rest }: Partial<RoutineMaison> & { id: number }) => modifierRoutineMaison(id, rest),
    { onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["maison", "routines"] }); dialog.fermer(); toast.success("Routine mise Ã  jour"); } }
  );

  const supprimer = utiliserMutation(
    (id: number) => supprimerRoutineMaison(id),
    { onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["maison", "routines"] }); toast.success("Routine supprimÃ©e"); } }
  );

  const toggleActif = utiliserMutation(
    ({ id, actif }: { id: number; actif: boolean }) => modifierRoutineMaison(id, { actif }),
    { onSuccess: () => queryClient.invalidateQueries({ queryKey: ["maison", "routines"] }) }
  );

  const initialiser = utiliserMutation(
    () => initialiserRoutinesDefaut(),
    { onSuccess: (d: { creees: number }) => { queryClient.invalidateQueries({ queryKey: ["maison", "routines"] }); toast.success(`${d.creees} routine(s) crÃ©Ã©e(s)`); } }
  );

  const champsCrud = [
    { nom: "nom", label: "Nom", type: "text" as const, obligatoire: true },
    { nom: "description", label: "Description", type: "text" as const },
    {
      nom: "categorie", label: "CatÃ©gorie", type: "select" as const,
      options: [
        { valeur: "menage", label: "MÃ©nage" },
        { valeur: "cuisine", label: "Cuisine" },
        { valeur: "rangement", label: "Rangement" },
        { valeur: "entretien", label: "Entretien" },
      ],
    },
    {
      nom: "frequence", label: "FrÃ©quence", type: "select" as const, obligatoire: true,
      options: [
        { valeur: "quotidien", label: "Quotidien" },
        { valeur: "hebdomadaire", label: "Hebdomadaire" },
        { valeur: "mensuel", label: "Mensuel" },
      ],
    },
    {
      nom: "moment_journee", label: "Moment", type: "select" as const,
      options: [
        { valeur: "matin", label: "Matin ðŸŒ…" },
        { valeur: "soir", label: "Soir ðŸŒ™" },
        { valeur: "flexible", label: "Flexible ðŸ•" },
      ],
    },
  ];

  const handleSubmit = (vals: Record<string, unknown>) => {
    if (dialog.elementEnEdition) {
      modifier.mutate({ id: dialog.elementEnEdition.id, ...vals });
    } else {
      creer.mutate(vals as Omit<RoutineMaison, "id" | "taches_count">);
    }
  };

  if (isLoading) return <p className="text-sm text-muted-foreground py-6 text-center">Chargement...</p>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{routines?.length ?? 0} routine(s) configurÃ©e(s)</p>
        <Button size="sm" onClick={dialog.ouvrirCreation}>
          <Plus className="h-4 w-4 mr-1" /> Nouvelle routine
        </Button>
      </div>

      {routines && routines.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center space-y-3">
            <p className="text-sm text-muted-foreground">Aucune routine configurÃ©e.</p>
            <Button variant="outline" size="sm" onClick={() => initialiser.mutate()} disabled={initialiser.isPending}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Initialiser les routines par dÃ©faut
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="space-y-3">
        {(routines ?? []).map((r) => (
          <Card key={r.id} className={!r.actif ? "opacity-60" : ""}>
            <CardContent className="flex items-center gap-3 py-3 px-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="font-medium text-sm">{r.nom}</p>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${COULEUR_FREQ[r.frequence] ?? "bg-muted text-muted-foreground"}`}>
                    {r.frequence}
                  </span>
                  {r.moment_journee && (
                    <span className="text-[10px] text-muted-foreground">
                      {r.moment_journee === "matin" ? "ðŸŒ…" : r.moment_journee === "soir" ? "ðŸŒ™" : "ðŸ•"}
                    </span>
                  )}
                  {(r.taches_count ?? 0) > 0 && (
                    <Badge variant="secondary" className="text-[10px] h-4">{r.taches_count} tÃ¢che{(r.taches_count ?? 0) > 1 ? "s" : ""}</Badge>
                  )}
                </div>
                {r.description && <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">{r.description}</p>}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Switch
                  checked={r.actif}
                  onCheckedChange={(checked) => toggleActif.mutate({ id: r.id, actif: checked })}
                />
                <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => dialog.ouvrirEdition(r)}>
                  <Pencil className="h-3.5 w-3.5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 text-destructive hover:text-destructive"
                  onClick={() => supprimer.mutate(r.id)}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <DialogueFormulaire
        ouvert={dialog.ouvert}
        onFermer={dialog.fermer}
        titre={dialog.elementEnEdition ? "Modifier la routine" : "Nouvelle routine"}
        champs={champsCrud}
        valeurInitiale={dialog.elementEnEdition ?? {}}
        onSoumettre={handleSubmit}
        enChargement={creer.isPending || modifier.isPending}
      />
    </div>
  );
}

// â”€â”€â”€ Page principale â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function ContenuMenage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const onglet = searchParams.get("tab") ?? "aujourd-hui";

  const { tachesTerminees, basculerTache } = utiliserStoreMaison();
  const [ficheOuverte, setFicheOuverte] = useState<{
    typeTache: string;
    nomTache: string;
  } | null>(null);

  // TÃ¢ches du jour
  const { data: tachesJour, isLoading: chargTaches } = utiliserRequete(
    ["taches-jour-maison"],
    obtenirTachesJourMaison
  );

  // Planning de la semaine
  const { data: planning, isLoading: chargPlanning } = utiliserRequete(
    ["planning-semaine-menage"],
    obtenirPlanningMenageSemaine
  );

  type TacheItem = { id?: string; nom?: string; categorie?: string; duree_estimee_min?: number };
  const tachesArray: TacheItem[] = Array.isArray(tachesJour)
    ? (tachesJour as TacheItem[])
    : ((tachesJour as { items?: TacheItem[] } | undefined)?.items ?? []);

  const tachesTermineesAujourdHui = tachesArray.filter((t) =>
    tachesTerminees.includes(String(t.id ?? t.nom))
  ).length;

  return (
    <div className="space-y-6 p-4 max-w-5xl mx-auto">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">MÃ©nage</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Planning, tÃ¢ches et guides pratiques
          </p>
        </div>
        {tachesArray.length > 0 && (
          <Badge variant="outline" className="text-sm">
            {tachesTermineesAujourdHui}/{tachesArray.length} faites
          </Badge>
        )}
      </div>

      <Tabs value={onglet} onValueChange={(v) => router.replace(`?tab=${v}`)}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="aujourd-hui">Aujourd&apos;hui</TabsTrigger>
          <TabsTrigger value="semaine">Semaine</TabsTrigger>
          <TabsTrigger value="guides">Guides</TabsTrigger>
          <TabsTrigger value="routines">
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
            Routines
          </TabsTrigger>
        </TabsList>

        {/* â”€â”€ Onglet Aujourd'hui â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
        <TabsContent value="aujourd-hui" className="space-y-6 mt-4">
          {/* TÃ¢ches du jour */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">TÃ¢ches du jour</CardTitle>
            </CardHeader>
            <CardContent>
              {chargTaches && (
                <p className="text-sm text-muted-foreground">Chargement...</p>
              )}
              {!chargTaches && tachesArray.length === 0 && (
                <p className="text-sm text-muted-foreground italic">
                  Aucune tÃ¢che prÃ©vue aujourd&apos;hui ðŸŽ‰
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

        {/* â”€â”€ Onglet Semaine â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
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
                  Aucun planning disponible. Configurez vos routines pour gÃ©nÃ©rer un planning automatique.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* â”€â”€ Onglet Guides â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
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

        {/* â”€â”€ Onglet Routines â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
        <TabsContent value="routines" className="mt-4">
          <OngletRoutines />
        </TabsContent>
      </Tabs>

      {/* Drawer fiche tÃ¢che */}
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

export default function MenagePage() {
  return (
    <Suspense>
      <ContenuMenage />
    </Suspense>
  );
}

