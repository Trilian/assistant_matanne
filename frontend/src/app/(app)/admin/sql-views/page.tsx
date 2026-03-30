"use client";

import { useState } from "react";
import { Database, RefreshCw } from "lucide-react";

import {
  lireVueSql,
  listerVuesSql,
  type VueSqlDataResponse,
  type VueSqlExposee,
} from "@/bibliotheque/api/admin";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Label } from "@/composants/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import { utiliserRequete } from "@/crochets/utiliser-api";

const PAGE_SIZE = 50;

export default function PageAdminSqlViews() {
  const [vueSelectionnee, setVueSelectionnee] = useState<string>("");
  const [page, setPage] = useState(1);

  const {
    data: vues,
    isLoading: chargementVues,
    refetch: rechargerVues,
  } = utiliserRequete(
    ["admin", "sql-views", "catalogue"],
    async (): Promise<{ items: VueSqlExposee[]; total: number }> => listerVuesSql(),
  );

  const vueActive = vueSelectionnee || vues?.items?.[0]?.nom || "";

  const {
    data: donneesVue,
    isLoading: chargementDonnees,
    refetch: rechargerDonnees,
  } = utiliserRequete(
    ["admin", "sql-views", vueActive, String(page), String(PAGE_SIZE)],
    async (): Promise<VueSqlDataResponse> =>
      lireVueSql(vueActive, { page, page_size: PAGE_SIZE }),
    {
      enabled: Boolean(vueActive),
    },
  );

  const colonnes = donneesVue?.items?.length ? Object.keys(donneesVue.items[0]) : [];

  const totalPages = donneesVue?.pages_totales ?? 1;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Database className="h-6 w-6" />
            Vues SQL (admin)
          </h1>
          <p className="text-muted-foreground">
            Consultation en lecture seule des vues SQL exposées par l&apos;API admin.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            void rechargerVues();
            void rechargerDonnees();
          }}
        >
          <RefreshCw className="mr-2 h-4 w-4" />
          Actualiser
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Source de données</CardTitle>
          <CardDescription>
            Sélectionnez une vue SQL pour afficher ses données paginées.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2 max-w-md">
            <Label htmlFor="vue-sql">Vue SQL</Label>
            <Select
              value={vueActive}
              onValueChange={(value) => {
                setVueSelectionnee(value);
                setPage(1);
              }}
              disabled={chargementVues || !vues?.items?.length}
            >
              <SelectTrigger id="vue-sql">
                <SelectValue placeholder="Choisir une vue" />
              </SelectTrigger>
              <SelectContent>
                {(vues?.items ?? []).map((vue) => (
                  <SelectItem key={vue.nom} value={vue.nom}>
                    {vue.nom}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  {colonnes.map((colonne) => (
                    <TableHead key={colonne}>{colonne}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {!chargementDonnees && (donneesVue?.items?.length ?? 0) === 0 && (
                  <TableRow>
                    <TableCell colSpan={Math.max(colonnes.length, 1)} className="text-center text-muted-foreground">
                      Aucune donnée pour cette vue.
                    </TableCell>
                  </TableRow>
                )}
                {(donneesVue?.items ?? []).map((ligne, index) => (
                  <TableRow key={`${index}-${String(ligne[colonnes[0] ?? "id"] ?? "row")}`}>
                    {colonnes.map((colonne) => {
                      const valeur = ligne[colonne];
                      return (
                        <TableCell key={`${index}-${colonne}`}>
                          {valeur === null || valeur === undefined
                            ? "-"
                            : typeof valeur === "object"
                              ? JSON.stringify(valeur)
                              : String(valeur)}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div>
              {donneesVue
                ? `${donneesVue.total} ligne(s) • page ${donneesVue.page}/${donneesVue.pages_totales}`
                : "Aucune vue sélectionnée"}
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1 || chargementDonnees}
              >
                Précédent
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages || chargementDonnees}
              >
                Suivant
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
