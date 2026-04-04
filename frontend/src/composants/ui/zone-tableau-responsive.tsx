"use client";

import type { ReactNode } from "react";
import { MoveHorizontal } from "lucide-react";
import { cn } from "@/bibliotheque/utils";

interface ZoneTableauResponsiveProps {
  children: ReactNode;
  className?: string;
  containerClassName?: string;
  aide?: string;
}

export function ZoneTableauResponsive({
  children,
  className,
  containerClassName,
  aide = "Balayer horizontalement pour voir toutes les colonnes",
}: ZoneTableauResponsiveProps) {
  return (
    <div className={cn("space-y-2", className)}>
      <p className="flex items-center gap-1 text-xs text-muted-foreground sm:hidden">
        <MoveHorizontal className="h-3.5 w-3.5" />
        <span>{aide}</span>
      </p>
      <div className={cn("overflow-x-auto", containerClassName)}>{children}</div>
    </div>
  );
}
