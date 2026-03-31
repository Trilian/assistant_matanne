"use client";

import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import { Card, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";

export interface BlocHabitat {
  titre: string;
  description: string;
  chemin: string;
  Icone: LucideIcon;
}

interface GrilleBlocsHabitatProps {
  blocs: BlocHabitat[];
}

export function GrilleBlocsHabitat({ blocs }: GrilleBlocsHabitatProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {blocs.map(({ titre, description, chemin, Icone }) => (
        <Link key={chemin} href={chemin}>
          <Card className="h-full transition-all hover:-translate-y-0.5 hover:bg-accent/40">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg"><Icone className="h-4 w-4" /> {titre}</CardTitle>
              <CardDescription>{description}</CardDescription>
            </CardHeader>
          </Card>
        </Link>
      ))}
    </div>
  );
}
