// ═══════════════════════════════════════════════════════════
// Courses — Bring!-style tiles par catégorie
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useMemo } from "react";
import {
  Plus,
  ShoppingCart,
  Check,
  Trash2,
  Loader2,
  ScanLine,
  Leaf,
  RotateCcw,
  CheckCircle2,
  QrCode,
  Download,
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
  validerCourses,
  obtenirSuggestionsBioLocal,
  obtenirRecurrentsSuggeres,
  obtenirPredictionsCourses,
  obtenirQrPartageListe,
} from "@/bibliotheque/api/courses";
import { schemaArticleCourses, type DonneesArticleCourses } from "@/bibliotheque/validateurs";
import { toast } from "sonner";
import type { ArticleCourses } from "@/types/courses";
import { ScanneurMultiCodes } from "@/composants/scanneur-multi-codes";
import type { ArticleBarcode } from "@/bibliotheque/api/inventaire";
import { TileArticle } from "@/composants/cuisine/tile-article";
import { CarteModeInvites } from "@/composants/cuisine/carte-mode-invites";
import { utiliserModeInvites } from "@/crochets/utiliser-mode-invites";
import { listerEvenementsFamiliaux } from "@/bibliotheque/api/famille";
import { listerEvenements } from "@/bibliotheque/api/calendriers";

/** Group articles by category for Bring!-style display */
function grouperParCategorie(articles: ArticleCourses[]): Record<string, ArticleCourses[]> {
  const groupes: Record<string, ArticleCourses[]> = {};
  for (const a of articles) {
    const cat = a.categorie || "Autre";
    (groupes[cat] ??= []).push(a);
  }
  return groupes;
}

export default function PageCourses() {
  const { contexte: modeInvites, mettreAJour: mettreAJourModeInvites, reinitialiser: reinitialiserModeInvites } = utiliserModeInvites();
  const [listeSelectionnee, setListeSelectionnee] = useState<number | null>(null);
  const [nomNouvelleListe, setNomNouvelleListe] = useState("");
  const [dialogueArticle, setDialogueArticle] = useState(false);
  const [scanneurOuvert, setScanneurOuvert] = useState(false);
  const [panneauBio, setPanneauBio] = useState(false);
  const [dialogueQr, setDialogueQr] = useState(false);
  const [qrUrl, setQrUrl] = useState<string | null>(null);
  const [chargementQr, setChargementQr] = useState(false);

  const invalider = utiliserInvalidation();
  const contexteInvitesActif = modeInvites.actif && modeInvites.nbInvites > 0;
  const evenementsModeInvites = useMemo(() => {
    const items = [...modeInvites.evenements];
    if (modeInvites.occasion.trim()) {
      items.unshift(modeInvites.occasion.trim());
    }
    return Array.from(new Set(items.filter(Boolean))).slice(0, 6);
  }, [modeInvites.evenements, modeInvites.occasion]);

  async function ouvrirQrPartage() {
    if (!listeSelectionnee) return;
    setDialogueQr(true);
    setChargementQr(true);
    try {
      const blob = await obtenirQrPartageListe(listeSelectionnee);
      const url = URL.createObjectURL(blob);
      setQrUrl((precedent) => {
        if (precedent) URL.revokeObjectURL(precedent);
        return url;
      });
    } catch {
      toast.error("Impossible de générer le QR de partage");
    } finally {
      setChargementQr(false);
    }
  }

  function telechargerQr() {
    if (!qrUrl || !detailListe) return;
    const a = document.createElement("a");
    a.href = qrUrl;
    a.download = `courses-${detailListe.nom.replace(/\s+/g, "-").toLowerCase()}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

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

  // Bio-local suggestions
  const { data: bioLocal } = utiliserRequete(
    ["courses", "bio-local", String(listeSelectionnee)],
    () => obtenirSuggestionsBioLocal(listeSelectionnee!),
    { enabled: listeSelectionnee !== null && panneauBio }
  );

  // Récurrents suggérés
  const { data: recurrents } = utiliserRequete(
    ["courses", "recurrents"],
    obtenirRecurrentsSuggeres
  );

  const { data: evenementsFamille } = utiliserRequete(
    ["famille", "evenements", "courses-invites"],
    listerEvenementsFamiliaux,
    { staleTime: 10 * 60 * 1000 }
  );

  const { data: evenementsCalendrier } = utiliserRequete(
    ["calendriers", "evenements", "courses-invites"],
    () => {
      const debut = new Date().toISOString().slice(0, 10);
      const fin = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
        .toISOString()
        .slice(0, 10);
      return listerEvenements({ date_debut: debut, date_fin: fin });
    },
    { staleTime: 10 * 60 * 1000 }
  );

  const suggestionsInvites = useMemo(() => {
    const libellesFamille = (evenementsFamille ?? []).map((item) => item.titre).filter(Boolean);
    const libellesCalendrier = (evenementsCalendrier ?? []).map((item) => item.titre).filter(Boolean);
    return Array.from(new Set([...libellesFamille, ...libellesCalendrier])).slice(0, 6);
  }, [evenementsCalendrier, evenementsFamille]);

  const { data: predictionsInvites } = utiliserRequete(
    [
      "courses",
      "predictions",
      String(modeInvites.nbInvites),
      evenementsModeInvites.join("|"),
    ],
    () =>
      obtenirPredictionsCourses({
        limite: 6,
        nbInvites: contexteInvitesActif ? modeInvites.nbInvites : 0,
        evenements: evenementsModeInvites,
      }),
    {
      enabled: contexteInvitesActif || evenementsModeInvites.length > 0,
      staleTime: 5 * 60 * 1000,
    }
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

  const { mutate: valider, isPending: enValidation } = utiliserMutation(
    () => validerCourses(listeSelectionnee!),
    {
      onSuccess: () => {
        invalider(["courses"]);
        invalider(["inventaire"]);
        toast.success("Courses validées ! Stock mis à jour.");
      },
      onError: () => toast.error("Erreur lors de la validation"),
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

  // Regrouper par catégorie
  const groupesNonCoches = useMemo(() => grouperParCategorie(articlesNonCoches), [articlesNonCoches]);
  const categoriesTriees = useMemo(() => Object.keys(groupesNonCoches).sort(), [groupesNonCoches]);

  // Scanner callback
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
      toast.warning(`${inconnus.length} code(s) non reconnu(s)`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🛒 Courses</h1>
          <p className="text-muted-foreground">Gérez vos listes de courses</p>
        </div>
        {listeSelectionnee && (
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={ouvrirQrPartage}>
              <QrCode className="mr-1 h-4 w-4" />
              QR partage
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPanneauBio((v) => !v)}
            >
              <Leaf className="mr-1 h-4 w-4" />
              Bio & Local
            </Button>
            <Button
              size="sm"
              onClick={() => valider(undefined)}
              disabled={enValidation || articlesNonCoches.length > 0}
            >
              {enValidation ? (
                <Loader2 className="mr-1 h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle2 className="mr-1 h-4 w-4" />
              )}
              Valider courses
            </Button>
          </div>
        )}
      </div>

      <CarteModeInvites
        contexte={modeInvites}
        onChange={mettreAJourModeInvites}
        onReset={reinitialiserModeInvites}
        suggestionsEvenements={suggestionsInvites}
        description="Le contexte invité alimente les suggestions d'achats et les quantités recommandées pour la liste active."
      />

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Panel listes */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Mes listes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
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

            {/* Récurrents suggérés */}
            {recurrents && recurrents.suggestions.length > 0 && listeSelectionnee && (
              <div className="border-t pt-3 mt-3">
                <p className="text-xs font-medium text-muted-foreground mb-2 flex items-center gap-1">
                  <RotateCcw className="h-3 w-3" />
                  Achats récurrents
                </p>
                <div className="space-y-1">
                  {recurrents.suggestions.slice(0, 5).map((r) => (
                    <button
                      key={r.article_nom}
                      className="w-full text-left text-xs rounded px-2 py-1 hover:bg-accent transition-colors"
                      onClick={() =>
                        ajouter({ nom: r.article_nom, categorie: r.categorie ?? undefined })
                      }
                    >
                      <span className="font-medium">{r.article_nom}</span>
                      <span className="text-muted-foreground ml-1">
                        +{r.retard_jours}j retard
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Panel articles — Bring!-style tiles */}
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
            <div className="flex gap-1">
              {listeSelectionnee && (
                <>
                  <Button size="sm" variant="outline" onClick={() => setScanneurOuvert(true)}>
                    <ScanLine className="mr-1 h-4 w-4" />
                    Scanner
                  </Button>
                  <Button size="sm" onClick={() => setDialogueArticle(true)}>
                    <Plus className="mr-1 h-4 w-4" />
                    Article
                  </Button>
                </>
              )}
            </div>
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
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                {Array.from({ length: 10 }).map((_, i) => (
                  <Skeleton key={i} className="aspect-square rounded-xl" />
                ))}
              </div>
            ) : articles.length === 0 ? (
              <div className="flex flex-col items-center gap-4 py-12">
                <p className="text-muted-foreground">Liste vide</p>
                <Button variant="outline" onClick={() => setDialogueArticle(true)}>
                  <Plus className="mr-1 h-4 w-4" />
                  Ajouter un article
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Articles par catégorie */}
                {categoriesTriees.map((cat) => (
                  <div key={cat}>
                    <h3 className="text-sm font-semibold mb-2">{cat}</h3>
                    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
                      {groupesNonCoches[cat].map((a) => (
                        <TileArticle
                          key={a.id}
                          nom={a.nom}
                          quantite={a.quantite}
                          unite={a.unite}
                          categorie={a.categorie}
                          onClick={() => cocher({ articleId: a.id, coche: true })}
                          onLongPress={() => supprimer(a.id)}
                        />
                      ))}
                    </div>
                  </div>
                ))}

                {/* Articles cochés */}
                {articlesCoches.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-muted-foreground mb-2">
                      Complétés ({articlesCoches.length})
                    </h3>
                    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
                      {articlesCoches.map((a) => (
                        <TileArticle
                          key={a.id}
                          nom={a.nom}
                          quantite={a.quantite}
                          unite={a.unite}
                          categorie={a.categorie}
                          estCoche
                          onClick={() => cocher({ articleId: a.id, coche: false })}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Panel Bio & Local */}
      {panneauBio && bioLocal && bioLocal.suggestions.length > 0 && (
        <Card className="border-green-300 bg-green-50 dark:border-green-800 dark:bg-green-950">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2 text-green-700 dark:text-green-300">
              <Leaf className="h-4 w-4" />
              Suggestions Bio & Local — {bioLocal.mois}
            </CardTitle>
            <CardDescription className="text-green-600 dark:text-green-400">
              {bioLocal.nb_en_saison} article(s) de saison dans votre liste
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 sm:grid-cols-2">
              {bioLocal.suggestions.map((s) => (
                <div
                  key={s.article_id}
                  className="flex items-center justify-between rounded-lg border border-green-200 dark:border-green-800 px-3 py-2 text-sm"

            {listeSelectionnee && predictionsInvites && predictionsInvites.items.length > 0 && (
              <div className="border-t pt-3 mt-3">
                <p className="text-xs font-medium text-muted-foreground mb-2">
                  Suggestions invites
                </p>
                <div className="space-y-2">
                  {predictionsInvites.items.slice(0, 5).map((prediction) => (
                    <button
                      key={`${prediction.article_nom}-${prediction.quantite_suggeree}`}
                      className="w-full rounded-md border px-2 py-2 text-left hover:bg-accent transition-colors"
                      onClick={() =>
                        ajouter({
                          nom: prediction.article_nom,
                          quantite: prediction.quantite_suggeree,
                          unite: prediction.unite_suggeree,
                          categorie:
                            prediction.categorie ?? prediction.rayon_magasin ?? undefined,
                        })
                      }
                    >
                      <div className="flex items-center justify-between gap-2 text-xs">
                        <span className="font-medium text-foreground">
                          {prediction.article_nom}
                        </span>
                        <span className="text-muted-foreground">
                          x{prediction.quantite_suggeree} {prediction.unite_suggeree}
                        </span>
                      </div>
                      <p className="mt-1 text-[11px] text-muted-foreground">
                        Confiance {Math.round(prediction.confiance_contextualisee * 100)}%
                        {prediction.contexte_applique.raisons.length > 0 && (
                          <span>
                            {" "}· {prediction.contexte_applique.raisons.join(", ")}
                          </span>
                        )}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            )}
                >
                  <div>
                    <span className="font-medium">{s.nom}</span>
                    <div className="flex gap-1 mt-0.5">
                      {s.en_saison && <Badge variant="secondary" className="text-[10px]">🌱 Saison</Badge>}
                      {s.bio_disponible && <Badge variant="secondary" className="text-[10px]">🌿 Bio</Badge>}
                      {s.local_disponible && <Badge variant="secondary" className="text-[10px]">📍 Local</Badge>}
                    </div>
                  </div>
                  {s.alternative_bio && (
                    <span className="text-xs text-muted-foreground">→ {s.alternative_bio}</span>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

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

      <ScanneurMultiCodes
        ouvert={scanneurOuvert}
        onFermer={() => setScanneurOuvert(false)}
        onImporter={importerDepuisScanner}
        labelImporter="Ajouter à la liste"
      />

      <Dialog
        open={dialogueQr}
        onOpenChange={(ouvert) => {
          setDialogueQr(ouvert);
          if (!ouvert) {
            setQrUrl((precedent) => {
              if (precedent) URL.revokeObjectURL(precedent);
              return null;
            });
          }
        }}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>QR de partage</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Scannez ce QR pour ouvrir la version texte de votre liste de courses.
            </p>
            <div className="flex justify-center rounded-lg border p-4 min-h-48 items-center">
              {chargementQr ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : qrUrl ? (
                <img src={qrUrl} alt="QR liste de courses" className="h-52 w-52" />
              ) : (
                <p className="text-sm text-muted-foreground">QR indisponible</p>
              )}
            </div>
            <div className="flex justify-end">
              <Button variant="outline" onClick={telechargerQr} disabled={!qrUrl}>
                <Download className="mr-1 h-4 w-4" />
                Télécharger
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
