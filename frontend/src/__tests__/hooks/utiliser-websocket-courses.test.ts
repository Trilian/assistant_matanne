import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useWebSocketCourses } from "@/crochets/utiliser-websocket-courses";

class MockWebSocket {
  static OPEN = 1;
  static CLOSED = 3;
  static instances: MockWebSocket[] = [];

  readyState = MockWebSocket.OPEN;
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  send = vi.fn();
  close = vi.fn(() => {
    this.readyState = MockWebSocket.CLOSED;
  });

  constructor(public url: string) {
    MockWebSocket.instances.push(this);
  }

  open() {
    this.onopen?.();
  }

  closeWithEvent() {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.();
  }

  message(data: unknown) {
    this.onmessage?.({ data: JSON.stringify(data) });
  }

  invalidMessage() {
    this.onmessage?.({ data: "{" });
  }
}

describe("useWebSocketCourses", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    MockWebSocket.instances = [];
    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("ouvre la connexion avec l'URL attendue", () => {
    const { result } = renderHook(() =>
      useWebSocketCourses({
        listeId: 42,
        userId: "anne-id",
        username: "Anne Martin",
      })
    );
    const ws = MockWebSocket.instances[0];

    expect(ws.url).toBe(
      "ws://localhost:8000/api/v1/ws/courses/42?user_id=anne-id&username=Anne%20Martin"
    );

    act(() => {
      ws.open();
    });

    expect(result.current.connected).toBe(true);
  });

  it("met à jour les utilisateurs connectés et notifie onUsersChange", () => {
    const onUsersChange = vi.fn();
    const { result } = renderHook(() =>
      useWebSocketCourses({
        listeId: 7,
        onUsersChange,
      })
    );
    const ws = MockWebSocket.instances[0];

    act(() => {
      ws.message({
        type: "users_list",
        users: [{ user_id: "u1", username: "Anne" }],
      });
      ws.message({ type: "user_joined", user_id: "u2", username: "Marc" });
      ws.message({ type: "user_joined", user_id: "u2", username: "Marc" });
      ws.message({ type: "user_left", user_id: "u1" });
    });

    expect(result.current.users).toEqual([{ user_id: "u2", username: "Marc" }]);
    expect(onUsersChange).toHaveBeenLastCalledWith([{ user_id: "u2", username: "Marc" }]);
  });

  it("ignore pong et délègue les autres messages applicatifs", () => {
    const onMessage = vi.fn();
    renderHook(() =>
      useWebSocketCourses({
        listeId: 8,
        onMessage,
      })
    );
    const ws = MockWebSocket.instances[0];

    act(() => {
      ws.message({ type: "pong" });
      ws.message({ type: "sync", action: "item_added", item: { nom: "Tomates" } });
      ws.invalidMessage();
    });

    expect(onMessage).toHaveBeenCalledTimes(1);
    expect(onMessage).toHaveBeenCalledWith({
      type: "sync",
      action: "item_added",
      item: { nom: "Tomates" },
    });
  });

  it("expose des helpers d'envoi cohérents", () => {
    const { result } = renderHook(() => useWebSocketCourses({ listeId: 9 }));
    const ws = MockWebSocket.instances[0];

    act(() => {
      ws.open();
      result.current.send("item_updated", { item_id: 3, updates: { quantite: 4 } });
      result.current.cocherArticle(3, true);
      result.current.ajouterArticle("Lait", 2);
      result.current.supprimerArticle(5);
    });

    expect(ws.send).toHaveBeenNthCalledWith(
      1,
      JSON.stringify({ action: "item_updated", item_id: 3, updates: { quantite: 4 } })
    );
    expect(ws.send).toHaveBeenNthCalledWith(
      2,
      JSON.stringify({ action: "item_checked", item_id: 3, checked: true })
    );
    expect(ws.send).toHaveBeenNthCalledWith(
      3,
      JSON.stringify({ action: "item_added", nom: "Lait", quantite: 2 })
    );
    expect(ws.send).toHaveBeenNthCalledWith(
      4,
      JSON.stringify({ action: "item_removed", item_id: 5 })
    );
  });

  it("reconnecte automatiquement après fermeture", () => {
    const { result } = renderHook(() => useWebSocketCourses({ listeId: 10 }));
    const ws = MockWebSocket.instances[0];

    act(() => {
      ws.open();
    });
    expect(result.current.connected).toBe(true);

    act(() => {
      ws.closeWithEvent();
    });
    expect(result.current.connected).toBe(false);

    act(() => {
      vi.advanceTimersByTime(3000);
    });

    expect(MockWebSocket.instances).toHaveLength(2);
  });
});