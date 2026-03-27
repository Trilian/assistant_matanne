// ═══════════════════════════════════════════════════════════
// Entretien — Gestion des tâches d'entretien
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  SprayCan, Plus, Trash2, CheckCircle2, Clock, Activity,
  AlertTriangle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
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
  listerTachesEntretien, obtenirSanteAppareils,
  creerTacheEntretien, supprimerTacheEntretien,
} from "@/bibliotheque/api/maison";
import type { TacheEntretien } from "@/types/maison";
import { toast } from "sonner";

// ─── Constantes ──────────────────────────────────────────────

const CATEGORIES = [
  "cuisine", "menage", "salle_de_bain", "chauffage", "electricite",
  "plomberie", "exterieur", "securite", "autre",
];

const PIECES = [
  "Cuisine", "Salon", "Chambre", "Salle de bain", "Garage",
  "Jardin", "Cave", "Grenier", "Extérieur", "Autre",
];

const COULEUR_CAT: Record<string, string> = {
  cuisine: "bg-orange-100 text-orange-700",
  menage: "bg-blue-100 text-blue-700",
  salle_de_bain: "bg-cyan-100 text-cyan-700",
  chauffage: "bg-red-100 text-red-700",
  electricite: "bg-yellow-100 text-yellow-700",
  plomberie: "bg-indigo-100 text-indigo-700",
  exterieur: "bg-green-100 text-green-700",
  securite: "bg-purple-100 text-purple-700",
  autre: "bg-gray-100 text-gray-700",
};

// ─── Carte Tâche ──────────────────────────────────────────────

function CarteTache({
  tache,
  onDelete,
}: {
  tache: TacheEntretien;
  onDelete: () => void;
}) {
  const estEnRetard =
    tache.prochaine_fois && new Date(tache.prochaine_fois) < new Date();

  return (
    <Card className={estEnRetard ? "border-amber-300" : ""}>
      <CardContent className="py-3">
        <div className="flex items-start gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              {tache.fait ? (
                <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
              ) : estEnRetard ? (
                <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0" />
              ) : (
                <Clock className="h-4 w-4 text-muted-foreground shrink-0" />
              )}
              <p className="text-sm font-medium">{tache.nom}</p>
              {tache.categorie && (
                <Badge
                  className={`text-[10px] ${COULEUR_CAT[tache.categorie] ?? COULEUR_CAT["autre"]}`}
                >
                  {tache.categorie.replace(/_/g, " ")}
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1">
              {tache.piece && (
                <span className="text-xs text-muted-foreground">{tache.piece}</span>
              )}
              {tache.frequence_jours != null && (
                <span className="text-xs text-muted-foreground">
                  Tous les {tache.frequence_jours} j
                </span>
              )}
              {tache.duree_minutes != null && (
                <span className="text-xs text-muted-foreground">
                  ~{tache.duree_minutes} min
                </span>
              )}
              {tache.prochaine_fois && (
                <span
                  className={`text-xs ${estEnRetard ? "text-amber-600 font-medium" : "text-muted-foreground"}`}
                >
                  Prochaine : {new Date(tache.prochaine_fois).toLocaleDateString("fr-FR")}
                </span>
              )}
            </div>
          </div>
          <Button
            variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive shrink-0"
            onClick={onDelete}
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Page principale ──────────────────────────────────────────

export default function PageEntretien() {
  const queryClient = useQueryClient();

  const formVide = {
    nom: "", categorie: "", piece: "",
    frequence_jours: "", duree_minutes: "", responsable: "",
  };
  const [form, setForm] = useState(formVide);

  const { dialogOuvert, setDialogOuvert, ouvrirCreation, fermerDialog } =
    utiliserDialogCrud<TacheEntretien>({
      onOuvrirCreation: () => setForm(formVide),
    });

  const { data: taches, isLoading } = utiliserRequete(
    ["maison", "entretien"],
    () => listerTachesEntretien()
  );
  const { data: sante } = utiliserRequete(
    ["maison", "entretien", "sante"],
    obtenirSanteAppareils
  );

  const invalider = () =>
    queryClient.invalidateQueries({ queryKey: ["maison", "entretien"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Omit<TacheEntretien, "id">) => creerTacheEntretien(data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Tâche ajoutée"); } }
  );
  const { mutate: supprimer } = utiliserMutation(supprimerTacheEntretien, {
    onSuccess: () => { invalider(); toast.success("Tâche supprimée"); },
  });

  const soumettre = () => {
    const payload = {
      nom: form.nom,
      categorie: form.categorie || undefined,
      piece: form.piece || undefined,
      frequence_jours: form.frequence_jours ? Number(form.frequence_jours) : undefined,
      duree_minutes: form.duree_minutes ? Number(form.duree_minutes) : undefined,
      responsable: form.responsable || undefined,
      fait: false,
    } as Omit<TacheEntretien, "id">;
    creer(payload);
  };

  const tachesEnRetard = taches?.filter(
    (t) => t.prochaine_fois && new Date(t.prochaine_fois) < new Date()
  ) ?? [];

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <SprayCan className="h-6 w-6 text-primary" />
          Entretien
        </h1>
        <p className="text-muted-foreground">Planifiez et suivez l&apos;entretien de votre maison</p>
      </div>

      {/* Santé appareils */}
      {sante && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Santé globale
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex items-center gap-3">
              <span
                className={`text-3xl font-bold ${
                  sante.score_global >= 80
                    ? "text-green-600"
                    : sante.score_global >= 50
                    ? "text-amber-600"
                    : "text-red-600"
                }`}
              >
                {sante.score_global}
              </span>
              <span className="text-sm text-muted-foreground">/100</span>
            </div>
            {sante.actions_urgentes.length > 0 && (
              <div className="mt-2 space-y-1">
                {sante.actions_urgentes.slice(0, 3).map((a, i) => (
                  <p key={i} className="text-xs text-amber-700 flex items-center gap-1">
                    <AlertTriangle className="h-3 w-3" />
                    {a.tache} — {a.zone} ({a.jours_retard} j de retard)
                  </p>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Alertes retard */}
      {tachesEnRetard.length > 0 && (
        <Card className="border-amber-300">
          <CardContent className="py-3">
            <p className="text-sm font-medium text-amber-700 flex items-center gap-1.5">
              <AlertTriangle className="h-4 w-4" />
              {tachesEnRetard.length} tâche(s) en retard
            </p>
          </CardContent>
        </Card>
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
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-16" />)}
        </div>
      ) : !taches?.length ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <SprayCan className="h-10 w-10 mx-auto mb-3 opacity-30" />
            <p className="font-medium">Aucune tâche d&apos;entretien</p>
            <p className="text-xs mt-1">Ajoutez vos routines d&apos;entretien pour les suivre</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {taches.map((t) => (
            <CarteTache
              key={t.id}
              tache={t}
              onDelete={() => supprimer(t.id)}
            />
          ))}
        </div>
      )}

      {/* Formulaire */}
      <DialogueFormulaire
        ouvert={dialogOuvert}
        onClose={fermerDialog}
        titre="Nouvelle tâche d'entretien"
        onSubmit={soumettre}
        enCours={enCreation}
      >
        <div className="space-y-3">
          <div className="space-y-1">
            <Label htmlFor="nom">Tâche *</Label>
            <Input
              id="nom"
              value={form.nom}
              onChange={(e) => setForm((f) => ({ ...f, nom: e.target.value }))}
              placeholder="ex: Nettoyer le four"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="categorie">Catégorie</Label>
              <Input
                id="categorie"
                value={form.categorie}
                onChange={(e) => setForm((f) => ({ ...f, categorie: e.target.value }))}
                list="categories-list"
                placeholder="ex: cuisine"
              />
              <datalist id="categories-list">
                {CATEGORIES.map((c) => <option key={c} value={c} />)}
              </datalist>
            </div>
            <div className="space-y-1">
              <Label htmlFor="piece">Pièce</Label>
              <Input
                id="piece"
                value={form.piece}
                onChange={(e) => setForm((f) => ({ ...f, piece: e.target.value }))}
                list="pieces-list"
                placeholder="ex: Cuisine"
              />
              <datalist id="pieces-list">
                {PIECES.map((p) => <option key={p} value={p} />)}
              </datalist>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="frequence">Fréquence (jours)</Label>
              <Input
                id="frequence"
                type="number"
                min="1"
                value={form.frequence_jours}
                onChange={(e) => setForm((f) => ({ ...f, frequence_jours: e.target.value }))}
                placeholder="ex: 30"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="duree">Durée (min)</Label>
              <Input
                id="duree"
                type="number"
                min="1"
                value={form.duree_minutes}
                onChange={(e) => setForm((f) => ({ ...f, duree_minutes: e.target.value }))}
                placeholder="ex: 30"
              />
            </div>
          </div>
          <div className="space-y-1">
            <Label htmlFor="responsable">Responsable</Label>
            <Input
              id="responsable"
              value={form.responsable}
              onChange={(e) => setForm((f) => ({ ...f, responsable: e.target.value }))}
              placeholder="ex: Papa, Maman…"
            />
          </div>
        </div>
      </DialogueFormulaire>
    </div>
  );
}

