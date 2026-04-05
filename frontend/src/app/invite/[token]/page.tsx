"use client";

import { useParams } from "next/navigation";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import type { ListeObjetsDonnees, ObjetDonnees } from "@/types/commun";

interface DonneesInvite {
  enfant: ObjetDonnees;
  routines: ListeObjetsDonnees;
  repas_semaine: ListeObjetsDonnees;
  contacts_urgence: ListeObjetsDonnees;
  notes: string;
}

async function obtenirDonneesInvite(token: string): Promise<DonneesInvite> {
  const { data } = await clientApi.get(`/api/v1/rapports/invite/${token}`);
  return data;
}

export default function PageInviteToken() {
  const params = useParams<{ token: string }>();
  const token = params?.token ?? "";

  const { data, isLoading, error } = utiliserRequete(
    ["invite", token],
    () => obtenirDonneesInvite(token),
    { enabled: !!token }
  );

  if (isLoading) {
    return <div className="p-6 text-sm text-muted-foreground">Chargement de l'accès invité...</div>;
  }

  if (error || !data) {
    return <div className="p-6 text-sm text-destructive">Lien invité invalide ou expiré.</div>;
  }

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">
      <h1 className="text-2xl font-bold">Mode invité</h1>
      <p className="text-sm text-muted-foreground">{data.notes}</p>

      <Card>
        <CardHeader><CardTitle className="text-base">Repas semaine</CardTitle></CardHeader>
        <CardContent className="text-sm space-y-1">
          {data.repas_semaine.length === 0 ? "Aucun repas partagé" : data.repas_semaine.map((r, i) => <div key={i}>{JSON.stringify(r)}</div>)}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Routines</CardTitle></CardHeader>
        <CardContent className="text-sm space-y-1">
          {data.routines.length === 0 ? "Aucune routine partagée" : data.routines.map((r, i) => <div key={i}>{JSON.stringify(r)}</div>)}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Contacts d'urgence</CardTitle></CardHeader>
        <CardContent className="text-sm space-y-1">
          {data.contacts_urgence.length === 0 ? "Aucun contact partagé" : data.contacts_urgence.map((c, i) => <div key={i}>{JSON.stringify(c)}</div>)}
        </CardContent>
      </Card>
    </div>
  );
}
