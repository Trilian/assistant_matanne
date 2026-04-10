import { Plus, RotateCcw, ShoppingCart } from "lucide-react";

import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { EtatVide } from "@/composants/ui/etat-vide";
import { Input } from "@/composants/ui/input";
import { Skeleton } from "@/composants/ui/skeleton";
import type {
  ArticleRecurrent,
  PredictionCoursesItem,
} from "@/bibliotheque/api/courses";
import type { ListeCourses } from "@/types/courses";

type PanneauListesCoursesProps = {
  nomNouvelleListe: string;
  enCreationListe: boolean;
  chargementListes: boolean;
  listeSelectionnee: number | null;
  listes?: ListeCourses[];
  suggestionsInvites: string[];
  predictionsInvites?: { items: PredictionCoursesItem[] };
  recurrents?: { suggestions: ArticleRecurrent[] };
  onNomNouvelleListeChange: (valeur: string) => void;
  onCreerListe: () => void;
  onSelectionnerListe: (id: number) => void;
  onAjouterRecurrent: (articleNom: string, categorie?: string) => void;
  onAjouterPrediction: (prediction: PredictionCoursesItem) => void;
};

export function PanneauListesCourses({
  nomNouvelleListe,
  enCreationListe,
  chargementListes,
  listeSelectionnee,
  listes,
  suggestionsInvites,
  predictionsInvites,
  recurrents,
  onNomNouvelleListeChange,
  onCreerListe,
  onSelectionnerListe,
  onAjouterRecurrent,
  onAjouterPrediction,
}: PanneauListesCoursesProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Mes listes</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <form
          className="flex gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            if (nomNouvelleListe.trim()) {
              onCreerListe();
            }
          }}
        >
          <Input
            placeholder="Nouvelle liste..."
            value={nomNouvelleListe}
            onChange={(event) => onNomNouvelleListeChange(event.target.value)}
          />
          <Button
            type="submit"
            size="icon"
            disabled={enCreationListe || !nomNouvelleListe.trim()}
            aria-label="Créer la liste"
          >
            <Plus className="h-4 w-4" />
          </Button>
        </form>

        {chargementListes ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, index) => (
              <Skeleton key={index} className="h-12 w-full" />
            ))}
          </div>
        ) : !listes?.length ? (
          <EtatVide
            Icone={ShoppingCart}
            titre="Aucune liste de courses"
            description="Cree ta premiere liste pour commencer."
            className="py-6"
          />
        ) : (
          <div className="space-y-1">
            {listes.map((liste) => (
              <button
                key={liste.id}
                onClick={() => onSelectionnerListe(liste.id)}
                className={`w-full rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-accent ${
                  listeSelectionnee === liste.id ? "bg-accent" : ""
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="truncate font-medium">{liste.nom}</span>
                  <Badge variant="secondary" className="text-xs">
                    {liste.nombre_coche}/{liste.nombre_articles}
                  </Badge>
                </div>
              </button>
            ))}
          </div>
        )}

        {recurrents?.suggestions?.length && listeSelectionnee && (
          <div className="mt-3 border-t pt-3">
            <p className="mb-2 flex items-center gap-1 text-xs font-medium text-muted-foreground">
              <RotateCcw className="h-3 w-3" />
              Achats récurrents
            </p>
            <div className="space-y-1">
              {recurrents.suggestions.slice(0, 5).map((suggestion) => (
                <button
                  key={suggestion.article_nom}
                  className="w-full rounded px-2 py-1 text-left text-xs transition-colors hover:bg-accent"
                  onClick={() =>
                    onAjouterRecurrent(
                      suggestion.article_nom,
                      suggestion.categorie ?? undefined,
                    )
                  }
                >
                  <span className="font-medium">{suggestion.article_nom}</span>
                  <span className="ml-1 text-muted-foreground">
                    +{suggestion.retard_jours}j retard
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {listeSelectionnee && predictionsInvites?.items?.length && (
          <div className="mt-3 border-t pt-3">
            <p className="mb-2 text-xs font-medium text-muted-foreground">
              Suggestions invites
            </p>
            <div className="space-y-2">
              {predictionsInvites.items.slice(0, 5).map((prediction) => (
                <button
                  key={`${prediction.article_nom}-${prediction.quantite_suggeree}`}
                  className="w-full rounded-md border px-2 py-2 text-left transition-colors hover:bg-accent"
                  onClick={() => onAjouterPrediction(prediction)}
                >
                  <div className="flex items-center justify-between gap-2 text-xs">
                    <span className="font-medium text-foreground">
                      {prediction.article_nom}
                    </span>
                    <span className="text-muted-foreground">
                      x{prediction.quantite_suggeree} {prediction.unite_suggeree}
                    </span>
                  </div>
                  <p className="mt-1 text-[11px] text-muted-foreground">
                    Confiance {Math.round(prediction.confiance_contextualisee * 100)}%
                    {prediction.contexte_applique?.raisons?.length ? (
                      <span>
                        {" "}· {prediction.contexte_applique.raisons.join(", ")}
                      </span>
                    ) : null}
                  </p>
                </button>
              ))}
            </div>
          </div>
        )}

        {suggestionsInvites.length > 0 && (
          <div className="flex flex-wrap gap-1 border-t pt-3">
            {suggestionsInvites.map((suggestion) => (
              <Badge key={suggestion} variant="outline" className="text-[10px]">
                {suggestion}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
