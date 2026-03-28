"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { Receipt } from "lucide-react";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerCharges } from "@/bibliotheque/api/maison";
import type { ChargesMaison } from "@/types/maison";

const ANNEE_COURANTE = new Date().getFullYear();

export default function ChargesPage() {
  const [annee, setAnnee] = useState(ANNEE_COURANTE);

  const { data: charges = [], isLoading } = utiliserRequete<ChargesMaison[]>(
    ["maison", "charges", annee],
    () => listerCharges(annee),
    { staleTime: 5 * 60 * 1000 }
  );

  const total = charges.reduce((sum, c) => sum + (c.montant ?? 0), 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Receipt className="h-8 w-8" /> Charges
        </h1>
        <div className="flex gap-2">
          {[ANNEE_COURANTE - 1, ANNEE_COURANTE].map((a) => (
            <button
              key={a}
              onClick={() => setAnnee(a)}
              className={`px-3 py-1 rounded-md text-sm font-medium border transition-colors ${
                annee === a
                  ? "bg-primary text-primary-foreground border-primary"
                  : "border-border hover:bg-accent"
              }`}
            >
              {a}
            </button>
          ))}
        </div>
      </div>

      {/* Résumé annuel */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-muted-foreground">Total {annee}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">{total.toFixed(2)} €</p>
        </CardContent>
      </Card>

      {/* Liste des charges */}
      <Card>
        <CardHeader>
          <CardTitle>Historique des charges</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : charges.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">
              Aucune charge pour {annee}
            </p>
          ) : (
            <div className="divide-y">
              {charges.map((c) => (
                <div key={c.id} className="flex items-center justify-between py-3">
                  <div>
                    <p className="font-medium">{c.type}</p>
                    {c.fournisseur && (
                      <p className="text-sm text-muted-foreground">{c.fournisseur}</p>
                    )}
                    <p className="text-xs text-muted-foreground">{c.mois} {c.annee}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">{c.montant.toFixed(2)} €</p>
                    {c.commentaire && (
                      <Badge variant="outline" className="text-xs">{c.commentaire}</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
