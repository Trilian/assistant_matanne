"use client";

import { useQuery } from "@tanstack/react-query";
import { FileWarning, AlertTriangle, CheckCircle } from "lucide-react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { clientApi } from "@/bibliotheque/api/client";

interface DocumentExpirant {
  id: number;
  titre: string;
  categorie: string;
  membre_famille: string;
  date_expiration: string;
  jours_restants: number;
  est_expire: boolean;
  severite: "danger" | "warning" | "info";
}

interface DocumentsExpirantsResponse {
  items: DocumentExpirant[];
  total: number;
  nb_expires: number;
  nb_bientot: number;
  message: string;
}

async function fetchDocumentsExpirants(): Promise<DocumentsExpirantsResponse> {
  const { data } = await clientApi.get("/api/v1/dashboard/documents-expirants", {
    params: { jours_horizon: 60 },
  });
  return data;
}

const severiteStyles = {
  danger: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  warning: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  info: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
} as const;

export function WidgetDocumentsExpirants() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard", "documents-expirants"],
    queryFn: fetchDocumentsExpirants,
    staleTime: 5 * 60 * 1000,
    refetchInterval: 30 * 60 * 1000,
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <FileWarning className="h-4 w-4" />
            Documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Chargement...</p>
        </CardContent>
      </Card>
    );
  }

  if (error || !data || data.total === 0) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            Documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Tous les documents sont a jour</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-orange-500" />
          Documents a renouveler
          {data.total > 0 && (
            <Badge variant="destructive" className="ml-auto text-xs">
              {data.total}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {(data.items ?? []).slice(0, 5).map((doc) => (
          <Link
            key={doc.id}
            href="/famille/documents"
            className="flex items-center gap-2 p-2 rounded-md hover:bg-accent transition-colors"
          >
            <FileWarning className={`h-4 w-4 shrink-0 ${
              doc.severite === "danger" ? "text-red-500" :
              doc.severite === "warning" ? "text-orange-500" : "text-blue-500"
            }`} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{doc.titre}</p>
              <p className="text-xs text-muted-foreground">{doc.membre_famille}</p>
            </div>
            <Badge variant="secondary" className={`text-xs shrink-0 ${severiteStyles[doc.severite]}`}>
              {doc.est_expire
                ? "Expire"
                : doc.jours_restants <= 1
                  ? "Demain"
                  : `${doc.jours_restants}j`}
            </Badge>
          </Link>
        ))}

        {data.total > 5 && (
          <Link
            href="/famille/documents"
            className="block text-xs text-primary hover:underline text-center pt-1"
          >
            Voir les {data.total} documents
          </Link>
        )}
      </CardContent>
    </Card>
  );
}
