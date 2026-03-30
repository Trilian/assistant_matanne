"use client";

import Link from "next/link";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/composants/ui/card";

export default function AppError({
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
          <CardTitle className="text-destructive">🏠 Erreur Application</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {error.message || "Une erreur inattendue est survenue."}
          </p>
        </CardContent>
        <CardFooter className="flex gap-2">
          <Button onClick={reset}>Réessayer</Button>
          <Button variant="outline" asChild>
            <Link href="/">Retour à l&apos;accueil</Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
