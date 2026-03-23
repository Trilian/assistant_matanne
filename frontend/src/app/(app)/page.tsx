// ═══════════════════════════════════════════════════════════
// Tableau de bord — Page d'accueil
// ═══════════════════════════════════════════════════════════

"use client";

import {
  ChefHat,
  ShoppingCart,
  CalendarDays,
  AlertTriangle,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { utiliserRequete } from "@/hooks/utiliser-api";
import { obtenirTableauBord } from "@/lib/api/tableau-bord";
import { utiliserAuth } from "@/hooks/utiliser-auth";

export default function PageAccueil() {
  const { utilisateur } = utiliserAuth();
  const { data, isLoading } = utiliserRequete(["tableau-bord"], obtenirTableauBord);

  return (
    <div className="space-y-6">
      {/* Salutation */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Bonjour {utilisateur?.nom ?? ""} 👋
        </h1>
        <p className="text-muted-foreground">
          Voici le résumé de votre journée
        </p>
      </div>

      {/* Cartes métriques */}
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        <CarteMetrique
          titre="Repas aujourd'hui"
          valeur={data?.repas_aujourd_hui.length ?? 0}
          icone={<ChefHat className="h-4 w-4" />}
          lien="/cuisine/planning"
          chargement={isLoading}
        />
        <CarteMetrique
          titre="Articles à acheter"
          valeur={data?.articles_courses_restants ?? 0}
          icone={<ShoppingCart className="h-4 w-4" />}
          lien="/cuisine/courses"
          chargement={isLoading}
        />
        <CarteMetrique
          titre="Activités semaine"
          valeur={data?.activites_semaine ?? 0}
          icone={<CalendarDays className="h-4 w-4" />}
          lien="/planning"
          chargement={isLoading}
        />
        <CarteMetrique
          titre="Alertes entretien"
          valeur={data?.taches_entretien_urgentes ?? 0}
          icone={<AlertTriangle className="h-4 w-4" />}
          lien="/maison/entretien"
          chargement={isLoading}
          alerte={(data?.taches_entretien_urgentes ?? 0) > 0}
        />
      </div>

      {/* Actions rapides */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Actions rapides</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 grid-cols-2 sm:grid-cols-4">
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <Link href="/cuisine/recettes/nouveau">
                <ChefHat className="h-5 w-5" />
                <span className="text-xs">Nouvelle recette</span>
              </Link>
            </Button>
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <Link href="/cuisine/courses">
                <ShoppingCart className="h-5 w-5" />
                <span className="text-xs">Liste courses</span>
              </Link>
            </Button>
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <Link href="/cuisine/planning">
                <CalendarDays className="h-5 w-5" />
                <span className="text-xs">Planning repas</span>
              </Link>
            </Button>
            <Button variant="outline" asChild className="h-auto py-3 flex-col gap-1">
              <Link href="/outils/chat-ia">
                <Sparkles className="h-5 w-5" />
                <span className="text-xs">Chat IA</span>
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Suggestion dîner IA */}
      {data?.suggestion_diner && (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Suggestion du soir
            </CardTitle>
            <CardDescription>{data.suggestion_diner}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" size="sm" asChild>
              <Link href="/cuisine/recettes" className="flex items-center gap-1">
                Voir les recettes <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function CarteMetrique({
  titre,
  valeur,
  icone,
  lien,
  chargement,
  alerte,
}: {
  titre: string;
  valeur: number;
  icone: React.ReactNode;
  lien: string;
  chargement: boolean;
  alerte?: boolean;
}) {
  return (
    <Link href={lien}>
      <Card className={alerte ? "border-destructive/50" : "hover:bg-accent/50 transition-colors"}>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {titre}
          </CardTitle>
          {icone}
        </CardHeader>
        <CardContent>
          {chargement ? (
            <Skeleton className="h-8 w-16" />
          ) : (
            <p className={`text-2xl font-bold ${alerte ? "text-destructive" : ""}`}>
              {valeur}
            </p>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
