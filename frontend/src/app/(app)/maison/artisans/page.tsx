// ═══════════════════════════════════════════════════════════
// Artisans — Carnet d'adresses et interventions
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Wrench, Phone, Mail, Star, Plus, Pencil, Trash2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerArtisans,
  creerArtisan,
  modifierArtisan,
  supprimerArtisan,
  statsArtisans,
} from "@/bibliotheque/api/maison";
import type { Artisan } from "@/types/maison";

export default function PageArtisans() {
  const [metier, setMetier] = useState<string | undefined>();
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [enEdition, setEnEdition] = useState<Artisan | null>(null);
  const [form, setForm] = useState({ nom: "", metier: "", telephone: "", email: "", adresse: "", note_satisfaction: "" });
  const queryClient = useQueryClient();

  const { data: artisans, isLoading } = utiliserRequete(
    ["maison", "artisans", metier ?? "all"],
    () => listerArtisans(metier)
  );

  const { data: stats } = utiliserRequete(
    ["maison", "artisans", "stats"],
    () => statsArtisans()
  );

  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "artisans"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) => creerArtisan(data as Omit<Artisan, "id">),
    { onSuccess: () => { invalider(); fermerDialog(); } }
  );

  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<Artisan> }) => modifierArtisan(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); } }
  );

  const { mutate: supprimer } = utiliserMutation(supprimerArtisan, { onSuccess: invalider });

  const ouvrirCreation = () => {
    setEnEdition(null);
    setForm({ nom: "", metier: "", telephone: "", email: "", adresse: "", note_satisfaction: "" });
    setDialogOuvert(true);
  };

  const ouvrirEdition = (a: Artisan) => {
    setEnEdition(a);
    setForm({
      nom: a.nom,
      metier: a.metier,
      telephone: a.telephone ?? "",
      email: a.email ?? "",
      adresse: a.adresse ?? "",
      note_satisfaction: a.note_satisfaction != null ? String(a.note_satisfaction) : "",
    });
    setDialogOuvert(true);
  };

  const fermerDialog = () => { setDialogOuvert(false); setEnEdition(null); };

  const soumettre = () => {
    const payload = {
      nom: form.nom,
      metier: form.metier,
      telephone: form.telephone || undefined,
      email: form.email || undefined,
      adresse: form.adresse || undefined,
      note_satisfaction: form.note_satisfaction ? Number(form.note_satisfaction) : undefined,
    };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload);
  };

  const metiers = stats?.par_metier ? Object.keys(stats.par_metier) : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🔧 Artisans</h1>
          <p className="text-muted-foreground">
            Carnet d'adresses — {stats?.total_artisans ?? 0} artisans,{" "}
            {stats?.total_interventions ?? 0} interventions
          </p>
        </div>
        <Button size="sm" onClick={ouvrirCreation}>
          <Plus className="mr-2 h-4 w-4" />
          Ajouter
        </Button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid gap-3 sm:grid-cols-3">
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{stats.total_artisans}</p>
              <p className="text-xs text-muted-foreground">Artisans</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{stats.total_interventions}</p>
              <p className="text-xs text-muted-foreground">Interventions</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">
                {stats.depenses_totales.toFixed(0)} €
              </p>
              <p className="text-xs text-muted-foreground">Dépenses totales</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filtres métier */}
      {metiers.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          <Button
            variant={!metier ? "default" : "outline"}
            size="sm"
            onClick={() => setMetier(undefined)}
          >
            Tous
          </Button>
          {metiers.map((m) => (
            <Button
              key={m}
              variant={metier === m ? "default" : "outline"}
              size="sm"
              onClick={() => setMetier(m)}
            >
              {m}
            </Button>
          ))}
        </div>
      )}

      {/* Liste artisans */}
      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-36" />
          ))}
        </div>
      ) : !artisans?.length ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            <Wrench className="h-8 w-8 mx-auto mb-2 opacity-50" />
            Aucun artisan enregistré
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {artisans.map((artisan) => (
            <Card key={artisan.id}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">{artisan.nom}</CardTitle>
                  <div className="flex items-center gap-1">
                    <Badge variant="outline">{artisan.metier}</Badge>
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(artisan)}>
                      <Pencil className="h-3 w-3" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => supprimer(artisan.id)}>
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-1">
                {artisan.telephone && (
                  <p className="text-sm flex items-center gap-2">
                    <Phone className="h-3 w-3 text-muted-foreground" />
                    {artisan.telephone}
                  </p>
                )}
                {artisan.email && (
                  <p className="text-sm flex items-center gap-2">
                    <Mail className="h-3 w-3 text-muted-foreground" />
                    {artisan.email}
                  </p>
                )}
                {artisan.note_satisfaction != null && (
                  <div className="flex items-center gap-1 mt-2">
                    {Array.from({ length: 5 }, (_, i) => (
                      <Star
                        key={i}
                        className={`h-3 w-3 ${
                          i < artisan.note_satisfaction!
                            ? "text-amber-400 fill-amber-400"
                            : "text-muted-foreground"
                        }`}
                      />
                    ))}
                  </div>
                )}
                {artisan.dernier_passage && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Dernier passage:{" "}
                    {new Date(artisan.dernier_passage).toLocaleDateString("fr-FR")}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Dialog CRUD */}
      <DialogueFormulaire
        ouvert={dialogOuvert}
        onClose={fermerDialog}
        titre={enEdition ? "Modifier l'artisan" : "Nouvel artisan"}
        onSubmit={soumettre}
        enCours={enCreation || enModif}
        texteBouton={enEdition ? "Modifier" : "Ajouter"}
      >
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="nom">Nom</Label>
            <Input id="nom" value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="metier">Métier</Label>
            <Input id="metier" value={form.metier} onChange={(e) => setForm({ ...form, metier: e.target.value })} required />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="telephone">Téléphone</Label>
            <Input id="telephone" value={form.telephone} onChange={(e) => setForm({ ...form, telephone: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="adresse">Adresse</Label>
          <Input id="adresse" value={form.adresse} onChange={(e) => setForm({ ...form, adresse: e.target.value })} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="note">Note (1-5)</Label>
          <Input id="note" type="number" min="1" max="5" value={form.note_satisfaction} onChange={(e) => setForm({ ...form, note_satisfaction: e.target.value })} />
        </div>
      </DialogueFormulaire>
    </div>
  );
}
