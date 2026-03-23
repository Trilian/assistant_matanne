// ═══════════════════════════════════════════════════════════
// Stocks — Stocks non-alimentaires
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Package, AlertTriangle, Filter } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerStocks } from "@/bibliotheque/api/maison";

export default function PageStocks() {
  const [alerteOnly, setAlerteOnly] = useState(false);

  const { data: stocks, isLoading } = utiliserRequete(
    ["maison", "stocks", String(alerteOnly)],
    () => listerStocks(undefined, alerteOnly)
  );

  const nbAlertes = stocks?.filter((s) => s.en_alerte).length ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📦 Stocks</h1>
        <p className="text-muted-foreground">
          Consommables et stocks non-alimentaires
        </p>
      </div>

      {/* Alerte résumé + filtre */}
      <div className="flex items-center justify-between">
        {nbAlertes > 0 && (
          <Badge variant="destructive" className="flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" />
            {nbAlertes} stock(s) bas
          </Badge>
        )}
        <div className="flex items-center gap-2 ml-auto">
          <Button
            variant={alerteOnly ? "default" : "outline"}
            size="sm"
            onClick={() => setAlerteOnly(!alerteOnly)}
          >
            <Filter className="mr-2 h-3 w-3" />
            {alerteOnly ? "Tous les stocks" : "Stocks bas uniquement"}
          </Button>
        </div>
      </div>

      {/* Liste stocks */}
      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : !stocks?.length ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            <Package className="h-8 w-8 mx-auto mb-2 opacity-50" />
            {alerteOnly ? "Aucun stock en alerte" : "Aucun stock enregistré"}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {stocks.map((stock) => (
            <Card
              key={stock.id}
              className={stock.en_alerte ? "border-destructive/30" : ""}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">{stock.nom}</CardTitle>
                  {stock.en_alerte && (
                    <AlertTriangle className="h-4 w-4 text-destructive" />
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-end justify-between">
                  <div>
                    <p className="text-2xl font-bold">
                      {stock.quantite}
                      <span className="text-sm font-normal text-muted-foreground ml-1">
                        {stock.unite ?? "unités"}
                      </span>
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Seuil: {stock.seuil_alerte} {stock.unite ?? "unités"}
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    {stock.categorie && (
                      <Badge variant="outline" className="text-xs">
                        {stock.categorie}
                      </Badge>
                    )}
                    {stock.emplacement && (
                      <span className="text-xs text-muted-foreground">
                        {stock.emplacement}
                      </span>
                    )}
                  </div>
                </div>
                {/* Barre de stock */}
                <div className="mt-2 bg-muted rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full ${
                      stock.en_alerte ? "bg-destructive" : "bg-green-500"
                    }`}
                    style={{
                      width: `${Math.min(
                        (stock.quantite / Math.max(stock.seuil_alerte * 2, 1)) * 100,
                        100
                      )}%`,
                    }}
                  />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
