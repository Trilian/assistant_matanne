"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, Trash2 } from "lucide-react";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { listerParis, obtenirStatsParis, listerMatchs, creerPari, supprimerPari } from "@/bibliotheque/api/jeux";
import dynamic from "next/dynamic";
import type { PariSportif, StatsParis, MatchJeu } from "@/types/jeux";
import { toast } from "sonner";

const GraphiqueROI = dynamic(
  () => import("@/composants/graphiques/graphique-roi").then((m) => m.GraphiqueROI),
  { ssr: false }
);

const FILTRES_STATUT = ["tous", "gagne", "perdu", "en_cours", "annule"] as const;

function couleurStatut(statut: string) {
  switch (statut) {
    case "gagne":
      return "default";
    case "perdu":
      return "destructive";
    case "en_cours":
      return "secondary";
    default:
      return "outline";
  }
}

export default function ParisPage() {
  const [filtreStatut, setFiltreStatut] = useState("tous");
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [matchId, setMatchId] = useState("");
  const [typePari, setTypePari] = useState("1X2");
  const [prediction, setPrediction] = useState("");
  const [cote, setCote] = useState("");
  const [mise, setMise] = useState("");

  const queryClient = useQueryClient();

  const mutationCreer = utiliserMutation(
    (data: { match_id: number; type_pari: string; prediction: string; cote: number; mise: number }) =>
      creerPari(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["jeux", "paris"] });
        setDialogOuvert(false);
        setMatchId("");
        setTypePari("1X2");
        setPrediction("");
        setCote("");
        setMise("");
        toast.success("Pari ajouté");
      },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const mutationSupprimer = utiliserMutation(
    (id: number) => supprimerPari(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["jeux", "paris"] });
        toast.success("Pari supprimé");
      },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

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

  const matchParId = new Map(matchs.map((m) => [m.id, m]));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">🏟️ Paris Sportifs</h1>
        <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-1" /> Nouveau pari
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Nouveau pari</DialogTitle>
            </DialogHeader>
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
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner un match" />
                  </SelectTrigger>
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
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
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
                <div>
                  <Label>Cote</Label>
                  <Input type="number" step="0.01" value={cote} onChange={(e) => setCote(e.target.value)} required />
                </div>
                <div>
                  <Label>Mise (€)</Label>
                  <Input type="number" step="0.01" value={mise} onChange={(e) => setMise(e.target.value)} required />
                </div>
              </div>
              <Button type="submit" className="w-full" disabled={mutationCreer.isPending}>
                {mutationCreer.isPending ? "Enregistrement…" : "Enregistrer le pari"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Statistiques */}
      {chargementStats ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">
                Total paris
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{stats.total_paris}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">
                Mises totales
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{stats.total_mise.toFixed(2)} €</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">
                Bénéfice
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p
                className={`text-2xl font-bold ${
                  stats.benefice >= 0 ? "text-green-600" : "text-red-600"
                }`}
              >
                {stats.benefice >= 0 ? "+" : ""}
                {stats.benefice.toFixed(2)} €
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">
                Taux réussite
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">
                {(stats.taux_reussite * 100).toFixed(1)}%
              </p>
            </CardContent>
          </Card>
        </div>
      ) : null}

      {/* Graphique ROI cumulé */}
      {paris.length >= 2 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Évolution gains/pertes</CardTitle>
          </CardHeader>
          <CardContent>
            <GraphiqueROI
              donnees={paris
                .filter((p) => p.statut === "gagne" || p.statut === "perdu")
                .reduce<{ index: number; label: string; cumul: number }[]>(
                  (acc, p, i) => {
                    const prev = acc.length > 0 ? acc[acc.length - 1].cumul : 0;
                    const gain = p.gain != null ? p.gain - p.mise : -p.mise;
                    acc.push({
                      index: i + 1,
                      label: `#${i + 1}`,
                      cumul: Math.round((prev + gain) * 100) / 100,
                    });
                    return acc;
                  },
                  []
                )}
            />
          </CardContent>
        </Card>
      )}

      {/* Filtres */}
      <div className="flex flex-wrap gap-2">
        {FILTRES_STATUT.map((s) => (
          <Button
            key={s}
            variant={filtreStatut === s ? "default" : "outline"}
            size="sm"
            onClick={() => setFiltreStatut(s)}
          >
            {s === "tous" ? "Tous" : s.replace("_", " ")}
          </Button>
        ))}
      </div>

      {/* Tableau des paris */}
      <Card>
        <CardHeader>
          <CardTitle>Historique des paris</CardTitle>
        </CardHeader>
        <CardContent>
          {chargementParis ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : paris.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">
              Aucun pari trouvé
            </p>
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
                    <TableRow key={p.id}>
                      <TableCell className="font-medium">
                        {match
                          ? `${match.equipe_domicile ?? "?"} vs ${match.equipe_exterieur ?? "?"}`
                          : `#${p.match_id ?? "-"}`}
                      </TableCell>
                      <TableCell>{p.type_pari}</TableCell>
                      <TableCell>{p.prediction ?? "-"}</TableCell>
                      <TableCell className="text-right">{p.cote.toFixed(2)}</TableCell>
                      <TableCell className="text-right">{p.mise.toFixed(2)} €</TableCell>
                      <TableCell className="text-right">
                        {p.gain != null ? `${p.gain.toFixed(2)} €` : "-"}
                      </TableCell>
                      <TableCell>
                        <Badge variant={couleurStatut(p.statut)}>
                          {p.statut}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-destructive"
                          onClick={() => mutationSupprimer.mutate(p.id)}
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
    </div>
  );
}
