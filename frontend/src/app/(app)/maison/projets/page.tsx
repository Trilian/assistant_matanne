// ═══════════════════════════════════════════════════════════
// Projets Maison — Travaux et améliorations
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Hammer, Filter, Clock, CheckCircle2, AlertCircle } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { utiliserRequete } from "@/hooks/utiliser-api";
import { listerProjets } from "@/lib/api/maison";

const STATUTS = [
  { value: "tous", label: "Tous" },
  { value: "en_cours", label: "En cours" },
  { value: "a_faire", label: "À faire" },
  { value: "termine", label: "Terminé" },
];

const COULEURS_STATUT: Record<string, string> = {
  en_cours: "bg-blue-500/10 text-blue-600",
  a_faire: "bg-yellow-500/10 text-yellow-600",
  termine: "bg-green-500/10 text-green-600",
  annule: "bg-red-500/10 text-red-600",
};

const COULEURS_PRIORITE: Record<string, "default" | "secondary" | "destructive"> = {
  haute: "destructive",
  moyenne: "default",
  basse: "secondary",
};

export default function PageProjets() {
  const [statut, setStatut] = useState("tous");

  const { data: projets, isLoading } = utiliserRequete(
    ["maison", "projets", statut],
    () => listerProjets(statut === "tous" ? undefined : statut)
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🔨 Projets</h1>
          <p className="text-muted-foreground">
            Travaux et améliorations de la maison
          </p>
        </div>
      </div>

      {/* Filtre statut */}
      <div className="flex items-center gap-3">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <Select value={statut} onValueChange={setStatut}>
          <SelectTrigger className="w-44">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {STATUTS.map((s) => (
              <SelectItem key={s.value} value={s.value}>
                {s.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Liste projets */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-28 w-full" />
          ))}
        </div>
      ) : !projets?.length ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            <Hammer className="h-8 w-8 mx-auto mb-2 opacity-50" />
            Aucun projet trouvé
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {projets.map((projet) => (
            <Card key={projet.id}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{projet.nom}</CardTitle>
                  <div className="flex items-center gap-2">
                    {projet.priorite && (
                      <Badge variant={COULEURS_PRIORITE[projet.priorite] ?? "secondary"}>
                        {projet.priorite}
                      </Badge>
                    )}
                    <Badge
                      variant="outline"
                      className={COULEURS_STATUT[projet.statut] ?? ""}
                    >
                      {projet.statut === "en_cours" && (
                        <Clock className="mr-1 h-3 w-3" />
                      )}
                      {projet.statut === "termine" && (
                        <CheckCircle2 className="mr-1 h-3 w-3" />
                      )}
                      {projet.statut === "a_faire" && (
                        <AlertCircle className="mr-1 h-3 w-3" />
                      )}
                      {projet.statut}
                    </Badge>
                  </div>
                </div>
                {projet.description && (
                  <CardDescription>{projet.description}</CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                  {projet.date_debut && (
                    <span>
                      Début:{" "}
                      {new Date(projet.date_debut).toLocaleDateString("fr-FR")}
                    </span>
                  )}
                  {projet.date_fin_prevue && (
                    <span>
                      Fin prévue:{" "}
                      {new Date(projet.date_fin_prevue).toLocaleDateString("fr-FR")}
                    </span>
                  )}
                  <span>{projet.taches_count} tâche(s)</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
