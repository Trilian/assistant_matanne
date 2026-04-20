import { useEffect, useMemo } from "react";
import type { Dispatch, SetStateAction } from "react";

import { listerEvenements } from "@/bibliotheque/api/calendriers";
import {
  listerListesCourses,
  obtenirListeCourses,
  obtenirPredictionsCourses,
  obtenirRecurrentsSuggeres,
  obtenirSuggestionsBioLocal,
} from "@/bibliotheque/api/courses";
import { listerEvenementsFamiliaux } from "@/bibliotheque/api/famille";
import { utiliserRequete } from "@/crochets/utiliser-api";
import type { ArticleCourses } from "@/types/courses";

export function grouperParCategorie(articles: ArticleCourses[]): Record<string, ArticleCourses[]> {
  const groupes: Record<string, ArticleCourses[]> = {};
  for (const article of articles) {
    const categorie = article.categorie || "Autre";
    (groupes[categorie] ??= []).push(article);
  }
  return groupes;
}

type ParamsRequetes = {
  listeSelectionnee: number | null;
  panneauBio: boolean;
  contexteInvitesActif: boolean;
  evenementsModeInvites: string[];
  modeInvitesNbInvites: number;
  setListeSelectionnee: Dispatch<SetStateAction<number | null>>;
};

/**
 * Requêtes TanStack Query pour la page courses + état dérivé (articles, groupes, suggestions).
 */
export function utiliserCoursesRequetes(p: ParamsRequetes) {
  const { data: listes, isLoading: chargementListes } = utiliserRequete(
    ["courses"],
    listerListesCourses,
  );

  // Auto-sélection : liste de la semaine > première active > première liste
  useEffect(() => {
    if (!listes?.length) return;
    p.setListeSelectionnee((current) => {
      if (current !== null && listes.some((l) => l.id === current)) return current;
      const listeSemaine = listes.find(
        (l) => !l.est_terminee && l.nom.toLowerCase().includes("semaine"),
      );
      const premiere = listeSemaine ?? listes.find((l) => !l.est_terminee) ?? listes[0];
      return premiere?.id ?? null;
    });
  }, [listes]); // eslint-disable-line react-hooks/exhaustive-deps

  const { data: detailListe, isLoading: chargementDetail } = utiliserRequete(
    ["courses", String(p.listeSelectionnee)],
    () => obtenirListeCourses(p.listeSelectionnee!),
    { enabled: p.listeSelectionnee !== null },
  );

  const { data: bioLocal } = utiliserRequete(
    ["courses", "bio-local", String(p.listeSelectionnee)],
    () => obtenirSuggestionsBioLocal(p.listeSelectionnee!),
    { enabled: p.listeSelectionnee !== null && p.panneauBio },
  );

  const { data: recurrents } = utiliserRequete(
    ["courses", "recurrents"],
    obtenirRecurrentsSuggeres,
  );

  const { data: evenementsFamille } = utiliserRequete(
    ["famille", "evenements", "courses-invites"],
    () => listerEvenementsFamiliaux(),
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
      String(p.modeInvitesNbInvites),
      p.evenementsModeInvites.join("|"),
    ],
    () =>
      obtenirPredictionsCourses({
        limite: 6,
        nbInvites: p.contexteInvitesActif ? p.modeInvitesNbInvites : 0,
        evenements: p.evenementsModeInvites,
      }),
    {
      enabled: p.contexteInvitesActif || p.evenementsModeInvites.length > 0,
      staleTime: 5 * 60 * 1000,
    },
  );

  const articles = detailListe?.articles ?? [];
  const articlesNonCoches = articles.filter((article) => !article.est_coche);
  const articlesCoches = articles.filter((article) => article.est_coche);

  const groupesNonCoches = useMemo(
    () => grouperParCategorie(articlesNonCoches),
    [articlesNonCoches],
  );
  const categoriesTriees = useMemo(
    () => Object.keys(groupesNonCoches).sort(),
    [groupesNonCoches],
  );

  return {
    listes,
    chargementListes,
    detailListe,
    chargementDetail,
    bioLocal,
    recurrents,
    predictionsInvites,
    suggestionsInvites,
    articles,
    articlesNonCoches,
    articlesCoches,
    groupesNonCoches,
    categoriesTriees,
  };
}
