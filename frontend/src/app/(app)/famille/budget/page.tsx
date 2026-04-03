// ═══════════════════════════════════════════════════════════
// Budget Famille — Dépenses et statistiques
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import {
  Wallet,
  TrendingUp,
  Filter,
  Plus,
  Trash2,
  ScanLine,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/composants/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import dynamic from "next/dynamic";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import {
  listerDepenses,
  obtenirStatsBudget,
  ajouterDepense,
  supprimerDepense,
  obtenirPredictionsBudget,
} from "@/bibliotheque/api/famille";
import { toast } from "sonner";
import { BudgetInsightsIA } from "@/composants/famille/budget-insights";
import { TreemapBudget } from "@/composants/graphiques/treemap-budget";
import { SankeyFluxFinanciers } from "@/composants/graphiques/sankey-flux-financiers";
import { UploadTicket } from "@/composants/famille/upload-ticket";
import { GraphiqueBudgetVsReel } from "@/composants/graphiques/graphique-budget-vs-reel";
import { lancerConfettis } from "@/bibliotheque/confettis";

const CamembertBudget = dynamic(
  () => import("@/composants/graphiques/camembert-budget").then((m) => m.CamembertBudget),
  { ssr: false }
);

const CATEGORIES_BUDGET = [
  "tous",
  "alimentation",
  "logement",
  "transport",
  "loisirs",
  "sante",
  "education",
  "vetements",
  "autre",
];

export default function PageBudget() {
  const [categorieFiltre, setCategorieFiltre] = useState("tous");
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [dialogScanner, setDialogScanner] = useState(false);
  const [montant, setMontant] = useState("");
  const [categorie, setCategorie] = useState("alimentation");
  const [description, setDescription] = useState("");
  const [magasin, setMagasin] = useState("");

  const queryClient = useQueryClient();

  const mutationAjouter = utiliserMutation(
    (data: { montant: number; categorie: string; description: string; magasin?: string }) =>
      ajouterDepense({
        libelle: data.description,
        montant: data.montant,
        categorie: data.categorie,
        date: new Date().toISOString().slice(0, 10),
        notes: data.magasin ? `Magasin: ${data.magasin}` : undefined,
      }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["famille", "budget"] });
        setDialogOuvert(false);
        setMontant("");
        setCategorie("alimentation");
        setDescription("");
        setMagasin("");
        toast.success("Dépense ajoutée");
      },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const mutationSupprimer = utiliserMutation(
    (id: number) => supprimerDepense(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["famille", "budget"] });
        toast.success("Dépense supprimée");
      },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  const { data: stats, isLoading: chargementStats } = utiliserRequete(
    ["famille", "budget", "stats"],
    obtenirStatsBudget
  );

  const { data: depenses, isLoading: chargementDepenses } = utiliserRequete(
    ["famille", "budget", "depenses", categorieFiltre],
    () =>
      listerDepenses(
        categorieFiltre !== "tous" ? categorieFiltre : undefined
      )
  );

  const { data: predictionBudget } = utiliserRequete(
    ["famille", "budget", "predictions"],
    obtenirPredictionsBudget,
    { staleTime: 5 * 60 * 1000 }
  );

  const totalMois = stats?.total_mois ?? 0;
  const parCategorie = stats?.par_categorie ?? {};
  const categoriesTriees = Object.entries(parCategorie).sort(
    ([, a], [, b]) => b - a
  );
  const donneesTreemap = categoriesTriees.map(([nom, montant]) => ({
    nom,
    montant,
    sous_categories: depenses
      ?.filter((depense) => depense.categorie === nom)
      .sort((a, b) => b.montant - a.montant)
      .slice(0, 4)
      .map((depense) => ({ nom: depense.libelle, montant: depense.montant })) ?? [],
  }));
  const donneesSankey = categoriesTriees.slice(0, 5).map(([nom, montant]) => ({
    nom,
    montant,
    details: depenses
      ?.filter((depense) => depense.categorie === nom)
      .sort((a, b) => b.montant - a.montant)
      .slice(0, 3)
      .map((depense) => ({ nom: depense.libelle, montant: depense.montant })) ?? [],
  }));

  const donneesBudgetVsReel = useMemo(() => {
    const previsions = predictionBudget?.predictions?.par_categorie ?? [];
    if (!previsions.length || !categoriesTriees.length) return [];

    const reelParCategorie = new Map(categoriesTriees);

    return previsions
      .map((prevision) => ({
        categorie: prevision.categorie,
        prevu: prevision.montant_prevu,
        reel: reelParCategorie.get(prevision.categorie) ?? 0,
      }))
      .sort((a, b) => b.prevu - a.prevu)
      .slice(0, 6);
  }, [predictionBudget?.predictions?.par_categorie, categoriesTriees]);

  const celebrationEffectuee = useRef(false);
  useEffect(() => {
    const totalPrevu = predictionBudget?.predictions?.total_prevu ?? 0;
    if (celebrationEffectuee.current || totalMois <= 0 || totalPrevu <= 0) return;

    // Celebration quand le reel reste sous la projection IA du mois.
    if (totalMois <= totalPrevu) {
      lancerConfettis({ particules: 22 });
      celebrationEffectuee.current = true;
    }
  }, [predictionBudget?.predictions?.total_prevu, totalMois]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">💰 Budget</h1>
          <p className="text-muted-foreground">
            Suivi des dépenses familiales
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/famille/achats">
            <Button variant="outline" size="sm">Voir achats</Button>
          </Link>
          <Link href="/famille/activites">
            <Button variant="outline" size="sm">Voir activités</Button>
          </Link>
          <Button variant="outline" size="sm" onClick={() => setDialogScanner(true)}>
            <ScanLine className="h-4 w-4 mr-1" />
            Scanner ticket
          </Button>
        </div>
      </div>

      <UploadTicket
        ouvert={dialogScanner}
        onFermer={() => setDialogScanner(false)}
        onCreerDepense={(dep) => {
          mutationAjouter.mutate(dep);
        }}
      />

      {/* Résumé mensuel */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Wallet className="h-8 w-8 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Total du mois</p>
                {chargementStats ? (
                  <Skeleton className="h-8 w-24" />
                ) : (
                  <p className="text-2xl font-bold">
                    {totalMois.toFixed(2)} €
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="sm:col-span-1 lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Répartition par catégorie
            </CardTitle>
          </CardHeader>
          <CardContent>
            {chargementStats ? (
              <Skeleton className="h-16 w-full" />
            ) : categoriesTriees.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Aucune donnée ce mois
              </p>
            ) : (
              <CamembertBudget
                donnees={categoriesTriees.map(([nom, montant]) => ({ nom, montant }))}
              />
            )}
          </CardContent>
        </Card>
      </div>

      {!!categoriesTriees.length && (
        <div className="grid gap-4 xl:grid-cols-2">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Treemap budget</CardTitle>
              <p className="text-sm text-muted-foreground">
                Vision surfacique des catégories et de leurs postes principaux.
              </p>
            </CardHeader>
            <CardContent>
              <TreemapBudget donnees={donneesTreemap} hauteur={320} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Flux financiers</CardTitle>
              <p className="text-sm text-muted-foreground">
                Répartition du budget mensuel depuis le total vers les catégories puis les plus gros postes.
              </p>
            </CardHeader>
            <CardContent>
              <SankeyFluxFinanciers donnees={donneesSankey} />
            </CardContent>
          </Card>
        </div>
      )}

      {!!donneesBudgetVsReel.length && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Budget prevu vs reel</CardTitle>
            <p className="text-sm text-muted-foreground">
              Comparaison par categorie entre projection IA et depenses reelles du mois.
            </p>
          </CardHeader>
          <CardContent>
            <GraphiqueBudgetVsReel donnees={donneesBudgetVsReel} hauteur={320} />
          </CardContent>
        </Card>
      )}

      {/* Liste dépenses */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Dépenses</h2>
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <Select value={categorieFiltre} onValueChange={setCategorieFiltre}>
              <SelectTrigger className="w-[160px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES_BUDGET.map((c) => (
                  <SelectItem key={c} value={c}>
                    {c === "tous"
                      ? "Toutes"
                      : c.charAt(0).toUpperCase() + c.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-1" /> Ajouter
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Nouvelle dépense</DialogTitle>
                </DialogHeader>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (!montant || !description) return;
                    mutationAjouter.mutate({
                      montant: parseFloat(montant),
                      categorie,
                      description,
                      magasin: magasin || undefined,
                    });
                  }}
                  className="space-y-4"
                >
                  <div>
                    <Label>Montant (€)</Label>
                    <Input
                      type="number"
                      step="0.01"
                      value={montant}
                      onChange={(e) => setMontant(e.target.value)}
                      required
                    />
                  </div>
                  <div>
                    <Label>Catégorie</Label>
                    <Select value={categorie} onValueChange={setCategorie}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {CATEGORIES_BUDGET.filter((c) => c !== "tous").map(
                          (c) => (
                            <SelectItem key={c} value={c}>
                              {c.charAt(0).toUpperCase() + c.slice(1)}
                            </SelectItem>
                          )
                        )}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Description</Label>
                    <Input
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      required
                    />
                  </div>
                  <div>
                    <Label>Magasin (optionnel)</Label>
                    <Input
                      value={magasin}
                      onChange={(e) => setMagasin(e.target.value)}
                    />
                  </div>
                  <Button type="submit" className="w-full" disabled={mutationAjouter.isPending}>
                    {mutationAjouter.isPending ? "Ajout…" : "Ajouter la dépense"}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {chargementDepenses ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-14 w-full" />
            ))}
          </div>
        ) : !depenses?.length ? (
          <Card>
            <CardContent className="py-8 text-center text-sm text-muted-foreground">
              Aucune dépense trouvée
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="p-0">
              <div className="divide-y">
                {depenses.map((d) => (
                  <div
                    key={d.id}
                    className="flex items-center justify-between px-4 py-3 hover:bg-accent/50 transition-colors"
                  >
                    <div>
                      <p className="text-sm font-medium">{d.libelle}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <Badge
                          variant="outline"
                          className="text-xs capitalize"
                        >
                          {d.categorie}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {new Date(d.date).toLocaleDateString("fr-FR")}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold tabular-nums">
                        {d.montant.toFixed(2)} €
                      </span>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-destructive"
                        onClick={() => mutationSupprimer.mutate(d.id)}
                        aria-label="Supprimer la dépense"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Insights IA */}
      <BudgetInsightsIA />
    </div>
  );
}
