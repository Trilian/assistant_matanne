import { useMemo, useState } from "react";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";

export const NOMS_JOURS_SEMAINE = [
  "Dimanche",
  "Lundi",
  "Mardi",
  "Mercredi",
  "Jeudi",
  "Vendredi",
  "Samedi",
] as const;

export function construireJoursOrdonnes(jourDebut: number): string[] {
  return Array.from({ length: 7 }, (_, i) => NOMS_JOURS_SEMAINE[(jourDebut + i) % 7]);
}

function getDebutDeSemaine(offset: number, jourDebut: number): string {
  const now = new Date();
  const jour = now.getDay();
  const diff = (jour - jourDebut + 7) % 7;
  const debut = new Date(now);
  debut.setDate(now.getDate() - diff + offset * 7);
  return debut.toISOString().split("T")[0];
}

function getDatesDeSemaine(dateDebut: string): string[] {
  const dates: string[] = [];
  const lundi = new Date(dateDebut);
  for (let i = 0; i < 7; i++) {
    const d = new Date(lundi);
    d.setDate(lundi.getDate() + i);
    dates.push(d.toISOString().split("T")[0]);
  }
  return dates;
}

export function utiliserPlanningNavigation() {
  const [modeAffichage, setModeAffichage] = useState<"semaine" | "mois">("semaine");
  const [offsetSemaine, setOffsetSemaine] = useState(0);
  const [offsetMois, setOffsetMois] = useState(0);
  const [jourDebutSemaine, setJourDebutSemaine] = utiliserStockageLocal<number>("planning.jourDebutSemaine", 1);

  const dateDebut = useMemo(() => getDebutDeSemaine(offsetSemaine, jourDebutSemaine), [offsetSemaine, jourDebutSemaine]);
  const datesSemaine = useMemo(() => getDatesDeSemaine(dateDebut), [dateDebut]);
  const jours = useMemo(() => construireJoursOrdonnes(jourDebutSemaine), [jourDebutSemaine]);

  const moisDate = useMemo(() => {
    const date = new Date();
    date.setMonth(date.getMonth() + offsetMois);
    return date;
  }, [offsetMois]);

  const moisSelectionne = useMemo(
    () => `${moisDate.getFullYear()}-${String(moisDate.getMonth() + 1).padStart(2, "0")}`,
    [moisDate]
  );

  const moisLabel = useMemo(
    () =>
      new Date(dateDebut).toLocaleDateString("fr-FR", {
        month: "long",
        year: "numeric",
      }),
    [dateDebut]
  );

  const moisLabelComplet = useMemo(
    () =>
      moisDate.toLocaleDateString("fr-FR", {
        month: "long",
        year: "numeric",
      }),
    [moisDate]
  );

  const reinitialiserPeriode = () => {
    setOffsetSemaine(0);
    setOffsetMois(0);
  };

  const allerPrecedent = () => {
    if (modeAffichage === "semaine") {
      setOffsetSemaine((o) => o - 1);
    } else {
      setOffsetMois((o) => o - 1);
    }
  };

  const allerSuivant = () => {
    if (modeAffichage === "semaine") {
      setOffsetSemaine((o) => o + 1);
    } else {
      setOffsetMois((o) => o + 1);
    }
  };

  return {
    modeAffichage,
    setModeAffichage,
    offsetSemaine,
    setOffsetSemaine,
    offsetMois,
    setOffsetMois,
    jourDebutSemaine,
    setJourDebutSemaine,
    dateDebut,
    datesSemaine,
    jours,
    moisDate,
    moisSelectionne,
    moisLabel,
    moisLabelComplet,
    reinitialiserPeriode,
    allerPrecedent,
    allerSuivant,
  };
}
