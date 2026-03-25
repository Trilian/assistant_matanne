// ═══════════════════════════════════════════════════════════
// Charges — Factures et abonnements
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Receipt, TrendingUp, Calendar } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerCharges } from "@/bibliotheque/api/maison";

const ANNEE_COURANTE = new Date().getFullYear();
const ANNEES = [ANNEE_COURANTE, ANNEE_COURANTE - 1, ANNEE_COURANTE - 2];

export default function PageCharges() {
  const [annee, setAnnee] = useState(String(ANNEE_COURANTE));

  const { data: charges, isLoading } = utiliserRequete(
    ["maison", "charges", annee],
    () => listerCharges(Number(annee))
  );

  const total = charges?.reduce((s, c) => s + c.montant, 0) ?? 0;

  // Grouper par type
  const parType: Record<string, number> = {};
  charges?.forEach((c) => {
    parType[c.type] = (parType[c.type] ?? 0) + c.montant;
  });
  const typesOrdres = Object.entries(parType).sort(([, a], [, b]) => b - a);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🧾 Charges</h1>
          <p className="text-muted-foreground">
            Factures, abonnements et charges récurrentes
          </p>
        </div>
        <Select value={annee} onValueChange={setAnnee}>
          <SelectTrigger className="w-28">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ANNEES.map((a) => (
              <SelectItem key={a} value={String(a)}>
                {a}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          <Skeleton className="h-24" />
          <Skeleton className="h-40" />
        </div>
      ) : (
        <>
          {/* Total */}
          <Card className="border-primary/30 bg-primary/5">
            <CardContent className="flex items-center gap-4 py-4">
              <div className="rounded-lg bg-primary/10 p-3">
                <TrendingUp className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {total.toLocaleString("fr-FR", {
                    style: "currency",
                    currency: "EUR",
                  })}
                </p>
                <p className="text-sm text-muted-foreground">
                  Total {annee}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Répartition par type */}
          {typesOrdres.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Par catégorie</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {typesOrdres.map(([type, montant]) => (
                  <div key={type} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="capitalize">{type}</span>
                      <span className="font-medium">
                        {montant.toLocaleString("fr-FR", {
                          style: "currency",
                          currency: "EUR",
                        })}
                      </span>
                    </div>
                    <div className="bg-muted rounded-full h-2">
                      <div
                        className="h-2 rounded-full bg-primary"
                        style={{
                          width: `${total > 0 ? (montant / total) * 100 : 0}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Liste */}
          <div className="space-y-2">
            <h2 className="text-lg font-semibold">Détails</h2>
            {!charges?.length ? (
              <Card>
                <CardContent className="py-8 text-center text-muted-foreground">
                  <Receipt className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  Aucune charge pour {annee}
                </CardContent>
              </Card>
            ) : (
              charges.map((c) => (
                <Card key={c.id}>
                  <CardContent className="flex items-center justify-between py-3">
                    <div>
                      <p className="text-sm font-medium">
                        {c.fournisseur || c.type}
                      </p>
                      <div className="flex gap-2 text-xs text-muted-foreground mt-1">
                        <Badge variant="outline" className="text-xs">
                          {c.type}
                        </Badge>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(c.date).toLocaleDateString("fr-FR")}
                        </span>
                      </div>
                    </div>
                    <span className="text-sm font-semibold">
                      {c.montant.toLocaleString("fr-FR", {
                        style: "currency",
                        currency: "EUR",
                      })}
                    </span>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
}
