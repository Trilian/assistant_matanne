"use client";

import { cn } from "@/bibliotheque/utils";
import { Skeleton } from "@/composants/ui/skeleton";

export function SkeletonPage({
  className,
  ariaLabel = "Chargement de la page",
  lignes = ["h-8 w-40", "h-10 w-64", "h-64 w-full"],
}: {
  className?: string;
  ariaLabel?: string;
  lignes?: string[];
}) {
  return (
    <div role="status" aria-label={ariaLabel} className={cn("space-y-4", className)}>
      {lignes.map((ligne, index) => (
        <Skeleton key={`${ligne}-${index}`} className={ligne} />
      ))}
    </div>
  );
}
