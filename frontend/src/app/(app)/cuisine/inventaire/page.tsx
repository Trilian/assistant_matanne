// ═══════════════════════════════════════════════════════════
// Inventaire — Stock alimentaire et alertes
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Plus,
  Package,
  AlertTriangle,
  Trash2,
  Loader2,
  Search,
} from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  listerInventaire,
  ajouterArticleInventaire,
  supprimerArticleInventaire,
  obtenirAlertes,
} from "@/bibliotheque/api/inventaire";
import {
  schemaArticleInventaire,
  type DonneesArticleInventaire,
} from "@/bibliotheque/validateurs";
import { toast } from "sonner";
import type { ArticleInventaire } from "@/types/inventaire";

const CATEGORIES = [
  "Tous",
  "Fruits",
  "Légumes",
  "Viande",
  "Poisson",
  "Laitier",
  "Épicerie",
  "Surgelés",
  "Boissons",
  "Autre",
];

const FILTRES_ETAT = [
  { valeur: "tous", label: "Tous" },
  { valeur: "bas", label: "Stock bas" },
  { valeur: "expire", label: "Périmés" },
  { valeur: "ok", label: "OK" },
];

export default function PageInventaire() {
  const [recherche, setRecherche] = useState("");
  const [categorie, setCategorie] = useState("Tous");
  const [filtreEtat, setFiltreEtat] = useState("tous");
  const [dialogueAjout, setDialogueAjout] = useState(false);

  const invalider = utiliserInvalidation();

  const { data: articles, isLoading } = utiliserRequete(
    ["inventaire"],
    listerInventaire
  );

  const { data: alertes } = utiliserRequete(
    ["inventaire", "alertes"],
    obtenirAlertes
  );

  const { mutate: ajouter, isPending: enAjout } = utiliserMutation(
    (dto: DonneesArticleInventaire) => ajouterArticleInventaire(dto),
    {
      onSuccess: () => {
        invalider(["inventaire"]);
        setDialogueAjout(false);
        reset();
        toast.success("Article ajouté à l'inventaire");
      },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const { mutate: supprimer } = utiliserMutation(
    (id: number) => supprimerArticleInventaire(id),
    {
      onSuccess: () => { invalider(["inventaire"]); toast.success("Article supprimé"); },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<DonneesArticleInventaire>({
    resolver: zodResolver(schemaArticleInventaire) as never,
  });

  // Filtrage
  const articlesFiltres = (articles ?? []).filter((a) => {
    if (recherche && !a.nom.toLowerCase().includes(recherche.toLowerCase()))
      return false;
    if (categorie !== "Tous" && a.categorie !== categorie) return false;
    if (filtreEtat === "bas" && !a.est_bas) return false;
    if (filtreEtat === "expire" && !a.est_expire) return false;
    if (filtreEtat === "ok" && (a.est_bas || a.est_expire)) return false;
    return true;
  });

  const nbAlertes = alertes?.length ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📦 Inventaire</h1>
          <p className="text-muted-foreground">Stock alimentaire et alertes</p>
        </div>
        <Button onClick={() => setDialogueAjout(true)}>
          <Plus className="mr-1 h-4 w-4" />
          Ajouter
        </Button>
      </div>

      {/* Alertes résumé */}
      {nbAlertes > 0 && (
        <Card className="border-orange-300 bg-orange-50 dark:border-orange-800 dark:bg-orange-950">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2 text-orange-700 dark:text-orange-300">
              <AlertTriangle className="h-4 w-4" />
              {nbAlertes} alerte{nbAlertes > 1 ? "s" : ""}
            </CardTitle>
            <CardDescription className="text-orange-600 dark:text-orange-400">
              Articles en stock bas ou bientôt périmés
            </CardDescription>
          </CardHeader>
        </Card>
      )}

      {/* Filtres */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher..."
            className="pl-9"
            value={recherche}
            onChange={(e) => setRecherche(e.target.value)}
          />
        </div>
        <Select value={categorie} onValueChange={setCategorie}>
          <SelectTrigger className="w-[160px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {CATEGORIES.map((c) => (
              <SelectItem key={c} value={c}>
                {c}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={filtreEtat} onValueChange={setFiltreEtat}>
          <SelectTrigger className="w-[140px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {FILTRES_ETAT.map((f) => (
              <SelectItem key={f.valeur} value={f.valeur}>
                {f.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Table articles */}
      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : articlesFiltres.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <Package className="h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">Aucun article trouvé</p>
            <Button variant="outline" onClick={() => setDialogueAjout(true)}>
              <Plus className="mr-1 h-4 w-4" />
              Ajouter un article
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3 font-medium">Article</th>
                    <th className="text-left p-3 font-medium">Quantité</th>
                    <th className="text-left p-3 font-medium hidden sm:table-cell">
                      Catégorie
                    </th>
                    <th className="text-left p-3 font-medium hidden md:table-cell">
                      Emplacement
                    </th>
                    <th className="text-left p-3 font-medium hidden md:table-cell">
                      Péremption
                    </th>
                    <th className="text-left p-3 font-medium">État</th>
                    <th className="p-3" />
                  </tr>
                </thead>
                <tbody>
                  {articlesFiltres.map((a) => (
                    <tr key={a.id} className="border-b last:border-0 hover:bg-accent/50">
                      <td className="p-3 font-medium">{a.nom}</td>
                      <td className="p-3">
                        {a.quantite}
                        {a.unite ? ` ${a.unite}` : ""}
                      </td>
                      <td className="p-3 hidden sm:table-cell">
                        {a.categorie ?? "—"}
                      </td>
                      <td className="p-3 hidden md:table-cell">
                        {a.emplacement ?? "—"}
                      </td>
                      <td className="p-3 hidden md:table-cell">
                        {a.date_peremption
                          ? new Date(a.date_peremption).toLocaleDateString("fr-FR")
                          : "—"}
                      </td>
                      <td className="p-3">
                        <EtatBadge article={a} />
                      </td>
                      <td className="p-3">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => supprimer(a.id)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Dialogue ajout */}
      <Dialog open={dialogueAjout} onOpenChange={setDialogueAjout}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ajouter un article</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit((d) => ajouter(d))} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="inv-nom">Nom *</Label>
              <Input id="inv-nom" {...register("nom")} placeholder="Ex: Lait" />
              {errors.nom && (
                <p className="text-sm text-destructive">{errors.nom.message}</p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="inv-qte">Quantité *</Label>
                <Input
                  id="inv-qte"
                  type="number"
                  min={0}
                  step="any"
                  {...register("quantite")}
                />
                {errors.quantite && (
                  <p className="text-sm text-destructive">
                    {errors.quantite.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="inv-unite">Unité</Label>
                <Input id="inv-unite" {...register("unite")} placeholder="L, kg..." />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="inv-cat">Catégorie</Label>
                <Input id="inv-cat" {...register("categorie")} placeholder="Laitier..." />
              </div>
              <div className="space-y-2">
                <Label htmlFor="inv-empl">Emplacement</Label>
                <Input
                  id="inv-empl"
                  {...register("emplacement")}
                  placeholder="Frigo, placard..."
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="inv-peremption">Date de péremption</Label>
                <Input id="inv-peremption" type="date" {...register("date_peremption")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="inv-seuil">Seuil d&apos;alerte</Label>
                <Input
                  id="inv-seuil"
                  type="number"
                  min={0}
                  step="any"
                  {...register("seuil_alerte")}
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogueAjout(false)}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={enAjout}>
                {enAjout && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Ajouter
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function EtatBadge({ article }: { article: ArticleInventaire }) {
  if (article.est_expire)
    return (
      <Badge variant="destructive" className="text-xs">
        Périmé
      </Badge>
    );
  if (article.est_bas)
    return (
      <Badge className="text-xs bg-orange-500 hover:bg-orange-600">
        Stock bas
      </Badge>
    );
  return (
    <Badge variant="secondary" className="text-xs">
      OK
    </Badge>
  );
}
