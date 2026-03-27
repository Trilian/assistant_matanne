// ═══════════════════════════════════════════════════════════
// Artisans — Répertoire des artisans & prestataires
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Hammer, Plus, Pencil, Trash2, Phone, Mail, Star,
} from "lucide-react";
import { Card, CardContent } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerArtisans, creerArtisan, modifierArtisan, supprimerArtisan, statsArtisans,
} from "@/bibliotheque/api/maison";
import type { Artisan } from "@/types/maison";
import { toast } from "sonner";

// ─── Constantes ──────────────────────────────────────────────

const METIERS = [
  "Plombier", "Électricien", "Maçon", "Menuisier", "Peintre",
  "Carreleur", "Couvreur", "Chauffagiste", "Jardinier", "Serrurier",
  "Vitrier", "Climatisation", "Déménageur", "Nettoyage", "Autre",
];

// ─── Carte Artisan ────────────────────────────────────────────

function CarteArtisan({
  artisan: a,
  onEdit,
  onDelete,
}: {
  artisan: Artisan;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <Card>
      <CardContent className="py-3">
        <div className="flex items-start gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <p className="text-sm font-medium">{a.nom}</p>
              <Badge variant="secondary" className="text-xs">{a.metier}</Badge>
              {a.note_satisfaction != null && (
                <span className="flex items-center gap-0.5 text-xs text-amber-600">
                  <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                  {a.note_satisfaction.toFixed(1)}
                </span>
              )}
            </div>
            <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1">
              {a.telephone && (
                <a
                  href={`tel:${a.telephone}`}
                  className="text-xs text-muted-foreground flex items-center gap-1 hover:text-foreground"
                >
                  <Phone className="h-3 w-3" />{a.telephone}
                </a>
              )}
              {a.email && (
                <a
                  href={`mailto:${a.email}`}
                  className="text-xs text-muted-foreground flex items-center gap-1 hover:text-foreground"
                >
                  <Mail className="h-3 w-3" />{a.email}
                </a>
              )}
              {a.adresse && (
                <span className="text-xs text-muted-foreground">{a.adresse}</span>
              )}
            </div>
            {a.commentaire && (
              <p className="text-xs text-muted-foreground mt-1 italic">{a.commentaire}</p>
            )}
          </div>
          <div className="flex items-center gap-1 shrink-0">
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onEdit}>
              <Pencil className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive"
              onClick={onDelete}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Page principale ──────────────────────────────────────────

export default function PageArtisans() {
  const queryClient = useQueryClient();

  const formVide = {
    nom: "", metier: "", telephone: "", email: "",
    adresse: "", note_satisfaction: "", commentaire: "",
  };
  const [form, setForm] = useState(formVide);

  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<Artisan>({
      onOuvrirCreation: () => setForm(formVide),
      onOuvrirEdition: (a) =>
        setForm({
          nom: a.nom ?? "",
          metier: a.metier ?? "",
          telephone: a.telephone ?? "",
          email: a.email ?? "",
          adresse: a.adresse ?? "",
          note_satisfaction: a.note_satisfaction != null ? String(a.note_satisfaction) : "",
          commentaire: a.commentaire ?? "",
        }),
    });

  const { data: artisans, isLoading } = utiliserRequete(
    ["maison", "artisans"],
    () => listerArtisans()
  );
  const { data: stats } = utiliserRequete(
    ["maison", "artisans", "stats"],
    statsArtisans
  );

  const invalider = () =>
    queryClient.invalidateQueries({ queryKey: ["maison", "artisans"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Omit<Artisan, "id">) => creerArtisan(data),
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
      commentaire: form.commentaire || undefined,
    } as Omit<Artisan, "id">;
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload);
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Hammer className="h-6 w-6 text-primary" />
          Artisans
        </h1>
        <p className="text-muted-foreground">Répertoire de vos prestataires et artisans</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-2xl font-bold">{stats.total_artisans}</p>
              <p className="text-xs text-muted-foreground">Artisans</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-2xl font-bold">{stats.total_interventions}</p>
              <p className="text-xs text-muted-foreground">Interventions</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-2xl font-bold">{stats.depenses_totales?.toLocaleString("fr-FR")} €</p>
              <p className="text-xs text-muted-foreground">Dépenses totales</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end">
        <Button size="sm" onClick={ouvrirCreation}>
          <Plus className="mr-1.5 h-4 w-4" />
          Ajouter
        </Button>
      </div>

      {/* Liste */}
      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20" />)}
        </div>
      ) : !artisans?.length ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <Hammer className="h-10 w-10 mx-auto mb-3 opacity-30" />
            <p className="font-medium">Aucun artisan enregistré</p>
            <p className="text-xs mt-1">Ajoutez vos prestataires pour les retrouver facilement</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {artisans.map((a) => (
            <CarteArtisan
              key={a.id}
              artisan={a}
              onEdit={() => ouvrirEdition(a)}
              onDelete={() => supprimer(a.id)}
            />
          ))}
        </div>
      )}

      {/* Formulaire */}
      <DialogueFormulaire
        ouvert={dialogOuvert}
        onClose={fermerDialog}
        titre={enEdition ? "Modifier l'artisan" : "Nouvel artisan"}
        onSubmit={soumettre}
        enCours={enCreation || enModif}
      >
        <div className="space-y-3">
          <div className="space-y-1">
            <Label htmlFor="nom">Nom / Entreprise *</Label>
            <Input
              id="nom"
              value={form.nom}
              onChange={(e) => setForm((f) => ({ ...f, nom: e.target.value }))}
              placeholder="ex: Dupont Plomberie"
              required
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="metier">Métier *</Label>
            <Input
              id="metier"
              value={form.metier}
              onChange={(e) => setForm((f) => ({ ...f, metier: e.target.value }))}
              list="metiers-list"
              placeholder="ex: Plombier"
              required
            />
            <datalist id="metiers-list">
              {METIERS.map((m) => <option key={m} value={m} />)}
            </datalist>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="telephone">Téléphone</Label>
              <Input
                id="telephone"
                type="tel"
                value={form.telephone}
                onChange={(e) => setForm((f) => ({ ...f, telephone: e.target.value }))}
                placeholder="06 12 34 56 78"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="note">Note (/5)</Label>
              <Input
                id="note"
                type="number"
                min="0"
                max="5"
                step="0.5"
                value={form.note_satisfaction}
                onChange={(e) => setForm((f) => ({ ...f, note_satisfaction: e.target.value }))}
                placeholder="4.5"
              />
            </div>
          </div>
          <div className="space-y-1">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              placeholder="contact@artisan.fr"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="adresse">Adresse / Ville</Label>
            <Input
              id="adresse"
              value={form.adresse}
              onChange={(e) => setForm((f) => ({ ...f, adresse: e.target.value }))}
              placeholder="ex: Paris 15e"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="commentaire">Commentaire</Label>
            <Input
              id="commentaire"
              value={form.commentaire}
              onChange={(e) => setForm((f) => ({ ...f, commentaire: e.target.value }))}
              placeholder="Spécialité, disponibilité…"
            />
          </div>
        </div>
      </DialogueFormulaire>
    </div>
  );
}

