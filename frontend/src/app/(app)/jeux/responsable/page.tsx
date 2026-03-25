// ═══════════════════════════════════════════════════════════
// Jeu Responsable — Budget, Auto-exclusion, Historique
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/composants/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import { Skeleton } from "@/composants/ui/skeleton";
import { Shield, AlertTriangle } from "lucide-react";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import {
  obtenirSuiviResponsable,
  modifierLimite,
  activerAutoExclusion,
  obtenirHistoriqueLimites,
} from "@/bibliotheque/api/jeux";
import type { SuiviResponsable } from "@/types/jeux";
import { toast } from "sonner";

function couleurBudget(pct: number) {
  if (pct >= 100) return "bg-red-600";
  if (pct >= 90) return "bg-red-500";
  if (pct >= 75) return "bg-orange-400";
  if (pct >= 50) return "bg-yellow-400";
  return "bg-green-500";
}

function badgeSeuil(suivi: SuiviResponsable) {
  const pct = suivi.pourcentage_utilise;
  if (pct >= 100) return <Badge variant="destructive">🚫 Budget atteint</Badge>;
  if (pct >= 90) return <Badge variant="destructive">⚠️ Danger (90%+)</Badge>;
  if (pct >= 75) return <Badge className="bg-orange-500">⚠️ Attention (75%+)</Badge>;
  if (pct >= 50) return <Badge variant="secondary">ℹ️ Info (50%+)</Badge>;
  return null;
}

type HistoriqueItem = Record<string, unknown>;

export default function ResponsablePage() {
  const queryClient = useQueryClient();
  const [nouvelleLimite, setNouvelleLimite] = useState("");
  const [dialogLimiteOuvert, setDialogLimiteOuvert] = useState(false);
  const [dialogExclusionOuvert, setDialogExclusionOuvert] = useState(false);

  const { data: suivi, isLoading: chSuivi } = utiliserRequete<SuiviResponsable>(
    ["jeux", "responsable", "suivi"],
    obtenirSuiviResponsable
  );

  const { data: historique = [], isLoading: chHistorique } = utiliserRequete<HistoriqueItem[]>(
    ["jeux", "responsable", "historique"],
    () => obtenirHistoriqueLimites(12) as Promise<HistoriqueItem[]>
  );

  const mutModifierLimite = utiliserMutation(
    (limite: number) => modifierLimite(limite),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["jeux", "responsable"] });
        setDialogLimiteOuvert(false);
        setNouvelleLimite("");
        toast.success("Limite mensuelle modifiée");
      },
    }
  );

  const mutAutoExclusion = utiliserMutation(
    (jours: number) => activerAutoExclusion(jours),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["jeux", "responsable"] });
        setDialogExclusionOuvert(false);
        toast.success("Auto-exclusion activée");
      },
    }
  );

  const countdown = suivi?.auto_exclusion_jusqu_a
    ? Math.ceil((new Date(suivi.auto_exclusion_jusqu_a).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    : null;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Shield className="h-7 w-7 text-primary" />
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Jeu Responsable</h1>
          <p className="text-muted-foreground">Gérez votre budget et vos limites</p>
        </div>
      </div>

      {/* Auto-exclusion active — bannière */}
      {suivi?.auto_exclusion_jusqu_a && countdown && countdown > 0 && (
        <Card className="border-red-500 bg-red-50 dark:bg-red-950">
          <CardContent className="pt-4">
            <p className="font-semibold text-red-700 dark:text-red-300 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Auto-exclusion active — encore {countdown} jours
            </p>
            <p className="text-sm text-red-600 dark:text-red-400 mt-1">
              Jusqu&apos;au {new Date(suivi.auto_exclusion_jusqu_a).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Budget mensuel */}
      {chSuivi ? (
        <Skeleton className="h-40" />
      ) : suivi ? (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              Budget mensuel
              {badgeSeuil(suivi)}
              {suivi.cooldown_actif && <Badge variant="secondary">⏸️ Cooldown actif</Badge>}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>{suivi.mises_cumulees.toFixed(2)}€ dépensés</span>
                <span className="font-medium">{suivi.reste_disponible.toFixed(2)}€ restants</span>
              </div>
              <div className="h-5 rounded-full bg-muted overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${couleurBudget(suivi.pourcentage_utilise)}`}
                  style={{ width: `${Math.min(suivi.pourcentage_utilise, 100)}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground text-right">
                {suivi.pourcentage_utilise.toFixed(0)}% de la limite {suivi.limite.toFixed(0)}€/mois
              </p>
            </div>

            {/* Alertes seuils */}
            <div className="grid grid-cols-4 gap-2 text-center text-xs">
              {[50, 75, 90, 100].map((seuil) => (
                <div key={seuil} className={`rounded p-2 ${suivi.pourcentage_utilise >= seuil ? "bg-orange-100 dark:bg-orange-950 font-semibold" : "bg-muted"}`}>
                  {seuil}%
                </div>
              ))}
            </div>

            <Dialog open={dialogLimiteOuvert} onOpenChange={setDialogLimiteOuvert}>
              <DialogTrigger asChild>
                <Button variant="outline" size="sm">✏️ Modifier la limite mensuelle</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>Modifier la limite mensuelle</DialogTitle></DialogHeader>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    const val = parseFloat(nouvelleLimite);
                    if (isNaN(val) || val <= 0) return;
                    mutModifierLimite.mutate(val);
                  }}
                  className="space-y-4 mt-2"
                >
                  <div>
                    <Label>Nouvelle limite (€/mois)</Label>
                    <Input
                      type="number"
                      min="0"
                      step="5"
                      value={nouvelleLimite}
                      onChange={(e) => setNouvelleLimite(e.target.value)}
                      placeholder={suivi.limite.toFixed(0)}
                      required
                    />
                  </div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <AlertTriangle className="h-3 w-3" />
                    Une augmentation de la limite prend effet après 7 jours.
                  </p>
                  <Button type="submit" className="w-full" disabled={mutModifierLimite.isPending}>
                    Confirmer
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </CardContent>
        </Card>
      ) : null}

      {/* Auto-exclusion */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Auto-exclusion — Faire une pause</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            L&apos;auto-exclusion vous bloque l&apos;accès aux paris pendant la durée choisie. Ce choix est irréversible.
          </p>
          <Dialog open={dialogExclusionOuvert} onOpenChange={setDialogExclusionOuvert}>
            <DialogTrigger asChild>
              <Button variant="destructive" size="sm">🚫 Activer l&apos;auto-exclusion</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Choisir la durée d&apos;exclusion</DialogTitle></DialogHeader>
              <div className="space-y-3 mt-2">
                <p className="text-sm text-muted-foreground">
                  Cette action est irréversible pour la durée choisie.
                </p>
                <div className="flex gap-3">
                  {[3, 7, 30].map((jours) => (
                    <Button
                      key={jours}
                      variant="outline"
                      className="flex-1"
                      onClick={() => mutAutoExclusion.mutate(jours)}
                      disabled={mutAutoExclusion.isPending}
                    >
                      {jours} jours
                    </Button>
                  ))}
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>

      {/* Historique limites */}
      <Card>
        <CardHeader><CardTitle>Historique des limites</CardTitle></CardHeader>
        <CardContent>
          {chHistorique ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
            </div>
          ) : historique.length === 0 ? (
            <p className="text-center py-6 text-muted-foreground">Aucun historique disponible</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Mois</TableHead>
                  <TableHead className="text-right">Limite (€)</TableHead>
                  <TableHead className="text-right">Dépensé (€)</TableHead>
                  <TableHead className="text-right">%</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {historique.map((h, i) => {
                  const mois = String(h.mois ?? "");
                  const limite = Number(h.limite ?? 0);
                  const mises = Number(h.mises_cumulees ?? 0);
                  const pct = limite > 0 ? (mises / limite * 100) : 0;
                  return (
                    <TableRow key={i}>
                      <TableCell>{mois}</TableCell>
                      <TableCell className="text-right">{limite.toFixed(0)}</TableCell>
                      <TableCell className="text-right">{mises.toFixed(0)}</TableCell>
                      <TableCell className="text-right">
                        <span className={pct >= 90 ? "text-red-600 font-bold" : pct >= 75 ? "text-orange-500" : ""}>
                          {pct.toFixed(0)}%
                        </span>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Informations */}
      <Card>
        <CardContent className="pt-4 text-sm text-muted-foreground space-y-2">
          <p className="font-semibold text-foreground flex items-center gap-2">
            <Shield className="h-4 w-4" /> Ressources d&apos;aide
          </p>
          <p>Si vous pensez avoir un problème avec le jeu, des ressources d&apos;aide sont disponibles :</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Aide Jeux — <span className="font-medium">0 974 200 000</span> (appel gratuit)</li>
            <li>Joueurs Info Service — joueurs-info-service.fr</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
