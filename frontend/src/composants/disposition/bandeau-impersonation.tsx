"use client";

import { useEffect, useState } from "react";
import { Eye, Undo2 } from "lucide-react";
import { Button } from "@/composants/ui/button";

type MetaImpersonation = {
  targetUserId?: string;
  targetEmail?: string;
  reason?: string;
  expiresAt?: string;
};

const CLE_META = "impersonation_meta";
const CLE_ADMIN_TOKEN = "admin_access_token";

export function BandeauImpersonation() {
  const [meta, setMeta] = useState<MetaImpersonation | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const raw = localStorage.getItem(CLE_META);
    if (!raw) {
      setMeta(null);
      return;
    }

    try {
      setMeta(JSON.parse(raw) as MetaImpersonation);
    } catch {
      localStorage.removeItem(CLE_META);
      setMeta(null);
    }
  }, []);

  const quitterModeApercu = () => {
    if (typeof window === "undefined") {
      return;
    }

    const tokenAdmin = localStorage.getItem(CLE_ADMIN_TOKEN);
    if (tokenAdmin) {
      localStorage.setItem("access_token", tokenAdmin);
    }
    localStorage.removeItem(CLE_ADMIN_TOKEN);
    localStorage.removeItem(CLE_META);
    window.location.href = "/admin";
  };

  if (!meta) {
    return null;
  }

  const cible = meta.targetEmail || meta.targetUserId || "utilisateur";
  const expiration = meta.expiresAt
    ? new Date(meta.expiresAt).toLocaleString("fr-FR", {
        day: "2-digit",
        month: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      })
    : null;

  return (
    <div className="border-b border-amber-200 bg-amber-50/90 px-3 py-2 text-amber-950 dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-100">
      <div className="mx-auto flex max-w-7xl flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-2">
          <Eye className="mt-0.5 h-4 w-4 shrink-0" />
          <div>
            <p className="text-sm font-medium">Mode admin — aperçu utilisateur actif</p>
            <p className="text-xs opacity-80">
              Vous naviguez actuellement en tant que <strong>{cible}</strong>
              {expiration ? ` jusqu'au ${expiration}` : ""}
              {meta.reason ? ` · ${meta.reason}` : ""}.
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={quitterModeApercu}>
          <Undo2 className="mr-2 h-4 w-4" />Revenir au compte admin
        </Button>
      </div>
    </div>
  );
}
