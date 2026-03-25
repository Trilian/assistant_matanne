"use client";

import { Card, CardContent, CardFooter } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Sparkles } from "lucide-react";

interface Props {
  titre: string;
  description: string;
  source: string;
  actionLabel?: string;
  onAction?: () => void;
}

const sourceColors: Record<string, string> = {
  weekend: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300",
  activites: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  soiree: "bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300",
  achats: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
};

export function CarteSuggestionIA({
  titre,
  description,
  source,
  actionLabel = "Voir détails",
  onAction,
}: Props) {
  const colorClass = sourceColors[source] ?? "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300";

  return (
    <Card className="bg-gradient-to-br from-purple-50/50 to-indigo-50/50 dark:from-purple-950/20 dark:to-indigo-950/20">
      <CardContent className="pt-5 space-y-3">
        <div className="flex items-start gap-2">
          <Sparkles className="h-4 w-4 text-purple-500 mt-0.5 shrink-0" />
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-sm">{titre}</h3>
            <p className="text-xs text-muted-foreground mt-1">{description}</p>
          </div>
          <Badge variant="outline" className={colorClass}>
            {source}
          </Badge>
        </div>
      </CardContent>
      {onAction && (
        <CardFooter className="pt-0">
          <Button size="sm" variant="outline" onClick={onAction} className="w-full">
            {actionLabel}
          </Button>
        </CardFooter>
      )}
    </Card>
  );
}
