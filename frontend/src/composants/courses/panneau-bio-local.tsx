import { Leaf } from "lucide-react";

import { Badge } from "@/composants/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import type { SuggestionBioLocal } from "@/bibliotheque/api/courses";

type PanneauBioLocalProps = {
  bioLocal: {
    mois: string;
    nb_en_saison: number;
    suggestions: SuggestionBioLocal[];
  };
};

export function PanneauBioLocal({ bioLocal }: PanneauBioLocalProps) {
  if (bioLocal.suggestions.length === 0) {
    return null;
  }

  return (
    <Card className="border-green-300 bg-green-50 dark:border-green-800 dark:bg-green-950">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base text-green-700 dark:text-green-300">
          <Leaf className="h-4 w-4" />
          Suggestions Bio & Local — {bioLocal.mois}
        </CardTitle>
        <CardDescription className="text-green-600 dark:text-green-400">
          {bioLocal.nb_en_saison} article(s) de saison dans votre liste
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-2 sm:grid-cols-2">
          {bioLocal.suggestions.map((suggestion) => (
            <div
              key={suggestion.article_id}
              className="flex items-center justify-between rounded-lg border border-green-200 px-3 py-2 text-sm dark:border-green-800"
            >
              <div>
                <span className="font-medium">{suggestion.nom}</span>
                <div className="mt-0.5 flex gap-1">
                  {suggestion.en_saison && (
                    <Badge variant="secondary" className="text-[10px]">
                      🌱 Saison
                    </Badge>
                  )}
                  {suggestion.bio_disponible && (
                    <Badge variant="secondary" className="text-[10px]">
                      🌿 Bio
                    </Badge>
                  )}
                  {suggestion.local_disponible && (
                    <Badge variant="secondary" className="text-[10px]">
                      📍 Local
                    </Badge>
                  )}
                </div>
              </div>
              {suggestion.alternative_bio && (
                <span className="text-xs text-muted-foreground">
                  → {suggestion.alternative_bio}
                </span>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
