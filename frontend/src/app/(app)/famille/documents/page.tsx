// ═══════════════════════════════════════════════════════════
// Documents — Fichiers et documents familiaux (CRUD)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  FileText,
  Upload,
  FolderOpen,
  Shield,
  Heart,
  Home,
  Plus,
  Pencil,
  Trash2,
  Search,
  AlertTriangle,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import {
  listerDocuments,
  creerDocument,
  modifierDocument,
  supprimerDocument,
  type DocumentFamille,
  type CreerDocumentDTO,
} from "@/bibliotheque/api/documents";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import { useQueryClient } from "@tanstack/react-query";

const CATEGORIES = [
  { value: "administratif", label: "Administratif", icone: Shield },
  { value: "sante", label: "Santé", icone: Heart },
  { value: "maison", label: "Maison", icone: Home },
];

const FORM_INITIAL: CreerDocumentDTO = {
  titre: "",
  categorie: "administratif",
  membre_famille: "",
  date_document: "",
  date_expiration: "",
  notes: "",
};

export default function PageDocuments() {
  const [categorieFiltre, setCategorieFiltre] = useState<string | undefined>();
  const [recherche, setRecherche] = useState("");
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [enEdition, setEnEdition] = useState<DocumentFamille | null>(null);
  const [form, setForm] = useState<CreerDocumentDTO>(FORM_INITIAL);

  const queryClient = useQueryClient();
  const invalider = utiliserInvalidation();

  const { data, isLoading } = utiliserRequete(
    ["documents", categorieFiltre ?? "all", recherche],
    () => listerDocuments(categorieFiltre, recherche || undefined)
  );

  const mutationCreer = utiliserMutation(
    (dto: CreerDocumentDTO) => creerDocument(dto),
    { onSuccess: () => { invalider(["documents"]); fermerDialog(); } }
  );

  const mutationModifier = utiliserMutation(
    ({ id, dto }: { id: number; dto: Partial<CreerDocumentDTO> }) =>
      modifierDocument(id, dto),
    { onSuccess: () => { invalider(["documents"]); fermerDialog(); } }
  );

  const mutationSupprimer = utiliserMutation(
    (id: number) => supprimerDocument(id),
    { onSuccess: () => invalider(["documents"]) }
  );

  function ouvrirCreation() {
    setEnEdition(null);
    setForm(FORM_INITIAL);
    setDialogOuvert(true);
  }

  function ouvrirEdition(doc: DocumentFamille) {
    setEnEdition(doc);
    setForm({
      titre: doc.titre,
      categorie: doc.categorie,
      membre_famille: doc.membre_famille ?? "",
      date_document: doc.date_document ?? "",
      date_expiration: doc.date_expiration ?? "",
      notes: doc.notes ?? "",
    });
    setDialogOuvert(true);
  }

  function fermerDialog() {
    setDialogOuvert(false);
    setEnEdition(null);
  }

  function soumettre() {
    if (enEdition) {
      mutationModifier.mutate({ id: enEdition.id, dto: form });
    } else {
      mutationCreer.mutate(form);
    }
  }

  const documents = data?.items ?? [];
  const documentsExpires = documents.filter((d) => d.est_expire);

  // Count per category
  const counts = CATEGORIES.map((c) => ({
    ...c,
    count: documents.filter((d) => d.categorie === c.value).length,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📄 Documents</h1>
          <p className="text-muted-foreground">
            Stockage et gestion des documents familiaux
          </p>
        </div>
        <Button onClick={ouvrirCreation}>
          <Plus className="h-4 w-4 mr-2" />
          Ajouter
        </Button>
      </div>

      {/* Alertes expiration */}
      {documentsExpires.length > 0 && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="flex items-center gap-3 py-3">
            <AlertTriangle className="h-5 w-5 text-destructive" />
            <span className="text-sm font-medium">
              {documentsExpires.length} document{documentsExpires.length > 1 ? "s" : ""} expiré{documentsExpires.length > 1 ? "s" : ""}
            </span>
          </CardContent>
        </Card>
      )}

      {/* Dossiers / catégories */}
      <div className="grid gap-3 sm:grid-cols-3">
        {counts.map(({ value, label, icone: Icone, count }) => (
          <Card
            key={value}
            className={`cursor-pointer hover:bg-accent/50 transition-colors ${
              categorieFiltre === value ? "ring-2 ring-primary" : ""
            }`}
            onClick={() =>
              setCategorieFiltre(categorieFiltre === value ? undefined : value)
            }
          >
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <FolderOpen className="h-4 w-4 text-primary" />
                {label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Icone className="h-3.5 w-3.5" />
                {count} document{count !== 1 ? "s" : ""}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recherche */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Rechercher un document..."
          className="pl-10"
          value={recherche}
          onChange={(e) => setRecherche(e.target.value)}
        />
      </div>

      {/* Liste des documents */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      ) : documents.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center gap-3 py-10 text-center">
            <Upload className="h-10 w-10 text-muted-foreground/50" />
            <p className="font-medium">Aucun document</p>
            <p className="text-sm text-muted-foreground">
              Cliquez sur &quot;Ajouter&quot; pour créer votre premier document
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {documents.map((doc) => (
            <Card key={doc.id}>
              <CardContent className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3 min-w-0">
                  <FileText className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="font-medium truncate">{doc.titre}</p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Badge variant="secondary" className="text-[10px]">
                        {doc.categorie}
                      </Badge>
                      {doc.membre_famille && (
                        <span>{doc.membre_famille}</span>
                      )}
                      {doc.date_document && (
                        <span>{doc.date_document}</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  {doc.est_expire && (
                    <Badge variant="destructive" className="text-[10px] mr-2">
                      Expiré
                    </Badge>
                  )}
                  {doc.jours_avant_expiration != null &&
                    doc.jours_avant_expiration <= 30 &&
                    !doc.est_expire && (
                      <Badge variant="outline" className="text-[10px] mr-2 border-orange-300 text-orange-600">
                        Expire dans {doc.jours_avant_expiration}j
                      </Badge>
                    )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => ouvrirEdition(doc)}
                  >
                    <Pencil className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive"
                    onClick={() => mutationSupprimer.mutate(doc.id)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Dialog création/édition */}
      <DialogueFormulaire
        ouvert={dialogOuvert}
        onClose={fermerDialog}
        titre={enEdition ? "Modifier le document" : "Nouveau document"}
        onSubmit={soumettre}
        enCours={mutationCreer.isPending || mutationModifier.isPending}
      >
        <div className="space-y-3">
          <div>
            <Label>Titre</Label>
            <Input
              value={form.titre}
              onChange={(e) => setForm({ ...form, titre: e.target.value })}
              placeholder="Carte d'identité Anne"
            />
          </div>
          <div>
            <Label>Catégorie</Label>
            <select
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={form.categorie}
              onChange={(e) => setForm({ ...form, categorie: e.target.value })}
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label>Membre de famille</Label>
            <Input
              value={form.membre_famille}
              onChange={(e) => setForm({ ...form, membre_famille: e.target.value })}
              placeholder="Anne, Jules..."
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Date du document</Label>
              <Input
                type="date"
                value={form.date_document}
                onChange={(e) => setForm({ ...form, date_document: e.target.value })}
              />
            </div>
            <div>
              <Label>Date d'expiration</Label>
              <Input
                type="date"
                value={form.date_expiration}
                onChange={(e) => setForm({ ...form, date_expiration: e.target.value })}
              />
            </div>
          </div>
          <div>
            <Label>Notes</Label>
            <Input
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              placeholder="Informations supplémentaires..."
            />
          </div>
        </div>
      </DialogueFormulaire>
    </div>
  );
}
