// ═══════════════════════════════════════════════════════════
// Jardin — Plantes et calendrier des semis
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Sprout, Flower2, Calendar, Leaf, Sun } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerElementsJardin, obtenirCalendrierSemis } from "@/bibliotheque/api/maison";

const NOMS_MOIS = [
  "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
];

export default function PageJardin() {
  const moisCourant = new Date().getMonth() + 1;
  const [moisSemis, setMoisSemis] = useState(String(moisCourant));

  const { data: elements, isLoading: chargementElements } = utiliserRequete(
    ["maison", "jardin", "elements"],
    () => listerElementsJardin()
  );

  const { data: calendrier, isLoading: chargementCalendrier } = utiliserRequete(
    ["maison", "jardin", "semis", moisSemis],
    () => obtenirCalendrierSemis(Number(moisSemis))
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🌱 Jardin</h1>
        <p className="text-muted-foreground">
          Plantes, calendrier des semis et suivi du potager
        </p>
      </div>

      <Tabs defaultValue="plantes">
        <TabsList>
          <TabsTrigger value="plantes">
            <Sprout className="mr-2 h-4 w-4" />
            Mes plantes
          </TabsTrigger>
          <TabsTrigger value="semis">
            <Calendar className="mr-2 h-4 w-4" />
            Calendrier semis
          </TabsTrigger>
        </TabsList>

        {/* ─── Onglet Plantes ─────────────────────────── */}
        <TabsContent value="plantes" className="space-y-4 mt-4">
          {chargementElements ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-32 w-full" />
              ))}
            </div>
          ) : !elements?.length ? (
            <Card>
              <CardContent className="py-10 text-center text-muted-foreground">
                <Flower2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                Aucune plante enregistrée
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {elements.map((el) => (
                <Card key={el.id}>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm">{el.nom}</CardTitle>
                      {el.statut && (
                        <Badge variant="secondary" className="text-xs">
                          {el.statut}
                        </Badge>
                      )}
                    </div>
                    {el.type && (
                      <CardDescription className="text-xs">
                        {el.type}
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                      {el.location && (
                        <span className="flex items-center gap-1">
                          <Sun className="h-3 w-3" />
                          {el.location}
                        </span>
                      )}
                      {el.date_plantation && (
                        <span>
                          Planté le{" "}
                          {new Date(el.date_plantation).toLocaleDateString("fr-FR")}
                        </span>
                      )}
                    </div>
                    {el.notes && (
                      <p className="mt-2 text-xs text-muted-foreground line-clamp-2">
                        {el.notes}
                      </p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* ─── Onglet Calendrier Semis ────────────────── */}
        <TabsContent value="semis" className="space-y-4 mt-4">
          <div className="flex items-center gap-3">
            <Select value={moisSemis} onValueChange={setMoisSemis}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {NOMS_MOIS.map((nom, i) => (
                  <SelectItem key={i + 1} value={String(i + 1)}>
                    {nom}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {chargementCalendrier ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-24" />
              ))}
            </div>
          ) : calendrier ? (
            <div className="grid gap-4 sm:grid-cols-3">
              {/* À semer */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Sprout className="h-4 w-4 text-green-600" />
                    À semer
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {calendrier.a_semer.length === 0 ? (
                    <p className="text-xs text-muted-foreground">
                      Rien à semer ce mois
                    </p>
                  ) : (
                    <ul className="space-y-1">
                      {calendrier.a_semer.map((p) => (
                        <li
                          key={p.nom}
                          className="text-sm flex items-center gap-2"
                        >
                          <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                          {p.nom}
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>

              {/* À planter */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Leaf className="h-4 w-4 text-emerald-600" />
                    À planter
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {calendrier.a_planter.length === 0 ? (
                    <p className="text-xs text-muted-foreground">
                      Rien à planter ce mois
                    </p>
                  ) : (
                    <ul className="space-y-1">
                      {calendrier.a_planter.map((p) => (
                        <li
                          key={p.nom}
                          className="text-sm flex items-center gap-2"
                        >
                          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                          {p.nom}
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>

              {/* À récolter */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Flower2 className="h-4 w-4 text-amber-600" />
                    À récolter
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {calendrier.a_recolter.length === 0 ? (
                    <p className="text-xs text-muted-foreground">
                      Rien à récolter ce mois
                    </p>
                  ) : (
                    <ul className="space-y-1">
                      {calendrier.a_recolter.map((p) => (
                        <li
                          key={p.nom}
                          className="text-sm flex items-center gap-2"
                        >
                          <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                          {p.nom}
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : null}
        </TabsContent>
      </Tabs>
    </div>
  );
}
