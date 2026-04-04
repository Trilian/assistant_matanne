import { useEffect, useMemo, useRef, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import {
  ajouterArticle,
  cocherArticle,
  confirmerCourses,
  creerListeCourses,
  listerListesCourses,
  obtenirListeCourses,
  obtenirPredictionsCourses,
  obtenirQrPartageListe,
  obtenirRecurrentsSuggeres,
  obtenirSuggestionsBioLocal,
  supprimerArticle,
  validerCourses,
} from "@/bibliotheque/api/courses";
import { listerEvenements } from "@/bibliotheque/api/calendriers";
import { listerEvenementsFamiliaux } from "@/bibliotheque/api/famille";
import { envoyerListeCoursesTelegram } from "@/bibliotheque/api/telegram";
import {
  schemaArticleCourses,
  type DonneesArticleCourses,
} from "@/bibliotheque/validateurs";
import type { ArticleBarcode } from "@/bibliotheque/api/inventaire";
import { utiliserInvalidation, utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import { utiliserModeInvites } from "@/crochets/utiliser-mode-invites";
import { utiliserRaccourcisPage } from "@/crochets/utiliser-raccourcis-page";
import { utiliserReconnaissanceVocale } from "@/crochets/utiliser-reconnaissance-vocale";
import { utiliserSuppressionAnnulable } from "@/crochets/utiliser-suppression-annulable";
import type { ArticleCourses, ListeCourses } from "@/types/courses";

function grouperParCategorie(articles: ArticleCourses[]): Record<string, ArticleCourses[]> {
  const groupes: Record<string, ArticleCourses[]> = {};
  for (const article of articles) {
    const categorie = article.categorie || "Autre";
    (groupes[categorie] ??= []).push(article);
  }
  return groupes;
}

export function utiliserPageCourses() {
  const {
    contexte: modeInvites,
    mettreAJour: mettreAJourModeInvites,
    reinitialiser: reinitialiserModeInvites,
  } = utiliserModeInvites();

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
  const queryClient = useQueryClient();
  const { planifierSuppression } = utiliserSuppressionAnnulable();

  const contexteInvitesActif = modeInvites.actif && modeInvites.nbInvites > 0;
  const evenementsModeInvites = useMemo(() => {
    const items = [...modeInvites.evenements];
    if (modeInvites.occasion.trim()) {
      items.unshift(modeInvites.occasion.trim());
    }
    return Array.from(new Set(items.filter(Boolean))).slice(0, 6);
  }, [modeInvites.evenements, modeInvites.occasion]);

  const { data: listes, isLoading: chargementListes } = utiliserRequete(
    ["courses"],
    listerListesCourses,
  );

  const { data: detailListe, isLoading: chargementDetail } = utiliserRequete(
    ["courses", String(listeSelectionnee)],
    () => obtenirListeCourses(listeSelectionnee!),
    { enabled: listeSelectionnee !== null },
  );

  const { data: bioLocal } = utiliserRequete(
    ["courses", "bio-local", String(listeSelectionnee)],
    () => obtenirSuggestionsBioLocal(listeSelectionnee!),
    { enabled: listeSelectionnee !== null && panneauBio },
  );

  const { data: recurrents } = utiliserRequete(
    ["courses", "recurrents"],
    obtenirRecurrentsSuggeres,
  );

  const { data: evenementsFamille } = utiliserRequete(
    ["famille", "evenements", "courses-invites"],
    listerEvenementsFamiliaux,
    { staleTime: 10 * 60 * 1000 },
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
    { staleTime: 10 * 60 * 1000 },
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
    },
  );

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
    },
  );

  type ContexteArticle = {
    precedentListes?: unknown;
    precedentDetail?: unknown;
    idTemp: number;
  };

  const { mutate: ajouter, isPending: enAjout } = utiliserMutation<
    ArticleCourses,
    DonneesArticleCourses,
    ContexteArticle
  >(
    (donnees: DonneesArticleCourses) => ajouterArticle(listeSelectionnee!, donnees),
    {
      onMutate: async (donnees) => {
        if (!listeSelectionnee) {
          return { idTemp: 0 };
        }

        const cleListes = ["courses"];
        const cleDetail = ["courses", String(listeSelectionnee)];

        await queryClient.cancelQueries({ queryKey: cleListes });
        await queryClient.cancelQueries({ queryKey: cleDetail });

        const precedentListes = queryClient.getQueryData(cleListes);
        const precedentDetail = queryClient.getQueryData(cleDetail);

        const articleTemp: ArticleCourses = {
          id: -Date.now(),
          nom: donnees.nom,
          quantite: donnees.quantite,
          unite: donnees.unite,
          categorie: donnees.categorie,
          magasin_cible: donnees.magasin_cible,
          est_coche: false,
        };

        queryClient.setQueryData<ListeCourses | undefined>(cleDetail, (old) => {
          if (!old) {
            return old;
          }
          return {
            ...old,
            articles: [...old.articles, articleTemp],
            nombre_articles: old.nombre_articles + 1,
          };
        });

        queryClient.setQueryData<ListeCourses[] | undefined>(cleListes, (old) => {
          if (!old) {
            return old;
          }
          return old.map((liste) =>
            liste.id === listeSelectionnee
              ? { ...liste, nombre_articles: liste.nombre_articles + 1 }
              : liste,
          );
        });

        return { precedentListes, precedentDetail, idTemp: articleTemp.id };
      },
      onSuccess: () => {
        invalider(["courses"]);
        setDialogueArticle(false);
        resetArticle();
        toast.success("Article ajouté");
      },
      onError: (_err, _variables, contexte) => {
        if (contexte?.precedentListes) {
          queryClient.setQueryData(["courses"], contexte.precedentListes);
        }
        if (contexte?.precedentDetail && listeSelectionnee) {
          queryClient.setQueryData(["courses", String(listeSelectionnee)], contexte.precedentDetail);
        }
        toast.error("Erreur lors de l'ajout");
      },
    },
  );

  const { mutate: cocher } = utiliserMutation(
    ({ articleId, coche }: { articleId: number; coche: boolean }) =>
      cocherArticle(listeSelectionnee!, articleId, coche),
    {
      onMutate: async ({ articleId, coche }) => {
        if (!listeSelectionnee) {
          return {};
        }

        const cleListes = ["courses"];
        const cleDetail = ["courses", String(listeSelectionnee)];

        await queryClient.cancelQueries({ queryKey: cleListes });
        await queryClient.cancelQueries({ queryKey: cleDetail });

        const precedentListes = queryClient.getQueryData(cleListes);
        const precedentDetail = queryClient.getQueryData(cleDetail);

        queryClient.setQueryData<ListeCourses | undefined>(cleDetail, (old) => {
          if (!old) {
            return old;
          }
          const article = old.articles.find((item) => item.id === articleId);
          if (!article || article.est_coche === coche) {
            return old;
          }

          return {
            ...old,
            articles: old.articles.map((item) =>
              item.id === articleId ? { ...item, est_coche: coche } : item,
            ),
            nombre_coche: old.nombre_coche + (coche ? 1 : -1),
          };
        });

        queryClient.setQueryData<ListeCourses[] | undefined>(cleListes, (old) => {
          if (!old) {
            return old;
          }
          return old.map((liste) =>
            liste.id === listeSelectionnee
              ? { ...liste, nombre_coche: liste.nombre_coche + (coche ? 1 : -1) }
              : liste,
          );
        });

        return { precedentListes, precedentDetail };
      },
      onSuccess: () => invalider(["courses"]),
      onError: (_err, _variables, contexte) => {
        if (contexte?.precedentListes) {
          queryClient.setQueryData(["courses"], contexte.precedentListes);
        }
        if (contexte?.precedentDetail && listeSelectionnee) {
          queryClient.setQueryData(["courses", String(listeSelectionnee)], contexte.precedentDetail);
        }
        toast.error("Erreur lors de la mise à jour");
      },
    },
  );

  const { mutateAsync: supprimerAsync } = utiliserMutation(
    (articleId: number) => supprimerArticle(listeSelectionnee!, articleId),
    {
      onMutate: async (articleId) => {
        if (!listeSelectionnee) {
          return {};
        }

        const cleListes = ["courses"];
        const cleDetail = ["courses", String(listeSelectionnee)];

        await queryClient.cancelQueries({ queryKey: cleListes });
        await queryClient.cancelQueries({ queryKey: cleDetail });

        const precedentListes = queryClient.getQueryData(cleListes);
        const precedentDetail = queryClient.getQueryData(cleDetail);

        queryClient.setQueryData<ListeCourses | undefined>(cleDetail, (old) => {
          if (!old) {
            return old;
          }
          const article = old.articles.find((item) => item.id === articleId);
          if (!article) {
            return old;
          }
          return {
            ...old,
            articles: old.articles.filter((item) => item.id !== articleId),
            nombre_articles: Math.max(0, old.nombre_articles - 1),
            nombre_coche: article.est_coche ? Math.max(0, old.nombre_coche - 1) : old.nombre_coche,
          };
        });

        queryClient.setQueryData<ListeCourses[] | undefined>(cleListes, (old) => {
          if (!old) {
            return old;
          }
          return old.map((liste) => {
            if (liste.id !== listeSelectionnee) {
              return liste;
            }
            return {
              ...liste,
              nombre_articles: Math.max(0, liste.nombre_articles - 1),
            };
          });
        });

        return { precedentListes, precedentDetail };
      },
      onError: (_err, _variables, contexte) => {
        if (contexte?.precedentListes) {
          queryClient.setQueryData(["courses"], contexte.precedentListes);
        }
        if (contexte?.precedentDetail && listeSelectionnee) {
          queryClient.setQueryData(["courses", String(listeSelectionnee)], contexte.precedentDetail);
        }
      },
    },
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
    },
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
    },
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
    },
  );

  const { mutate: confirmer, isPending: enConfirmation } = utiliserMutation(
    () => confirmerCourses(listeSelectionnee!),
    {
      onSuccess: async () => {
        const idListe = listeSelectionnee;
        invalider(["courses"]);
        toast.success("Liste confirmée, vous pouvez maintenant cocher vos achats.");

        if (idListe) {
          try {
            await envoyerListeCoursesTelegram(idListe);
          } catch {
            toast.info("Liste confirmée, notification Telegram non envoyée.");
          }
        }
      },
      onError: () => toast.error("Impossible de confirmer cette liste"),
    },
  );

  const { mutate: cocherTout, isPending: enCochageGlobal } = utiliserMutation(
    async () => {
      if (!listeSelectionnee || articlesNonCoches.length === 0) {
        return { total: 0 };
      }
      await Promise.all(
        articlesNonCoches.map((article) => cocherArticle(listeSelectionnee, article.id, true)),
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
    },
  );

  const { mutate: cocherCategorie, isPending: enCochageCategorie } = utiliserMutation(
    async (categorie: string) => {
      if (!listeSelectionnee) {
        return { categorie, total: 0 };
      }
      const cibles = articlesNonCoches.filter(
        (article) => (article.categorie || "Autre") === categorie,
      );
      await Promise.all(
        cibles.map((article) => cocherArticle(listeSelectionnee, article.id, true)),
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
    },
  );

  const { mutate: finaliserCourses, isPending: enFinalisationCourses } = utiliserMutation(
    async () => {
      if (!listeSelectionnee) {
        throw new Error("Aucune liste sélectionnée");
      }

      const nonCoches = [...articlesNonCoches];
      let listeReportId: number | null = null;

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
              magasin_cible: article.magasin_cible,
            }),
          ),
        );
      }

      if (nonCoches.length > 0) {
        await Promise.all(
          nonCoches.map((article) => cocherArticle(listeSelectionnee, article.id, true)),
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
    },
  );

  const {
    register: regArticle,
    handleSubmit: submitArticle,
    reset: resetArticle,
    setValue: definirValeurArticle,
    formState: { errors: erreursArticle },
  } = useForm<DonneesArticleCourses>({
    resolver: zodResolver(schemaArticleCourses) as never,
  });

  const { enEcoute, estSupporte, demarrerEcoute, arreterEcoute } = utiliserReconnaissanceVocale({
    continu: false,
    resultatsInterimaires: false,
    onResultat: (texte) => {
      const nettoye = texte.replace(/^ajoute(?:r)?\s+/i, "").trim();
      if (!nettoye) {
        return;
      }
      definirValeurArticle("nom", nettoye, { shouldValidate: true, shouldDirty: true });
      toast.success(`Article détecté: ${nettoye}`);
    },
  });

  const articles = detailListe?.articles ?? [];
  const articlesNonCoches = articles.filter((article) => !article.est_coche);
  const articlesCoches = articles.filter((article) => article.est_coche);

  const basculerSelectionArticle = (articleId: number) => {
    setArticlesSelectionnes((precedent) => {
      const suivant = new Set(precedent);
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
    setArticlesSelectionnes((precedent) => {
      const idsDisponibles = new Set(articlesNonCoches.map((article) => article.id));
      const filtres = Array.from(precedent).filter((id) => idsDisponibles.has(id));
      return filtres.length === precedent.size ? precedent : new Set(filtres);
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

  const groupesNonCoches = useMemo(
    () => grouperParCategorie(articlesNonCoches),
    [articlesNonCoches],
  );
  const categoriesTriees = useMemo(
    () => Object.keys(groupesNonCoches).sort(),
    [groupesNonCoches],
  );

  async function importerDepuisScanner(trouves: ArticleBarcode[], inconnus: string[]) {
    if (!listeSelectionnee) {
      return;
    }
    let importes = 0;
    for (const trouve of trouves) {
      const nom = trouve.article.nom;
      if (!nom) {
        continue;
      }
      await ajouterArticle(listeSelectionnee, {
        nom,
        quantite: 1,
        categorie: trouve.article.categorie ?? undefined,
      }).catch(() => null);
      importes += 1;
    }
    if (importes > 0) {
      invalider(["courses"]);
      toast.success(`${importes} article(s) ajouté(s) à la liste`);
    }
    if (inconnus.length > 0) {
      toast.warning(`${inconnus.length} code(s) non reconnu(s)`);
    }
  }

  async function ouvrirQrPartage() {
    if (!listeSelectionnee) {
      return;
    }
    setDialogueQr(true);
    setChargementQr(true);
    try {
      const blob = await obtenirQrPartageListe(listeSelectionnee);
      const url = URL.createObjectURL(blob);
      setQrUrl((precedent) => {
        if (precedent) {
          URL.revokeObjectURL(precedent);
        }
        return url;
      });
    } catch {
      toast.error("Impossible de générer le QR de partage");
    } finally {
      setChargementQr(false);
    }
  }

  function telechargerQr() {
    if (!qrUrl || !detailListe) {
      return;
    }
    const ancre = document.createElement("a");
    ancre.href = qrUrl;
    ancre.download = `courses-${detailListe.nom.replace(/\s+/g, "-").toLowerCase()}.png`;
    document.body.appendChild(ancre);
    ancre.click();
    document.body.removeChild(ancre);
  }

  return {
    modeInvites,
    mettreAJourModeInvites,
    reinitialiserModeInvites,
    listeSelectionnee,
    setListeSelectionnee,
    nomNouvelleListe,
    setNomNouvelleListe,
    dialogueArticle,
    setDialogueArticle,
    scanneurOuvert,
    setScanneurOuvert,
    panneauBio,
    setPanneauBio,
    dialogueQr,
    setDialogueQr,
    qrUrl,
    setQrUrl,
    chargementQr,
    modeSelection,
    setModeSelection,
    articlesSelectionnes,
    setArticlesSelectionnes,
    inputAjoutRef,
    listes,
    detailListe,
    bioLocal,
    recurrents,
    predictionsInvites,
    suggestionsInvites,
    chargementListes,
    chargementDetail,
    enCreationListe,
    enAjout,
    enEcoute,
    estSupporte,
    enCochageSelection,
    enSuppressionSelection,
    enValidation,
    enConfirmation,
    enCochageGlobal,
    enCochageCategorie,
    enFinalisationCourses,
    regArticle,
    submitArticle,
    erreursArticle,
    articles,
    articlesNonCoches,
    articlesCoches,
    groupesNonCoches,
    categoriesTriees,
    ouvrirQrPartage,
    telechargerQr,
    creerListe,
    ajouter,
    cocher,
    confirmer,
    valider,
    cocherTout,
    cocherSelection,
    supprimerSelection,
    cocherCategorie,
    finaliserCourses,
    basculerSelectionArticle,
    supprimerAvecUndo,
    importerDepuisScanner,
    demarrerEcoute,
    arreterEcoute,
    evenementsModeInvites,
  };
}
