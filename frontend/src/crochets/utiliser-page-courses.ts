import { useRef } from "react";

import { utiliserCoursesEtat } from "@/crochets/utiliser-courses-etat";
import { utiliserCoursesRequetes } from "@/crochets/utiliser-courses-requetes";
import { utiliserCoursesMutations } from "@/crochets/utiliser-courses-mutations";
import { utiliserCoursesFormulaire } from "@/crochets/utiliser-courses-formulaire";

/**
 * Hook principal de la page courses.
 * Orchestre les 4 sous-hooks specialises (etat, requetes, mutations, formulaire).
 * Le ref resetArticleRef brise la dependance circulaire mutations <-> formulaire.
 */
export function utiliserPageCourses() {
  const etat = utiliserCoursesEtat();

  const requetes = utiliserCoursesRequetes({
    listeSelectionnee: etat.listeSelectionnee,
    panneauBio: etat.panneauBio,
    contexteInvitesActif: etat.contexteInvitesActif,
    evenementsModeInvites: etat.evenementsModeInvites,
    modeInvitesNbInvites: etat.modeInvites.nbInvites,
    setListeSelectionnee: etat.setListeSelectionnee,
  });

  // Ref pour briser la dependance circulaire : mutations a besoin de resetArticle
  // qui vient de formulaireBase, mais formulaireBase a besoin de supprimerSelection
  // qui vient de mutations.
  const resetArticleRef = useRef<() => void>(() => {});

  const mutations = utiliserCoursesMutations({
    listeSelectionnee: etat.listeSelectionnee,
    setListeSelectionnee: etat.setListeSelectionnee,
    detailListe: requetes.detailListe,
    articlesNonCoches: requetes.articlesNonCoches,
    articlesSelectionnes: etat.articlesSelectionnes,
    setArticlesSelectionnes: etat.setArticlesSelectionnes,
    setModeSelection: etat.setModeSelection,
    setDialogueArticle: etat.setDialogueArticle,
    resetArticle: () => resetArticleRef.current(),
  });

  const formulaireBase = utiliserCoursesFormulaire({
    listeSelectionnee: etat.listeSelectionnee,
    detailListe: requetes.detailListe,
    modeSelection: etat.modeSelection,
    articlesSelectionnes: etat.articlesSelectionnes,
    setDialogueArticle: etat.setDialogueArticle,
    inputAjoutRef: etat.inputAjoutRef,
    supprimerSelection: () => mutations.supprimerSelection(),
    qrUrl: etat.qrUrl,
    setDialogueQr: etat.setDialogueQr,
    setQrUrl: etat.setQrUrl,
    setChargementQr: etat.setChargementQr,
  });

  // Mise a jour du ref apres chaque rendu — toujours pointe vers resetArticle courant
  resetArticleRef.current = formulaireBase.resetArticle;

  return {
    // Mode invites
    modeInvites: etat.modeInvites,
    mettreAJourModeInvites: etat.mettreAJourModeInvites,
    reinitialiserModeInvites: etat.reinitialiserModeInvites,
    evenementsModeInvites: etat.evenementsModeInvites,
    // Selection liste
    listeSelectionnee: etat.listeSelectionnee,
    setListeSelectionnee: etat.setListeSelectionnee,
    nomNouvelleListe: etat.nomNouvelleListe,
    setNomNouvelleListe: etat.setNomNouvelleListe,
    // Dialogues
    dialogueArticle: etat.dialogueArticle,
    setDialogueArticle: etat.setDialogueArticle,
    scanneurOuvert: etat.scanneurOuvert,
    setScanneurOuvert: etat.setScanneurOuvert,
    panneauBio: etat.panneauBio,
    setPanneauBio: etat.setPanneauBio,
    dialogueQr: etat.dialogueQr,
    setDialogueQr: etat.setDialogueQr,
    qrUrl: etat.qrUrl,
    setQrUrl: etat.setQrUrl,
    chargementQr: etat.chargementQr,
    // Mode selection
    modeSelection: etat.modeSelection,
    setModeSelection: etat.setModeSelection,
    articlesSelectionnes: etat.articlesSelectionnes,
    setArticlesSelectionnes: etat.setArticlesSelectionnes,
    inputAjoutRef: etat.inputAjoutRef,
    // Donnees
    listes: requetes.listes,
    detailListe: requetes.detailListe,
    bioLocal: requetes.bioLocal,
    recurrents: requetes.recurrents,
    predictionsInvites: requetes.predictionsInvites,
    suggestionsInvites: requetes.suggestionsInvites,
    chargementListes: requetes.chargementListes,
    chargementDetail: requetes.chargementDetail,
    articles: requetes.articles,
    articlesNonCoches: requetes.articlesNonCoches,
    articlesCoches: requetes.articlesCoches,
    groupesNonCoches: requetes.groupesNonCoches,
    categoriesTriees: requetes.categoriesTriees,
    // Mutations
    creerListe: mutations.creerListe,
    enCreationListe: mutations.enCreationListe,
    ajouter: mutations.ajouter,
    enAjout: mutations.enAjout,
    cocher: mutations.cocher,
    confirmer: mutations.confirmer,
    enConfirmation: mutations.enConfirmation,
    valider: mutations.valider,
    enValidation: mutations.enValidation,
    cocherTout: mutations.cocherTout,
    enCochageGlobal: mutations.enCochageGlobal,
    cocherSelection: mutations.cocherSelection,
    enCochageSelection: mutations.enCochageSelection,
    supprimerSelection: mutations.supprimerSelection,
    enSuppressionSelection: mutations.enSuppressionSelection,
    cocherCategorie: mutations.cocherCategorie,
    enCochageCategorie: mutations.enCochageCategorie,
    finaliserCourses: mutations.finaliserCourses,
    enFinalisationCourses: mutations.enFinalisationCourses,
    basculerSelectionArticle: mutations.basculerSelectionArticle,
    supprimerAvecUndo: mutations.supprimerAvecUndo,
    importerDepuisScanner: mutations.importerDepuisScanner,
    // Formulaire
    regArticle: formulaireBase.regArticle,
    submitArticle: formulaireBase.submitArticle,
    erreursArticle: formulaireBase.erreursArticle,
    enEcoute: formulaireBase.enEcoute,
    estSupporte: formulaireBase.estSupporte,
    demarrerEcoute: formulaireBase.demarrerEcoute,
    arreterEcoute: formulaireBase.arreterEcoute,
    ouvrirQrPartage: formulaireBase.ouvrirQrPartage,
    telechargerQr: formulaireBase.telechargerQr,
  };
}