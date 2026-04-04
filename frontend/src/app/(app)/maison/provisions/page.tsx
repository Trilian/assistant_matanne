// ═══════════════════════════════════════════════════════════
// Provisions — Stocks · Cellier (fusionnés en tabs)
// Page provisions maison
// ═══════════════════════════════════════════════════════════

"use client";

import { Suspense, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Package, Wine, Plus, Trash2, Pencil, AlertTriangle,
} from "lucide-react";
import {
  Card, CardContent, CardHeader, CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { Switch } from "@/composants/ui/switch";
import { Label } from "@/composants/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerStocks, creerStock, modifierStock, supprimerStock,
  listerArticlesCellier, creerArticleCellier, modifierArticleCellier, supprimerArticleCellier,
  alertesPeremptionCellier, statsCellier,
} from "@/bibliotheque/api/maison";
import type { ArticleCellier, StockMaison } from "@/types/maison";
import { toast } from "sonner";
import { BandeauIA } from "@/composants/maison/bandeau-ia";
import { BoutonAchat } from "@/composants/bouton-achat";

// ─── Onglet Stocks ────────────────────────────────────────────
function OngletStocks() {
  const [alerteUniquement, setAlerteUniquement] = useState(false);
  const queryClient = useQueryClient();
  const formsVide = { nom: "", categorie: "", quantite: "", seuil_alerte: "", emplacement: "", unite: "" };
  const [form, setForm] = useState(formsVide);

  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<StockMaison>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (s) => setForm({
        nom: s.nom,
        categorie: s.categorie ?? "",
        quantite: String(s.quantite ?? ""),
        seuil_alerte: s.seuil_alerte != null ? String(s.seuil_alerte) : "",
        emplacement: s.emplacement ?? "",
        unite: s.unite ?? "",
      }),
    });

  const { data: stocks, isLoading } = utiliserRequete(
    ["maison", "stocks", String(alerteUniquement)],
    () => listerStocks(undefined, alerteUniquement)
  );
  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "stocks"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Parameters<typeof creerStock>[0]) => creerStock(data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Stock créé"); } }
  );
  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<StockMaison> }) => modifierStock(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Stock modifié"); } }
  );
  const { mutate: supprimer } = utiliserMutation(supprimerStock, { onSuccess: () => { invalider(); toast.success("Stock supprimé"); } });

  const soumettre = () => {
    const payload: Parameters<typeof creerStock>[0] = {
      nom: form.nom,
      categorie: form.categorie || undefined,
      quantite: form.quantite ? Number(form.quantite) : 0,
      seuil_alerte: form.seuil_alerte ? Number(form.seuil_alerte) : undefined,
      emplacement: form.emplacement || undefined,
      unite: form.unite || undefined,
    };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload);
  };

  const champs = [
    { id: "nom", label: "Produit", type: "text" as const, value: form.nom, onChange: (v: string) => setForm(f => ({ ...f, nom: v })), required: true },
    { id: "categorie", label: "Catégorie", type: "text" as const, value: form.categorie, onChange: (v: string) => setForm(f => ({ ...f, categorie: v })) },
    { id: "quantite", label: "Quantité", type: "number" as const, value: form.quantite, onChange: (v: string) => setForm(f => ({ ...f, quantite: v })) },
    { id: "seuil_alerte", label: "Seuil d'alerte", type: "number" as const, value: form.seuil_alerte, onChange: (v: string) => setForm(f => ({ ...f, seuil_alerte: v })) },
    { id: "emplacement", label: "Emplacement", type: "text" as const, value: form.emplacement, onChange: (v: string) => setForm(f => ({ ...f, emplacement: v })) },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Label htmlFor="alerte-toggle" className="text-sm">Alertes seulement</Label>
          <Switch id="alerte-toggle" checked={alerteUniquement} onCheckedChange={setAlerteUniquement} />
        </div>
        <Button size="sm" onClick={ouvrirCreation}><Plus className="mr-1.5 h-4 w-4" />Ajouter</Button>
      </div>

      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1,2,3].map(i => <Skeleton key={i} className="h-24" />)}</div>
      ) : !stocks?.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground">
          <Package className="h-8 w-8 mx-auto mb-2 opacity-50" />
          {alerteUniquement ? "Aucune alerte stock" : "Aucun stock enregistré"}
        </CardContent></Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {stocks.map((s: StockMaison) => {
            const enAlerte = s.seuil_alerte != null && s.quantite <= s.seuil_alerte;
            return (
              <Card key={s.id} className={enAlerte ? "border-amber-300" : ""}>
                <CardHeader className="pb-1">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-sm">{s.nom}</CardTitle>
                    <div className="flex items-center gap-1">
                      {enAlerte && <BoutonAchat article={{ nom: s.nom }} taille="xs" />}
                      <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => ouvrirEdition(s)}><Pencil className="h-3 w-3" /></Button>
                      <Button variant="ghost" size="icon" className="h-6 w-6 hover:text-destructive" onClick={() => supprimer(s.id)}><Trash2 className="h-3 w-3" /></Button>
                    </div>
                  </div>
                  <div className="flex gap-1.5 flex-wrap">
                    {s.categorie && <Badge variant="secondary" className="text-xs">{s.categorie}</Badge>}
                    {s.emplacement && <Badge variant="outline" className="text-xs">{s.emplacement}</Badge>}
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-sm">
                    <span className={`font-semibold ${enAlerte ? "text-amber-600" : ""}`}>{s.quantite}</span>
                    {s.seuil_alerte != null && <span className="text-xs text-muted-foreground"> / seuil {s.seuil_alerte}</span>}
                  </p>
                  {enAlerte && <p className="text-xs text-amber-600 flex items-center gap-1 mt-1"><AlertTriangle className="h-3 w-3" />À réapprovisionner</p>}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <DialogueFormulaire
        ouvert={dialogOuvert}
        onChangerOuvert={setDialogOuvert}
        titre={enEdition ? "Modifier le stock" : "Nouveau stock"}
        champs={champs}
        onSoumettre={soumettre}
        enChargement={enCreation || enModif}
      />
    </div>
  );
}

// ─── Onglet Cellier ───────────────────────────────────────────
function OngletCellier() {
  const formsVide = { nom: "", categorie: "", quantite: "", date_achat: "", date_peremption: "", emplacement: "", prix_unitaire: "", notes: "" };
  const [form, setForm] = useState(formsVide);
  const queryClient = useQueryClient();

  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<ArticleCellier>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (a) => setForm({
        nom: a.nom, categorie: a.categorie ?? "", quantite: String(a.quantite ?? 1),
        date_achat: a.date_achat ?? "", date_peremption: a.date_peremption ?? "",
        emplacement: a.emplacement ?? "", prix_unitaire: a.prix_unitaire != null ? String(a.prix_unitaire) : "",
        notes: a.notes ?? "",
      }),
    });

  const { data: articles, isLoading } = utiliserRequete(["maison", "cellier", "articles"], () => listerArticlesCellier());
  const { data: alertes } = utiliserRequete(["maison", "cellier", "alertes"], () => alertesPeremptionCellier(14));
  const { data: stats } = utiliserRequete(["maison", "cellier", "stats"], statsCellier);
  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "cellier"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Parameters<typeof creerArticleCellier>[0]) => creerArticleCellier(data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Article créé"); } }
  );
  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<ArticleCellier> }) => modifierArticleCellier(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Article modifié"); } }
  );
  const { mutate: supprimer } = utiliserMutation(supprimerArticleCellier, { onSuccess: () => { invalider(); toast.success("Article supprimé"); } });

  const soumettre = () => {
    const payload: Parameters<typeof creerArticleCellier>[0] = { nom: form.nom, categorie: form.categorie || undefined, quantite: form.quantite ? Number(form.quantite) : undefined, date_achat: form.date_achat || undefined, date_peremption: form.date_peremption || undefined, emplacement: form.emplacement || undefined, prix_unitaire: form.prix_unitaire ? Number(form.prix_unitaire) : undefined, notes: form.notes || undefined };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload);
  };

  const champs = [
    { id: "nom", label: "Nom", type: "text" as const, value: form.nom, onChange: (v: string) => setForm(f => ({ ...f, nom: v })), required: true },
    { id: "categorie", label: "Catégorie", type: "text" as const, value: form.categorie, onChange: (v: string) => setForm(f => ({ ...f, categorie: v })) },
    { id: "quantite", label: "Quantité", type: "number" as const, value: form.quantite, onChange: (v: string) => setForm(f => ({ ...f, quantite: v })) },
    { id: "date_peremption", label: "Date de péremption", type: "date" as const, value: form.date_peremption, onChange: (v: string) => setForm(f => ({ ...f, date_peremption: v })) },
    { id: "emplacement", label: "Emplacement", type: "text" as const, value: form.emplacement, onChange: (v: string) => setForm(f => ({ ...f, emplacement: v })) },
  ];

  return (
    <div className="space-y-4">
      {stats && (
        <div className="grid grid-cols-3 gap-3">
          <Card><CardContent className="py-3 text-center"><p className="text-xl font-bold">{stats.total_articles ?? 0}</p><p className="text-xs text-muted-foreground">Articles</p></CardContent></Card>
          <Card><CardContent className="py-3 text-center"><p className="text-xl font-bold text-amber-600">{stats.articles_perimes_bientot ?? 0}</p><p className="text-xs text-muted-foreground">Expirent bientôt</p></CardContent></Card>
          <Card><CardContent className="py-3 text-center"><p className="text-xl font-bold">{(stats.valeur_totale ?? 0).toFixed(0)} €</p><p className="text-xs text-muted-foreground">Valeur</p></CardContent></Card>
        </div>
      )}

      {/* Alertes péremption */}
      {(alertes?.length ?? 0) > 0 && (
        <Card className="border-amber-300">
          <CardContent className="py-3">
            <p className="text-sm font-medium text-amber-700 mb-2 flex items-center gap-1.5"><AlertTriangle className="h-4 w-4" />{alertes!.length} article(s) à consommer vite</p>
            {alertes!.slice(0, 3).map((a: { id: number; nom: string; date_peremption?: string }) => (
              <p key={a.id} className="text-xs text-muted-foreground">• {a.nom}{a.date_peremption ? ` (exp. ${new Date(a.date_peremption).toLocaleDateString("fr-FR")})` : ""}</p>
            ))}
          </CardContent>
        </Card>
      )}

      <div className="flex justify-end">
        <Button size="sm" onClick={ouvrirCreation}><Plus className="mr-2 h-4 w-4" />Ajouter au cellier</Button>
      </div>

      {isLoading ? (
        <div className="space-y-2">{[1,2,3].map(i => <Skeleton key={i} className="h-14" />)}</div>
      ) : !articles?.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><Wine className="h-8 w-8 mx-auto mb-2 opacity-50" />Cellier vide</CardContent></Card>
      ) : (
        <div className="space-y-2">
          {articles.map((a: ArticleCellier) => {
            const bientotPerime = a.date_peremption && new Date(a.date_peremption) < new Date(Date.now() + 14 * 86400000);
            return (
              <Card key={a.id} className={bientotPerime ? "border-amber-200" : ""}>
                <CardContent className="py-2.5 flex items-center gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{a.nom}</p>
                    <p className="text-xs text-muted-foreground">
                      {a.categorie ?? ""}{a.quantite != null ? ` · qté ${a.quantite}` : ""}
                      {a.date_peremption ? ` · exp. ${new Date(a.date_peremption).toLocaleDateString("fr-FR")}` : ""}
                    </p>
                  </div>
                  <BoutonAchat article={{ nom: a.nom }} />
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(a)}><Pencil className="h-3.5 w-3.5" /></Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive" onClick={() => supprimer(a.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <DialogueFormulaire
        ouvert={dialogOuvert}
        onChangerOuvert={setDialogOuvert}
        titre={enEdition ? "Modifier l'article" : "Ajouter au cellier"}
        champs={champs}
        onSoumettre={soumettre}
        enChargement={enCreation || enModif}
      />
    </div>
  );
}

// ─── Page principale ──────────────────────────────────────────
function ContenuProvisions() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = searchParams.get("tab") ?? "stocks";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📦 Provisions</h1>
        <p className="text-muted-foreground">Stocks de la maison et cellier</p>
      </div>

      <BandeauIA section="provisions" />

      <Tabs value={tab} onValueChange={(val) => router.replace(`?tab=${val}`)}>
        <TabsList>
          <TabsTrigger value="stocks"><Package className="h-4 w-4 mr-1.5" />Stocks</TabsTrigger>
          <TabsTrigger value="cellier"><Wine className="h-4 w-4 mr-1.5" />Cellier</TabsTrigger>
        </TabsList>
        <TabsContent value="stocks" className="mt-4"><OngletStocks /></TabsContent>
        <TabsContent value="cellier" className="mt-4"><OngletCellier /></TabsContent>
      </Tabs>
    </div>
  );
}

export default function PageProvisions() {
  return (
    <Suspense fallback={<div className="space-y-4"><Skeleton className="h-8 w-40" /><Skeleton className="h-10 w-48" /><Skeleton className="h-64" /></div>}>
      <ContenuProvisions />
    </Suspense>
  );
}
