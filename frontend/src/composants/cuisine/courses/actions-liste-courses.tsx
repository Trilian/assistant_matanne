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
import type { ListeCourses } from "@/types/courses";

export function ActionsListeCourses({
  listeSelectionnee,
  detailListe,
  modeSelection,
  onToggleModeSelection,
  onConfirmer,
  enConfirmation,
  onCocherTout,
  enCochageGlobal,
  articlesNonCochesCount,
  onOuvrirQr,
  onToggleBio,
  onFinaliser,
  enFinalisationCourses,
  enCochageCategorie,
  onValider,
  enValidation,
}: {
  listeSelectionnee: number | null;
  detailListe?: ListeCourses;
  modeSelection: boolean;
  onToggleModeSelection: () => void;
  onConfirmer: () => void;
  enConfirmation: boolean;
  onCocherTout: () => void;
  enCochageGlobal: boolean;
  articlesNonCochesCount: number;
  onOuvrirQr: () => void;
  onToggleBio: () => void;
  onFinaliser: () => void;
  enFinalisationCourses: boolean;
  enCochageCategorie: boolean;
  onValider: () => void;
  enValidation: boolean;
}) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🛒 Courses</h1>
        <p className="text-muted-foreground">Gérez vos listes de courses</p>
      </div>

      {listeSelectionnee && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {detailListe?.etat === "brouillon" && (
            <Button size="sm" onClick={onConfirmer} disabled={enConfirmation}>
              {enConfirmation ? (
                <Loader2 className="mr-1 h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle2 className="mr-1 h-4 w-4" />
              )}
              Confirmer la liste
            </Button>
          )}

          <Button variant={modeSelection ? "default" : "outline"} size="sm" onClick={onToggleModeSelection}>
            {modeSelection ? <CheckSquare className="mr-1 h-4 w-4" /> : <Square className="mr-1 h-4 w-4" />}
            Sélection multiple
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={onCocherTout}
            disabled={enCochageGlobal || articlesNonCochesCount === 0}
          >
            <CheckCheck className="mr-1 h-4 w-4" />
            Tout cocher
          </Button>

          <Button variant="outline" size="sm" onClick={onOuvrirQr}>
            <QrCode className="mr-1 h-4 w-4" />
            QR partage
          </Button>

          <Button variant="outline" size="sm" onClick={onToggleBio}>
            <Leaf className="mr-1 h-4 w-4" />
            Bio & Local
          </Button>

          <Button
            size="sm"
            variant="secondary"
            onClick={onFinaliser}
            disabled={enFinalisationCourses || enCochageGlobal || enCochageCategorie || detailListe?.etat === "brouillon"}
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
            onClick={onValider}
            disabled={enValidation || articlesNonCochesCount > 0 || enFinalisationCourses || detailListe?.etat === "brouillon"}
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
  );
}
