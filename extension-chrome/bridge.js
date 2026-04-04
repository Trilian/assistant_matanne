document.documentElement.dataset.assistantMatanneDriveBridge = "ready";
window.dispatchEvent(new CustomEvent("assistant-matanne-drive-bridge-ready"));

window.addEventListener("message", (event) => {
  if (event.source !== window) {
    return;
  }

  const data = event.data;
  if (!data || data.source !== "assistant-matanne" || data.type !== "SYNC_CARREFOUR_DRIVE") {
    return;
  }

  chrome.runtime.sendMessage(
    {
      type: "SYNC_FROM_APP",
      payload: data.payload || {},
    },
    (response) => {
      const detail = chrome.runtime.lastError
        ? { ok: false, error: chrome.runtime.lastError.message }
        : response || { ok: false, error: "Aucune réponse de l'extension." };

      window.dispatchEvent(
        new CustomEvent("assistant-matanne-drive-sync-result", {
          detail,
        })
      );
    }
  );
});
