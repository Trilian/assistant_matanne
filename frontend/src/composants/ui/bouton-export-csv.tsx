"use client";

import type { ComponentProps } from "react";
import { Download } from "lucide-react";
import { CSVLink } from "react-csv";
import { Button } from "@/composants/ui/button";

type LigneExportCsv = Record<string, string | number | boolean | null | undefined>;

interface BoutonExportCsvProps {
  data: LigneExportCsv[];
  filename: string;
  label?: string;
  className?: string;
  disabled?: boolean;
  variant?: ComponentProps<typeof Button>["variant"];
  size?: ComponentProps<typeof Button>["size"];
}

export function BoutonExportCsv({
  data,
  filename,
  label = "Export CSV",
  className,
  disabled,
  variant = "outline",
  size = "sm",
}: BoutonExportCsvProps) {
  const estDesactive = disabled || data.length === 0;

  if (estDesactive) {
    return (
      <Button variant={variant} size={size} className={className} disabled>
        <Download className="mr-2 h-4 w-4" />
        {label}
      </Button>
    );
  }

  return (
    <Button asChild variant={variant} size={size} className={className}>
      <CSVLink data={data} filename={filename} separator=";">
        <Download className="mr-2 h-4 w-4" />
        {label}
      </CSVLink>
    </Button>
  );
}
