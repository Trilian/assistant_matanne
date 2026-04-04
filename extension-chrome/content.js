function trouverBoutonAjout() {
  const selecteurs = [
    '[data-testid*="add-to-cart"]',
    'button[aria-label*="Ajouter"]',
    'button[title*="Ajouter"]',
    'button[class*="add"]',
    'button[class*="cart"]'
  ];

  for (const selecteur of selecteurs) {
    const bouton = document.querySelector(selecteur);
    if (bouton instanceof HTMLButtonElement && !bouton.disabled) {
      return bouton;
    }
  }

  const boutons = Array.from(document.querySelectorAll("button"));
  return boutons.find((bouton) => {
    const texte = (bouton.textContent || "").trim().toLowerCase();
    return (
      bouton instanceof HTMLButtonElement &&
      !bouton.disabled &&
      (texte.includes("ajouter au panier") || texte === "ajouter" || texte.includes("panier"))
    );
  }) || null;
}

async function marquerResultat(article, statut) {
  const stockage = await chrome.storage.local.get("driveSyncResults");
  const resultats = stockage.driveSyncResults || {};
  resultats[article.id] = {
    nom: article.nom,
    statut,
    url: window.location.href,
    horodatage: new Date().toISOString(),
  };
  await chrome.storage.local.set({ driveSyncResults: resultats });
}

async function traiterArticleCourant() {
  const stockage = await chrome.storage.local.get("driveSyncQueue");
  const queue = stockage.driveSyncQueue || [];
  const article = queue.find((item) => {
    const url = item.correspondance?.produit_drive_url;
    return typeof url === "string" && window.location.href.startsWith(url);
  });

  if (!article) return;

  await new Promise((resolve) => setTimeout(resolve, 1500));
  const bouton = trouverBoutonAjout();
  if (!bouton) {
    await marquerResultat(article, "bouton_introuvable");
    return;
  }

  bouton.click();
  await marquerResultat(article, "ajout_tente");
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    traiterArticleCourant().catch(() => undefined);
  });
} else {
  traiterArticleCourant().catch(() => undefined);
}
