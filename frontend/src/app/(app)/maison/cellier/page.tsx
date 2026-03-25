// ═══════════════════════════════════════════════════════════
// Cellier — Cave et garde-manger
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Wine, AlertTriangle, Filter, Plus, Clock, Pencil, Trash2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { toast } from "sonner";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerArticlesCellier,
  creerArticleCellier,
  modifierArticleCellier,
  supprimerArticleCellier,
  alertesPeremptionCellier,
  statsCellier,
} from "@/bibliotheque/api/maison";
import type { ArticleCellier } from "@/types/maison";

export default function PageCellier() {
  const [categorie, setCategorie] = useState<string | undefined>();
  const formsVide = { nom: "", categorie: "", quantite: "1", unite: "", emplacement: "", date_peremption: "", prix_unitaire: "" };
  const [form, setForm] = useState(formsVide);
  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<ArticleCellier>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (a) => setForm({ nom: a.nom, categorie: a.categorie ?? "", quantite: String(a.quantite), unite: a.unite ?? "", emplacement: a.emplacement ?? "", date_peremption: a.date_peremption ?? "", prix_unitaire: a.prix_unitaire ? String(a.prix_unitaire) : "" }),
    });
  const queryClient = useQueryClient();

  const { data: articles, isLoading } = utiliserRequete(
    ["maison", "cellier", categorie ?? "all"],
    () => listerArticlesCellier(categorie)
  );

  const { data: alertes } = utiliserRequete(
    ["maison", "cellier", "alertes-peremption"],
    () => alertesPeremptionCellier(14)
  );

  const { data: stats } = utiliserRequete(
    ["maison", "cellier", "stats"],
    () => statsCellier()
  );

  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "cellier"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) => creerArticleCellier(data as Omit<ArticleCellier, "id">),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Article ajouté"); } }
  );

  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<ArticleCellier> }) => modifierArticleCellier(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Article modifié"); } }
  );

  const { mutate: supprimer } = utiliserMutation(supprimerArticleCellier, {
    onSuccess: () => { invalider(); toast.success("Article supprimé"); },
  });



  const soumettre = () => {
    const payload = {
      nom: form.nom,
      categorie: form.categorie || undefined,
      quantite: Number(form.quantite),
      unite: form.unite || undefined,
      emplacement: form.emplacement || undefined,
      date_peremption: form.date_peremption || undefined,
      prix_unitaire: form.prix_unitaire ? Number(form.prix_unitaire) : undefined,
    };
    if (enEdition) {
      modifier({ id: enEdition.id, data: payload });
    } else {
      creer(payload);
    }
  };

  const categories = articles
    ? [...new Set(articles.map((a) => a.categorie).filter(Boolean))]
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🍷 Cellier</h1>
          <p className="text-muted-foreground">
            Cave et garde-manger — {stats?.total_articles ?? 0} articles
          </p>
        </div>
        <Button size="sm" onClick={ouvrirCreation}>
          <Plus className="mr-2 h-4 w-4" />
          Ajouter
        </Button>
      </div>

      {/* Stats rapides */}
      {stats && (
        <div className="grid gap-3 sm:grid-cols-3">
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{stats.total_articles}</p>
              <p className="text-xs text-muted-foreground">Articles</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">
                {stats.valeur_totale.toFixed(0)} €
              </p>
              <p className="text-xs text-muted-foreground">Valeur estimée</p>
            </CardContent>
          </Card>
          <Card className={stats.articles_bientot_perimes > 0 ? "border-amber-500/30" : ""}>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{stats.articles_bientot_perimes}</p>
              <p className="text-xs text-muted-foreground">Péremption proche</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Alertes péremption */}
      {alertes && alertes.length > 0 && (
        <Card className="border-amber-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Clock className="h-4 w-4 text-amber-500" />
              Péremption proche
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {alertes.slice(0, 5).map((a) => (
                <div key={a.id} className="flex justify-between text-sm">
                  <span>{a.nom}</span>
                  <Badge variant={a.jours_restants <= 3 ? "destructive" : "secondary"}>
                    {a.jours_restants}j
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filtres catégorie */}
      {categories.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          <Button
            variant={!categorie ? "default" : "outline"}
            size="sm"
            onClick={() => setCategorie(undefined)}
          >
            Tous
          </Button>
          {categories.map((cat) => (
            <Button
              key={cat}
              variant={categorie === cat ? "default" : "outline"}
              size="sm"
              onClick={() => setCategorie(cat as string)}
            >
              {cat}
            </Button>
          ))}
        </div>
      )}

      {/* Liste articles */}
      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : !articles?.length ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            <Wine className="h-8 w-8 mx-auto mb-2 opacity-50" />
            Aucun article dans le cellier
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {articles.map((article) => (
            <Card key={article.id}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">{article.nom}</CardTitle>
                  <div className="flex items-center gap-1">
                    {article.categorie && (
                      <Badge variant="outline" className="text-xs">
                        {article.categorie}
                      </Badge>
                    )}
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(article)}>
                      <Pencil className="h-3 w-3" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => supprimer(article.id)}>
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">
                  {article.quantite}
                  <span className="text-sm font-normal text-muted-foreground ml-1">
                    {article.unite ?? "unités"}
                  </span>
                </p>
                {article.emplacement && (
                  <p className="text-xs text-muted-foreground mt-1">
                    📍 {article.emplacement}
                  </p>
                )}
                {article.date_peremption && (
                  <p className="text-xs text-muted-foreground mt-1">
                    ⏳ Expire le {new Date(article.date_peremption).toLocaleDateString("fr-FR")}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Dialog CRUD */}
      <DialogueFormulaire
        ouvert={dialogOuvert}
        onClose={fermerDialog}
        titre={enEdition ? "Modifier l'article" : "Nouvel article"}
        onSubmit={soumettre}
        enCours={enCreation || enModif}
        texteBouton={enEdition ? "Modifier" : "Ajouter"}
      >
        <div className="space-y-2">
          <Label htmlFor="nom">Nom</Label>
          <Input id="nom" value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })} required />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="categorie">Catégorie</Label>
            <Input id="categorie" value={form.categorie} onChange={(e) => setForm({ ...form, categorie: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="emplacement">Emplacement</Label>
            <Input id="emplacement" value={form.emplacement} onChange={(e) => setForm({ ...form, emplacement: e.target.value })} />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-2">
            <Label htmlFor="quantite">Quantité</Label>
            <Input id="quantite" type="number" value={form.quantite} onChange={(e) => setForm({ ...form, quantite: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="unite">Unité</Label>
            <Input id="unite" value={form.unite} onChange={(e) => setForm({ ...form, unite: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="prix">Prix unit.</Label>
            <Input id="prix" type="number" step="0.01" value={form.prix_unitaire} onChange={(e) => setForm({ ...form, prix_unitaire: e.target.value })} />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="peremption">Date péremption</Label>
          <Input id="peremption" type="date" value={form.date_peremption} onChange={(e) => setForm({ ...form, date_peremption: e.target.value })} />
        </div>
      </DialogueFormulaire>
    </div>
  );
}
