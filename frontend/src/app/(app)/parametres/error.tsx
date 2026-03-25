"use client";

import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/composants/ui/card";

export default function ParametresError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex items-center justify-center p-8">
      <Card className="max-w-md w-full">
        <CardHeader>
          <CardTitle className="text-destructive">⚙️ Erreur Paramètres</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {error.message || "Une erreur est survenue dans les paramètres."}
          </p>
        </CardContent>
        <CardFooter className="flex gap-2">
          <Button onClick={reset}>Réessayer</Button>
          <Button variant="outline" asChild>
            <a href="/">Retour à l&apos;Accueil</a>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
