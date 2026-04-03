"use client";

import type { LucideIcon } from "lucide-react";

export function EtatVide({
  Icone,
  titre,
  description,
  action,
  className,
}: {
  Icone: LucideIcon;
  titre: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`flex flex-col items-center gap-3 rounded-xl border border-dashed p-8 text-center ${className ?? ""}`}>
      <div className="rounded-full bg-muted p-3">
        <Icone className="h-5 w-5 text-muted-foreground" />
      </div>
      <div>
        <p className="text-sm font-medium">{titre}</p>
        {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
      </div>
      {action}
    </div>
  );
}
