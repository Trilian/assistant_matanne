"use client";

import type { ReactNode } from "react";
import { Card, CardContent } from "@/composants/ui/card";

interface EtatVidePlanningProps {
  icon: ReactNode;
  message: string;
}

export function EtatVidePlanning({ icon, message }: EtatVidePlanningProps) {
  return (
    <Card>
      <CardContent className="py-10 text-center text-muted-foreground">
        <div className="mx-auto mb-2 h-8 w-8 opacity-50">{icon}</div>
        {message}
      </CardContent>
    </Card>
  );
}
