import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { GrilleDashboardDnd, WidgetSortable } from "./grille-dashboard-dnd";

vi.mock("@dnd-kit/core", () => ({
  DndContext: ({ children, onDragEnd }: { children: React.ReactNode; onDragEnd?: (event: unknown) => void }) => (
    <div>
      <button
        type="button"
        onClick={() => onDragEnd?.({ active: { id: "b" }, over: { id: "a" } })}
      >
        Simuler drag reorder
      </button>
      <button
        type="button"
        onClick={() => onDragEnd?.({ active: { id: "a" }, over: { id: "a" } })}
      >
        Simuler drag noop
      </button>
      {children}
    </div>
  ),
  closestCenter: vi.fn(),
  KeyboardSensor: vi.fn(),
  PointerSensor: vi.fn(),
  useSensor: vi.fn(() => ({})),
  useSensors: vi.fn(() => []),
}));

vi.mock("@dnd-kit/sortable", () => ({
  SortableContext: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  sortableKeyboardCoordinates: vi.fn(),
  useSortable: vi.fn(() => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    isDragging: false,
  })),
  verticalListSortingStrategy: {},
  arrayMove: (items: string[], oldIndex: number, newIndex: number) => {
    const clone = [...items];
    const [moved] = clone.splice(oldIndex, 1);
    clone.splice(newIndex, 0, moved);
    return clone;
  },
}));

describe("GrilleDashboardDnd", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("réordonne les widgets et envoie les détails de reorder", async () => {
    const user = userEvent.setup();
    const onOrdreChange = vi.fn();
    const onWidgetReorder = vi.fn();

    render(
      <GrilleDashboardDnd
        ordre={["a", "b", "c"]}
        onOrdreChange={onOrdreChange}
        onWidgetReorder={onWidgetReorder}
      >
        <WidgetSortable id="a"><div>A</div></WidgetSortable>
        <WidgetSortable id="b"><div>B</div></WidgetSortable>
        <WidgetSortable id="c"><div>C</div></WidgetSortable>
      </GrilleDashboardDnd>
    );

    await user.click(screen.getByRole("button", { name: /Simuler drag reorder/i }));

    expect(onOrdreChange).toHaveBeenCalledWith(["b", "a", "c"]);
    expect(onWidgetReorder).toHaveBeenCalledWith({
      widgetId: "b",
      fromIndex: 1,
      toIndex: 0,
      ordre: ["b", "a", "c"],
    });
  });

  it("n'émet pas de changement quand active et over sont identiques", async () => {
    const user = userEvent.setup();
    const onOrdreChange = vi.fn();
    const onWidgetReorder = vi.fn();

    render(
      <GrilleDashboardDnd ordre={["a", "b", "c"]} onOrdreChange={onOrdreChange} onWidgetReorder={onWidgetReorder}>
        <WidgetSortable id="a"><div>A</div></WidgetSortable>
      </GrilleDashboardDnd>
    );

    await user.click(screen.getByRole("button", { name: /Simuler drag noop/i }));

    expect(onOrdreChange).not.toHaveBeenCalled();
    expect(onWidgetReorder).not.toHaveBeenCalled();
  });

  it("affiche une poignée de réorganisation sur chaque widget", () => {
    render(
      <GrilleDashboardDnd ordre={["a"]} onOrdreChange={vi.fn()}>
        <WidgetSortable id="a"><div>A</div></WidgetSortable>
      </GrilleDashboardDnd>
    );

    expect(screen.getByRole("button", { name: /Réorganiser le widget/i })).toBeInTheDocument();
  });
});
