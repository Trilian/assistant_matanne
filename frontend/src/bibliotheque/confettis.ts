// Confettis leger sans dependance externe.

interface OptionsConfettis {
  particules?: number;
}

const COULEURS = ["#22c55e", "#3b82f6", "#f97316", "#eab308", "#ef4444", "#a855f7"];

export function lancerConfettis(options?: OptionsConfettis): void {
  if (typeof window === "undefined" || typeof document === "undefined") return;

  const total = Math.max(8, Math.min(60, options?.particules ?? 24));
  const zone = document.createElement("div");
  zone.style.position = "fixed";
  zone.style.inset = "0";
  zone.style.pointerEvents = "none";
  zone.style.zIndex = "100";
  document.body.appendChild(zone);

  for (let i = 0; i < total; i += 1) {
    const morceau = document.createElement("span");
    const taille = 5 + Math.random() * 7;
    const departX = window.innerWidth * (0.15 + Math.random() * 0.7);
    const finX = departX + (Math.random() - 0.5) * 180;
    const departY = window.innerHeight * 0.28;
    const finY = window.innerHeight + 24;

    morceau.style.position = "absolute";
    morceau.style.left = `${departX}px`;
    morceau.style.top = `${departY}px`;
    morceau.style.width = `${taille}px`;
    morceau.style.height = `${taille}px`;
    morceau.style.background = COULEURS[i % COULEURS.length];
    morceau.style.borderRadius = "2px";
    morceau.style.opacity = "0.95";
    morceau.style.transform = `rotate(${Math.random() * 180}deg)`;

    zone.appendChild(morceau);

    morceau.animate(
      [
        { transform: `translate(0px, 0px) rotate(0deg)`, opacity: 1 },
        {
          transform: `translate(${finX - departX}px, ${finY - departY}px) rotate(${540 + Math.random() * 420}deg)`,
          opacity: 0,
        },
      ],
      {
        duration: 700 + Math.random() * 500,
        easing: "cubic-bezier(0.12, 0.75, 0.25, 1)",
        fill: "forwards",
      }
    );
  }

  window.setTimeout(() => {
    zone.remove();
  }, 1400);
}
