"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerTirages, listerGrilles } from "@/bibliotheque/api/jeux";
import type { TirageLoto, GrilleLoto } from "@/types/jeux";

function formaterDate(iso: string) {
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function LotoPage() {
  const { data: tirages = [], isLoading: chargementTirages } = utiliserRequete<TirageLoto[]>(
    ["jeux", "loto", "tirages"],
    listerTirages
  );

  const { data: grilles = [], isLoading: chargementGrilles } = utiliserRequete<GrilleLoto[]>(
    ["jeux", "loto", "grilles"],
    listerGrilles
  );

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">🎱 Loto</h1>

      {/* Derniers tirages */}
      <Card>
        <CardHeader>
          <CardTitle>Derniers tirages</CardTitle>
        </CardHeader>
        <CardContent>
          {chargementTirages ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : tirages.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">
              Aucun tirage enregistré
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Numéros</TableHead>
                  <TableHead>N° Chance</TableHead>
                  <TableHead className="text-right">Jackpot</TableHead>
                  <TableHead className="text-right">Gagnants rang 1</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tirages.map((t) => (
                  <TableRow key={t.id}>
                    <TableCell>{formaterDate(t.date_tirage)}</TableCell>
                    <TableCell>
                      <div className="flex gap-1.5">
                        {t.numeros.map((n, i) => (
                          <span
                            key={i}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-bold"
                          >
                            {n}
                          </span>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      {t.numero_chance != null ? (
                        <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-yellow-500 text-white text-sm font-bold">
                          {t.numero_chance}
                        </span>
                      ) : (
                        "-"
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      {t.jackpot_euros
                        ? `${(t.jackpot_euros / 1_000_000).toFixed(1)} M€`
                        : "-"}
                    </TableCell>
                    <TableCell className="text-right">
                      {t.gagnants_rang1 ?? "-"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Grilles jouées */}
      <Card>
        <CardHeader>
          <CardTitle>Mes grilles</CardTitle>
        </CardHeader>
        <CardContent>
          {chargementGrilles ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : grilles.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">
              Aucune grille enregistrée
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tirage</TableHead>
                  <TableHead>Numéros</TableHead>
                  <TableHead>N° Chance</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Type</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {grilles.map((g) => (
                  <TableRow key={g.id}>
                    <TableCell>#{g.tirage_id ?? "-"}</TableCell>
                    <TableCell>
                      <div className="flex gap-1.5">
                        {g.numeros.map((n, i) => (
                          <span
                            key={i}
                            className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-secondary-foreground text-sm font-bold"
                          >
                            {n}
                          </span>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      {g.numero_chance != null ? (
                        <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-yellow-500 text-white text-sm font-bold">
                          {g.numero_chance}
                        </span>
                      ) : (
                        "-"
                      )}
                    </TableCell>
                    <TableCell>{g.source_prediction ?? "-"}</TableCell>
                    <TableCell>
                      <Badge variant={g.est_virtuelle ? "secondary" : "default"}>
                        {g.est_virtuelle ? "Virtuelle" : "Réelle"}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
