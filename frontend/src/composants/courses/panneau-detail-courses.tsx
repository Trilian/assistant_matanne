import type { RefObject } from "react";
import type {
  FieldErrors,
  UseFormHandleSubmit,
  UseFormRegister,
} from "react-hook-form";
import { AnimatePresence, motion } from "framer-motion";
import {
  CheckSquare,
  Loader2,
  Mic,
  MicOff,
  Plus,
  ScanLine,
  ShoppingCart,
  Trash2,
} from "lucide-react";

import type { DonneesArticleCourses } from "@/bibliotheque/validateurs";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { EtatVide } from "@/composants/ui/etat-vide";
import { Input } from "@/composants/ui/input";
import { Skeleton } from "@/composants/ui/skeleton";
import { ItemAnime } from "@/composants/ui/motion-utils";
import { TileArticle } from "@/composants/cuisine/tile-article";
import type { ArticleCourses, ListeCourses } from "@/types/courses";

type PanneauDetailCoursesProps = {
  listeSelectionnee: number | null;
  detailListe?: ListeCourses;
  chargementDetail: boolean;
  enAjout: boolean;
  estSupporte: boolean;
  enEcoute: boolean;
  modeSelection: boolean;
  enCochageSelection: boolean;
  enSuppressionSelection: boolean;
  enCochageCategorie: boolean;
  enFinalisationCourses: boolean;
  articles: ArticleCourses[];
  articlesNonCoches: ArticleCourses[];
  articlesCoches: ArticleCourses[];
  categoriesTriees: string[];
  magasinActif?: string | null;
  groupesNonCoches: Record<string, ArticleCourses[]>;
  articlesSelectionnes: Set<number>;
  inputAjoutRef: RefObject<HTMLInputElement | null>;
  erreursArticle: FieldErrors<DonneesArticleCourses>;
  regArticle: UseFormRegister<DonneesArticleCourses>;
  submitArticle: UseFormHandleSubmit<DonneesArticleCourses>;
  onAjouterArticle: (data: DonneesArticleCourses) => void;
  onToggleVocal: () => void;
  onOuvrirScanneur: () => void;
  onOuvrirDialogueArticle: () => void;
  onBasculerSelectionArticle: (articleId: number) => void;
  onBasculerToutSelectionner: () => void;
  onCocherSelection: () => void;
  onSupprimerSelection: () => void;
  onCocherCategorie: (categorie: string) => void;
  onCocherArticle: (articleId: number, coche: boolean) => void;
  onSupprimerArticle: (article: ArticleCourses) => void;
};

export function PanneauDetailCourses({
  listeSelectionnee,
  detailListe,
  chargementDetail,
  enAjout,
  estSupporte,
  enEcoute,
  modeSelection,
  enCochageSelection,
  enSuppressionSelection,
  enCochageCategorie,
  enFinalisationCourses,
  articles,
  articlesNonCoches,
  articlesCoches,
  categoriesTriees,
  magasinActif,
  groupesNonCoches,
  articlesSelectionnes,
  inputAjoutRef,
  erreursArticle,
  regArticle,
  submitArticle,
  onAjouterArticle,
  onToggleVocal,
  onOuvrirScanneur,
  onOuvrirDialogueArticle,
  onBasculerSelectionArticle,
  onBasculerToutSelectionner,
  onCocherSelection,
  onSupprimerSelection,
  onCocherCategorie,
  onCocherArticle,
  onSupprimerArticle,
}: PanneauDetailCoursesProps) {
  return (
    <Card className="lg:col-span-2">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-lg">
            {detailListe?.nom ?? "Sélectionner une liste"}
          </CardTitle>
          {detailListe && (
            <CardDescription>
              {articlesNonCoches.length} restant(s) sur {articles.length} article(s)
            </CardDescription>
          )}
        </div>
        <div className="flex gap-1">
          {listeSelectionnee && (
            <>
              <Button size="sm" variant="outline" onClick={onOuvrirScanneur}>
                <ScanLine className="mr-1 h-4 w-4" />
                Scanner
              </Button>
              <Button size="sm" onClick={onOuvrirDialogueArticle}>
                <Plus className="mr-1 h-4 w-4" />
                Article
              </Button>
            </>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {!listeSelectionnee ? (
          <EtatVide
            Icone={ShoppingCart}
            titre="Selectionnez une liste"
            description="Choisissez une liste existante ou creez-en une nouvelle pour ajouter des articles."
            className="py-10"
          />
        ) : (
          <div className="space-y-4">
            {detailListe?.etat === "brouillon" && (
              <div className="rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900">
                Cette liste est en brouillon. Confirmez-la avant de finaliser les courses.
              </div>
            )}

            <motion.form
              onSubmit={submitArticle((data) => onAjouterArticle(data))}
              className="sticky top-0 z-10 flex gap-2 border-b bg-card pb-3"
              animate={erreursArticle.nom ? { x: [0, -6, 6, -4, 4, 0] } : { x: 0 }}
              transition={{ duration: 0.35 }}
            >
              <Input
                {...regArticle("nom")}
                ref={(element) => {
                  regArticle("nom").ref(element);
                  inputAjoutRef.current = element;
                }}
                placeholder="+ Ajouter un article..."
                className="flex-1"
                disabled={enAjout}
              />
              <Button type="submit" size="sm" disabled={enAjout} aria-label="Ajouter l'article">
                {enAjout ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
              </Button>
              {estSupporte && (
                <Button
                  type="button"
                  size="sm"
                  variant={enEcoute ? "secondary" : "outline"}
                  aria-label="Saisie vocale"
                  onClick={onToggleVocal}
                >
                  {enEcoute ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                </Button>
              )}
            </motion.form>

            {modeSelection && (
              <div className="flex flex-wrap items-center gap-2 rounded-lg border bg-muted/40 px-3 py-2 text-sm">
                <span className="font-medium">{articlesSelectionnes.size} sélectionné(s)</span>
                <Button size="sm" variant="outline" onClick={onBasculerToutSelectionner}>
                  {articlesSelectionnes.size === articlesNonCoches.length
                    ? "Tout désélectionner"
                    : "Tout sélectionner"}
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={onCocherSelection}
                  disabled={articlesSelectionnes.size === 0 || enCochageSelection}
                >
                  <CheckSquare className="mr-1 h-4 w-4" />
                  Cocher la sélection
                </Button>
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={onSupprimerSelection}
                  disabled={articlesSelectionnes.size === 0 || enSuppressionSelection}
                >
                  <Trash2 className="mr-1 h-4 w-4" />
                  Supprimer la sélection
                </Button>
              </div>
            )}

            {chargementDetail ? (
              <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-5">
                {Array.from({ length: 10 }).map((_, index) => (
                  <Skeleton key={index} className="aspect-square rounded-xl" />
                ))}
              </div>
            ) : articles.length === 0 ? (
              <EtatVide
                Icone={ShoppingCart}
                titre={magasinActif ? "Aucun article pour ce magasin" : "Liste vide"}
                description={
                  magasinActif
                    ? "Ajoutez des articles pour ce magasin ou changez le filtre actif."
                    : "Ajoutez un article via le champ rapide ou le scan code-barres."
                }
                className="py-10"
              />
            ) : (
              <div className="space-y-6">
                {categoriesTriees.map((categorie) => (
                  <div key={categorie}>
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <h3 className="text-sm font-semibold">{categorie}</h3>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 px-2 text-xs"
                        onClick={() => onCocherCategorie(categorie)}
                        disabled={enCochageCategorie || enFinalisationCourses}
                      >
                        Cocher catégorie
                      </Button>
                    </div>
                    <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-5">
                      <AnimatePresence mode="popLayout">
                      {groupesNonCoches[categorie].map((article, idx) => (
                        <ItemAnime key={article.id} index={idx}>
                        <TileArticle
                          key={article.id}
                          nom={article.nom}
                          quantite={article.quantite}
                          unite={article.unite}
                          categorie={article.categorie}
                          magasinCible={article.magasin_cible}
                          driveMappe={article.drive_mappe}
                          prixEstime={article.prix_estime}
                          estSelectionne={articlesSelectionnes.has(article.id)}
                          onClick={() => {
                            if (modeSelection) {
                              onBasculerSelectionArticle(article.id);
                            } else {
                              onCocherArticle(article.id, true);
                            }
                          }}
                          onLongPress={() => {
                            if (modeSelection) {
                              onBasculerSelectionArticle(article.id);
                            } else {
                              onSupprimerArticle(article);
                            }
                          }}
                        />
                        </ItemAnime>
                      ))}
                      </AnimatePresence>
                    </div>
                  </div>
                ))}

                {articlesCoches.length > 0 && (
                  <div>
                    <h3 className="mb-2 text-sm font-semibold text-muted-foreground">
                      Complétés ({articlesCoches.length})
                    </h3>
                    <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-5">
                      <AnimatePresence mode="popLayout">
                      {articlesCoches.map((article, idx) => (
                        <ItemAnime key={article.id} index={idx}>
                        <TileArticle
                          key={article.id}
                          nom={article.nom}
                          quantite={article.quantite}
                          unite={article.unite}
                          categorie={article.categorie}
                          magasinCible={article.magasin_cible}
                          driveMappe={article.drive_mappe}
                          prixEstime={article.prix_estime}
                          estCoche
                          onClick={() => onCocherArticle(article.id, false)}
                        />
                        </ItemAnime>
                      ))}
                      </AnimatePresence>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
