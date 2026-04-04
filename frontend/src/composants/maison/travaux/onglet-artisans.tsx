"use client";

import { useState } from "react";
import { Mail, Pencil, Phone, Plus, Trash2, Wrench } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { EtatVide } from "@/composants/ui/etat-vide";
import { Skeleton } from "@/composants/ui/skeleton";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import {
  creerArtisan,
  listerArtisans,
  modifierArtisan,
  statsArtisans,
  supprimerArtisan,
} from "@/bibliotheque/api/maison";
import type { Artisan } from "@/types/maison";
import { toast } from "sonner";

export function OngletArtisans() {
  const [metier] = useState<string | undefined>();
  const formsVide = { nom: "", metier: "", telephone: "", email: "", adresse: "", note_satisfaction: "" };
  const [form, setForm] = useState(formsVide);
  const queryClient = useQueryClient();
  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<Artisan>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (artisan) =>
        setForm({
          nom: artisan.nom,
          metier: artisan.metier,
          telephone: artisan.telephone ?? "",
          email: artisan.email ?? "",
          adresse: artisan.adresse ?? "",
          note_satisfaction: artisan.note_satisfaction != null ? String(artisan.note_satisfaction) : "",
        }),
    });

  const { data: artisans, isLoading } = utiliserRequete(
    ["maison", "artisans", metier ?? "all"],
    () => listerArtisans(metier)
  );
  const { data: stats } = utiliserRequete(["maison", "artisans", "stats"], statsArtisans);
  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "artisans"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Parameters<typeof creerArtisan>[0]) => creerArtisan(data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Artisan ajouté"); } }
  );
  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<Artisan> }) => modifierArtisan(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Artisan modifié"); } }
  );
  const { mutate: supprimer } = utiliserMutation(supprimerArtisan, {
    onSuccess: () => { invalider(); toast.success("Artisan supprimé"); },
  });

  const soumettre = () => {
    const payload = {
      nom: form.nom,
      metier: form.metier,
      telephone: form.telephone || undefined,
      email: form.email || undefined,
      adresse: form.adresse || undefined,
      note_satisfaction: form.note_satisfaction ? Number(form.note_satisfaction) : undefined,
    };

    if (enEdition) {
      modifier({ id: enEdition.id, data: payload });
    } else {
      creer(payload);
    }
  };

  const champsForme = [
    { id: "nom", label: "Nom", type: "text" as const, value: form.nom, onChange: (v: string) => setForm((f) => ({ ...f, nom: v })), required: true },
    { id: "metier", label: "Métier", type: "text" as const, value: form.metier, onChange: (v: string) => setForm((f) => ({ ...f, metier: v })), required: true },
    { id: "telephone", label: "Téléphone", type: "text" as const, value: form.telephone, onChange: (v: string) => setForm((f) => ({ ...f, telephone: v })) },
    { id: "email", label: "Email", type: "email" as const, value: form.email, onChange: (v: string) => setForm((f) => ({ ...f, email: v })) },
  ];

  return (
    <div className="space-y-4">
      {stats && (
        <div className="grid grid-cols-3 gap-3">
          <Card><CardContent className="py-3 text-center"><p className="text-xl font-bold">{stats.total_artisans ?? 0}</p><p className="text-xs text-muted-foreground">Artisans</p></CardContent></Card>
          <Card><CardContent className="py-3 text-center"><p className="text-xl font-bold">{stats.total_interventions ?? 0}</p><p className="text-xs text-muted-foreground">Interventions</p></CardContent></Card>
          <Card><CardContent className="py-3 text-center"><p className="text-xl font-bold">{(stats.total_depenses ?? 0).toFixed(0)} €</p><p className="text-xs text-muted-foreground">Dépenses</p></CardContent></Card>
        </div>
      )}

      <div className="flex justify-end">
        <Button size="sm" onClick={ouvrirCreation}><Plus className="mr-2 h-4 w-4" />Ajouter un artisan</Button>
      </div>

      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-28" />)}</div>
      ) : !artisans?.length ? (
        <Card>
          <CardContent className="py-6">
            <EtatVide
              Icone={Wrench}
              titre="Aucun artisan enregistre"
              description="Ajoutez vos contacts de confiance pour les interventions maison."
            />
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {artisans.map((artisan) => (
            <Card key={artisan.id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-sm">{artisan.nom}</CardTitle>
                    <Badge variant="secondary" className="mt-1 text-xs">{artisan.metier}</Badge>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(artisan)}><Pencil className="h-3.5 w-3.5" /></Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive" onClick={() => supprimer(artisan.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-1 pt-0">
                {artisan.telephone && <p className="flex items-center gap-1.5 text-xs"><Phone className="h-3 w-3" />{artisan.telephone}</p>}
                {artisan.email && <p className="flex items-center gap-1.5 text-xs"><Mail className="h-3 w-3" />{artisan.email}</p>}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <DialogueFormulaire
        ouvert={dialogOuvert}
        onChangerOuvert={setDialogOuvert}
        titre={enEdition ? "Modifier l'artisan" : "Ajouter un artisan"}
        champs={champsForme}
        onSoumettre={soumettre}
        enChargement={enCreation || enModif}
      />
    </div>
  );
}
