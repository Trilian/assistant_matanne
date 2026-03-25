// ═══════════════════════════════════════════════════════════
// Contacts — Répertoire familial (connecté API)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Users,
  Phone,
  Mail,
  Search,
  MapPin,
  Plus,
  Star,
  Trash2,
  Pencil,
  Clock,
} from "lucide-react";
import { Card, CardContent } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/composants/ui/dialog";
import { Label } from "@/composants/ui/label";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  listerContacts,
  creerContact,
  modifierContact,
  supprimerContact,
  type ContactUtile,
} from "@/bibliotheque/api/utilitaires";
import { toast } from "sonner";

const CATEGORIES = [
  "Tous",
  "famille",
  "sante",
  "garde",
  "ecole",
  "pro",
  "ami",
  "autre",
];
const LABELS_CAT: Record<string, string> = {
  Tous: "Tous",
  famille: "Famille",
  sante: "Santé",
  garde: "Garde",
  ecole: "École",
  pro: "Pro",
  ami: "Amis",
  autre: "Autre",
};

export default function PageContacts() {
  const [recherche, setRecherche] = useState("");
  const [categorie, setCategorie] = useState("Tous");
  const [ouvert, setOuvert] = useState(false);
  const [edition, setEdition] = useState<ContactUtile | null>(null);

  const invalider = utiliserInvalidation();
  const { data: contacts = [], isLoading } = utiliserRequete(
    ["contacts", categorie, recherche],
    () =>
      listerContacts({
        categorie: categorie === "Tous" ? undefined : categorie,
        search: recherche || undefined,
      })
  );

  const mutCreer = utiliserMutation(
    (c: Omit<ContactUtile, "id">) => creerContact(c),
    {
      onSuccess: () => { invalider(["contacts"]); setOuvert(false); toast.success("Contact créé"); },
      onError: () => toast.error("Erreur lors de la création"),
    }
  );
  const mutModifier = utiliserMutation(
    ({ id, patch }: { id: number; patch: Partial<ContactUtile> }) =>
      modifierContact(id, patch),
    {
      onSuccess: () => { invalider(["contacts"]); setEdition(null); setOuvert(false); toast.success("Contact modifié"); },
      onError: () => toast.error("Erreur lors de la modification"),
    }
  );
  const mutSupprimer = utiliserMutation(
    (id: number) => supprimerContact(id),
    {
      onSuccess: () => { invalider(["contacts"]); toast.success("Contact supprimé"); },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const payload = {
      nom: fd.get("nom") as string,
      categorie: fd.get("categorie") as string,
      specialite: (fd.get("specialite") as string) || undefined,
      telephone: (fd.get("telephone") as string) || undefined,
      email: (fd.get("email") as string) || undefined,
      adresse: (fd.get("adresse") as string) || undefined,
      horaires: (fd.get("horaires") as string) || undefined,
      favori: false,
    };
    if (edition) {
      mutModifier.mutate({ id: edition.id, patch: payload });
    } else {
      mutCreer.mutate(payload);
    }
  }

  function ouvrir(contact?: ContactUtile) {
    setEdition(contact ?? null);
    setOuvert(true);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📇 Contacts</h1>
          <p className="text-muted-foreground">
            Répertoire familial et contacts utiles
          </p>
        </div>
        <Dialog open={ouvert} onOpenChange={(o) => { setOuvert(o); if (!o) setEdition(null); }}>
          <DialogTrigger asChild>
            <Button onClick={() => ouvrir()}>
              <Plus className="mr-2 h-4 w-4" />
              Ajouter
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {edition ? "Modifier le contact" : "Nouveau contact"}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={onSubmit} className="space-y-3 pt-2">
              <div>
                <Label htmlFor="nom">Nom *</Label>
                <Input id="nom" name="nom" required defaultValue={edition?.nom ?? ""} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="categorie">Catégorie</Label>
                  <select
                    id="categorie"
                    name="categorie"
                    defaultValue={edition?.categorie ?? "autre"}
                    className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  >
                    {CATEGORIES.filter((c) => c !== "Tous").map((c) => (
                      <option key={c} value={c}>{LABELS_CAT[c]}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label htmlFor="specialite">Spécialité</Label>
                  <Input id="specialite" name="specialite" defaultValue={edition?.specialite ?? ""} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="telephone">Téléphone</Label>
                  <Input id="telephone" name="telephone" defaultValue={edition?.telephone ?? ""} />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" name="email" type="email" defaultValue={edition?.email ?? ""} />
                </div>
              </div>
              <div>
                <Label htmlFor="adresse">Adresse</Label>
                <Input id="adresse" name="adresse" defaultValue={edition?.adresse ?? ""} />
              </div>
              <div>
                <Label htmlFor="horaires">Horaires</Label>
                <Input id="horaires" name="horaires" defaultValue={edition?.horaires ?? ""} />
              </div>
              <Button type="submit" className="w-full">
                {edition ? "Enregistrer" : "Ajouter"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filtres */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher un contact..."
            value={recherche}
            onChange={(e) => setRecherche(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => (
            <Badge
              key={cat}
              variant={categorie === cat ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() => setCategorie(cat)}
            >
              {LABELS_CAT[cat]}
            </Badge>
          ))}
        </div>
      </div>

      {/* Liste */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <CardContent className="py-4">
                  <div className="h-5 w-48 animate-pulse rounded bg-muted" />
                  <div className="mt-2 h-4 w-32 animate-pulse rounded bg-muted" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : contacts.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
              Aucun contact trouvé
            </CardContent>
          </Card>
        ) : (
          contacts.map((contact) => (
            <Card key={contact.id}>
              <CardContent className="flex items-start justify-between py-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{contact.nom}</p>
                    {contact.favori && (
                      <Star className="h-3.5 w-3.5 fill-yellow-400 text-yellow-400" />
                    )}
                  </div>
                  {contact.specialite && (
                    <p className="text-xs text-muted-foreground">
                      {contact.specialite}
                    </p>
                  )}
                  <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
                    {contact.telephone && (
                      <span className="flex items-center gap-1">
                        <Phone className="h-3.5 w-3.5" />
                        {contact.telephone}
                      </span>
                    )}
                    {contact.email && (
                      <span className="flex items-center gap-1">
                        <Mail className="h-3.5 w-3.5" />
                        {contact.email}
                      </span>
                    )}
                    {contact.adresse && (
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5" />
                        {contact.adresse}
                      </span>
                    )}
                    {contact.horaires && (
                      <span className="flex items-center gap-1">
                        <Clock className="h-3.5 w-3.5" />
                        {contact.horaires}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">
                    {LABELS_CAT[contact.categorie] ?? contact.categorie}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => ouvrir(contact)}
                  >
                    <Pencil className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive"
                    onClick={() => mutSupprimer.mutate(contact.id)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
