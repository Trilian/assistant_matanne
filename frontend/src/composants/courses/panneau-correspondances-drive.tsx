"use client";

import { ExternalLink, Link2, Link2Off, RefreshCcw, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { supprimerCorrespondanceDrive } from "@/bibliotheque/api/courses";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import { utiliserInvalidation, utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import type { CorrespondanceDrive } from "@/types/courses";
import { listerCorrespondancesDrive } from "@/bibliotheque/api/courses";

type PanneauCorrespondancesDriveProps = {
  visible?: boolean;
};

function lancerRemappageDepuisExtension(correspondance: CorrespondanceDrive) {
  if (typeof window === "undefined") {
    toast.error("Le remappage n'est disponible que dans le navigateur.");
    return;
  }

  const apiBaseUrl = `${window.location.origin}/api/v1`.replace("/connexion/api/v1", "/api/v1");
  const apiToken = window.localStorage.getItem("access_token");

  window.postMessage(
    {
      source: "assistant-matanne",
      type: "REMAP_CARREFOUR_DRIVE",
      payload: {
        apiBaseUrl,
        apiToken,
        article: {
          id: correspondance.id,
          nom: correspondance.nom_article,
          ingredient_id: correspondance.ingredient_id,
          quantite: correspondance.quantite_par_defaut,
          categorie: "carrefour_drive",
        },
      },
    },
    window.location.origin
  );

  toast.info(`Recherche Carrefour ouverte pour remapper « ${correspondance.nom_article} ».`);
}

export function PanneauCorrespondancesDrive({ visible = true }: PanneauCorrespondancesDriveProps) {
  const invalider = utiliserInvalidation();
  const { data: correspondances, isLoading, refetch, isRefetching } = utiliserRequete(
    ["courses", "correspondances-drive"],
    () => listerCorrespondancesDrive(true),
    { enabled: visible, staleTime: 30_000 }
  );

  const { mutate: desactiver, isPending: enSuppression } = utiliserMutation(
    (id: number) => supprimerCorrespondanceDrive(id),
    {
      onSuccess: () => {
        invalider(["courses", "correspondances-drive"]);
        invalider(["courses"]);
        toast.success("Correspondance Drive désactivée");
      },
      onError: () => toast.error("Impossible de désactiver cette correspondance"),
    }
  );

  if (!visible) return null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-3">
        <div>
          <CardTitle className="text-base">Correspondances Carrefour Drive</CardTitle>
          <CardDescription>
            Produits déjà associés pour l’ajout automatique au panier.
          </CardDescription>
        </div>
        <Button size="sm" variant="outline" onClick={() => refetch()} disabled={isRefetching}>
          <RefreshCcw className="mr-1 h-4 w-4" />
          Actualiser
        </Button>
      </CardHeader>
      <CardContent>
        <div className="mb-4 rounded-lg border border-dashed bg-muted/30 px-4 py-3 text-sm">
          <p className="font-medium">Comment ça marche ?</p>
          <ol className="mt-2 list-decimal space-y-1 pl-5 text-muted-foreground">
            <li>Un premier choix manuel sur Carrefour crée la correspondance automatiquement.</li>
            <li>Ensuite, l’article est ajouté directement au Drive sans re-choix.</li>
            <li>Le bouton <strong>Forcer remappage</strong> relance une recherche si le produit a changé.</li>
          </ol>
        </div>

        {isLoading ? (
          <p className="text-sm text-muted-foreground">Chargement des correspondances…</p>
        ) : !correspondances?.length ? (
          <div className="rounded-lg border border-dashed px-4 py-6 text-sm text-muted-foreground">
            Aucune correspondance enregistrée pour le moment.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Article liste</TableHead>
                <TableHead>Produit Carrefour</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Usage</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {correspondances.map((correspondance: CorrespondanceDrive) => (
                <TableRow key={correspondance.id}>
                  <TableCell className="font-medium">{correspondance.nom_article}</TableCell>
                  <TableCell>
                    <div className="max-w-[280px] whitespace-normal">
                      <div>{correspondance.produit_drive_nom}</div>
                      {correspondance.produit_drive_ean ? (
                        <div className="text-xs text-muted-foreground">
                          EAN : {correspondance.produit_drive_ean}
                        </div>
                      ) : null}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className="bg-emerald-100 text-emerald-800">
                      {correspondance.actif ? "Actif" : "Inactif"}
                    </Badge>
                  </TableCell>
                  <TableCell>{correspondance.nb_utilisations}</TableCell>
                  <TableCell>
                    <div className="flex justify-end gap-2">
                      {correspondance.produit_drive_url ? (
                        <Button asChild size="sm" variant="outline">
                          <a href={correspondance.produit_drive_url} target="_blank" rel="noreferrer">
                            <ExternalLink className="mr-1 h-4 w-4" />
                            Ouvrir
                          </a>
                        </Button>
                      ) : (
                        <Button size="sm" variant="outline" disabled>
                          <Link2Off className="mr-1 h-4 w-4" />
                          Sans lien
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => lancerRemappageDepuisExtension(correspondance)}
                      >
                        <Link2 className="mr-1 h-4 w-4" />
                        Forcer remappage
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => desactiver(correspondance.id)}
                        disabled={enSuppression}
                      >
                        <Trash2 className="mr-1 h-4 w-4" />
                        Retirer
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
