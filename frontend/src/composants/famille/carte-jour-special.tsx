"use client";

import { Card, CardContent } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import type { JourSpecial } from "@/types/famille";

interface Props {
  jour: JourSpecial;
}

const typeEmoji: Record<string, string> = {
  ferie: "🏖️",
  pont: "🌉",
  creche: "🏫",
};

export function CarteJourSpecial({ jour }: Props) {
  const emoji = typeEmoji[jour.type] ?? "📅";

  return (
    <Card>
      <CardContent className="flex items-center gap-3 p-4">
        <span className="text-xl">{emoji}</span>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm truncate">{jour.nom}</p>
          <p className="text-xs text-muted-foreground">
            {new Date(jour.date).toLocaleDateString("fr-FR", {
              weekday: "long",
              day: "numeric",
              month: "long",
            })}
          </p>
        </div>
        <Badge variant="outline">
          {jour.jours_restants === 0
            ? "Aujourd'hui"
            : jour.jours_restants === 1
              ? "Demain"
              : `J-${jour.jours_restants}`}
        </Badge>
      </CardContent>
    </Card>
  );
}
