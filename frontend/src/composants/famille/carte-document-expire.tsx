"use client";

import { FileWarning } from "lucide-react";
import { Card, CardContent } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import type { DocumentExpirant } from "@/types/famille";

interface Props {
  document: DocumentExpirant;
}

const severiteStyles = {
  danger: {
    badge: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    icon: "text-red-500",
  },
  warning: {
    badge: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
    icon: "text-orange-500",
  },
  info: {
    badge: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    icon: "text-blue-500",
  },
};

export function CarteDocumentExpire({ document }: Props) {
  const style = severiteStyles[document.severite] ?? severiteStyles.info;

  return (
    <Card>
      <CardContent className="flex items-center gap-3 p-4">
        <FileWarning className={`h-5 w-5 ${style.icon}`} />
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm truncate">{document.titre}</p>
        </div>
        <Badge variant="secondary" className={style.badge}>
          {document.jours_restants <= 1
            ? "Expire demain"
            : `${document.jours_restants}j restants`}
        </Badge>
      </CardContent>
    </Card>
  );
}
