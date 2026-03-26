// ═══════════════════════════════════════════════════════════
// Page Calendriers externes — famille
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Calendar,
  Plus,
  Trash2,
  RefreshCw,
  Link2,
  Loader2,
  CalendarCheck,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import {
  listerCalendriers,
  listerEvenements,
  obtenirUrlAuthGoogle,
  synchroniserGoogle,
  statutGoogle,
  deconnecterGoogle,
  ajouterCalendrierIcal,
  supprimerCalendrier,
  type EvenementCalendrier,
} from "@/bibliotheque/api/calendriers";
import { toast } from "sonner";

export default function PageCalendriers() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📅 Calendriers</h1>
        <p className="text-muted-foreground">
          Synchronisez vos calendriers Google et iCal pour tout avoir au même endroit.
        </p>
      </div>

      <CarteGoogleCalendar />
      <CarteCalendrierIcal />
      <CarteEvenementsSemaine />
    </div>
  );
}

// ─── Google Calendar ───────────────────────────────────────

function CarteGoogleCalendar() {
  const invalider = utiliserInvalidation();

  const { data: statut, isLoading } = utiliserRequete(
    ["calendriers", "google", "statut"],
    statutGoogle
  );

  const { mutate: synchroniser, isPending: syncEnCours } = utiliserMutation(
    () => synchroniserGoogle(),
    {
      onSuccess: (res) => {
        invalider(["calendriers"]);
        toast.success(
          `Synchronisation terminée — ${res.events_imported} événement(s) importé(s)`
        );
      },
      onError: () => toast.error("Erreur lors de la synchronisation Google"),
    }
  );

  const { mutate: deconnecter, isPending: deconnexionEnCours } = utiliserMutation(
    () => deconnecterGoogle(),
    {
      onSuccess: () => {
        invalider(["calendriers", "google", "statut"]);
        toast.success("Compte Google déconnecté");
      },
      onError: () => toast.error("Erreur lors de la déconnexion"),
    }
  );

  async function connecterGoogle() {
    try {
      const { auth_url } = await obtenirUrlAuthGoogle();
      window.location.href = auth_url;
    } catch {
      toast.error("Impossible d'obtenir l'URL d'authentification Google");
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-blue-500" />
          Google Calendar
        </CardTitle>
        <CardDescription>
          Importez et synchronisez vos événements Google Calendar.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading ? (
          <Skeleton className="h-8 w-48" />
        ) : statut?.connected ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-green-700 bg-green-100">
                <CalendarCheck className="mr-1 h-3 w-3" />
                Connecté{statut.nom ? ` — ${statut.nom}` : ""}
              </Badge>
              {statut.last_sync && (
                <span className="text-xs text-muted-foreground">
                  Dernière sync : {new Date(statut.last_sync).toLocaleString("fr-FR")}
                </span>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => synchroniser(undefined)}
                disabled={syncEnCours}
              >
                {syncEnCours ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="mr-2 h-4 w-4" />
                )}
                Synchroniser
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => deconnecter(undefined)}
                disabled={deconnexionEnCours}
              >
                <Trash2 className="mr-2 h-4 w-4 text-destructive" />
                Déconnecter
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              Connectez votre compte Google pour importer vos événements automatiquement.
            </p>
            <Button variant="outline" onClick={connecterGoogle}>
              <Link2 className="mr-2 h-4 w-4" />
              Connecter Google Calendar
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ─── Calendriers iCal ──────────────────────────────────────

function CarteCalendrierIcal() {
  const invalider = utiliserInvalidation();
  const [nom, setNom] = useState("");
  const [url, setUrl] = useState("");

  const { data: calendriers, isLoading } = utiliserRequete(
    ["calendriers", "ical"],
    () => listerCalendriers("ical_url")
  );

  const { mutate: ajouter, isPending: ajoutEnCours } = utiliserMutation(
    () => ajouterCalendrierIcal({ nom, url }),
    {
      onSuccess: () => {
        invalider(["calendriers"]);
        toast.success("Calendrier iCal ajouté");
        setNom("");
        setUrl("");
      },
      onError: () => toast.error("Erreur lors de l'ajout du calendrier"),
    }
  );

  const { mutate: supprimer } = utiliserMutation(
    (id: number) => supprimerCalendrier(id),
    {
      onSuccess: () => {
        invalider(["calendriers"]);
        toast.success("Calendrier supprimé");
      },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Link2 className="h-5 w-5 text-purple-500" />
          Calendriers iCal
        </CardTitle>
        <CardDescription>
          Ajoutez n&apos;importe quel calendrier via son URL iCal (.ics).
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3">
          <div className="space-y-1">
            <Label htmlFor="cal-nom">Nom du calendrier</Label>
            <Input
              id="cal-nom"
              placeholder="Ex : Anniversaires famille"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="cal-url">URL iCal</Label>
            <Input
              id="cal-url"
              placeholder="https://calendar.google.com/...ical/..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>
          <Button
            variant="outline"
            onClick={() => ajouter(undefined)}
            disabled={!nom.trim() || !url.trim() || ajoutEnCours}
          >
            {ajoutEnCours ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Plus className="mr-2 h-4 w-4" />
            )}
            Ajouter
          </Button>
        </div>

        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </div>
        ) : calendriers && calendriers.length > 0 ? (
          <ul className="space-y-2">
            {calendriers.map((cal) => (
              <li
                key={cal.id}
                className="flex items-center justify-between rounded-lg border px-3 py-2"
              >
                <div>
                  <p className="text-sm font-medium">{cal.nom}</p>
                  {cal.url && (
                    <p className="text-xs text-muted-foreground truncate max-w-xs">
                      {cal.url}
                    </p>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => supprimer(cal.id)}
                  aria-label="Supprimer ce calendrier"
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">Aucun calendrier iCal ajouté.</p>
        )}
      </CardContent>
    </Card>
  );
}

// ─── Événements de la semaine ──────────────────────────────

function CarteEvenementsSemaine() {
  const today = new Date();
  const endOfWeek = new Date(today);
  endOfWeek.setDate(today.getDate() + 7);

  const { data: evenements, isLoading } = utiliserRequete(
    ["calendriers", "evenements", "semaine"],
    () =>
      listerEvenements({
        date_debut: today.toISOString().slice(0, 10),
        date_fin: endOfWeek.toISOString().slice(0, 10),
      })
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CalendarCheck className="h-5 w-5 text-emerald-500" />
          7 prochains jours
        </CardTitle>
        <CardDescription>Événements à venir issus de vos calendriers.</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        ) : evenements && evenements.length > 0 ? (
          <ul className="space-y-2">
            {evenements.map((ev) => (
              <EvenementItem key={ev.id} evenement={ev} />
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">
            Aucun événement dans les 7 prochains jours.
          </p>
        )}
      </CardContent>
    </Card>
  );
}

function EvenementItem({ evenement }: { evenement: EvenementCalendrier }) {
  const date = new Date(evenement.date_debut);
  const dateStr = date.toLocaleDateString("fr-FR", {
    weekday: "short",
    day: "numeric",
    month: "short",
  });
  const heureStr = evenement.all_day
    ? "Toute la journée"
    : date.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });

  return (
    <li className="flex items-start gap-3 rounded-lg border px-3 py-2">
      <div className="text-center min-w-[52px]">
        <p className="text-xs font-semibold uppercase text-muted-foreground">{dateStr}</p>
        <p className="text-xs text-muted-foreground">{heureStr}</p>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{evenement.titre}</p>
        {evenement.lieu && (
          <p className="text-xs text-muted-foreground truncate">{evenement.lieu}</p>
        )}
      </div>
    </li>
  );
}
