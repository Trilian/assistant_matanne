import { useMemo, useRef, useState } from "react";

import { utiliserModeInvites } from "@/crochets/utiliser-mode-invites";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";

/**
 * État UI brut de la page courses : sélection liste, dialogues, mode sélection, mode invités.
 */
export function utiliserCoursesEtat() {
  const {
    contexte: modeInvites,
    mettreAJour: mettreAJourModeInvites,
    reinitialiser: reinitialiserModeInvites,
  } = utiliserModeInvites();

  const [listeSelectionnee, setListeSelectionnee] = utiliserStockageLocal<number | null>(
    "courses.listeSelectionnee",
    null,
  );
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

  const contexteInvitesActif = modeInvites.actif && modeInvites.nbInvites > 0;

  const evenementsModeInvites = useMemo(() => {
    const items = [...modeInvites.evenements];
    if (modeInvites.occasion.trim()) {
      items.unshift(modeInvites.occasion.trim());
    }
    return Array.from(new Set(items.filter(Boolean))).slice(0, 6);
  }, [modeInvites.evenements, modeInvites.occasion]);

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
    setChargementQr,
    modeSelection,
    setModeSelection,
    articlesSelectionnes,
    setArticlesSelectionnes,
    inputAjoutRef,
    contexteInvitesActif,
    evenementsModeInvites,
  };
}
