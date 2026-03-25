"use client";

import Link from "next/link";
import { Cake } from "lucide-react";
import { Card, CardContent } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import type { AnniversaireContexte } from "@/types/famille";

interface Props {
  anniversaire: AnniversaireContexte;
  urgence?: "danger" | "warning" | "info";
}

const urgenceBadge = {
  danger: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  warning: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  info: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
};

export function CarteAnniversaire({ anniversaire, urgence }: Props) {
  const jours = anniversaire.jours_restants;
  const badge = urgence ?? (jours <= 2 ? "danger" : jours <= 7 ? "warning" : "info");
  const countdownText =
    jours === 0 ? "Aujourd'hui !" : jours === 1 ? "Demain" : `Dans ${jours} jours`;

  return (
    <Card className="relative overflow-hidden">
      <CardContent className="flex items-center gap-3 p-4">
        <div className="rounded-full bg-pink-100 dark:bg-pink-900/30 p-2">
          <Cake className="h-5 w-5 text-pink-600 dark:text-pink-400" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm truncate">
            {anniversaire.nom_personne}
            {anniversaire.age != null && (
              <span className="text-muted-foreground ml-1">
                ({anniversaire.age + 1} ans)
              </span>
            )}
          </p>
          <p className="text-xs text-muted-foreground">{anniversaire.relation}</p>
        </div>
        <Badge variant="secondary" className={urgenceBadge[badge]}>
          {countdownText}
        </Badge>
      </CardContent>
      {anniversaire.idees_cadeaux && (
        <div className="px-4 pb-3">
          <Link
            href="/famille/anniversaires"
            className="text-xs text-primary hover:underline"
          >
            Voir idées cadeaux →
          </Link>
        </div>
      )}
    </Card>
  );
}
