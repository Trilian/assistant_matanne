import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { CarteAnniversaire } from "@/composants/famille/carte-anniversaire";
import { CarteDocumentExpire } from "@/composants/famille/carte-document-expire";
import { CarteSuggestionIA } from "@/composants/famille/carte-suggestion-ia";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

describe("Composants famille", () => {
  it("affiche une carte anniversaire avec le bon countdown", () => {
    render(
      <CarteAnniversaire
        anniversaire={{
          nom_personne: "Jules",
          relation: "fils",
          jours_restants: 1,
          age: 2,
          idees_cadeaux: "Livre",
        } as never}
      />,
    );

    expect(screen.getByText("Jules")).toBeInTheDocument();
    expect(screen.getByText("Demain")).toBeInTheDocument();
    expect(screen.getByText(/Voir idées cadeaux/i)).toBeInTheDocument();
  });

  it("affiche une carte document expirant", () => {
    render(
      <CarteDocumentExpire
        document={{
          titre: "Passeport",
          severite: "warning",
          jours_restants: 5,
        } as never}
      />,
    );

    expect(screen.getByText("Passeport")).toBeInTheDocument();
    expect(screen.getByText("5j restants")).toBeInTheDocument();
  });

  it("affiche une suggestion IA et execute son action", () => {
    const onAction = vi.fn();

    render(
      <CarteSuggestionIA
        titre="Idee weekend"
        description="Sortie au parc"
        source="weekend"
        actionLabel="Planifier"
        onAction={onAction}
      />,
    );

    expect(screen.getByText("Idee weekend")).toBeInTheDocument();
    expect(screen.getByText("Sortie au parc")).toBeInTheDocument();
    expect(screen.getByText("weekend")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Planifier" }));
    expect(onAction).toHaveBeenCalledTimes(1);
  });
});
