// ═══════════════════════════════════════════════════════════
// Énergie — Consommation énergétique (CRUD relevés)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Zap, Droplets, Flame, Gauge, Plus, Trash2, TrendingUp, AlertTriangle } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerReleves,
  creerReleve,
  supprimerReleve,
  historiqueEnergie,
  obtenirTendancesEnergie,
} from "@/bibliotheque/api/maison";
import type { ReleveCompteur } from "@/types/maison";
import { toast } from "sonner";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Dot,
} from "recharts";

type TypeCompteur = "electricite" | "eau" | "gaz";

const COMPTEURS: { cle: TypeCompteur; nom: string; Icone: typeof Zap; unite: string; couleur: string }[] = [
  { cle: "electricite", nom: "Électricité", Icone: Zap, unite: "kWh", couleur: "text-yellow-500" },
  { cle: "eau", nom: "Eau", Icone: Droplets, unite: "m³", couleur: "text-blue-500" },
  { cle: "gaz", nom: "Gaz", Icone: Flame, unite: "m³", couleur: "text-orange-500" },
];

export default function PageEnergie() {
  const [typeActif, setTypeActif] = useState<TypeCompteur>("electricite");
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [form, setForm] = useState({ type_compteur: "electricite", valeur: "", date_releve: new Date().toISOString().slice(0, 10), notes: "" });
  const queryClient = useQueryClient();

  const { data: releves, isLoading } = utiliserRequete(
    ["maison", "releves"],
    listerReleves
  );

  const { data: histoElec } = utiliserRequete(
    ["maison", "energie", "electricite"],
    () => historiqueEnergie("electricite", 12),
    { enabled: typeActif === "electricite" }
  );
  const { data: histoEau } = utiliserRequete(
    ["maison", "energie", "eau"],
    () => historiqueEnergie("eau", 12),
    { enabled: typeActif === "eau" }
  );
  const { data: histoGaz } = utiliserRequete(
    ["maison", "energie", "gaz"],
    () => historiqueEnergie("gaz", 12),
    { enabled: typeActif === "gaz" }
  );

  const { data: tendances, isLoading: chargementTendances } = utiliserRequete(
    ["maison", "energie", "tendances", typeActif],
    () => obtenirTendancesEnergie(typeActif, 12)
  );

  const invalider = () =>
    queryClient.invalidateQueries({ queryKey: ["maison"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Omit<ReleveCompteur, "id">) => creerReleve(data),
    {
      onSuccess: () => { invalider(); setDialogOuvert(false); toast.success("Relevé ajouté"); },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const { mutate: supprimer } = utiliserMutation(supprimerReleve, {
    onSuccess: () => { invalider(); toast.success("Relevé supprimé"); },
    onError: () => toast.error("Erreur lors de la suppression"),
  });

  const ouvrirAjout = () => {
    setForm({
      type_compteur: typeActif,
      valeur: "",
      date_releve: new Date().toISOString().slice(0, 10),
      notes: "",
    });
    setDialogOuvert(true);
  };

  const soumettre = () => {
    creer({
      type_compteur: form.type_compteur,
      valeur: Number(form.valeur),
      date_releve: form.date_releve,
      notes: form.notes || undefined,
    });
  };

  // Dernier relevé par type
  const dernierReleve = (type: string) => {
    const filtres = releves?.filter((r) => r.type_compteur === type).sort(
      (a, b) => b.date_releve.localeCompare(a.date_releve)
    );
    return filtres?.[0];
  };

  const relevesFiltres = releves
    ?.filter((r) => r.type_compteur === typeActif)
    .sort((a, b) => b.date_releve.localeCompare(a.date_releve));

  const compteurActif = COMPTEURS.find((c) => c.cle === typeActif)!;

  // Calculer consommation entre relevés consécutifs
  const consommations = relevesFiltres && relevesFiltres.length >= 2
    ? relevesFiltres.slice(0, -1).map((r, i) => ({
        date: r.date_releve,
        delta: r.valeur - relevesFiltres[i + 1].valeur,
      }))
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">⚡ Énergie</h1>
          <p className="text-muted-foreground">
            Suivi de la consommation énergétique du foyer
          </p>
        </div>
        <Button size="sm" onClick={ouvrirAjout}>
          <Plus className="mr-2 h-4 w-4" />
          Saisir un relevé
        </Button>
      </div>

      {/* Compteurs résumé */}
      <div className="grid gap-4 sm:grid-cols-3">
        {COMPTEURS.map((c) => {
          const dernier = dernierReleve(c.cle);
          return (
            <Card
              key={c.cle}
              className={`cursor-pointer transition-colors ${typeActif === c.cle ? "border-primary" : "hover:bg-accent/50"}`}
              onClick={() => setTypeActif(c.cle)}
            >
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <c.Icone className={`h-5 w-5 ${c.couleur}`} />
                  {c.nom}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {dernier ? (
                  <>
                    <p className="text-2xl font-bold">
                      {dernier.valeur.toLocaleString("fr-FR")} {c.unite}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Relevé du {dernier.date_releve}
                    </p>
                  </>
                ) : (
                  <>
                    <p className="text-2xl font-bold">— {c.unite}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Aucun relevé
                    </p>
                  </>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Consommation inter-relevés */}
      {consommations.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Gauge className="h-4 w-4" />
              Consommation entre relevés — {compteurActif.nom}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {consommations.slice(0, 6).map((c, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span>{c.date}</span>
                  <Badge variant={c.delta > 0 ? "secondary" : "destructive"}>
                    {c.delta > 0 ? "+" : ""}{c.delta.toLocaleString("fr-FR")} {compteurActif.unite}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tendances mensuelles Recharts */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Tendance mensuelle — {compteurActif.nom}
            {tendances && (
              <span className="ml-auto text-xs font-normal text-muted-foreground">
                moy. {tendances.moyenne.toLocaleString("fr-FR")} {compteurActif.unite}
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {chargementTendances ? (
            <Skeleton className="h-48 w-full" />
          ) : !tendances?.points.length ? (
            <p className="text-xs text-muted-foreground py-8 text-center">
              Ajoutez des relevés avec la consommation de la période pour voir les tendances
            </p>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={tendances.points} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis
                  dataKey="mois"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(v: string) => v.slice(5)}
                />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ fontSize: 12 }}
                  formatter={(value: number) => [`${value.toLocaleString("fr-FR")} ${compteurActif.unite}`, "Conso"]}
                  labelFormatter={(label: string) => `Mois ${label}`}
                />
                <Line
                  type="monotone"
                  dataKey="conso"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  dot={(props) => {
                    const { cx, cy, payload } = props as { cx: number; cy: number; payload: { anomalie: boolean } };
                    return (
                      <Dot
                        key={`dot-${cx}-${cy}`}
                        cx={cx}
                        cy={cy}
                        r={payload.anomalie ? 6 : 3}
                        fill={payload.anomalie ? "hsl(var(--destructive))" : "hsl(var(--primary))"}
                        stroke="none"
                      />
                    );
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
          {tendances?.points.some((p) => p.anomalie) && (
            <div className="mt-2 flex items-center gap-1.5 text-xs text-destructive">
              <AlertTriangle className="h-3 w-3" />
              Les points rouges indiquent une anomalie (écart &gt; 20 % vs la moyenne)
            </div>
          )}
        </CardContent>
      </Card>

      {/* Historique des relevés */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">
            Historique {compteurActif.nom}
          </CardTitle>
          <CardDescription className="text-xs">
            {relevesFiltres?.length ?? 0} relevés enregistrés
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-10" />)}
            </div>
          ) : !relevesFiltres?.length ? (
            <div className="py-8 text-center text-muted-foreground">
              <compteurActif.Icone className="h-8 w-8 mx-auto mb-2 opacity-30" />
              <p className="text-sm">Aucun relevé pour {compteurActif.nom.toLowerCase()}</p>
            </div>
          ) : (
            <div className="space-y-1">
              {relevesFiltres.map((r) => (
                <div key={r.id} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div>
                    <p className="text-sm font-medium">
                      {r.valeur.toLocaleString("fr-FR")} {compteurActif.unite}
                    </p>
                    <p className="text-xs text-muted-foreground">{r.date_releve}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {r.notes && (
                      <span className="text-xs text-muted-foreground max-w-32 truncate">{r.notes}</span>
                    )}
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => supprimer(r.id)} aria-label="Supprimer le relevé">
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog ajout relevé */}
      <DialogueFormulaire
        ouvert={dialogOuvert}
        onClose={() => setDialogOuvert(false)}
        titre="Nouveau relevé compteur"
        onSubmit={soumettre}
        enCours={enCreation}
      >
        <div className="space-y-3">
          <div className="space-y-1">
            <Label>Type de compteur</Label>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={form.type_compteur}
              onChange={(e) => setForm({ ...form, type_compteur: e.target.value })}
            >
              {COMPTEURS.map((c) => (
                <option key={c.cle} value={c.cle}>{c.nom} ({c.unite})</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Valeur *</Label>
              <Input type="number" step="0.01" min="0" value={form.valeur} onChange={(e) => setForm({ ...form, valeur: e.target.value })} />
            </div>
            <div className="space-y-1">
              <Label>Date *</Label>
              <Input type="date" value={form.date_releve} onChange={(e) => setForm({ ...form, date_releve: e.target.value })} />
            </div>
          </div>
          <div className="space-y-1">
            <Label>Notes</Label>
            <Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          </div>
        </div>
      </DialogueFormulaire>
    </div>
  );
}
