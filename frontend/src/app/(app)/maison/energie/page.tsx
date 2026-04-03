// ═══════════════════════════════════════════════════════════
// Énergie Temps Réel — Tableau de bord Linky + estimations
// Page énergie maison
// ═══════════════════════════════════════════════════════════

"use client";

import { Zap, TrendingUp, TrendingDown, Minus, AlertCircle, RefreshCw, Wifi, WifiOff } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirEnergieTempsReel } from "@/bibliotheque/api/avance";

function iconeTendance(tendance: string) {
  if (tendance === "hausse") return <TrendingUp className="h-5 w-5 text-destructive" />;
  if (tendance === "baisse") return <TrendingDown className="h-5 w-5 text-green-600" />;
  return <Minus className="h-5 w-5 text-muted-foreground" />;
}

function labelTendance(tendance: string) {
  if (tendance === "hausse") return "En hausse";
  if (tendance === "baisse") return "En baisse";
  return "Stable";
}

export default function EnergiePage() {
  const { data, isLoading, isFetching, refetch } = utiliserRequete(
    ["innovations", "energie-temps-reel"],
    obtenirEnergieTempsReel,
    { staleTime: 5 * 60 * 1000, refetchInterval: 5 * 60 * 1000 } // rafraîchissement 5 min
  );

  const horodatage = data?.horodatage
    ? new Date(data.horodatage).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })
    : null;

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Zap className="h-8 w-8 text-yellow-500" /> Énergie
          </h1>
          <p className="text-muted-foreground mt-1">
            Suivi de consommation électrique en temps réel
          </p>
        </div>
        <div className="flex items-center gap-2">
          {data && (
            <Badge variant={data.linky_connecte ? "default" : "secondary"} className="gap-1">
              {data.linky_connecte
                ? <><Wifi className="h-3 w-3" /> Linky connecté</>
                : <><WifiOff className="h-3 w-3" /> Estimation</>
              }
            </Badge>
          )}
          <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCw className={`h-4 w-4 mr-1 ${isFetching ? "animate-spin" : ""}`} />
            Actualiser
          </Button>
        </div>
      </div>

      {/* Alertes */}
      {!isLoading && data && data.alertes.length > 0 && (
        <Card className="border-destructive/40 bg-destructive/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-destructive flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              {data.alertes.length} alerte{data.alertes.length > 1 ? "s" : ""} énergie
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              {data.alertes.map((a, i) => (
                <li key={i} className="text-sm text-destructive flex items-start gap-2">
                  <span className="mt-0.5">•</span>
                  <span>{a}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* KPIs principaux */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Puissance instantanée */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Puissance instantanée</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-10 w-28" />
            ) : (
              <p className="text-3xl font-bold">
                {data?.puissance_instantanee_w !== null && data?.puissance_instantanee_w !== undefined
                  ? `${data.puissance_instantanee_w.toFixed(0)} W`
                  : "–"}
              </p>
            )}
            {data?.linky_connecte && (
              <p className="text-xs text-muted-foreground mt-1">Mesure Linky en direct</p>
            )}
          </CardContent>
        </Card>

        {/* Consommation du jour */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Consommation aujourd&apos;hui</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-10 w-24" />
            ) : (
              <p className="text-3xl font-bold">
                {data?.consommation_jour_estimee_kwh !== null && data?.consommation_jour_estimee_kwh !== undefined
                  ? `${data.consommation_jour_estimee_kwh.toFixed(1)} kWh`
                  : "–"}
              </p>
            )}
            <p className="text-xs text-muted-foreground mt-1">Estimation journalière</p>
          </CardContent>
        </Card>

        {/* Consommation du mois */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Ce mois-ci</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-10 w-24" />
            ) : (
              <p className="text-3xl font-bold">
                {data?.consommation_mois_kwh !== null && data?.consommation_mois_kwh !== undefined
                  ? `${data.consommation_mois_kwh.toFixed(0)} kWh`
                  : "–"}
              </p>
            )}
            <p className="text-xs text-muted-foreground mt-1">Cumulé depuis le 1er</p>
          </CardContent>
        </Card>
      </div>

      {/* Tendance */}
      {!isLoading && data && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {iconeTendance(data.tendance)}
              Tendance mensuelle
            </CardTitle>
            <CardDescription>Comparaison avec le mois précédent</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center gap-4">
            <p className={`text-xl font-semibold ${
              data.tendance === "hausse"
                ? "text-destructive"
                : data.tendance === "baisse"
                ? "text-green-600"
                : "text-muted-foreground"
            }`}>
              {labelTendance(data.tendance)}
            </p>
            <Badge variant="outline" className="text-xs">
              Source : {data.source === "linky" ? "Linky temps réel" : "Relevés enregistrés"}
            </Badge>
          </CardContent>
        </Card>
      )}

      {/* Pied de page */}
      {horodatage && (
        <p className="text-xs text-center text-muted-foreground">
          Dernière mise à jour : {horodatage} — actualisation automatique toutes les 5 min
        </p>
      )}
    </div>
  );
}
