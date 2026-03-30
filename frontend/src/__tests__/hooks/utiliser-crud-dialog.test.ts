import { describe, expect, it } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";

describe("utiliserDialogCrud", () => {
  it("ouvre en mode création", () => {
    const { result } = renderHook(() => utiliserDialogCrud<{ id: number; nom: string }>());

    act(() => {
      result.current.ouvrirCreation();
    });

    expect(result.current.dialogOuvert).toBe(true);
    expect(result.current.estEnEdition).toBe(false);
    expect(result.current.mode).toBe("creation");
  });

  it("ouvre en mode édition", () => {
    const { result } = renderHook(() => utiliserDialogCrud<{ id: number; nom: string }>());

    act(() => {
      result.current.ouvrirEdition({ id: 1, nom: "Projet" });
    });

    expect(result.current.dialogOuvert).toBe(true);
    expect(result.current.estEnEdition).toBe(true);
    expect(result.current.mode).toBe("edition");
    expect(result.current.enEdition?.nom).toBe("Projet");
  });

  it("ferme et réinitialise l'état", () => {
    const { result } = renderHook(() => utiliserDialogCrud<{ id: number; nom: string }>());

    act(() => {
      result.current.ouvrirEdition({ id: 2, nom: "Tâche" });
      result.current.fermerDialog();
    });

    expect(result.current.dialogOuvert).toBe(false);
    expect(result.current.enEdition).toBeNull();
    expect(result.current.estEnEdition).toBe(false);
  });
});
