// ═══════════════════════════════════════════════════════════
// Courses — Bring!-style tiles par catégorie
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useMemo, useState } from "react";
import {
  CheckCheck,
  CheckCircle2,
  CheckSquare,
  Leaf,
  Link2,
  Loader2,
  QrCode,
  Square,
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/composants/ui/button";
import { DialogueArticleCourses } from "@/composants/courses/dialogue-article-courses";
import { DialogueQrCourses } from "@/composants/courses/dialogue-qr-courses";
import { FiltreMagasins } from "@/composants/courses/filtre-magasins";
import { PanneauBioLocal } from "@/composants/courses/panneau-bio-local";
import { PanneauCorrespondancesDrive } from "@/composants/courses/panneau-correspondances-drive";
import { PanneauDetailCourses } from "@/composants/courses/panneau-detail-courses";
import { PanneauListesCourses } from "@/composants/courses/panneau-listes-courses";
import { CarteModeInvites } from "@/composants/cuisine/carte-mode-invites";
import { ScanneurMultiCodes } from "@/composants/scanneur-multi-codes";
import { obtenirArticlesDrive } from "@/bibliotheque/api/courses";
import { envoyerCoursesMagasinTelegram } from "@/bibliotheque/api/telegram";
import { PREFIXE_API, URL_API } from "@/bibliotheque/constantes";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { utiliserPageCourses } from "@/crochets/utiliser-page-courses";
import type { MagasinCible } from "@/types/courses";

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

  // ─── Filtre par magasin ─────────────────────────────────
  const [magasinActif, setMagasinActif] = useState<string | null>(null);
  const [enEnvoiTelegram, setEnEnvoiTelegram] = useState(false);
  const [extensionDriveDisponible, setExtensionDriveDisponible] = useState(false);
  const [afficherCorrespondancesDrive, setAfficherCorrespondancesDrive] = useState(false);

  const { data: articlesDrive = [] } = utiliserRequete(
    ["courses", "articles-drive", String(listeSelectionnee)],
    () => obtenirArticlesDrive(listeSelectionnee!),
    { enabled: listeSelectionnee !== null }
  );

  const compteursMagasins = useMemo(() => {
    const compteurs: Record<string, number> = {};
    for (const article of articles) {
      const cle = article.magasin_cible || "non_assigne";
      compteurs[cle] = (compteurs[cle] ?? 0) + 1;
    }
    return compteurs;
  }, [articles]);

  const articlesAvecStatutDrive = useMemo(() => {
    const idsMappes = new Set(
      articlesDrive.filter((article) => Boolean(article.correspondance?.produit_drive_id)).map((article) => article.id)
    );

    return articles.map((article) => ({
      ...article,
      drive_mappe: article.magasin_cible === "carrefour_drive" ? idsMappes.has(article.id) : undefined,
    }));
  }, [articles, articlesDrive]);

  const driveStats = useMemo(() => {
    const driveArticles = articlesAvecStatutDrive.filter((article) => article.magasin_cible === "carrefour_drive");
    const mappes = driveArticles.filter((article) => article.drive_mappe).length;
    return {
      mappes,
      aMapper: Math.max(0, driveArticles.length - mappes),
    };
  }, [articlesAvecStatutDrive]);

  const articlesFiltres = useMemo(() => {
    if (!magasinActif) return articlesAvecStatutDrive;
    return articlesAvecStatutDrive.filter((a) => a.magasin_cible === magasinActif);
  }, [articlesAvecStatutDrive, magasinActif]);

  const articlesNonCochesFiltres = useMemo(
    () => articlesFiltres.filter((a) => !a.est_coche),
    [articlesFiltres]
  );

  const articlesCochesFiltres = useMemo(
    () => articlesFiltres.filter((a) => a.est_coche),
    [articlesFiltres]
  );

  const groupesNonCochesFiltres = useMemo(() => {
    return articlesNonCochesFiltres.reduce<Record<string, typeof articlesNonCochesFiltres>>(
      (acc, article) => {
        const categorie = article.categorie || "Autre";
        (acc[categorie] ??= []).push(article);
        return acc;
      },
      {}
    );
  }, [articlesNonCochesFiltres]);

  const categoriesTrieesFiltrees = useMemo(
    () => Object.keys(groupesNonCochesFiltres).sort(),
    [groupesNonCochesFiltres]
  );

  const handleEnvoyerTelegram = async (magasin: MagasinCible) => {
    if (!listeSelectionnee) return;
    setEnEnvoiTelegram(true);
    try {
      await envoyerCoursesMagasinTelegram(listeSelectionnee, magasin);
      toast.success("Liste envoyée sur Telegram");
    } catch {
      toast.error("Erreur lors de l'envoi Telegram");
    } finally {
      setEnEnvoiTelegram(false);
    }
  };

  useEffect(() => {
    const estPret = document.documentElement.dataset.assistantMatanneDriveBridge === "ready";
    if (estPret) {
      setExtensionDriveDisponible(true);
    }

    const handleBridgeReady = () => setExtensionDriveDisponible(true);
    const handleDriveResult = (event: Event) => {
      const detail = (event as CustomEvent<{ ok?: boolean; total?: number; mappes?: number; recherches?: number; error?: string }>).detail;
      if (!detail) return;

      if (detail.ok) {
        toast.success(
          `Drive lancé : ${detail.mappes ?? 0} produit(s) mappé(s), ${detail.recherches ?? 0} recherche(s) ouverte(s).`
        );
      } else if (detail.error) {
        toast.error(`Extension Drive : ${detail.error}`);
      }
    };

    window.addEventListener("assistant-matanne-drive-bridge-ready", handleBridgeReady);
    window.addEventListener("assistant-matanne-drive-sync-result", handleDriveResult as EventListener);

    return () => {
      window.removeEventListener("assistant-matanne-drive-bridge-ready", handleBridgeReady);
      window.removeEventListener("assistant-matanne-drive-sync-result", handleDriveResult as EventListener);
    };
  }, []);

  const handleSyncDrive = () => {
    if (!listeSelectionnee) return;

    const apiBaseUrl = `${URL_API}${PREFIXE_API}`;
    const apiToken = typeof window !== "undefined" ? window.localStorage.getItem("access_token") : null;

    if (extensionDriveDisponible) {
      window.postMessage(
        {
          source: "assistant-matanne",
          type: "SYNC_CARREFOUR_DRIVE",
          payload: {
            listeId: listeSelectionnee,
            apiBaseUrl,
            apiToken,
          },
        },
        window.location.origin
      );
      toast.info("Demande envoyée à l'extension Carrefour Drive...");
      return;
    }

    window.open("https://www.carrefour.fr/courses-en-ligne", "_blank", "noopener,noreferrer");
    toast.info("Carrefour Drive ouvert. Installe l'extension pour l'ajout automatique en 1 clic.");
  };

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
              variant="outline"
              size="sm"
              onClick={() => setAfficherCorrespondancesDrive((valeur) => !valeur)}
            >
              <Link2 className="mr-1 h-4 w-4" />
              Correspondances Drive
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

      {listeSelectionnee && (
        <>
          <FiltreMagasins
            compteurs={compteursMagasins}
            magasinActif={magasinActif}
            driveStats={driveStats}
            onChangerMagasin={setMagasinActif}
            onEnvoyerTelegram={handleEnvoyerTelegram}
            onSyncDrive={handleSyncDrive}
            enEnvoiTelegram={enEnvoiTelegram}
          />

          {magasinActif === "carrefour_drive" && (
            <div className="rounded-lg border border-dashed bg-muted/30 px-4 py-3 text-sm">
              <p className="font-medium">Guide rapide Carrefour Drive</p>
              <ol className="mt-2 list-decimal space-y-1 pl-5 text-muted-foreground">
                <li>Ajoute ou filtre tes articles sur <strong>Carrefour Drive</strong>.</li>
                <li>Clique sur <strong>Ajouter au Drive</strong>.</li>
                <li>Si un article est <strong>À mapper</strong>, choisis le bon produit Carrefour une fois.</li>
                <li>Au clic sur <strong>Ajouter au panier</strong>, la correspondance est mémorisée automatiquement.</li>
              </ol>
              <p className="mt-2 text-xs text-muted-foreground">
                Configuration détaillée : <strong>Paramètres → Intégrations</strong>.
              </p>
            </div>
          )}
        </>
      )}

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
          articles={articlesFiltres}
          articlesNonCoches={articlesNonCochesFiltres}
          articlesCoches={articlesCochesFiltres}
          categoriesTriees={categoriesTrieesFiltrees}
          magasinActif={magasinActif}
          groupesNonCoches={groupesNonCochesFiltres}
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
            if (articlesSelectionnes.size === articlesNonCochesFiltres.length) {
              setArticlesSelectionnes(new Set());
            } else {
              setArticlesSelectionnes(new Set(articlesNonCochesFiltres.map((article) => article.id)));
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

      {afficherCorrespondancesDrive && <PanneauCorrespondancesDrive />}

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
