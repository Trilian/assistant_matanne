"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Textarea } from "@/composants/ui/textarea";
import { Badge } from "@/composants/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/composants/ui/dialog";
import { Label } from "@/composants/ui/label";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import { listerNotes, creerNote, modifierNote, supprimerNote, listerTagsNotes } from "@/bibliotheque/api/outils";
import type { Note, NoteCreate } from "@/types/outils";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { schemaNote, type DonneesNote } from "@/bibliotheque/validateurs";

const CATEGORIES = ["general", "travail", "personnel", "course", "idee"] as const;
const COULEURS = [
  { valeur: "#fef08a", nom: "Jaune" },
  { valeur: "#bbf7d0", nom: "Vert" },
  { valeur: "#bfdbfe", nom: "Bleu" },
  { valeur: "#fecaca", nom: "Rouge" },
  { valeur: "#e9d5ff", nom: "Violet" },
] as const;

const CLASSES_COULEUR_BOUTON: Record<string, string> = {
  "#fef08a": "bg-yellow-200",
  "#bbf7d0": "bg-green-200",
  "#bfdbfe": "bg-blue-200",
  "#fecaca": "bg-red-200",
  "#e9d5ff": "bg-violet-200",
};

const CLASSES_COULEUR_BORDURE: Record<string, string> = {
  "#fef08a": "border-l-yellow-200",
  "#bbf7d0": "border-l-green-200",
  "#bfdbfe": "border-l-blue-200",
  "#fecaca": "border-l-red-200",
  "#e9d5ff": "border-l-violet-200",
};

export default function NotesPage() {
  const [recherche, setRecherche] = useState("");
  const [filtre, setFiltre] = useState("toutes");
  const [filtreTag, setFiltreTag] = useState<string>("tous");
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [champTags, setChampTags] = useState("");

  const invalider = utiliserInvalidation();

  const { data: notes = [], isLoading } = utiliserRequete<Note[]>(
    ["outils", "notes", filtre, filtreTag, recherche],
    () =>
      listerNotes({
        categorie: filtre === "toutes" ? undefined : filtre,
        tag: filtreTag === "tous" ? undefined : filtreTag,
        archive: false,
        recherche: recherche || undefined,
      })
  );

  const { data: tagsDisponibles = [] } = utiliserRequete(
    ["outils", "notes", "tags"],
    listerTagsNotes,
  );

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schemaNote),
    defaultValues: { titre: "", contenu: "", categorie: "general", couleur: "#fef08a", tags: [] as string[] },
  });

  const tagsForm = (watch("tags") ?? []) as string[];

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: DonneesNote) => creerNote(data as unknown as NoteCreate),
    {
      onSuccess: () => {
        toast.success("Note créée");
        invalider(["outils", "notes"]);
        invalider(["outils", "notes", "tags"]);
        setDialogOuvert(false);
        reset();
        setChampTags("");
      },
    }
  );

  const { mutate: basculerEpingle } = utiliserMutation(
    ({ id, epingle }: { id: number; epingle: boolean }) => modifierNote(id, { epingle: !epingle }),
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
        invalider(["outils", "notes", "tags"]);
      },
    }
  );

  const ajouterTagForm = () => {
    const nouveauxTags = champTags
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean);
    if (nouveauxTags.length === 0) {
      return;
    }
    setValue("tags", Array.from(new Set([...tagsForm, ...nouveauxTags])));
    setChampTags("");
  };

  const retirerTagForm = (tag: string) => {
    setValue("tags", tagsForm.filter((item) => item !== tag));
  };

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
                <Input {...register("titre")} placeholder="Ma note" />
                {errors.titre && <p className="text-sm text-destructive mt-1">{errors.titre.message}</p>}
              </div>
              <div>
                <Label>Contenu</Label>
                <Textarea {...register("contenu")} rows={5} placeholder="Contenu…" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Catégorie</Label>
                  <Select value={watch("categorie") ?? "general"} onValueChange={(v) => setValue("categorie", v)}>
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
                        className={`h-8 w-8 rounded-full border-2 ${CLASSES_COULEUR_BOUTON[c.valeur] ?? "bg-muted"} ${watch("couleur") === c.valeur ? "border-primary" : "border-transparent"}`}
                        onClick={() => setValue("couleur", c.valeur)}
                        title={c.nom}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Tags</Label>
                <div className="flex gap-2">
                  <Input
                    value={champTags}
                    onChange={(e) => setChampTags(e.target.value)}
                    placeholder="urgent, batch, idées"
                  />
                  <Button type="button" variant="outline" onClick={ajouterTagForm}>
                    Ajouter
                  </Button>
                </div>
                {tagsForm.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {tagsForm.map((tag) => (
                      <Badge key={tag} variant="secondary" className="cursor-pointer" onClick={() => retirerTagForm(tag)}>
                        #{tag} ×
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
              <Button type="submit" className="w-full" disabled={enCreation}>
                Créer
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex flex-wrap gap-2">
        <Input
          placeholder="Rechercher…"
          value={recherche}
          onChange={(e) => setRecherche(e.target.value)}
          className="w-60"
        />
        {["toutes", ...CATEGORIES].map((c) => (
          <Button key={c} variant={filtre === c ? "default" : "outline"} size="sm" onClick={() => setFiltre(c)}>
            {c}
          </Button>
        ))}
        {tagsDisponibles.slice(0, 8).map((item) => (
          <Button
            key={item.tag}
            variant={filtreTag === item.tag ? "default" : "outline"}
            size="sm"
            onClick={() => setFiltreTag((prev) => (prev === item.tag ? "tous" : item.tag))}
          >
            #{item.tag} ({item.count})
          </Button>
        ))}
      </div>

      {filtreTag !== "tous" && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>Filtre tag actif: #{filtreTag}</span>
          <Button variant="ghost" size="sm" onClick={() => setFiltreTag("tous")}>Réinitialiser</Button>
        </div>
      )}

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
              className={`relative overflow-hidden border-l-4 ${CLASSES_COULEUR_BORDURE[n.couleur ?? ""] ?? "border-l-border"}`}
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
                {n.contenu && <p className="text-sm text-muted-foreground line-clamp-3 mb-3">{n.contenu}</p>}
                {n.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {n.tags.map((t) => (
                      <Badge
                        key={t}
                        variant="secondary"
                        className="text-xs cursor-pointer"
                        onClick={() => setFiltreTag(t)}
                      >
                        #{t}
                      </Badge>
                    ))}
                  </div>
                )}
                <div className="flex gap-1">
                  <Button variant="ghost" size="sm" onClick={() => basculerEpingle({ id: n.id, epingle: n.epingle })}>
                    {n.epingle ? "Désépingler" : "📌 Épingler"}
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => archiver(n.id)}>
                    Archiver
                  </Button>
                  <Button variant="ghost" size="sm" className="text-destructive" onClick={() => supprimer(n.id)}>
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
