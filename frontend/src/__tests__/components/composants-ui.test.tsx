import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Calendar, Package, ShoppingCart, CheckCircle2 } from "lucide-react";
import { describe, expect, it, vi } from "vitest";

import { FriseFluxCuisine } from "@/composants/cuisine/frise-flux-cuisine";
import { SkeletonPage } from "@/composants/ui/skeleton-page";

describe("FriseFluxCuisine", () => {
  it("affiche les étapes et permet de naviguer dans le flux", async () => {
    const user = userEvent.setup();
    const onSelectionEtape = vi.fn();

    render(
      <FriseFluxCuisine
        etapeActive={1}
        progression={50}
        onSelectionEtape={onSelectionEtape}
        etapes={[
          {
            id: "planning",
            titre: "Planning",
            description: "Créer la semaine",
            icone: Calendar,
            resume: "7 repas planifiés",
          },
          {
            id: "inventaire",
            titre: "Inventaire",
            description: "Vérifier le stock",
            icone: Package,
            resume: "12 articles disponibles",
            meta: "2 alertes stock à vérifier",
            alerte: true,
          },
          {
            id: "courses",
            titre: "Courses",
            description: "Générer la liste",
            icone: ShoppingCart,
            resume: "Liste en attente",
          },
          {
            id: "recap",
            titre: "Récapitulatif",
            description: "Valider et préparer",
            icone: CheckCircle2,
            resume: "Synthèse prête",
          },
        ]}
      />
    );

    expect(screen.getByText("Flux interactif repas → inventaire → courses")).toBeInTheDocument();
    expect(screen.getByText("12 articles disponibles")).toBeInTheDocument();
    expect(screen.getByText("50% du parcours")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /courses/i }));
    expect(onSelectionEtape).toHaveBeenCalledWith(2);
  });
});

describe("SkeletonPage", () => {
  it("rend un squelette de page réutilisable", () => {
    const { container } = render(
      <SkeletonPage ariaLabel="Chargement de test" lignes={["h-4 w-20", "h-8 w-40", "h-16 w-full"]} />
    );

    expect(screen.getByLabelText("Chargement de test")).toBeInTheDocument();
    expect(container.querySelectorAll('[data-slot="skeleton"]')).toHaveLength(3);
  });
});
