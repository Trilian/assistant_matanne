"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/composants/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/composants/ui/sheet";
import { Skeleton } from "@/composants/ui/skeleton";
import { Plus, Trash2, TrendingUp, AlertTriangle } from "lucide-react";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import {
  listerParis,
  obtenirStatsParis,
  listerMatchs,
  creerPari,
  supprimerPari,
  obtenirValueBets,
  obtenirSeriesActives,
  obtenirPredictionMatch,
  obtenirAnalyseIA,
  obtenirAnalysePatterns,
  verifierMise,
  enregistrerMise,
  obtenirSuiviResponsable,
  obtenirHistoriqueCotes,
} from "@/bibliotheque/api/jeux";
import dynamic from "next/dynamic";
import type { PariSportif, StatsParis, MatchJeu, ValueBet, SerieJeux, PredictionMatch, AnalyseIA, SuiviResponsable } from "@/types/jeux";
import { toast } from "sonner";
import { HeatmapCotes } from "@/composants/jeux/heatmap-cotes";
import { TableauMatchsExpert } from "@/composants/jeux/tableau-matchs-expert";
import { BankrollWidget } from "@/composants/jeux/bankroll-widget";
import { DetectionPatternModal } from "@/composants/jeux/detection-pattern-modal";
import { StatsPersonnelles } from "@/composants/jeux/stats-personnelles";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { utiliserAuth } from "@/crochets/utiliser-auth";

const GraphiqueROI = dynamic(
  () => import("@/composants/graphiques/graphique-roi").then((m) => m.GraphiqueROI),
  { ssr: false }
);

const FILTRES_STATUT = ["tous", "gagne", "perdu", "en_cours", "annule"] as const;

function couleurStatut(statut: string) {
  switch (statut) {
    case "gagne": return "default";
    case "perdu": return "destructive";
    case "en_cours": return "secondary";
    default: return "outline";
  }
}

function couleurConfiance(confiance: number) {
  if (confiance >= 0.7) return "text-green-600";
  if (confiance >= 0.5) return "text-yellow-600";
  return "text-red-600";
}

function BadgePrediction({ prediction, confiance }: { prediction: string; confiance: number }) {
  const emoji = prediction.toLowerCase().includes("dom") ? "🏠" :
                prediction.toLowerCase().includes("ext") ? "✈️" : "🤝";
  return (
    <span className={`text-xs font-medium ${couleurConfiance(confiance)}`}>
      {emoji} {prediction} {(confiance * 100).toFixed(0)}%
    </span>
  );
}

// ─── Drawer détail match ─────────────────────────────────

function DrawerMatchDetail({
  matchId,
  open,
  onClose,
  onParier,
}: {
  matchId: number | null;
  open: boolean;
  onClose: () => void;
  onParier: (matchId: number, prediction: string, cote: number) => void;
}) {
  const matchKey = matchId != null ? String(matchId) : "none";

  const { data: pred, isLoading: chPred } = utiliserRequete<PredictionMatch>(
    ["jeux", "prediction", matchKey],
    () => obtenirPredictionMatch(matchId!),
    { enabled: !!matchId }
  );

  const { data: analyseIA, isLoading: chIA } = utiliserRequete<AnalyseIA>(
    ["jeux", "analyse-ia-match", matchKey],
    () => obtenirAnalyseIA("paris", { match_id: matchId }),
    { enabled: !!matchId }
  );

  const { data: historiqueCotes, isLoading: chCotes } = utiliserRequete(
    ["jeux", "cotes-historique", matchKey],
    () => obtenirHistoriqueCotes(matchId!),
    { enabled: !!matchId }
  );

  return (
    <Sheet open={open} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="overflow-y-auto">
        <SheetHeader>
          <SheetTitle>
            {pred ? `${pred.equipe_domicile ?? "?"} vs ${pred.equipe_exterieur ?? "?"}` : "Détail match"}
          </SheetTitle>
        </SheetHeader>

        {chPred ? (
          <div className="space-y-3 mt-4">
            <Skeleton className="h-6 w-full" />
            <Skeleton className="h-6 w-3/4" />
          </div>
        ) : pred ? (
          <div className="space-y-4 mt-4">
            {/* Probas */}
            <div>
              <p className="text-sm font-semibold mb-2">Probabilités estimées</p>
              <div className="grid grid-cols-3 gap-2 text-center">
                {Object.entries(pred.probas).map(([k, v]) => (
                  <div key={k} className="rounded-lg bg-muted p-2">
                    <p className="text-lg font-bold">{(v * 100).toFixed(0)}%</p>
                    <p className="text-xs text-muted-foreground capitalize">{k}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Confiance */}
            <div className="flex items-center gap-2">
              <Badge variant={pred.confiance >= 0.6 ? "default" : "secondary"}>
                Confiance : {(pred.confiance * 100).toFixed(0)}%
              </Badge>
              <span className="text-xs text-muted-foreground">{pred.niveau_confiance}</span>
            </div>

            {/* Raisons */}
            {pred.raisons.length > 0 && (
              <div>
                <p className="text-sm font-semibold mb-1">Raisons</p>
                <ul className="text-sm list-disc pl-5 space-y-1">
                  {pred.raisons.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>
            )}

            {/* Conseil */}
            <p className="text-sm bg-muted p-3 rounded-lg">{pred.conseil}</p>

            {/* Bouton parier */}
            <Button className="w-full" onClick={() => onParier(pred.match_id, pred.resultat, 0)}>
              📝 Parier sur ce match
            </Button>
          </div>
        ) : null}

        {/* Analyse IA */}
        {chIA ? (
          <Skeleton className="h-20 mt-4" />
        ) : analyseIA ? (
          <div className="mt-4 space-y-2 border-t pt-4">
            <p className="text-sm font-semibold">🤖 Analyse IA</p>
            <p className="text-sm">{analyseIA.resume}</p>
            {analyseIA.recommandations.length > 0 && (
              <ul className="text-sm list-disc pl-5">
                {analyseIA.recommandations.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            )}
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <AlertTriangle className="h-3 w-3" />
              {analyseIA.avertissement}
            </p>
          </div>
        ) : null}

        {/* Évolution des cotes (Phase T) */}
        {chCotes ? (
          <Skeleton className="h-40 mt-4" />
        ) : historiqueCotes && historiqueCotes.nb_points > 0 ? (
          <div className="mt-4 space-y-2 border-t pt-4">
            <p className="text-sm font-semibold">📊 Évolution des cotes</p>
            <HeatmapCotes
              points={historiqueCotes.points}
              matchInfo={pred ? `${pred.equipe_domicile} vs ${pred.equipe_exterieur}` : undefined}
            />
            <p className="text-xs text-muted-foreground">
              {historiqueCotes.nb_points} relevés — {historiqueCotes.points[0]?.bookmaker ?? "Bookmaker"}
            </p>
          </div>
        ) : null}
      </SheetContent>
    </Sheet>
  );
}

// ─── Page principale ─────────────────────────────────────

export default function ParisPage() {
  const { user } = utiliserAuth();
  const searchParams = useSearchParams();
  const [filtreStatut, setFiltreStatut] = useState("tous");
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [matchId, setMatchId] = useState("");
  const [typePari, setTypePari] = useState("1X2");
  const [prediction, setPrediction] = useState("");
  const [cote, setCote] = useState("");
  const [mise, setMise] = useState("");
  const [drawerMatch, setDrawerMatch] = useState<number | null>(null);
  const [showSeries, setShowSeries] = useState(false);
  const [modeVue, setModeVue] = useState<"simple" | "expert">("simple");
  const [modalPatternsOuvert, setModalPatternsOuvert] = useState(false);

  const sourceOCR = useMemo(() => searchParams.get("source_ocr") === "1", [searchParams]);

  const queryClient = useQueryClient();

  // ─── Patterns analysis ─────────────────────
  const { data: patternsData } = utiliserRequete(
    ["jeux", "patterns-analysis", user?.id],
    () => obtenirAnalysePatterns(user!.id),
    { enabled: !!user?.id, staleTime: 10 * 60 * 1000 }
  );

  // ─── Value Bets ────────────────────────────
  const { data: valueBets = [], isLoading: chVB } = utiliserRequete<ValueBet[]>(
    ["jeux", "value-bets"],
    () => obtenirValueBets(5.0)
  );

  // ─── Séries actives ────────────────────────
  const { data: series = [] } = utiliserRequete<SerieJeux[]>(
    ["jeux", "series-paris"],
    () => obtenirSeriesActives("paris", 2.0)
  );

  // ─── Suivi responsable (pour alerte série) ─
  const { data: suiviResp } = utiliserRequete<SuiviResponsable>(
    ["jeux", "suivi-responsable"],
    obtenirSuiviResponsable,
    { staleTime: 5 * 60 * 1000 }
  );

  // ─── Mutations ─────────────────────────────
  const mutationCreer = utiliserMutation(
    async (data: { match_id: number; type_pari: string; prediction: string; cote: number; mise: number }) => {
      // Vérifier budget avant de parier
      const check = await verifierMise(data.mise);
      if (!check.autorise) {
        throw new Error(check.raison ?? "Budget mensuel atteint");
      }
      const result = await creerPari(data);
      await enregistrerMise(data.mise, "paris");
      return result;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["jeux"] });
        setDialogOuvert(false);
        resetForm();
        toast.success("Pari ajouté");
      },
    }
  );

  const mutationSupprimer = utiliserMutation(
    (id: number) => supprimerPari(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["jeux", "paris"] });
        toast.success("Pari supprimé");
      },
    }
  );

  function resetForm() {
    setMatchId("");
    setTypePari("1X2");
    setPrediction("");
    setCote("");
    setMise("");
  }

  function preRemplirPari(mId: number, pred: string, c: number) {
    setMatchId(String(mId));
    setPrediction(pred);
    if (c > 0) setCote(String(c));
    setDialogOuvert(true);
    setDrawerMatch(null);
  }

  const { data: stats, isLoading: chargementStats } = utiliserRequete<StatsParis>(
    ["jeux", "paris", "stats"],
    obtenirStatsParis
  );

  const { data: paris = [], isLoading: chargementParis } = utiliserRequete<PariSportif[]>(
    ["jeux", "paris", filtreStatut],
    () => listerParis(filtreStatut === "tous" ? undefined : filtreStatut)
  );

  const { data: matchs = [] } = utiliserRequete<MatchJeu[]>(
    ["jeux", "matchs"],
    () => listerMatchs()
  );

  useEffect(() => {
    if (!sourceOCR) return;

    const typePariParam = searchParams.get("type_pari");
    const predictionParam = searchParams.get("prediction");
    const coteParam = searchParams.get("cote");
    const miseParam = searchParams.get("mise");
    const matchParam = searchParams.get("match_id");

    if (typePariParam) setTypePari(typePariParam);
    if (predictionParam) setPrediction(predictionParam);
    if (coteParam) setCote(coteParam);
    if (miseParam) setMise(miseParam);
    if (matchParam) setMatchId(matchParam);

    setDialogOuvert(true);
  }, [sourceOCR, searchParams]);

  const matchParId = new Map(matchs.map((m) => [m.id, m]));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">🏟️ Paris Sportifs</h1>
        <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
          <DialogTrigger asChild>
            <Button><Plus className="h-4 w-4 mr-1" /> Nouveau pari</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Nouveau pari</DialogTitle></DialogHeader>
            {suiviResp?.serie_actuelle?.alerte_active && (
              <div className="rounded-md border border-orange-400 bg-orange-50 dark:bg-orange-950 px-3 py-2 text-sm text-orange-700 dark:text-orange-300 flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
                <span>
                  <strong>{suiviResp.serie_actuelle.nb} défaites consécutives.</strong> Prenez une pause avant de jouer.{" "}
                  <span className="text-xs">Joueurs Info Service : 09 74 75 13 13</span>
                </span>
              </div>
            )}
            {sourceOCR && (
              <div className="rounded-md border border-emerald-300 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
                Pré-remplissage OCR appliqué. Vérifiez le match, la cote et la mise avant validation.
              </div>
            )}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (!matchId || !prediction || !cote || !mise) return;
                mutationCreer.mutate({
                  match_id: parseInt(matchId),
                  type_pari: typePari,
                  prediction,
                  cote: parseFloat(cote),
                  mise: parseFloat(mise),
                });
              }}
              className="space-y-4"
            >
              <div>
                <Label>Match</Label>
                <Select value={matchId} onValueChange={setMatchId}>
                  <SelectTrigger><SelectValue placeholder="Sélectionner un match" /></SelectTrigger>
                  <SelectContent>
                    {matchs.map((m) => (
                      <SelectItem key={m.id} value={String(m.id)}>
                        {m.equipe_domicile ?? "?"} vs {m.equipe_exterieur ?? "?"}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Type de pari</Label>
                <Select value={typePari} onValueChange={setTypePari}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1X2">1X2</SelectItem>
                    <SelectItem value="over_under">Over/Under</SelectItem>
                    <SelectItem value="score_exact">Score exact</SelectItem>
                    <SelectItem value="buteur">Buteur</SelectItem>
                    <SelectItem value="mi_temps">Mi-temps</SelectItem>
                    <SelectItem value="autre">Autre</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Prédiction</Label>
                <Input value={prediction} onChange={(e) => setPrediction(e.target.value)} required placeholder="ex: Victoire domicile" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><Label>Cote</Label><Input type="number" step="0.01" value={cote} onChange={(e) => setCote(e.target.value)} required /></div>
                <div><Label>Mise (€)</Label><Input type="number" step="0.01" value={mise} onChange={(e) => setMise(e.target.value)} required /></div>
              </div>
              <Button type="submit" className="w-full" disabled={mutationCreer.isPending}>
                {mutationCreer.isPending ? "Enregistrement…" : "Enregistrer le pari"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Widget Bankroll & Money Management */}
      {user && (
        <BankrollWidget
          userId={user.id}
        />
      )}

      {/* Tabs: Paris / Stats */}
      <Tabs defaultValue="paris">
        <TabsList>
          <TabsTrigger value="paris">💰 Paris</TabsTrigger>
          <TabsTrigger value="stats">📊 Mes Stats</TabsTrigger>
        </TabsList>

        <TabsContent value="paris" className="space-y-6 mt-6">
          {/* Toggle Simple / Expert */}
          <div className="flex items-center gap-2 border-b pb-2">
            <Button
              variant={modeVue === "simple" ? "default" : "outline"}
              size="sm"
              onClick={() => setModeVue("simple")}
            >
              🎯 Simple
            </Button>
            <Button
              variant={modeVue === "expert" ? "default" : "outline"}
              size="sm"
              onClick={() => setModeVue("expert")}
            >
              📊 Expert
            </Button>
          </div>

          {modeVue === "expert" ? (
            <TableauMatchsExpert
              onCreerPari={preRemplirPari}
              onVoirDetails={setDrawerMatch}
            />
          ) : (
            <>
          {/* Vue Simple (contenu existant) */}
          {/* Value Bets */}
      {chVB ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-28" />)}
        </div>
      ) : valueBets.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-600" /> Value Bets
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {valueBets.map((vb) => (
              <Card key={vb.match_id} className="hover:bg-accent/50 transition-colors">
                <CardContent className="pt-4 space-y-2">
                  <p className="font-medium text-sm truncate">
                    {vb.equipe_domicile} vs {vb.equipe_exterieur}
                  </p>
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="default">💰 +{Number(vb.edge_pct ?? 0).toFixed(1)}%</Badge>
                    <span className="text-xs text-muted-foreground">cote {Number(vb.cote_bookmaker ?? 0).toFixed(2)}</span>
                    <BadgePrediction prediction={vb.prediction ?? "N/A"} confiance={Number(vb.proba_estimee ?? 0)} />
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => setDrawerMatch(vb.match_id)}>
                      Détail
                    </Button>
                    <Button size="sm" onClick={() => preRemplirPari(vb.match_id, vb.prediction ?? "N/A", Number(vb.cote_bookmaker ?? 0))}>
                      Parier
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Statistiques */}
      {chargementStats ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24 rounded-xl" />)}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Total paris</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{stats.total_paris}</p></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Mises totales</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{stats.total_mise.toFixed(2)} €</p></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Bénéfice</CardTitle></CardHeader><CardContent><p className={`text-2xl font-bold ${stats.benefice >= 0 ? "text-green-600" : "text-red-600"}`}>{stats.benefice >= 0 ? "+" : ""}{stats.benefice.toFixed(2)} €</p></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Taux réussite</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{(stats.taux_reussite * 100).toFixed(1)}%</p></CardContent></Card>
        </div>
      ) : null}

      {/* Graphique ROI */}
      {paris.length >= 2 && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">Évolution gains/pertes</CardTitle></CardHeader>
          <CardContent>
            <GraphiqueROI
              donnees={paris
                .filter((p) => p.statut === "gagne" || p.statut === "perdu")
                .reduce<{ index: number; label: string; cumul: number }[]>((acc, p, i) => {
                  const prev = acc.length > 0 ? acc[acc.length - 1].cumul : 0;
                  const gain = p.gain != null ? p.gain - p.mise : -p.mise;
                  acc.push({ index: i + 1, label: `#${i + 1}`, cumul: Math.round((prev + gain) * 100) / 100 });
                  return acc;
                }, [])}
            />
          </CardContent>
        </Card>
      )}

      {/* Séries actives */}
      {series.length > 0 && (
        <div>
          <Button variant="ghost" size="sm" onClick={() => setShowSeries(!showSeries)} className="mb-2">
            🔥 Séries actives ({series.length}) {showSeries ? "▲" : "▼"}
          </Button>
          {showSeries && (
            <div className="grid gap-2 sm:grid-cols-2">
              {series.sort((a, b) => b.value - a.value).map((s) => (
                <Card key={s.id}>
                  <CardContent className="pt-3 flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">{s.marche}</p>
                      <p className="text-xs text-muted-foreground">{s.championnat ?? s.type_jeu}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">Série {s.serie_actuelle}</Badge>
                      <span className="text-sm font-bold">{s.value.toFixed(1)}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Filtres */}
      <div className="flex flex-wrap gap-2">
        {FILTRES_STATUT.map((s) => (
          <Button key={s} variant={filtreStatut === s ? "default" : "outline"} size="sm" onClick={() => setFiltreStatut(s)}>
            {s === "tous" ? "Tous" : s.replace("_", " ")}
          </Button>
        ))}
      </div>

      {/* Tableau des paris */}
      <Card>
        <CardHeader><CardTitle>Historique des paris</CardTitle></CardHeader>
        <CardContent>
          {chargementParis ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
            </div>
          ) : paris.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">Aucun pari trouvé</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Match</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Prédiction</TableHead>
                  <TableHead className="text-right">Cote</TableHead>
                  <TableHead className="text-right">Mise</TableHead>
                  <TableHead className="text-right">Gain</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead className="w-10"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paris.map((p) => {
                  const match = p.match_id ? matchParId.get(p.match_id) : undefined;
                  return (
                    <TableRow key={p.id} className="cursor-pointer" onClick={() => p.match_id && setDrawerMatch(p.match_id)}>
                      <TableCell className="font-medium">
                        {match ? `${match.equipe_domicile ?? "?"} vs ${match.equipe_exterieur ?? "?"}` : `#${p.match_id ?? "-"}`}
                      </TableCell>
                      <TableCell>{p.type_pari}</TableCell>
                      <TableCell>{p.prediction ?? "-"}</TableCell>
                      <TableCell className="text-right">{p.cote.toFixed(2)}</TableCell>
                      <TableCell className="text-right">{p.mise.toFixed(2)} €</TableCell>
                      <TableCell className="text-right">{p.gain != null ? `${p.gain.toFixed(2)} €` : "-"}</TableCell>
                      <TableCell><Badge variant={couleurStatut(p.statut)}>{p.statut}</Badge></TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-destructive"
                          onClick={(e) => { e.stopPropagation(); mutationSupprimer.mutate(p.id); }}
                          aria-label="Supprimer le pari"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

            </>
          )}
        </TabsContent>

        <TabsContent value="stats" className="mt-6">
          {user && <StatsPersonnelles userId={user.id} />}
        </TabsContent>
      </Tabs>

      {/* Drawer détail match */}
      <DrawerMatchDetail
        matchId={drawerMatch}
        open={drawerMatch !== null}
        onClose={() => setDrawerMatch(null)}
        onParier={preRemplirPari}
      />

      {/* Modal détection patterns cognitifs */}
      {user && patternsData && (
        <DetectionPatternModal
          open={modalPatternsOuvert}
          onClose={() => setModalPatternsOuvert(false)}
          alerts={patternsData}
          userId={user.id}
        />
      )}
    </div>
  );
}
