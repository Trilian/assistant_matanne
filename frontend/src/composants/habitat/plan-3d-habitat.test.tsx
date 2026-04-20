import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import Plan3DHabitat from "@/composants/habitat/plan-3d-habitat";
import type { PlanHabitatConfiguration3DServeur } from "@/types/habitat";

vi.mock("@react-three/fiber", () => ({
  Canvas: () => <div data-testid="canvas" />,
}));

vi.mock("@react-three/drei", () => ({
  OrbitControls: () => <div data-testid="orbit-controls" />,
  Text: ({ children }: { children: unknown }) => <span>{children as string}</span>,
}));

const piecesBase = [
  {
    id: 1,
    plan_id: 1,
    nom: "Salon",
    type_piece: "salon",
    surface_m2: 24,
  },
];

const configurationServeurBase: PlanHabitatConfiguration3DServeur = {
  plan_id: 1,
  configuration_courante: {
    layout_edition: [{ id: 1, x: 4, z: 5, width: 3.2, depth: 2.8, nom: "Salon", type_piece: "salon" }],
    palette_par_type: { salon: "#445566" },
  },
  variantes: [
    {
      id: "var-1",
      nom: "Option IA",
      source: "ia",
      configuration: {
        layout_edition: [{ id: 1, x: 5, z: 6, width: 3.4, depth: 2.9, nom: "Salon", type_piece: "salon" }],
        palette_par_type: { salon: "#556677" },
      },
    },
  ],
  variante_active_id: "var-1",
};

describe("Plan3DHabitat import/export", () => {
  const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();

    Object.defineProperty(window.URL, "createObjectURL", {
      value: vi.fn(() => "blob:test"),
      writable: true,
      configurable: true,
    });
    Object.defineProperty(window.URL, "revokeObjectURL", {
      value: vi.fn(),
      writable: true,
      configurable: true,
    });
  });

  afterEach(() => {
    localStorage.clear();
  });

  it("exporte la configuration en JSON", async () => {
    render(<Plan3DHabitat pieces={piecesBase} nomPlan="Plan test" planId={1} />);

    fireEvent.click(screen.getByRole("button", { name: /Exporter JSON/i }));

    expect(window.URL.createObjectURL).toHaveBeenCalledOnce();
    expect(clickSpy).toHaveBeenCalledOnce();
    expect(screen.getByText(/Configuration exportee en JSON/i)).toBeInTheDocument();
  });

  it("affiche un message si le JSON est invalide", async () => {
    render(<Plan3DHabitat pieces={piecesBase} nomPlan="Plan test" planId={1} />);

    const input = screen.getByTitle(/Importer une configuration 3D/i) as HTMLInputElement;
    const fichierInvalide = new File(["{invalide"], "bad.json", { type: "application/json" });

    fireEvent.change(input, { target: { files: [fichierInvalide] } });

    await waitFor(() => {
      expect(screen.getByText(/Import impossible: fichier JSON invalide/i)).toBeInTheDocument();
    });
  });

  it("affiche un apercu puis importe apres confirmation", async () => {
    render(<Plan3DHabitat pieces={piecesBase} nomPlan="Plan test" planId={1} />);

    const input = screen.getByTitle(/Importer une configuration 3D/i) as HTMLInputElement;
    const fichierValide = new File(
      [
        JSON.stringify({
          version: 1,
          plan_id: 999,
          nom_plan: "Autre plan",
          layoutEdition: [{ id: 1, x: 4, z: 5, width: 3.2, depth: 2.8 }],
          paletteParType: { salon: "#112233" },
        }),
      ],
      "plan_3d.json",
      { type: "application/json" }
    );

    fireEvent.change(input, { target: { files: [fichierValide] } });

    await waitFor(() => {
      expect(screen.getByText(/Apercu import JSON/i)).toBeInTheDocument();
      expect(screen.getByText(/Fichier: plan_3d.json/i)).toBeInTheDocument();
      expect(screen.getByText(/Plan source: Autre plan/i)).toBeInTheDocument();
      expect(screen.getByText(/Pieces importees: 1/i)).toBeInTheDocument();
      expect(screen.getByText(/Compatibilite locale: 1\/1 piece\(s\) correspondante\(s\)/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Confirmer import/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/Configuration importee depuis un autre plan: verifiez l'alignement des pieces\. \(1\/1 piece\(s\) appliquee\(s\)\)/i)
      ).toBeInTheDocument();
    });

    const etiquetteSalon = screen.getByText("salon").closest("label");
    const inputCouleur = etiquetteSalon?.querySelector("input[type='color']") as HTMLInputElement;
    expect(inputCouleur.value.toLowerCase()).toBe("#112233");
  });

  it("importe directement si la confirmation est desactivee", async () => {
    render(<Plan3DHabitat pieces={piecesBase} nomPlan="Plan test" planId={1} />);

    fireEvent.click(screen.getByRole("checkbox", { name: /Toujours demander confirmation avant import JSON/i }));

    expect(screen.getByRole("button", { name: /Reactiver confirmation/i })).toBeInTheDocument();

    const input = screen.getByTitle(/Importer une configuration 3D/i) as HTMLInputElement;
    const fichierValide = new File(
      [
        JSON.stringify({
          version: 1,
          plan_id: 1,
          nom_plan: "Plan test",
          layoutEdition: [{ id: 1, x: 4, z: 5, width: 3.2, depth: 2.8 }],
          paletteParType: { salon: "#223344" },
        }),
      ],
      "plan_3d_direct.json",
      { type: "application/json" }
    );

    fireEvent.change(input, { target: { files: [fichierValide] } });

    await waitFor(() => {
      expect(screen.getByText(/Configuration importee\. \(1\/1 piece\(s\) appliquee\(s\)\)/i)).toBeInTheDocument();
    });

    expect(screen.queryByText(/Apercu import JSON/i)).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Reactiver confirmation/i }));
    expect(screen.getByRole("checkbox", { name: /Toujours demander confirmation avant import JSON/i })).toBeChecked();
    expect(screen.getByText(/Confirmation avant import reactivee/i)).toBeInTheDocument();
  });

  it("sauvegarde la configuration courante sur le serveur", async () => {
    const onSauvegarderConfigurationServeur = vi.fn().mockResolvedValue(undefined);

    render(
      <Plan3DHabitat
        pieces={piecesBase}
        nomPlan="Plan test"
        planId={1}
        configurationServeur={configurationServeurBase}
        onSauvegarderConfigurationServeur={onSauvegarderConfigurationServeur}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder serveur/i }));

    await waitFor(() => {
      expect(onSauvegarderConfigurationServeur).toHaveBeenCalledTimes(1);
    });

    expect(onSauvegarderConfigurationServeur).toHaveBeenCalledWith({
      configuration_courante: {
        layout_edition: [expect.objectContaining({ id: 1, x: 4, z: 5, width: 3.2, depth: 2.8 })],
        palette_par_type: { salon: "#445566" },
      },
      variantes: [expect.objectContaining({ id: "var-1", nom: "Option IA", source: "ia" })],
      variante_active_id: "var-1",
    });

    expect(screen.getByText(/Configuration 3D sauvegardee sur le serveur/i)).toBeInTheDocument();
  });

  it("enregistre une variante nommee et la pousse au serveur", async () => {
    const onSauvegarderConfigurationServeur = vi.fn().mockResolvedValue(undefined);

    render(
      <Plan3DHabitat
        pieces={piecesBase}
        nomPlan="Plan test"
        planId={1}
        configurationServeur={{ ...configurationServeurBase, variantes: [], variante_active_id: null }}
        onSauvegarderConfigurationServeur={onSauvegarderConfigurationServeur}
      />
    );

    fireEvent.change(screen.getByPlaceholderText(/Ex: Variante rangements/i), {
      target: { value: "Variante bureau" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Enregistrer variante/i }));

    await waitFor(() => {
      expect(onSauvegarderConfigurationServeur).toHaveBeenCalledTimes(1);
    });

    const payload = onSauvegarderConfigurationServeur.mock.calls[0][0];
    expect(payload.variantes).toHaveLength(1);
    expect(payload.variantes[0]).toMatchObject({ nom: "Variante bureau", source: "manuel" });
    expect(payload.variante_active_id).toBe(payload.variantes[0].id);
    expect(screen.getByText(/Configuration 3D sauvegardee sur le serveur/i)).toBeInTheDocument();
    expect(screen.getByRole("option", { name: /Variante bureau · manuel/i })).toBeInTheDocument();
  });
});
