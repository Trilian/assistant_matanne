// ═══════════════════════════════════════════════════════════
// Courses — Bring!-style tiles par catégorie
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  Plus,
  ShoppingCart,
  Loader2,
  ScanLine,
  Leaf,
  RotateCcw,
  CheckCircle2,
  QrCode,
  Download,
  CheckCheck,
  Mic,
  MicOff,
  CheckSquare,
  Square,
  Trash2,
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
import { utiliserReconnaissanceVocale } from "@/crochets/utiliser-reconnaissance-vocale";
import { utiliserSuppressionAnnulable } from "@/crochets/utiliser-suppression-annulable";
import { utiliserRaccourcisPage } from "@/crochets/utiliser-raccourcis-page";

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
  const [modeSelection, setModeSelection] = useState(false);
  const [articlesSelectionnes, setArticlesSelectionnes] = useState<Set<number>>(new Set());
  const inputAjoutRef = useRef<HTMLInputElement | null>(null);

  const invalider = utiliserInvalidation();
  const { planifierSuppression } = utiliserSuppressionAnnulable();
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
      onSuccess: () => { invalider(["courses"]); },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  const { mutateAsync: supprimerAsync } = utiliserMutation(
    (articleId: number) => supprimerArticle(listeSelectionnee!, articleId)
  );

  const { mutate: cocherSelection, isPending: enCochageSelection } = utiliserMutation(
    async () => {
      if (!listeSelectionnee || articlesSelectionnes.size === 0) {
        return { total: 0 };
      }
      const ids = Array.from(articlesSelectionnes);
      await Promise.all(ids.map((id) => cocherArticle(listeSelectionnee, id, true)));
      return { total: ids.length };
    },
    {
      onSuccess: ({ total }) => {
        invalider(["courses"]);
        setArticlesSelectionnes(new Set());
        setModeSelection(false);
        if (total > 0) {
          toast.success(`${total} article(s) cochés depuis la sélection`);
        }
      },
      onError: () => toast.error("Erreur lors du cochage de la sélection"),
    }
  );

  const { mutate: supprimerSelection, isPending: enSuppressionSelection } = utiliserMutation(
    async () => {
      const ids = Array.from(articlesSelectionnes);
      for (const id of ids) {
        await supprimerAsync(id);
      }
      return { total: ids.length };
    },
    {
      onSuccess: ({ total }) => {
        invalider(["courses"]);
        setArticlesSelectionnes(new Set());
        setModeSelection(false);
        if (total > 0) {
          toast.success(`${total} article(s) supprimés`);
        }
      },
      onError: () => toast.error("Erreur lors de la suppression groupée"),
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

  const { mutate: cocherTout, isPending: enCochageGlobal } = utiliserMutation(
    async () => {
      if (!listeSelectionnee || articlesNonCoches.length === 0) {
        return { total: 0 };
      }
      await Promise.all(
        articlesNonCoches.map((article) =>
          cocherArticle(listeSelectionnee, article.id, true)
        )
      );
      return { total: articlesNonCoches.length };
    },
    {
      onSuccess: ({ total }) => {
        invalider(["courses"]);
        if (total > 0) {
          toast.success(`${total} article(s) cochés`);
        }
      },
      onError: () => toast.error("Erreur lors du cochage global"),
    }
  );

  const { mutate: cocherCategorie, isPending: enCochageCategorie } = utiliserMutation(
    async (categorie: string) => {
      if (!listeSelectionnee) return { categorie, total: 0 };
      const cibles = articlesNonCoches.filter(
        (article) => (article.categorie || "Autre") === categorie
      );
      await Promise.all(
        cibles.map((article) => cocherArticle(listeSelectionnee, article.id, true))
      );
      return { categorie, total: cibles.length };
    },
    {
      onSuccess: ({ categorie, total }) => {
        invalider(["courses"]);
        if (total > 0) {
          toast.success(`${total} article(s) cochés dans ${categorie}`);
        }
      },
      onError: () => toast.error("Erreur lors du cochage par catégorie"),
    }
  );

  const { mutate: finaliserCourses, isPending: enFinalisationCourses } = utiliserMutation(
    async () => {
      if (!listeSelectionnee) {
        throw new Error("Aucune liste sélectionnée");
      }

      const nonCoches = [...articlesNonCoches];
      let listeReportId: number | null = null;

      // Reporter les articles non cochés dans une nouvelle liste active.
      if (nonCoches.length > 0) {
        const sourceNom = detailListe?.nom || "Courses";
        const listeReport = await creerListeCourses(`${sourceNom} - report`);
        listeReportId = listeReport.id;

        await Promise.all(
          nonCoches.map((article) =>
            ajouterArticle(listeReport.id, {
              nom: article.nom,
              quantite: article.quantite,
              unite: article.unite,
              categorie: article.categorie,
            })
          )
        );
      }

      // Cocher tous les articles de la liste courante puis valider pour sync inventaire.
      if (nonCoches.length > 0) {
        await Promise.all(
          nonCoches.map((article) =>
            cocherArticle(listeSelectionnee, article.id, true)
          )
        );
      }
      await validerCourses(listeSelectionnee);

      return {
        reportes: nonCoches.length,
        listeReportId,
      };
    },
    {
      onSuccess: ({ reportes, listeReportId }) => {
        invalider(["courses"]);
        invalider(["inventaire"]);
        if (listeReportId) {
          setListeSelectionnee(listeReportId);
        }
        if (reportes > 0) {
          toast.success(`Courses finalisées, ${reportes} article(s) reporté(s) dans une nouvelle liste`);
        } else {
          toast.success("Courses finalisées, inventaire mis à jour");
        }
      },
      onError: () => toast.error("Erreur lors de la finalisation des courses"),
    }
  );

  // Formulaire article
  const {
    register: regArticle,
    handleSubmit: submitArticle,
    reset: resetArticle,
    setValue: definirValeurArticle,
    formState: { errors: erreursArticle },
  } = useForm<DonneesArticleCourses>({
    resolver: zodResolver(schemaArticleCourses) as never,
  });

  const {
    enEcoute,
    estSupporte,
    demarrerEcoute,
    arreterEcoute,
  } = utiliserReconnaissanceVocale({
    continu: false,
    resultatsInterimaires: false,
    onResultat: (texte) => {
      const nettoye = texte
        .replace(/^ajoute(?:r)?\s+/i, "")
        .trim();
      if (!nettoye) return;
      definirValeurArticle("nom", nettoye, { shouldValidate: true, shouldDirty: true });
      toast.success(`Article détecté: ${nettoye}`);
    },
  });

  const articles = detailListe?.articles ?? [];
  const articlesNonCoches = articles.filter((a) => !a.est_coche);
  const articlesCoches = articles.filter((a) => a.est_coche);

  const basculerSelectionArticle = (articleId: number) => {
    setArticlesSelectionnes((prev) => {
      const suivant = new Set(prev);
      if (suivant.has(articleId)) {
        suivant.delete(articleId);
      } else {
        suivant.add(articleId);
      }
      return suivant;
    });
  };

  const supprimerAvecUndo = (article: ArticleCourses) => {
    planifierSuppression(`courses-${article.id}`, {
      libelle: article.nom,
      onConfirmer: async () => {
        await supprimerAsync(article.id);
        invalider(["courses"]);
      },
      onErreur: () => toast.error("Erreur lors de la suppression"),
    });
  };

  useEffect(() => {
    setArticlesSelectionnes((prev) => {
      const idsDisponibles = new Set(articlesNonCoches.map((article) => article.id));
      const filtres = Array.from(prev).filter((id) => idsDisponibles.has(id));
      return filtres.length === prev.size ? prev : new Set(filtres);
    });
  }, [articlesNonCoches]);

  utiliserRaccourcisPage([
    {
      touche: "n",
      action: () => {
        if (listeSelectionnee) {
          setDialogueArticle(true);
        }
      },
      actif: !!listeSelectionnee,
    },
    {
      touche: "s",
      action: () => inputAjoutRef.current?.focus(),
      actif: !!listeSelectionnee,
    },
    {
      touche: "Delete",
      action: () => {
        if (modeSelection && articlesSelectionnes.size > 0) {
          supprimerSelection(undefined);
        }
      },
      actif: modeSelection && articlesSelectionnes.size > 0,
    },
  ]);

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
            <Button
              variant={modeSelection ? "default" : "outline"}
              size="sm"
              onClick={() => {
                setModeSelection((prev) => !prev);
                setArticlesSelectionnes(new Set());
              }}
            >
              {modeSelection ? <CheckSquare className="mr-1 h-4 w-4" /> : <Square className="mr-1 h-4 w-4" />}
              Sélection multiple
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => cocherTout(undefined)}
              disabled={enCochageGlobal || articlesNonCoches.length === 0}
            >
              <CheckCheck className="mr-1 h-4 w-4" />
              Tout cocher
            </Button>
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
              variant="secondary"
              onClick={() => finaliserCourses(undefined)}
              disabled={enFinalisationCourses || enCochageGlobal || enCochageCategorie}
            >
              {enFinalisationCourses ? (
                <Loader2 className="mr-1 h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle2 className="mr-1 h-4 w-4" />
              )}
              Courses faites
            </Button>
            <Button
              size="sm"
              onClick={() => valider(undefined)}
              disabled={enValidation || articlesNonCoches.length > 0 || enFinalisationCourses}
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
            ) : (
              <div className="space-y-4">
                {/* Champ "Ajouter article" toujours visible (4.5) */}
                <form 
                  onSubmit={submitArticle((data) => ajouter(data))}
                  className="flex gap-2 sticky top-0 bg-card pb-3 z-10 border-b"
                >
                  <Input
                    {...regArticle("nom")}
                    ref={(element) => {
                      regArticle("nom").ref(element);
                      inputAjoutRef.current = element;
                    }}
                    placeholder="+ Ajouter un article..."
                    className="flex-1"
                    disabled={enAjout}
                  />
                  <Button
                    type="submit"
                    size="sm"
                    disabled={enAjout}
                    aria-label="Ajouter l'article"
                  >
                    {enAjout ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Plus className="h-4 w-4" />
                    )}
                  </Button>
                  {estSupporte && (
                    <Button
                      type="button"
                      size="sm"
                      variant={enEcoute ? "secondary" : "outline"}
                      aria-label="Saisie vocale"
                      onClick={() => {
                        if (enEcoute) {
                          arreterEcoute();
                        } else {
                          demarrerEcoute();
                        }
                      }}
                    >
                      {enEcoute ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                    </Button>
                  )}
                </form>

                {modeSelection && (
                  <div className="flex flex-wrap items-center gap-2 rounded-lg border bg-muted/40 px-3 py-2 text-sm">
                    <span className="font-medium">{articlesSelectionnes.size} sélectionné(s)</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        if (articlesSelectionnes.size === articlesNonCoches.length) {
                          setArticlesSelectionnes(new Set());
                        } else {
                          setArticlesSelectionnes(new Set(articlesNonCoches.map((article) => article.id)));
                        }
                      }}
                    >
                      {articlesSelectionnes.size === articlesNonCoches.length ? "Tout désélectionner" : "Tout sélectionner"}
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => cocherSelection(undefined)}
                      disabled={articlesSelectionnes.size === 0 || enCochageSelection}
                    >
                      Cocher la sélection
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => supprimerSelection(undefined)}
                      disabled={articlesSelectionnes.size === 0 || enSuppressionSelection}
                    >
                      <Trash2 className="mr-1 h-4 w-4" />
                      Supprimer la sélection
                    </Button>
                  </div>
                )}

                {/* Affichage articles */}
                {chargementDetail ? (
                  <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                    {Array.from({ length: 10 }).map((_, i) => (
                      <Skeleton key={i} className="aspect-square rounded-xl" />
                    ))}
                  </div>
                ) : articles.length === 0 ? (
                  <div className="flex flex-col items-center gap-4 py-12">
                    <p className="text-muted-foreground">Liste vide</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Articles par catégorie */}
                    {categoriesTriees.map((cat) => (
                      <div key={cat}>
                        <div className="mb-2 flex items-center justify-between gap-2">
                          <h3 className="text-sm font-semibold">{cat}</h3>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-7 px-2 text-xs"
                            onClick={() => cocherCategorie(cat)}
                            disabled={enCochageCategorie || enFinalisationCourses}
                          >
                            Cocher catégorie
                          </Button>
                        </div>
                        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
                          {groupesNonCoches[cat].map((a) => (
                            <TileArticle
                              key={a.id}
                              nom={a.nom}
                              quantite={a.quantite}
                              unite={a.unite}
                              categorie={a.categorie}
                              estSelectionne={articlesSelectionnes.has(a.id)}
                              onClick={() => {
                                if (modeSelection) {
                                  basculerSelectionArticle(a.id);
                                } else {
                                  cocher({ articleId: a.id, coche: true });
                                }
                              }}
                              onLongPress={() => {
                                if (modeSelection) {
                                  basculerSelectionArticle(a.id);
                                } else {
                                  supprimerAvecUndo(a);
                                }
                              }}
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
