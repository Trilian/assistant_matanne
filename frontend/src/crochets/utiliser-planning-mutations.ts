import { useCallback, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { utiliserInvalidation, utiliserMutation } from "@/crochets/utiliser-api";
import { utiliserSuppressionAnnulable } from "@/crochets/utiliser-suppression-annulable";
import {
  definirRepas,
  supprimerRepas,
  mettreAJourRepas,
  genererPlanningSemaine,
  validerPlanning,
  regenererPlanning,
  regenererRepasIA,
  type ResultatGenerationPlanning,
} from "@/bibliotheque/api/planning";
import { genererCoursesDepuisPlanning, type GenererCoursesResult } from "@/bibliotheque/api/courses";
import { envoyerPlanningTelegram } from "@/bibliotheque/api/telegram";
import { genererSessionDepuisPlanning } from "@/bibliotheque/api/batch-cooking";
import { obtenirFluxCuisine, type FluxCuisine } from "@/bibliotheque/api/ia-bridges";
import {
  analyserVarietePlanningRepas,
  optimiserNutritionPlanningRepas,
  suggererSimplificationPlanningRepas,
} from "@/bibliotheque/api/ia-modules";
import type { CreerRepasPlanningDTO, RepasPlanning } from "@/types/planning";
import type { GenererSessionDepuisPlanningResult } from "@/types/batch-cooking";
import type { AnalysePlanningIaResultat } from "@/composants/planning/panneau-analyse-ia";
import type { ObjetDonnees } from "@/types/commun";

type ModeInvites = {
  nbInvites: number;
  occasion: string;
  evenements: string[];
};

type PlanningAnalyseLigne = {
  jour: string;
  petit_dej: string;
  midi: string;
  soir: string;
};

type UtiliserPlanningMutationsParams = {
  dateDebut: string;
  nbPersonnesBase: number;
  contexteInvitesActif: boolean;
  modeInvites: ModeInvites;
  evenementsModeInvites: string[];
  identifiantPresencePlanning: string;
  diffuserPlanning: (message: ObjetDonnees) => void;
  setRepasIdCree: (id: number | null) => void;
  setDialogueEtape: (etape: "choisir" | "equilibre") => void;
  setDialogueOuvert: (ouvert: boolean) => void;
  setNotesRepas: (notes: string) => void;
  setErreurIA: (message: string | null) => void;
  setCoursesResultat: (resultat: GenererCoursesResult | null) => void;
  setCoursesDialogue: (ouvert: boolean) => void;
  planningPourAnalyseIa: PlanningAnalyseLigne[];
  setAnalysePlanningIa: (resultat: AnalysePlanningIaResultat | null) => void;
  planningId?: number;
  setBatchResultat: (resultat: GenererSessionDepuisPlanningResult | null) => void;
  setBatchDialogue: (ouvert: boolean) => void;
};

export function utiliserPlanningMutations({
  dateDebut,
  nbPersonnesBase,
  contexteInvitesActif,
  modeInvites,
  evenementsModeInvites,
  identifiantPresencePlanning,
  diffuserPlanning,
  setRepasIdCree,
  setDialogueEtape,
  setDialogueOuvert,
  setNotesRepas,
  setErreurIA,
  setCoursesResultat,
  setCoursesDialogue,
  planningPourAnalyseIa,
  setAnalysePlanningIa,
  planningId,
  setBatchResultat,
  setBatchDialogue,
}: UtiliserPlanningMutationsParams) {
  const invalider = utiliserInvalidation();
  const queryClient = useQueryClient();
  const { planifierSuppression } = utiliserSuppressionAnnulable({ ttlMs: 8000 });
  const toastIaRef = useRef<string | number | null>(null);

  const { mutate: ajouterRepas, isPending: enAjout } = utiliserMutation(
    (dto: CreerRepasPlanningDTO) => definirRepas(dto),
    {
      onSuccess: (resultat, dto) => {
        invalider(["planning"]);
        diffuserPlanning({
          action: "repas_added",
          data: { date: dto.date, type_repas: dto.type_repas },
          user_id: identifiantPresencePlanning,
        });
        if (dto.type_repas !== "petit_dejeuner" && "id" in resultat && typeof (resultat as { id: number }).id === "number") {
          setRepasIdCree((resultat as { id: number }).id);
          setDialogueEtape("equilibre");
          toast.success("Repas ajouté — ajoutez les accompagnements !");
        } else {
          setDialogueOuvert(false);
          setNotesRepas("");
          toast.success("Repas ajouté");
        }
      },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const { mutate: confirmerSuppressionRepas } = utiliserMutation((repas: RepasPlanning) => supprimerRepas(repas.id), {
    onSuccess: (_resultat, repas) => {
      invalider(["planning"]);
      diffuserPlanning({
        action: "repas_removed",
        data: { repas_id: repas.id, date: repas.date_repas || repas.date, type_repas: repas.type_repas },
        user_id: identifiantPresencePlanning,
      });
      toast.success("Repas retiré");
    },
    onError: () => toast.error("Erreur lors de la suppression"),
  });

  const retirerRepas = useCallback(
    (repas: RepasPlanning) => {
      const libelle = repas.recette_nom || repas.notes || `${repas.type_repas} du ${repas.date_repas || repas.date}`;
      planifierSuppression(`repas-${repas.id}`, {
        libelle,
        onConfirmer: () => confirmerSuppressionRepas(repas),
        onErreur: () => toast.error("Erreur lors de la suppression"),
      });
    },
    [confirmerSuppressionRepas, planifierSuppression]
  );

  const modifierChampRepas = useCallback(
    async (repasId: number, champ: string, valeur: string) => {
      try {
        await mettreAJourRepas(repasId, { [champ]: valeur } as Record<string, string>);
        invalider(["planning"]);
      } catch {
        toast.error("Erreur lors de la modification");
      }
    },
    [invalider]
  );

  const { mutate: genererIA, isPending: enGeneration } = utiliserMutation(
    (params?: { legumes_souhaites?: string[]; feculents_souhaites?: string[]; plats_souhaites?: string[]; ingredients_interdits?: string[]; autoriser_restes?: boolean; nb_personnes?: number; cuisines_souhaitees?: string[] }) =>
      genererPlanningSemaine({
        date_debut: dateDebut,
        nb_personnes: params?.nb_personnes ?? nbPersonnesBase + (contexteInvitesActif ? modeInvites.nbInvites : 0),
        preferences:
          contexteInvitesActif || evenementsModeInvites.length > 0
            ? {
                mode_invites: contexteInvitesActif,
                nb_invites: contexteInvitesActif ? modeInvites.nbInvites : 0,
                occasion: modeInvites.occasion || undefined,
                evenements: evenementsModeInvites,
              }
            : undefined,
        legumes_souhaites: params?.legumes_souhaites ?? [],
        feculents_souhaites: params?.feculents_souhaites ?? [],
        plats_souhaites: params?.plats_souhaites ?? [],
        ingredients_interdits: params?.ingredients_interdits ?? [],
        autoriser_restes: params?.autoriser_restes ?? true,
        cuisines_souhaitees: params?.cuisines_souhaitees ?? [],
      }),
    {
      onSuccess: async (resultat: ResultatGenerationPlanning) => {
        if (toastIaRef.current !== null) {
          toast.dismiss(toastIaRef.current);
          toastIaRef.current = null;
        }

        if (resultat.planning_id) {
          queryClient.setQueryData(["flux", "cuisine", String(resultat.planning_id)], {
            etape_actuelle: "valider_planning",
            planning: {
              id: resultat.planning_id,
              semaine: resultat.date_debut,
              etat: "brouillon",
            },
            courses: null,
            actions_suivantes: [],
          });
          void queryClient.invalidateQueries({ queryKey: ["flux", "cuisine", String(resultat.planning_id)] });
          void obtenirFluxCuisine(resultat.planning_id);
        }

        void queryClient.refetchQueries({ queryKey: ["planning", dateDebut], exact: true });
        invalider(["planning"]);
        setTimeout(() => {
          void queryClient.refetchQueries({ queryKey: ["planning", dateDebut], exact: true });
        }, 3000);

        if (!resultat.genere_par_ia) {
          const msg = "Le planning a été créé sans IA. Réessayez ou vérifiez la clé Mistral.";
          setErreurIA(msg);
          toast.error(msg, { duration: 8000 });
        } else {
          setErreurIA(null);
          toast.success("Planning généré par l'IA !", { duration: 5000 });
        }

        if (resultat?.planning_id) {
          try {
            await envoyerPlanningTelegram(resultat.planning_id);
          } catch {
            if (resultat.genere_par_ia) {
              toast.info("Planning généré, notification Telegram non envoyée.");
            }
          }
        }
      },
      onError: (erreur) => {
        if (toastIaRef.current !== null) {
          toast.dismiss(toastIaRef.current);
          toastIaRef.current = null;
        }
        invalider(["planning"]);
        invalider(["flux", "cuisine"]);
        const detail =
          (erreur as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
        const msg = detail ?? "Erreur lors de la génération IA";
        setErreurIA(msg);
        toast.error(msg, { duration: 6000 });
      },
    }
  );

  const lancerGenerationIA = (params?: { legumes_souhaites?: string[]; feculents_souhaites?: string[]; plats_souhaites?: string[]; ingredients_interdits?: string[]; autoriser_restes?: boolean; nb_personnes?: number; cuisines_souhaitees?: string[] }) => {
    toastIaRef.current = toast.loading("Génération IA en cours… cela peut prendre 1 à 2 minutes ☕", {
      duration: Infinity,
    });
    genererIA(params);
  };

  const { mutate: genererCourses, isPending: enGenerationCourses } = utiliserMutation(
    () =>
      genererCoursesDepuisPlanning(dateDebut, {
        nbInvites: contexteInvitesActif ? modeInvites.nbInvites : 0,
        nbPersonnes: nbPersonnesBase,
        evenements: evenementsModeInvites,
        nomListe:
          contexteInvitesActif && modeInvites.occasion
            ? `Courses ${modeInvites.occasion}`
            : undefined,
      }),
    {
      onSuccess: (result) => {
        setCoursesResultat(result);
        setCoursesDialogue(true);
        toast.success(`${result.total_articles} articles ajoutés !`);
      },
      onError: (err) => {
        const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
        toast.error(detail ?? "Erreur lors de la génération des courses", { duration: 8000 });
      },
    }
  );

  const { mutate: analyserPlanningIA, isPending: enAnalysePlanningIA } = utiliserMutation(
    async () => {
      if (planningPourAnalyseIa.length === 0) {
        throw new Error("Ajoutez au moins un repas sur la semaine avant l'analyse IA.");
      }

      const [variete, nutritionIA, simplification] = await Promise.all([
        analyserVarietePlanningRepas({ planning_repas: planningPourAnalyseIa }),
        optimiserNutritionPlanningRepas({ planning_repas: planningPourAnalyseIa }),
        suggererSimplificationPlanningRepas({
          planning_repas: planningPourAnalyseIa,
          nb_heures_cuisine_max: 4,
        }),
      ]);

      return { variete, nutrition: nutritionIA, simplification };
    },
    {
      onSuccess: (resultat) => {
        setAnalysePlanningIa(resultat);
        toast.success("Analyse IA du planning prête");
      },
      onError: (erreur) => {
        toast.error(erreur instanceof Error ? erreur.message : "Erreur lors de l'analyse IA");
      },
    }
  );

  const { mutate: validerBrouillonPlanning, isPending: enValidationPlanning } = utiliserMutation(
    (ciblePlanningId: number) => validerPlanning(ciblePlanningId),
    {
      onSuccess: () => {
        queryClient.setQueriesData<FluxCuisine>(
          { queryKey: ["flux", "cuisine"] },
          (old) => (old?.etape_actuelle === "valider_planning" ? { ...old, etape_actuelle: "generer_courses" } : old)
        );
        invalider(["planning"]);
        invalider(["flux", "cuisine"]);
        toast.success("Planning validé, vous pouvez confirmer la liste de courses ensuite.");
      },
      onError: () => toast.error("Impossible de valider ce planning"),
    }
  );

  const { mutate: regenererBrouillonPlanning, isPending: enRegenerationPlanning } = utiliserMutation(
    (ciblePlanningId: number) => regenererPlanning(ciblePlanningId),
    {
      onSuccess: () => {
        invalider(["planning"]);
        invalider(["flux", "cuisine"]);
        toast.success("Nouveau brouillon généré");
      },
      onError: () => toast.error("Impossible de régénérer le planning"),
    }
  );

  const { mutate: regenererUnRepas, isPending: enRegenerationRepas } = utiliserMutation(
    (repasId: number) => regenererRepasIA(repasId),
    {
      onSuccess: (result) => {
        invalider(["planning"]);
        toast.success(result.message || "Repas régénéré");
      },
      onError: () => toast.error("Impossible de régénérer ce repas"),
    }
  );

  const { mutate: genererBatch, isPending: enGenerationBatch } = utiliserMutation(
    () => {
      if (!planningId) {
        throw new Error("Planning sans identifiant. Générez d'abord un planning persistant.");
      }
      const dimanche = new Date(dateDebut);
      dimanche.setDate(dimanche.getDate() + 6);
      return genererSessionDepuisPlanning({
        planning_id: planningId,
        date_session: dimanche.toISOString().split("T")[0],
      });
    },
    {
      onSuccess: (result) => {
        setBatchResultat(result);
        setBatchDialogue(true);
        toast.success(`Session batch créée avec ${result.nb_recettes} recettes !`);
      },
      onError: () => toast.error("Erreur lors de la création de la session batch"),
    }
  );

  return {
    ajouterRepas,
    enAjout,
    retirerRepas,
    modifierChampRepas,
    lancerGenerationIA,
    enGeneration,
    genererCourses,
    enGenerationCourses,
    analyserPlanningIA,
    enAnalysePlanningIA,
    validerBrouillonPlanning,
    enValidationPlanning,
    regenererBrouillonPlanning,
    enRegenerationPlanning,
    regenererUnRepas,
    enRegenerationRepas,
    genererBatch,
    enGenerationBatch,
  };
}
