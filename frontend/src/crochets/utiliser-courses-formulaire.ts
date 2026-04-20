import type { Dispatch, RefObject, SetStateAction } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { obtenirQrPartageListe } from "@/bibliotheque/api/courses";
import {
  schemaArticleCourses,
  type DonneesArticleCourses,
} from "@/bibliotheque/validateurs";
import { utiliserRaccourcisPage } from "@/crochets/utiliser-raccourcis-page";
import { utiliserReconnaissanceVocale } from "@/crochets/utiliser-reconnaissance-vocale";
import type { ListeCourses } from "@/types/courses";

type ParamsFormulaire = {
  listeSelectionnee: number | null;
  detailListe: ListeCourses | undefined;
  modeSelection: boolean;
  articlesSelectionnes: Set<number>;
  setDialogueArticle: Dispatch<SetStateAction<boolean>>;
  inputAjoutRef: RefObject<HTMLInputElement | null>;
  supprimerSelection: () => void;
  qrUrl: string | null;
  setDialogueQr: Dispatch<SetStateAction<boolean>>;
  setQrUrl: Dispatch<SetStateAction<string | null>>;
  setChargementQr: Dispatch<SetStateAction<boolean>>;
};

/**
 * Formulaire article, reconnaissance vocale, partage QR et raccourcis clavier de la page courses.
 */
export function utiliserCoursesFormulaire(p: ParamsFormulaire) {
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
      if (!nettoye) return;
      definirValeurArticle("nom", nettoye, { shouldValidate: true, shouldDirty: true });
      toast.success(`Article détecté: ${nettoye}`);
    },
  });

  utiliserRaccourcisPage([
    {
      touche: "n",
      action: () => {
        if (p.listeSelectionnee) p.setDialogueArticle(true);
      },
      actif: !!p.listeSelectionnee,
    },
    {
      touche: "s",
      action: () => p.inputAjoutRef.current?.focus(),
      actif: !!p.listeSelectionnee,
    },
    {
      touche: "Delete",
      action: () => {
        if (p.modeSelection && p.articlesSelectionnes.size > 0) {
          p.supprimerSelection();
        }
      },
      actif: p.modeSelection && p.articlesSelectionnes.size > 0,
    },
  ]);

  async function ouvrirQrPartage() {
    if (!p.listeSelectionnee) return;
    p.setDialogueQr(true);
    p.setChargementQr(true);
    try {
      const blob = await obtenirQrPartageListe(p.listeSelectionnee);
      const url = URL.createObjectURL(blob);
      p.setQrUrl((precedent) => {
        if (precedent) URL.revokeObjectURL(precedent);
        return url;
      });
    } catch {
      toast.error("Impossible de générer le QR de partage");
    } finally {
      p.setChargementQr(false);
    }
  }

  function telechargerQr() {
    if (!p.qrUrl || !p.detailListe) return;
    const ancre = document.createElement("a");
    ancre.href = p.qrUrl;
    ancre.download = `courses-${p.detailListe.nom.replace(/\s+/g, "-").toLowerCase()}.png`;
    document.body.appendChild(ancre);
    ancre.click();
    document.body.removeChild(ancre);
  }

  return {
    regArticle,
    submitArticle,
    resetArticle,
    erreursArticle,
    enEcoute,
    estSupporte,
    demarrerEcoute,
    arreterEcoute,
    ouvrirQrPartage,
    telechargerQr,
  };
}
