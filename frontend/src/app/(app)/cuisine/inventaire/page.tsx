// ═══════════════════════════════════════════════════════════
// Inventaire — Stock alimentaire avec onglets emplacement
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
  Camera,
  ScanLine,
  QrCode,
  Refrigerator,
  Archive,
  Warehouse,
  DoorOpen,
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
import { EtatVide } from "@/composants/ui/etat-vide";
import { ZoneTableauResponsive } from "@/composants/ui/zone-tableau-responsive";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  listerInventaire,
  ajouterArticleInventaire,
  modifierArticleInventaire,
  supprimerArticleInventaire,
  obtenirAlertes,
  detecterPhotoFrigoSansImport,
  ajouterArticlesBulk,
  enrichirParCodeBarres,
  type ResultatOCRFrigo,
  type ArticleBulk,
} from "@/bibliotheque/api/inventaire";
import {
  schemaArticleInventaire,
  type DonneesArticleInventaire,
} from "@/bibliotheque/validateurs-cuisine";
import { toast } from "sonner";
import type { ArticleInventaire } from "@/types/inventaire";
import { ScanneurMultiCodes } from "@/composants/scanneur-multi-codes";
import type { ArticleBarcode } from "@/bibliotheque/api/inventaire";
import { EtiquetteQR } from "@/composants/cuisine/etiquette-qr";
import type { LucideIcon } from "lucide-react";
import { utiliserSuppressionAnnulable } from "@/crochets/utiliser-suppression-annulable";
import { TreemapInventaire } from "@/composants/graphiques/treemap-inventaire";
import { construireDonneesTreemapInventaire } from "@/bibliotheque/inventaire-treemap";
import { predireConsommationInventaire } from "@/bibliotheque/api/ia-modules";

const EMPLACEMENTS: { id: string; label: string; icone: LucideIcon }[] = [
  { id: "Frigo", label: "Frigo", icone: Refrigerator },
  { id: "Congélateur Tiroir", label: "Congél. Tiroir", icone: Archive },
  { id: "Congélateur Coffre", label: "Congél. Coffre", icone: Archive },
  { id: "Cellier", label: "Cellier", icone: Warehouse },
  { id: "Placard", label: "Placard", icone: DoorOpen },
];

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
  const [ongletActif, setOngletActif] = useState("Frigo");
  const [recherche, setRecherche] = useState("");
  const [categorie, setCategorie] = useState("Tous");
  const [filtreEtat, setFiltreEtat] = useState("tous");
  const [dialogueAjout, setDialogueAjout] = useState(false);
  const [ocrResultat, setOcrResultat] = useState<ResultatOCRFrigo | null>(null);
  const [ocrSelectionnes, setOcrSelectionnes] = useState<Set<number>>(new Set());
  const [scanneurOuvert, setScanneurOuvert] = useState(false);
  const [qrArticle, setQrArticle] = useState<ArticleInventaire | null>(null);

  const invalider = utiliserInvalidation();
  const { planifierSuppression } = utiliserSuppressionAnnulable();

  const { data: articles, isLoading } = utiliserRequete(
    ["inventaire", ongletActif],
    () => listerInventaire(ongletActif)
  );

  const { data: alertes } = utiliserRequete(
    ["inventaire", "alertes"],
    obtenirAlertes
  );

  const articlePrediction = (articles ?? []).find(
    (article) =>
      (article.quantite ?? 0) > 0 &&
      (article.est_bas || article.est_expire)
  );

  const { data: predictionStock } = utiliserRequete(
    ["inventaire", "prediction-stock", String(articlePrediction?.id ?? "none")],
    () =>
      predireConsommationInventaire({
        ingredient_nom: articlePrediction?.nom ?? "",
        stock_actuel_kg: Number(articlePrediction?.quantite ?? 0),
        historique_achat_mensuel: [],
      }),
    {
      enabled: Boolean(articlePrediction?.id),
      staleTime: 10 * 60 * 1000,
    }
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
      onSuccess: () => { invalider(["inventaire"]); },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );
  const supprimerAvecUndo = (article: ArticleInventaire) => {
    planifierSuppression(`inventaire-${article.id}`, {
      libelle: article.nom,
      onConfirmer: () => supprimer(article.id),
      onErreur: () => toast.error("Erreur lors de la suppression"),
    });
  };


  const { mutate: lancerOCR, isPending: ocrEnCours } = utiliserMutation(
    (fichier: File) => detecterPhotoFrigoSansImport(fichier),
    {
      onSuccess: (res) => {
        if (res.total > 0) {
          setOcrResultat(res);
          // Par défaut, tout est sélectionné
          setOcrSelectionnes(new Set(res.articles.map((_, i) => i)));
          toast.success(`📷 ${res.total} aliment(s) détecté(s) — sélectionnez ceux à importer`);
        } else {
          toast.info("Aucun aliment détecté dans la photo");
        }
      },
      onError: () => toast.error("Erreur lors de l'analyse photo"),
    }
  );

  const { mutate: importerSelectionnes, isPending: importEnCours } = utiliserMutation(
    (articles: ArticleBulk[]) => ajouterArticlesBulk(articles, ongletActif),
    {
      onSuccess: (res) => {
        invalider(["inventaire"]);
        setOcrResultat(null);
        setOcrSelectionnes(new Set());
        toast.success(`✅ ${res.message}`);
      },
      onError: () => toast.error("Erreur lors de l'import des articles"),
    }
  );

  function importerArticlesSelectionnes() {
    if (!ocrResultat) return;
    const articlesAImporter = ocrResultat.articles.filter((_, i) => ocrSelectionnes.has(i));
    if (articlesAImporter.length === 0) {
      toast.warning("Sélectionnez au moins un article");
      return;
    }
    importerSelectionnes(articlesAImporter);
  }

  function basculerSelectionOCR(index: number) {
    setOcrSelectionnes((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  }

  function toutSelectionner() {
    if (!ocrResultat) return;
    if (ocrSelectionnes.size === ocrResultat.articles.length) {
      setOcrSelectionnes(new Set());
    } else {
      setOcrSelectionnes(new Set(ocrResultat.articles.map((_, i) => i)));
    }
  }

  async function importerStockDepuisScanner(
    trouves: ArticleBarcode[],
    inconnus: string[]
  ) {
    let misAJour = 0;
    let enrichis = 0;
    for (const t of trouves) {
      try {
        await modifierArticleInventaire(t.article.id, {
          quantite: (t.article.quantite ?? 0) + 1,
        });
        misAJour++;
        // Auto-enrichissement OpenFoodFacts (nutriscore, ecoscore)
        if (t.article.code_barres) {
          try {
            const res = await enrichirParCodeBarres(t.article.code_barres);
            if (res.enrichi) enrichis++;
          } catch {
            // Enrichissement optionnel — ne pas bloquer
          }
        }
      } catch {
        // Ignore individual failures
      }
    }
    if (misAJour > 0) {
      invalider(["inventaire"]);
      const msg = enrichis > 0
        ? `${misAJour} article(s) mis à jour, ${enrichis} enrichi(s) via OFF`
        : `${misAJour} article(s) mis à jour`;
      toast.success(msg);
    }
    if (inconnus.length > 0) {
      toast.info(`${inconnus.length} code(s) non reconnu(s)`);
    }
  }

  function ouvrirSelecteurPhoto() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/jpeg,image/png,image/webp";
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) lancerOCR(file);
    };
    input.click();
  }

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
  const donneesTreemap = construireDonneesTreemapInventaire(articles ?? []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📦 Inventaire</h1>
          <p className="text-muted-foreground">Stock alimentaire et alertes</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setScanneurOuvert(true)}
            aria-label="Scanner plusieurs codes-barres"
          >
            <ScanLine className="mr-1 h-4 w-4" />
            Scanner
          </Button>
          <Button variant="outline" onClick={ouvrirSelecteurPhoto} disabled={ocrEnCours}>
            {ocrEnCours ? (
              <Loader2 className="mr-1 h-4 w-4 animate-spin" />
            ) : (
              <Camera className="mr-1 h-4 w-4" />
            )}
            Photo frigo
          </Button>
          <Button onClick={() => setDialogueAjout(true)}>
            <Plus className="mr-1 h-4 w-4" />
            Ajouter
          </Button>
        </div>
      </div>

      {/* Résultat OCR photo-frigo */}
      {ocrResultat && ocrResultat.total > 0 && (
        <Card className="border-emerald-300 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950">
          <CardContent className="pt-4 space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <p className="font-semibold text-emerald-700 dark:text-emerald-300 flex items-center gap-2">
                  <Camera className="h-4 w-4" />
                  Photo analysée — {ocrResultat.total} aliment(s) détecté(s)
                </p>
                <p className="text-sm text-emerald-600 dark:text-emerald-400 mt-1">
                  Sélectionnez les articles à ajouter à l&apos;inventaire
                </p>
              </div>
              <Button size="sm" variant="ghost" onClick={() => { setOcrResultat(null); setOcrSelectionnes(new Set()); }} aria-label="Fermer">×</Button>
            </div>
            <div className="space-y-1">
              <Button
                size="sm"
                variant="ghost"
                className="text-xs h-7 px-2"
                onClick={toutSelectionner}
              >
                {ocrSelectionnes.size === ocrResultat.articles.length ? "Tout désélectionner" : "Tout sélectionner"}
              </Button>
              <div className="grid grid-cols-2 gap-1 sm:grid-cols-3">
                {ocrResultat.articles.map((article, i) => (
                  <label key={i} className="flex items-center gap-2 rounded-md border bg-background/70 px-2 py-1.5 cursor-pointer hover:bg-accent/50">
                    <input
                      type="checkbox"
                      checked={ocrSelectionnes.has(i)}
                      onChange={() => basculerSelectionOCR(i)}
                      className="rounded"
                    />
                    <span className="text-xs truncate">{article.nom}</span>
                    {article.quantite && (
                      <span className="text-xs text-muted-foreground ml-auto">×{article.quantite}</span>
                    )}
                  </label>
                ))}
              </div>
            </div>
            <div className="flex items-center justify-between pt-1">
              <p className="text-xs text-muted-foreground">{ocrSelectionnes.size} article(s) sélectionné(s)</p>
              <Button
                size="sm"
                onClick={importerArticlesSelectionnes}
                disabled={importEnCours || ocrSelectionnes.size === 0}
              >
                {importEnCours ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : null}
                Tout ajouter à l&apos;inventaire
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

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

      {articlePrediction && predictionStock && (
        <Card className="border-amber-300/60 bg-amber-50/60 dark:border-amber-900/40 dark:bg-amber-950/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              Prévision IA de réapprovisionnement
            </CardTitle>
            <CardDescription>
              Anticipation pour l&apos;article le plus exposé dans l&apos;emplacement actif.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-3">
            <div>
              <p className="text-sm font-medium">{predictionStock.ingredient_nom}</p>
              <p className="text-xs text-muted-foreground">Stock actuel: {predictionStock.stock_actuel_kg}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Autonomie estimée</p>
              <p className="text-xs text-muted-foreground">{predictionStock.jours_autonomie} jour(s)</p>
              <p className="text-xs text-muted-foreground">Seuil conseillé: {predictionStock.seuil_reapprovisionnement_kg}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Explication</p>
              <p className="text-xs text-muted-foreground">{predictionStock.raison}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {!!donneesTreemap.length && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Treemap inventaire</CardTitle>
            <CardDescription>
              Vue surfacique des categories et principaux articles pour l&apos;emplacement actif.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TreemapInventaire donnees={donneesTreemap} hauteur={300} />
          </CardContent>
        </Card>
      )}

      {/* Onglets par emplacement */}
      <Tabs value={ongletActif} onValueChange={setOngletActif}>
        <TabsList className="w-full grid grid-cols-5">
          {EMPLACEMENTS.map((e) => {
            const Icone = e.icone;
            const nb = (articles ?? []).length;
            return (
              <TabsTrigger key={e.id} value={e.id} className="gap-1 text-xs sm:text-sm">
                <Icone className="h-4 w-4 hidden sm:inline" />
                {e.label}
                {ongletActif === e.id && nb > 0 && (
                  <Badge variant="secondary" className="ml-1 text-[10px] px-1.5 py-0">
                    {nb}
                  </Badge>
                )}
              </TabsTrigger>
            );
          })}
        </TabsList>

        {EMPLACEMENTS.map((e) => (
          <TabsContent key={e.id} value={e.id} className="space-y-4 mt-4">
            {/* Filtres */}
            <div className="flex flex-wrap gap-3">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Rechercher..."
                  className="pl-9"
                  value={recherche}
                  onChange={(ev) => setRecherche(ev.target.value)}
                />
              </div>
              <Select value={categorie} onValueChange={setCategorie}>
                <SelectTrigger className="w-[160px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIES.map((c) => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={filtreEtat} onValueChange={setFiltreEtat}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {FILTRES_ETAT.map((f) => (
                    <SelectItem key={f.valeur} value={f.valeur}>{f.label}</SelectItem>
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
                <CardContent className="py-6">
                  <EtatVide
                    Icone={Package}
                    titre={`Aucun article dans ${e.label}`}
                    description="Ajoute un premier produit pour suivre ton stock et les alertes de péremption."
                    action={
                      <Button variant="outline" onClick={() => setDialogueAjout(true)}>
                        <Plus className="mr-1 h-4 w-4" />
                        Ajouter un article
                      </Button>
                    }
                    className="border-0 bg-muted/20 py-6"
                  />
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="p-0">
                  <ZoneTableauResponsive className="p-3 pb-0" containerClassName="overflow-auto">
                    <table className="w-full min-w-[720px] text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-3 font-medium">Article</th>
                          <th className="text-left p-3 font-medium">Quantité</th>
                          <th className="text-left p-3 font-medium hidden sm:table-cell">Catégorie</th>
                          <th className="text-left p-3 font-medium hidden md:table-cell">Péremption</th>
                          <th className="text-left p-3 font-medium">État</th>
                          <th className="text-left p-3 font-medium hidden lg:table-cell">Qualité</th>
                          <th className="p-3" />
                        </tr>
                      </thead>
                      <tbody>
                        {articlesFiltres.map((a) => (
                          <tr key={a.id} className="border-b last:border-0 hover:bg-accent/50">
                            <td className="p-3 font-medium">{a.nom}</td>
                            <td className="p-3">
                              {a.quantite}{a.unite ? ` ${a.unite}` : ""}
                            </td>
                            <td className="p-3 hidden sm:table-cell">{a.categorie ?? "—"}</td>
                            <td className="p-3 hidden md:table-cell">
                              {a.date_peremption
                                ? new Date(a.date_peremption).toLocaleDateString("fr-FR")
                                : "—"}
                            </td>
                            <td className="p-3"><EtatBadge article={a} /></td>
                            <td className="p-3 hidden lg:table-cell"><BadgesOFF article={a} /></td>
                            <td className="p-3">
                              <div className="flex items-center gap-1">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-7 w-7"
                                  onClick={() => setQrArticle(a)}
                                  aria-label="QR Code"
                                >
                                  <QrCode className="h-3.5 w-3.5" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-7 w-7"
                                  onClick={() => supprimerAvecUndo(a)}
                                  aria-label="Supprimer l'article"
                                >
                                  <Trash2 className="h-3.5 w-3.5" />
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </ZoneTableauResponsive>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        ))}
      </Tabs>

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
                <Select
                  defaultValue={ongletActif}
                  onValueChange={(v) => {
                    // react-hook-form manual setValue
                    const ev = { target: { name: "emplacement", value: v } };
                    register("emplacement").onChange(ev as never);
                  }}
                >
                  <SelectTrigger id="inv-empl">
                    <SelectValue placeholder="Choisir..." />
                  </SelectTrigger>
                  <SelectContent>
                    {EMPLACEMENTS.map((em) => (
                      <SelectItem key={em.id} value={em.id}>{em.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
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

      {/* Étiquette QR */}
      {qrArticle && (
        <EtiquetteQR
          ouvert
          onFermer={() => setQrArticle(null)}
          articleId={qrArticle.id}
          articleNom={qrArticle.nom}
          emplacement={qrArticle.emplacement}
          datePeremption={qrArticle.date_peremption}
        />
      )}

      <ScanneurMultiCodes
        ouvert={scanneurOuvert}
        onFermer={() => setScanneurOuvert(false)}
        onImporter={importerStockDepuisScanner}
        labelImporter="Mettre à jour stock"
      />
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

const NUTRISCORE_COLORS: Record<string, string> = {
  a: "bg-green-500",
  b: "bg-lime-500",
  c: "bg-yellow-400",
  d: "bg-orange-500",
  e: "bg-red-500",
};

const NOVA_COLORS: Record<number, string> = {
  1: "bg-green-500",
  2: "bg-lime-500",
  3: "bg-yellow-400",
  4: "bg-red-500",
};

// Produits de saison par mois (source: data/reference/produits_de_saison.json)
const PRODUITS_SAISON: Record<number, string[]> = {
  1: ["endive","mâche","céleri","poireau","topinambour","chou","betterave","carotte","navet","panais","pomme","poire","kiwi","clémentine","orange"],
  2: ["endive","mâche","céleri","poireau","chou","carotte","navet","panais","pomme","poire","kiwi","orange"],
  3: ["épinard","radis","asperge","ail","oignon","carotte","chou","pomme","poire","kiwi"],
  4: ["asperge","épinard","radis","oseille","chou","carotte","pomme","fraise"],
  5: ["asperge","artichaut","fève","petit pois","épinard","radis","fraise","cerise","rhubarbe"],
  6: ["artichaut","courgette","concombre","tomate","haricot vert","petit pois","fraise","cerise","abricot","melon","framboise"],
  7: ["courgette","tomate","poivron","aubergine","concombre","haricot vert","abricot","melon","pêche","nectarine","fraise","cerise","framboise","myrtille"],
  8: ["courgette","tomate","poivron","aubergine","haricot vert","melon","pêche","nectarine","figue","mirabelle","prune","framboise","myrtille","mûre"],
  9: ["poivron","tomate","courgette","aubergine","champignon","potiron","courge","pêche","poire","pomme","raisin","figue","prune","mûre"],
  10: ["potiron","courge","champignon","chou","betterave","carotte","poireau","pomme","poire","raisin","châtaigne"],
  11: ["potiron","chou","poireau","carotte","céleri","betterave","endive","pomme","poire","kiwi","châtaigne","clémentine"],
  12: ["endive","chou","poireau","carotte","céleri","navet","topinambour","pomme","poire","kiwi","clémentine","orange"],
};

function estProduitSaisonnier(nom: string): boolean {
  const mois = new Date().getMonth() + 1;
  const produits = PRODUITS_SAISON[mois] ?? [];
  const nomLower = nom.toLowerCase();
  return produits.some((p) => nomLower.includes(p));
}

function BadgesOFF({ article }: { article: ArticleInventaire }) {
  const badges: React.ReactNode[] = [];

  if (estProduitSaisonnier(article.nom)) {
    badges.push(
      <span
        key="saison"
        title="Produit de saison"
        className="inline-flex items-center rounded px-1.5 py-0.5 text-xs font-bold text-white bg-green-600"
      >
        🌱
      </span>
    );
  }

  if (article.nutriscore) {
    const grade = article.nutriscore.toLowerCase();
    const color = NUTRISCORE_COLORS[grade] ?? "bg-gray-400";
    badges.push(
      <span
        key="nutri"
        title={`Nutri-Score ${grade.toUpperCase()}`}
        className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs font-bold text-white ${color}`}
      >
        N-{grade.toUpperCase()}
      </span>
    );
  }

  if (article.ecoscore) {
    const grade = article.ecoscore.toLowerCase();
    const color = NUTRISCORE_COLORS[grade] ?? "bg-gray-400";
    badges.push(
      <span
        key="eco"
        title={`Éco-Score ${grade.toUpperCase()}`}
        className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs font-bold text-white ${color}`}
      >
        E-{grade.toUpperCase()}
      </span>
    );
  }

  if (article.nova_group) {
    const color = NOVA_COLORS[article.nova_group] ?? "bg-gray-400";
    badges.push(
      <span
        key="nova"
        title={`Groupe NOVA ${article.nova_group} (${article.nova_group === 1 ? "non transformé" : article.nova_group === 4 ? "ultra-transformé" : "transformé"})`}
        className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs font-bold text-white ${color}`}
      >
        G{article.nova_group}
      </span>
    );
  }

  if (badges.length === 0) return <span className="text-xs text-muted-foreground">—</span>;
  return <div className="flex flex-wrap gap-1">{badges}</div>;
}
