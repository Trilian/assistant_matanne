"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/hooks/utiliser-api";
import { listerNotes, creerNote, modifierNote, supprimerNote } from "@/lib/api/outils";
import type { Note, NoteCreate } from "@/types/outils";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

const CATEGORIES = ["general", "travail", "personnel", "course", "idee"] as const;
const COULEURS = [
  { valeur: "#fef08a", nom: "Jaune" },
  { valeur: "#bbf7d0", nom: "Vert" },
  { valeur: "#bfdbfe", nom: "Bleu" },
  { valeur: "#fecaca", nom: "Rouge" },
  { valeur: "#e9d5ff", nom: "Violet" },
] as const;

export default function NotesPage() {
  const [recherche, setRecherche] = useState("");
  const [filtre, setFiltre] = useState("toutes");
  const [dialogOuvert, setDialogOuvert] = useState(false);

  const invalider = utiliserInvalidation();

  const { data: notes = [], isLoading } = utiliserRequete<Note[]>(
    ["outils", "notes", filtre, recherche],
    () =>
      listerNotes({
        categorie: filtre === "toutes" ? undefined : filtre,
        archive: false,
        recherche: recherche || undefined,
      })
  );

  const { register, handleSubmit, reset, setValue, watch } = useForm<NoteCreate>({
    defaultValues: { titre: "", contenu: "", categorie: "general", couleur: "#fef08a", tags: [] },
  });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: NoteCreate) => creerNote(data),
    {
      onSuccess: () => {
        toast.success("Note créée");
        invalider(["outils", "notes"]);
        setDialogOuvert(false);
        reset();
      },
    }
  );

  const { mutate: basculerEpingle } = utiliserMutation(
    ({ id, epingle }: { id: number; epingle: boolean }) =>
      modifierNote(id, { epingle: !epingle }),
    { onSuccess: () => invalider(["outils", "notes"]) }
  );

  const { mutate: archiver } = utiliserMutation(
    (id: number) => modifierNote(id, { archive: true }),
    {
      onSuccess: () => {
        toast.success("Note archivée");
        invalider(["outils", "notes"]);
      },
    }
  );

  const { mutate: supprimer } = utiliserMutation(
    (id: number) => supprimerNote(id),
    {
      onSuccess: () => {
        toast.success("Note supprimée");
        invalider(["outils", "notes"]);
      },
    }
  );

  const notesTriees = [...notes].sort((a, b) => {
    if (a.epingle !== b.epingle) return a.epingle ? -1 : 1;
    return 0;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">📝 Notes</h1>
        <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
          <DialogTrigger asChild>
            <Button>+ Nouvelle note</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Créer une note</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit((d) => creer(d))} className="space-y-4">
              <div>
                <Label>Titre</Label>
                <Input {...register("titre", { required: true })} placeholder="Ma note" />
              </div>
              <div>
                <Label>Contenu</Label>
                <Textarea {...register("contenu")} rows={5} placeholder="Contenu…" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Catégorie</Label>
                  <Select
                    value={watch("categorie") ?? "general"}
                    onValueChange={(v) => setValue("categorie", v)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {CATEGORIES.map((c) => (
                        <SelectItem key={c} value={c}>
                          {c}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Couleur</Label>
                  <div className="flex gap-2 mt-1">
                    {COULEURS.map((c) => (
                      <button
                        key={c.valeur}
                        type="button"
                        className={`h-8 w-8 rounded-full border-2 ${
                          watch("couleur") === c.valeur
                            ? "border-primary"
                            : "border-transparent"
                        }`}
                        style={{ backgroundColor: c.valeur }}
                        onClick={() => setValue("couleur", c.valeur)}
                        title={c.nom}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <Button type="submit" className="w-full" disabled={enCreation}>
                Créer
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filtres */}
      <div className="flex flex-wrap gap-2">
        <Input
          placeholder="Rechercher…"
          value={recherche}
          onChange={(e) => setRecherche(e.target.value)}
          className="w-60"
        />
        {["toutes", ...CATEGORIES].map((c) => (
          <Button
            key={c}
            variant={filtre === c ? "default" : "outline"}
            size="sm"
            onClick={() => setFiltre(c)}
          >
            {c}
          </Button>
        ))}
      </div>

      {/* Grille de notes */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-36 rounded-xl" />
          ))}
        </div>
      ) : notesTriees.length === 0 ? (
        <p className="text-center py-12 text-muted-foreground">Aucune note</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {notesTriees.map((n) => (
            <Card
              key={n.id}
              className="relative overflow-hidden"
              style={{
                borderLeftWidth: 4,
                borderLeftColor: n.couleur ?? "#e5e7eb",
              }}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-base">
                    {n.epingle ? "📌 " : ""}
                    {n.titre}
                  </CardTitle>
                  <Badge variant="outline" className="text-xs shrink-0">
                    {n.categorie}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                {n.contenu && (
                  <p className="text-sm text-muted-foreground line-clamp-3 mb-3">
                    {n.contenu}
                  </p>
                )}
                {n.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {n.tags.map((t) => (
                      <Badge key={t} variant="secondary" className="text-xs">
                        {t}
                      </Badge>
                    ))}
                  </div>
                )}
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => basculerEpingle({ id: n.id, epingle: n.epingle })}
                  >
                    {n.epingle ? "Désépingler" : "📌 Épingler"}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => archiver(n.id)}
                  >
                    Archiver
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive"
                    onClick={() => supprimer(n.id)}
                  >
                    Supprimer
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
