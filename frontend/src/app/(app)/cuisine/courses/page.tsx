// ═══════════════════════════════════════════════════════════
// Courses — Bring!-style tiles par catégorie
// ═══════════════════════════════════════════════════════════

"use client";

import {
  CheckCheck,
  CheckCircle2,
  CheckSquare,
  Leaf,
  Loader2,
  QrCode,
  Square,
} from "lucide-react";

import { Button } from "@/composants/ui/button";
import { DialogueArticleCourses } from "@/composants/courses/dialogue-article-courses";
import { DialogueQrCourses } from "@/composants/courses/dialogue-qr-courses";
import { PanneauBioLocal } from "@/composants/courses/panneau-bio-local";
import { PanneauDetailCourses } from "@/composants/courses/panneau-detail-courses";
import { PanneauListesCourses } from "@/composants/courses/panneau-listes-courses";
import { CarteModeInvites } from "@/composants/cuisine/carte-mode-invites";
import { ScanneurMultiCodes } from "@/composants/scanneur-multi-codes";
import { utiliserPageCourses } from "@/crochets/utiliser-page-courses";

export default function PageCourses() {
  const {
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
  } = utiliserPageCourses();

  const messageTempsReel = !listeSelectionnee
    ? "Sélectionnez une liste pour activer le suivi et les annonces en temps réel."
    : chargementDetail
      ? "Synchronisation de la liste en cours…"
      : enEcoute
        ? "Ajout vocal actif : vos nouveaux articles sont annoncés automatiquement."
        : detailListe?.etat === "brouillon"
          ? `La liste ${detailListe.nom} est encore en brouillon : confirmez-la pour partager les changements.`
          : `${articlesNonCoches.length} article(s) restant(s) sur ${detailListe?.nom ?? "la liste active"}.`;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🛒 Courses</h1>
          <p className="text-muted-foreground">Gérez vos listes de courses</p>
        </div>

        {listeSelectionnee && (
          <div className="flex gap-2 overflow-x-auto pb-1">
            {detailListe?.etat === "brouillon" && (
              <Button size="sm" onClick={() => confirmer(undefined)} disabled={enConfirmation}>
                {enConfirmation ? (
                  <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircle2 className="mr-1 h-4 w-4" />
                )}
                Confirmer la liste
              </Button>
            )}

            <Button
              variant={modeSelection ? "default" : "outline"}
              size="sm"
              onClick={() => {
                setModeSelection((prev) => !prev);
                setArticlesSelectionnes(new Set());
              }}
            >
              {modeSelection ? (
                <CheckSquare className="mr-1 h-4 w-4" />
              ) : (
                <Square className="mr-1 h-4 w-4" />
              )}
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

            <Button variant="outline" size="sm" onClick={() => setPanneauBio((valeur) => !valeur)}>
              <Leaf className="mr-1 h-4 w-4" />
              Bio & Local
            </Button>

            <Button
              size="sm"
              variant="secondary"
              onClick={() => finaliserCourses(undefined)}
              disabled={
                enFinalisationCourses ||
                enCochageGlobal ||
                enCochageCategorie ||
                detailListe?.etat === "brouillon"
              }
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
              disabled={
                enValidation ||
                articlesNonCoches.length > 0 ||
                enFinalisationCourses ||
                detailListe?.etat === "brouillon"
              }
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

      <div className="rounded-lg border border-dashed bg-muted/30 px-4 py-3">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm font-medium">Suivi temps réel</p>
          {listeSelectionnee ? (
            <span className="text-xs text-muted-foreground">
              {detailListe?.nom ?? `Liste #${listeSelectionnee}`}
            </span>
          ) : null}
        </div>
        <p className="text-sm text-muted-foreground" role="status" aria-live="polite" aria-atomic="true">
          {messageTempsReel}
        </p>
      </div>

      <CarteModeInvites
        contexte={modeInvites}
        onChange={mettreAJourModeInvites}
        onReset={reinitialiserModeInvites}
        suggestionsEvenements={suggestionsInvites}
        description="Le contexte invité alimente les suggestions d'achats et les quantités recommandées pour la liste active."
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <PanneauListesCourses
          nomNouvelleListe={nomNouvelleListe}
          enCreationListe={enCreationListe}
          chargementListes={chargementListes}
          listeSelectionnee={listeSelectionnee}
          listes={listes}
          suggestionsInvites={suggestionsInvites}
          predictionsInvites={predictionsInvites}
          recurrents={recurrents}
          onNomNouvelleListeChange={setNomNouvelleListe}
          onCreerListe={() => creerListe(nomNouvelleListe.trim())}
          onSelectionnerListe={setListeSelectionnee}
          onAjouterRecurrent={(articleNom, categorie) => ajouter({ nom: articleNom, categorie })}
          onAjouterPrediction={(prediction) =>
            ajouter({
              nom: prediction.article_nom,
              quantite: prediction.quantite_suggeree,
              unite: prediction.unite_suggeree,
              categorie: prediction.categorie ?? prediction.rayon_magasin ?? undefined,
            })
          }
        />

        <PanneauDetailCourses
          listeSelectionnee={listeSelectionnee}
          detailListe={detailListe}
          chargementDetail={chargementDetail}
          enAjout={enAjout}
          estSupporte={estSupporte}
          enEcoute={enEcoute}
          modeSelection={modeSelection}
          enCochageSelection={enCochageSelection}
          enSuppressionSelection={enSuppressionSelection}
          enCochageCategorie={enCochageCategorie}
          enFinalisationCourses={enFinalisationCourses}
          articles={articles}
          articlesNonCoches={articlesNonCoches}
          articlesCoches={articlesCoches}
          categoriesTriees={categoriesTriees}
          groupesNonCoches={groupesNonCoches}
          articlesSelectionnes={articlesSelectionnes}
          inputAjoutRef={inputAjoutRef}
          erreursArticle={erreursArticle}
          regArticle={regArticle}
          submitArticle={submitArticle}
          onAjouterArticle={(data) => ajouter(data)}
          onToggleVocal={() => {
            if (enEcoute) {
              arreterEcoute();
            } else {
              demarrerEcoute();
            }
          }}
          onOuvrirScanneur={() => setScanneurOuvert(true)}
          onOuvrirDialogueArticle={() => setDialogueArticle(true)}
          onBasculerSelectionArticle={basculerSelectionArticle}
          onBasculerToutSelectionner={() => {
            if (articlesSelectionnes.size === articlesNonCoches.length) {
              setArticlesSelectionnes(new Set());
            } else {
              setArticlesSelectionnes(new Set(articlesNonCoches.map((article) => article.id)));
            }
          }}
          onCocherSelection={() => cocherSelection(undefined)}
          onSupprimerSelection={() => supprimerSelection(undefined)}
          onCocherCategorie={(categorie) => cocherCategorie(categorie)}
          onCocherArticle={(articleId, coche) => cocher({ articleId, coche })}
          onSupprimerArticle={supprimerAvecUndo}
        />
      </div>

      {panneauBio && bioLocal && bioLocal.suggestions.length > 0 && (
        <PanneauBioLocal bioLocal={bioLocal} />
      )}

      <DialogueArticleCourses
        ouvert={dialogueArticle}
        enAjout={enAjout}
        erreursArticle={erreursArticle}
        regArticle={regArticle}
        submitArticle={submitArticle}
        onOpenChange={setDialogueArticle}
        onAjouterArticle={(data) => ajouter(data)}
      />

      <ScanneurMultiCodes
        ouvert={scanneurOuvert}
        onFermer={() => setScanneurOuvert(false)}
        onImporter={importerDepuisScanner}
        labelImporter="Ajouter à la liste"
      />

      <DialogueQrCourses
        ouvert={dialogueQr}
        qrUrl={qrUrl}
        chargementQr={chargementQr}
        onTelecharger={telechargerQr}
        onOpenChange={(ouvert) => {
          setDialogueQr(ouvert);
          if (!ouvert) {
            setQrUrl((precedent) => {
              if (precedent) {
                URL.revokeObjectURL(precedent);
              }
              return null;
            });
          }
        }}
      />
    </div>
  );
}
