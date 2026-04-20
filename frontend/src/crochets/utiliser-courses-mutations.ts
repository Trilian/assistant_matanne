import { useEffect } from "react";
import type { Dispatch, SetStateAction } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import {
  ajouterArticle,
  cocherArticle,
  confirmerCourses,
  creerListeCourses,
  supprimerArticle,
  validerCourses,
} from "@/bibliotheque/api/courses";
import { envoyerListeCoursesTelegram } from "@/bibliotheque/api/telegram";
import type { ArticleBarcode } from "@/bibliotheque/api/inventaire";
import { utiliserInvalidation, utiliserMutation } from "@/crochets/utiliser-api";
import { utiliserSuppressionAnnulable } from "@/crochets/utiliser-suppression-annulable";
import type { ArticleCourses, ListeCourses } from "@/types/courses";
import type { DonneesArticleCourses } from "@/bibliotheque/validateurs";

type ParamsMutations = {
  listeSelectionnee: number | null;
  setListeSelectionnee: Dispatch<SetStateAction<number | null>>;
  detailListe: ListeCourses | undefined;
  articlesNonCoches: ArticleCourses[];
  articlesSelectionnes: Set<number>;
  setArticlesSelectionnes: Dispatch<SetStateAction<Set<number>>>;
  setModeSelection: Dispatch<SetStateAction<boolean>>;
  setDialogueArticle: Dispatch<SetStateAction<boolean>>;
  resetArticle: () => void;
};

/**
 * Toutes les mutations CRUD courses + suppression annulable + sélection + import scanner.
 */
export function utiliserCoursesMutations(p: ParamsMutations) {
  const invalider = utiliserInvalidation();
  const queryClient = useQueryClient();
  const { planifierSuppression } = utiliserSuppressionAnnulable();

  // Nettoyage sélection quand des articles disparaissent
  useEffect(() => {
    p.setArticlesSelectionnes((precedent) => {
      const idsDisponibles = new Set(p.articlesNonCoches.map((article) => article.id));
      const filtres = Array.from(precedent).filter((id) => idsDisponibles.has(id));
      return filtres.length === precedent.size ? precedent : new Set(filtres);
    });
  }, [p.articlesNonCoches]); // eslint-disable-line react-hooks/exhaustive-deps

  const { mutate: creerListe, isPending: enCreationListe } = utiliserMutation(
    (nom: string) => creerListeCourses(nom),
    {
      onSuccess: (liste) => {
        invalider(["courses"]);
        p.setListeSelectionnee(liste.id);
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
    (donnees: DonneesArticleCourses) => ajouterArticle(p.listeSelectionnee!, donnees),
    {
      onMutate: async (donnees) => {
        if (!p.listeSelectionnee) return { idTemp: 0 };

        const cleListes = ["courses"];
        const cleDetail = ["courses", String(p.listeSelectionnee)];

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
          if (!old) return old;
          return {
            ...old,
            articles: [...old.articles, articleTemp],
            nombre_articles: old.nombre_articles + 1,
          };
        });

        queryClient.setQueryData<ListeCourses[] | undefined>(cleListes, (old) => {
          if (!old) return old;
          return old.map((liste) =>
            liste.id === p.listeSelectionnee
              ? { ...liste, nombre_articles: liste.nombre_articles + 1 }
              : liste,
          );
        });

        return { precedentListes, precedentDetail, idTemp: articleTemp.id };
      },
      onSuccess: () => {
        invalider(["courses"]);
        p.setDialogueArticle(false);
        p.resetArticle();
        toast.success("Article ajouté");
      },
      onError: (_err, _variables, contexte) => {
        if (contexte?.precedentListes) {
          queryClient.setQueryData(["courses"], contexte.precedentListes);
        }
        if (contexte?.precedentDetail && p.listeSelectionnee) {
          queryClient.setQueryData(["courses", String(p.listeSelectionnee)], contexte.precedentDetail);
        }
        toast.error("Erreur lors de l'ajout");
      },
    },
  );

  const { mutate: cocher } = utiliserMutation(
    ({ articleId, coche }: { articleId: number; coche: boolean }) =>
      cocherArticle(p.listeSelectionnee!, articleId, coche),
    {
      onMutate: async ({ articleId, coche }) => {
        if (!p.listeSelectionnee) return {};

        const cleListes = ["courses"];
        const cleDetail = ["courses", String(p.listeSelectionnee)];

        await queryClient.cancelQueries({ queryKey: cleListes });
        await queryClient.cancelQueries({ queryKey: cleDetail });

        const precedentListes = queryClient.getQueryData(cleListes);
        const precedentDetail = queryClient.getQueryData(cleDetail);

        queryClient.setQueryData<ListeCourses | undefined>(cleDetail, (old) => {
          if (!old) return old;
          const article = old.articles.find((item) => item.id === articleId);
          if (!article || article.est_coche === coche) return old;
          return {
            ...old,
            articles: old.articles.map((item) =>
              item.id === articleId ? { ...item, est_coche: coche } : item,
            ),
            nombre_coche: old.nombre_coche + (coche ? 1 : -1),
          };
        });

        queryClient.setQueryData<ListeCourses[] | undefined>(cleListes, (old) => {
          if (!old) return old;
          return old.map((liste) =>
            liste.id === p.listeSelectionnee
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
        if (contexte?.precedentDetail && p.listeSelectionnee) {
          queryClient.setQueryData(["courses", String(p.listeSelectionnee)], contexte.precedentDetail);
        }
        toast.error("Erreur lors de la mise à jour");
      },
    },
  );

  const { mutateAsync: supprimerAsync } = utiliserMutation(
    (articleId: number) => supprimerArticle(p.listeSelectionnee!, articleId),
    {
      onMutate: async (articleId) => {
        if (!p.listeSelectionnee) return {};

        const cleListes = ["courses"];
        const cleDetail = ["courses", String(p.listeSelectionnee)];

        await queryClient.cancelQueries({ queryKey: cleListes });
        await queryClient.cancelQueries({ queryKey: cleDetail });

        const precedentListes = queryClient.getQueryData(cleListes);
        const precedentDetail = queryClient.getQueryData(cleDetail);

        queryClient.setQueryData<ListeCourses | undefined>(cleDetail, (old) => {
          if (!old) return old;
          const article = old.articles.find((item) => item.id === articleId);
          if (!article) return old;
          return {
            ...old,
            articles: old.articles.filter((item) => item.id !== articleId),
            nombre_articles: Math.max(0, old.nombre_articles - 1),
            nombre_coche: article.est_coche ? Math.max(0, old.nombre_coche - 1) : old.nombre_coche,
          };
        });

        queryClient.setQueryData<ListeCourses[] | undefined>(cleListes, (old) => {
          if (!old) return old;
          return old.map((liste) => {
            if (liste.id !== p.listeSelectionnee) return liste;
            return { ...liste, nombre_articles: Math.max(0, liste.nombre_articles - 1) };
          });
        });

        return { precedentListes, precedentDetail };
      },
      onError: (_err, _variables, contexte) => {
        if (contexte?.precedentListes) {
          queryClient.setQueryData(["courses"], contexte.precedentListes);
        }
        if (contexte?.precedentDetail && p.listeSelectionnee) {
          queryClient.setQueryData(["courses", String(p.listeSelectionnee)], contexte.precedentDetail);
        }
      },
    },
  );

  const { mutate: cocherSelection, isPending: enCochageSelection } = utiliserMutation(
    async () => {
      if (!p.listeSelectionnee || p.articlesSelectionnes.size === 0) return { total: 0 };
      const ids = Array.from(p.articlesSelectionnes);
      await Promise.all(ids.map((id) => cocherArticle(p.listeSelectionnee!, id, true)));
      return { total: ids.length };
    },
    {
      onSuccess: ({ total }) => {
        invalider(["courses"]);
        p.setArticlesSelectionnes(new Set());
        p.setModeSelection(false);
        if (total > 0) toast.success(`${total} article(s) cochés depuis la sélection`);
      },
      onError: () => toast.error("Erreur lors du cochage de la sélection"),
    },
  );

  const { mutate: supprimerSelection, isPending: enSuppressionSelection } = utiliserMutation(
    async () => {
      const ids = Array.from(p.articlesSelectionnes);
      for (const id of ids) {
        await supprimerAsync(id);
      }
      return { total: ids.length };
    },
    {
      onSuccess: ({ total }) => {
        invalider(["courses"]);
        p.setArticlesSelectionnes(new Set());
        p.setModeSelection(false);
        if (total > 0) toast.success(`${total} article(s) supprimés`);
      },
      onError: () => toast.error("Erreur lors de la suppression groupée"),
    },
  );

  const { mutate: valider, isPending: enValidation } = utiliserMutation(
    () => validerCourses(p.listeSelectionnee!),
    {
      onSuccess: (data) => {
        queryClient.setQueryData(
          ["courses", String(p.listeSelectionnee)],
          (old: ListeCourses | undefined) => (old ? { ...old, etat: "terminee" } : old),
        );
        invalider(["courses"]);
        invalider(["inventaire"]);
        toast.success(data?.message || "Courses validées ! Stock mis à jour.");
      },
      onError: () => toast.error("Erreur lors de la validation"),
    },
  );

  const { mutate: confirmer, isPending: enConfirmation } = utiliserMutation(
    (idListe: number) => confirmerCourses(idListe),
    {
      onSuccess: (_data, idListe) => {
        queryClient.setQueryData(
          ["courses", String(idListe)],
          (old: ListeCourses | undefined) => (old ? { ...old, etat: "active" } : old),
        );
        queryClient.setQueryData<ListeCourses[] | undefined>(["courses"], (old) => {
          if (!old) return old;
          return old.map((liste) => (liste.id === idListe ? { ...liste, etat: "active" } : liste));
        });
        invalider(["courses"]);
        toast.success("Liste confirmée, vous pouvez maintenant cocher vos achats.");
        void envoyerListeCoursesTelegram(idListe).catch(() => {
          toast.info("Liste confirmée, notification Telegram non envoyée.");
        });
      },
      onError: () => toast.error("Impossible de confirmer cette liste"),
    },
  );

  const { mutate: cocherTout, isPending: enCochageGlobal } = utiliserMutation(
    async () => {
      if (!p.listeSelectionnee || p.articlesNonCoches.length === 0) return { total: 0 };
      await Promise.all(
        p.articlesNonCoches.map((article) => cocherArticle(p.listeSelectionnee!, article.id, true)),
      );
      return { total: p.articlesNonCoches.length };
    },
    {
      onSuccess: ({ total }) => {
        invalider(["courses"]);
        if (total > 0) toast.success(`${total} article(s) cochés`);
      },
      onError: () => toast.error("Erreur lors du cochage global"),
    },
  );

  const { mutate: cocherCategorie, isPending: enCochageCategorie } = utiliserMutation(
    async (categorie: string) => {
      if (!p.listeSelectionnee) return { categorie, total: 0 };
      const cibles = p.articlesNonCoches.filter(
        (article) => (article.categorie || "Autre") === categorie,
      );
      await Promise.all(
        cibles.map((article) => cocherArticle(p.listeSelectionnee!, article.id, true)),
      );
      return { categorie, total: cibles.length };
    },
    {
      onSuccess: ({ categorie, total }) => {
        invalider(["courses"]);
        if (total > 0) toast.success(`${total} article(s) cochés dans ${categorie}`);
      },
      onError: () => toast.error("Erreur lors du cochage par catégorie"),
    },
  );

  const { mutate: finaliserCourses, isPending: enFinalisationCourses } = utiliserMutation(
    async () => {
      if (!p.listeSelectionnee) throw new Error("Aucune liste sélectionnée");

      const nonCoches = [...p.articlesNonCoches];
      let listeReportId: number | null = null;

      if (nonCoches.length > 0) {
        const sourceNom = p.detailListe?.nom || "Courses";
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
        await Promise.all(
          nonCoches.map((article) => cocherArticle(p.listeSelectionnee!, article.id, true)),
        );
      }

      await validerCourses(p.listeSelectionnee);
      return { reportes: nonCoches.length, listeReportId };
    },
    {
      onSuccess: ({ reportes, listeReportId }) => {
        invalider(["courses"]);
        invalider(["inventaire"]);
        if (listeReportId) p.setListeSelectionnee(listeReportId);
        toast.success(
          reportes > 0
            ? `Courses finalisées, ${reportes} article(s) reporté(s) dans une nouvelle liste`
            : "Courses finalisées, inventaire mis à jour",
        );
      },
      onError: () => toast.error("Erreur lors de la finalisation des courses"),
    },
  );

  function basculerSelectionArticle(articleId: number) {
    p.setArticlesSelectionnes((precedent) => {
      const suivant = new Set(precedent);
      if (suivant.has(articleId)) suivant.delete(articleId);
      else suivant.add(articleId);
      return suivant;
    });
  }

  function supprimerAvecUndo(article: ArticleCourses) {
    planifierSuppression(`courses-${article.id}`, {
      libelle: article.nom,
      onConfirmer: async () => {
        await supprimerAsync(article.id);
        invalider(["courses"]);
      },
      onErreur: () => toast.error("Erreur lors de la suppression"),
    });
  }

  async function importerDepuisScanner(trouves: ArticleBarcode[], inconnus: string[]) {
    if (!p.listeSelectionnee) return;
    let importes = 0;
    for (const trouve of trouves) {
      const nom = trouve.article.nom;
      if (!nom) continue;
      await ajouterArticle(p.listeSelectionnee, {
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

  return {
    creerListe,
    enCreationListe,
    ajouter,
    enAjout,
    cocher,
    supprimerAvecUndo,
    cocherSelection,
    enCochageSelection,
    supprimerSelection,
    enSuppressionSelection,
    valider,
    enValidation,
    confirmer,
    enConfirmation,
    cocherTout,
    enCochageGlobal,
    cocherCategorie,
    enCochageCategorie,
    finaliserCourses,
    enFinalisationCourses,
    basculerSelectionArticle,
    importerDepuisScanner,
  };
}
