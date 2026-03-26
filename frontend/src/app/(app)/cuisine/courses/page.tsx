// ═══════════════════════════════════════════════════════════
// Courses — Gestion des listes de courses
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Plus,
  ShoppingCart,
  Check,
  Trash2,
  Loader2,
  ScanLine,
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
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  listerListesCourses,
  obtenirListeCourses,
  creerListeCourses,
  ajouterArticle,
  cocherArticle,
  supprimerArticle,
} from "@/bibliotheque/api/courses";
import { schemaArticleCourses, type DonneesArticleCourses } from "@/bibliotheque/validateurs";
import { toast } from "sonner";
import type { ListeCourses } from "@/types/courses";
import { SwipeableItem } from "@/composants/swipeable-item";
import { ScanneurMultiCodes } from "@/composants/scanneur-multi-codes";
import type { ArticleBarcode } from "@/bibliotheque/api/inventaire";

export default function PageCourses() {
  const [listeSelectionnee, setListeSelectionnee] = useState<number | null>(null);
  const [nomNouvelleListe, setNomNouvelleListe] = useState("");
  const [dialogueArticle, setDialogueArticle] = useState(false);
  const [scanneurOuvert, setScanneurOuvert] = useState(false);

  const invalider = utiliserInvalidation();

  // Listes
  const { data: listes, isLoading: chargementListes } = utiliserRequete(
    ["courses"],
    listerListesCourses
  );

  // Détail liste sélectionnée
  const { data: detailListe, isLoading: chargementDetail } = utiliserRequete(
    ["courses", String(listeSelectionnee)],
    () => obtenirListeCourses(listeSelectionnee!),
    { enabled: listeSelectionnee !== null }
  );

  // Mutations
  const { mutate: creerListe, isPending: enCreationListe } = utiliserMutation(
    (nom: string) => creerListeCourses(nom),
    {
      onSuccess: (liste) => {
        invalider(["courses"]);
        setListeSelectionnee(liste.id);
        setNomNouvelleListe("");
        toast.success("Liste créée");
      },
      onError: () => toast.error("Erreur lors de la création"),
    }
  );

  const { mutate: ajouter, isPending: enAjout } = utiliserMutation(
    (donnees: DonneesArticleCourses) =>
      ajouterArticle(listeSelectionnee!, donnees),
    {
      onSuccess: () => {
        invalider(["courses"]);
        setDialogueArticle(false);
        resetArticle();
        toast.success("Article ajouté");
      },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const { mutate: cocher } = utiliserMutation(
    ({ articleId, coche }: { articleId: number; coche: boolean }) =>
      cocherArticle(listeSelectionnee!, articleId, coche),
    {
      onSuccess: () => invalider(["courses"]),
      onError: () => toast.error("Erreur lors de la mise à jour"),
    }
  );

  const { mutate: supprimer } = utiliserMutation(
    (articleId: number) => supprimerArticle(listeSelectionnee!, articleId),
    {
      onSuccess: () => { invalider(["courses"]); toast.success("Article supprimé"); },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  // Formulaire article
  const {
    register: regArticle,
    handleSubmit: submitArticle,
    reset: resetArticle,
    formState: { errors: erreursArticle },
  } = useForm<DonneesArticleCourses>({
    resolver: zodResolver(schemaArticleCourses) as never,
  });

  const articles = detailListe?.articles ?? [];
  const articlesNonCoches = articles.filter((a) => !a.est_coche);
  const articlesCoches = articles.filter((a) => a.est_coche);

  // Callback scanner : coche les articles trouvés dans la liste courante
  const importerDepuisScanner = async (
    trouves: ArticleBarcode[],
    inconnus: string[]
  ) => {
    if (!listeSelectionnee) return;
    let importes = 0;
    for (const t of trouves) {
      const nom = t.article.nom;
      if (!nom) continue;
      await ajouterArticle(listeSelectionnee, {
        nom,
        quantite: 1,
        categorie: t.article.categorie ?? undefined,
      }).catch(() => null);
      importes++;
    }
    if (importes > 0) {
      invalider(["courses"]);
      toast.success(`${importes} article(s) ajouté(s) à la liste`);
    }
    if (inconnus.length > 0) {
      toast.warning(`${inconnus.length} code(s) non reconnu(s) dans l'inventaire`);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🛒 Courses</h1>
        <p className="text-muted-foreground">Gérez vos listes de courses</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Panel listes */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Mes listes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Créer une nouvelle liste */}
            <form
              className="flex gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                if (nomNouvelleListe.trim()) creerListe(nomNouvelleListe.trim());
              }}
            >
              <Input
                placeholder="Nouvelle liste..."
                value={nomNouvelleListe}
                onChange={(e) => setNomNouvelleListe(e.target.value)}
              />
              <Button
                type="submit"
                size="icon"
                disabled={enCreationListe || !nomNouvelleListe.trim()}
                aria-label="Créer la liste"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </form>

            {/* Liste des listes */}
            {chargementListes ? (
              <div className="space-y-2">
                {Array.from({ length: 3 }).map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : !listes?.length ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                Aucune liste de courses
              </p>
            ) : (
              <div className="space-y-1">
                {listes.map((l) => (
                  <button
                    key={l.id}
                    onClick={() => setListeSelectionnee(l.id)}
                    className={`w-full text-left rounded-md px-3 py-2 text-sm transition-colors hover:bg-accent ${
                      listeSelectionnee === l.id ? "bg-accent" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium truncate">{l.nom}</span>
                      <Badge variant="secondary" className="text-xs">
                        {l.nombre_coche}/{l.nombre_articles}
                      </Badge>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Panel articles */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg">
                {detailListe?.nom ?? "Sélectionner une liste"}
              </CardTitle>
              {detailListe && (
                <CardDescription>
                  {articlesNonCoches.length} restant(s) sur{" "}
                  {articles.length} article(s)
                </CardDescription>
              )}
            </div>
            {listeSelectionnee && (
              <Button size="sm" onClick={() => setDialogueArticle(true)}>
                <Plus className="mr-1 h-4 w-4" />
                Article
              </Button>
            )}
            {listeSelectionnee && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => setScanneurOuvert(true)}
                aria-label="Scanner plusieurs codes-barres"
              >
                <ScanLine className="mr-1 h-4 w-4" />
                Scanner
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {!listeSelectionnee ? (
              <div className="flex flex-col items-center gap-4 py-12 text-center">
                <ShoppingCart className="h-12 w-12 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Sélectionnez ou créez une liste pour commencer
                </p>
              </div>
            ) : chargementDetail ? (
              <div className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : articles.length === 0 ? (
              <div className="flex flex-col items-center gap-4 py-12">
                <p className="text-muted-foreground">Liste vide</p>
                <Button
                  variant="outline"
                  onClick={() => setDialogueArticle(true)}
                >
                  <Plus className="mr-1 h-4 w-4" />
                  Ajouter un article
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Articles non cochés */}
                {articlesNonCoches.length > 0 && (
                  <div className="space-y-1">
                    {articlesNonCoches.map((a) => (
                      <SwipeableItem
                        key={a.id}
                        onSwipeRight={() => cocher({ articleId: a.id, coche: true })}
                        onSwipeLeft={() => supprimer(a.id)}
                        labelDroit="Cocher"
                        labelGauche="Supprimer"
                        iconeDroit={<Check className="h-4 w-4" />}
                        iconeGauche={<Trash2 className="h-4 w-4" />}
                      >
                        <div className="flex items-center gap-3 rounded-md px-2 py-1.5 bg-background">
                          <Button
                            variant="outline"
                            size="icon"
                            className="h-6 w-6 shrink-0 rounded-full"
                            onClick={() =>
                              cocher({ articleId: a.id, coche: true })
                            }
                          >
                            <span className="sr-only">Cocher</span>
                          </Button>
                          <div className="flex-1 min-w-0">
                            <span className="text-sm font-medium">
                              {a.nom}
                            </span>
                            {(a.quantite || a.categorie) && (
                              <span className="text-xs text-muted-foreground ml-2">
                                {a.quantite
                                  ? `${a.quantite}${a.unite ? " " + a.unite : ""}`
                                  : ""}
                                {a.categorie ? ` · ${a.categorie}` : ""}
                              </span>
                            )}
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 shrink-0"
                            onClick={() => supprimer(a.id)}
                            aria-label="Supprimer l'article"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </SwipeableItem>
                    ))}
                  </div>
                )}

                {/* Articles cochés */}
                {articlesCoches.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-muted-foreground mb-2">
                      Complétés ({articlesCoches.length})
                    </p>
                    <div className="space-y-1 opacity-60">
                      {articlesCoches.map((a) => (
                        <div
                          key={a.id}
                          className="flex items-center gap-3 rounded-md px-2 py-1.5"
                        >
                          <Button
                            variant="outline"
                            size="icon"
                            className="h-6 w-6 shrink-0 rounded-full bg-primary text-primary-foreground"
                            onClick={() =>
                              cocher({ articleId: a.id, coche: false })
                            }
                          >
                            <Check className="h-3 w-3" />
                          </Button>
                          <span className="text-sm line-through">{a.nom}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Dialogue ajout article */}
      <Dialog open={dialogueArticle} onOpenChange={setDialogueArticle}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ajouter un article</DialogTitle>
          </DialogHeader>
          <form
            onSubmit={submitArticle((data) => ajouter(data))}
            className="space-y-4"
          >
            <div className="space-y-2">
              <Label htmlFor="nom-article">Nom *</Label>
              <Input
                id="nom-article"
                {...regArticle("nom")}
                placeholder="Ex: Tomates"
              />
              {erreursArticle.nom && (
                <p className="text-sm text-destructive">
                  {erreursArticle.nom.message}
                </p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="qte-article">Quantité</Label>
                <Input
                  id="qte-article"
                  type="number"
                  min={0}
                  step="any"
                  {...regArticle("quantite")}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="unite-article">Unité</Label>
                <Input
                  id="unite-article"
                  {...regArticle("unite")}
                  placeholder="kg, L, pièces..."
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="cat-article">Catégorie</Label>
              <Input
                id="cat-article"
                {...regArticle("categorie")}
                placeholder="Fruits, Légumes, Viande..."
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogueArticle(false)}
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

      {/* Scanner multi-codes */}
      <ScanneurMultiCodes
        ouvert={scanneurOuvert}
        onFermer={() => setScanneurOuvert(false)}
        onImporter={importerDepuisScanner}
        labelImporter="Ajouter à la liste"
      />
    </div>
  );
}
