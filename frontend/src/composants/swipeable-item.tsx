// ═══════════════════════════════════════════════════════════
// SwipeableItem — Composant swipeable pour les listes mobile
// ═══════════════════════════════════════════════════════════
// Swipe gauche → action destructive (rouge)
// Swipe droite → action principale (vert/bleu)

"use client";

import { useRef, useState, type ReactNode, type CSSProperties } from "react";
import { Trash2, Check } from "lucide-react";

interface SwipeableItemProps {
  /** Contenu principal de l'élément */
  children: ReactNode;
  /** Callback swipe gauche (ex: supprimer) */
  onSwipeLeft?: () => void;
  /** Callback swipe droite (ex: cocher/compléter) */
  onSwipeRight?: () => void;
  /** Label du bouton gauche (défaut: "Supprimer") */
  labelGauche?: string;
  /** Icône du bouton gauche */
  iconeGauche?: ReactNode;
  /** Label du bouton droit (défaut: "Fait") */
  labelDroit?: string;
  /** Icône du bouton droit */
  iconeDroit?: ReactNode;
  /** Désactiver le swipe gauche */
  desactiverGauche?: boolean;
  /** Désactiver le swipe droit */
  desactiverDroit?: boolean;
  className?: string;
}

const SEUIL_PIXELS = 72; // pixels pour déclencher l'action
const SEUIL_RATIO = 0.35; // ratio largeur écran

export function SwipeableItem({
  children,
  onSwipeLeft,
  onSwipeRight,
  labelGauche = "Supprimer",
  iconeGauche = <Trash2 className="h-5 w-5" />,
  labelDroit = "Fait",
  iconeDroit = <Check className="h-5 w-5" />,
  desactiverGauche = false,
  desactiverDroit = false,
  className = "",
}: SwipeableItemProps) {
  const touchStartX = useRef<number | null>(null);
  const touchStartY = useRef<number | null>(null);
  const [translateX, setTranslateX] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [actionDeclenche, setActionDeclenche] = useState<"left" | "right" | null>(null);

  function onTouchStart(e: React.TouchEvent) {
    touchStartX.current = e.touches[0].clientX;
    touchStartY.current = e.touches[0].clientY;
    setIsAnimating(false);
  }

  function onTouchMove(e: React.TouchEvent) {
    if (touchStartX.current === null || touchStartY.current === null) return;

    const dx = e.touches[0].clientX - touchStartX.current;
    const dy = e.touches[0].clientY - touchStartY.current;

    // Ignorer les gestes principalement verticaux
    if (Math.abs(dy) > Math.abs(dx) * 1.5) return;

    // Limiter selon les actions disponibles
    if (dx > 0 && desactiverDroit) return;
    if (dx < 0 && desactiverGauche) return;

    const maxDeplacement = window.innerWidth * SEUIL_RATIO;
    const deplacement = Math.max(-maxDeplacement, Math.min(maxDeplacement, dx));
    setTranslateX(deplacement);
  }

  function onTouchEnd() {
    if (touchStartX.current === null) return;

    const seuil = Math.min(SEUIL_PIXELS, window.innerWidth * SEUIL_RATIO);
    setIsAnimating(true);

    if (translateX < -seuil && onSwipeLeft && !desactiverGauche) {
      // Swipe gauche confirmé
      setTranslateX(-window.innerWidth);
      setActionDeclenche("left");
      setTimeout(() => {
        setTranslateX(0);
        setIsAnimating(false);
        setActionDeclenche(null);
        onSwipeLeft();
      }, 300);
    } else if (translateX > seuil && onSwipeRight && !desactiverDroit) {
      // Swipe droit confirmé
      setActionDeclenche("right");
      setTranslateX(window.innerWidth);
      setTimeout(() => {
        setTranslateX(0);
        setIsAnimating(false);
        setActionDeclenche(null);
        onSwipeRight();
      }, 300);
    } else {
      // Retour position initiale
      setTranslateX(0);
      setTimeout(() => setIsAnimating(false), 250);
    }

    touchStartX.current = null;
    touchStartY.current = null;
  }

  const itemStyle: CSSProperties = {
    transform: `translateX(${translateX}px)`,
    transition: isAnimating ? "transform 0.25s ease-out" : "none",
    touchAction: "pan-y",
  };

  // Opacité des révélateurs proportionnelle au déplacement
  const ratioGauche = Math.min(1, Math.abs(translateX) / SEUIL_PIXELS);
  const ratioActivation = translateX < -SEUIL_PIXELS / 2 ? 1 : ratioGauche;
  const ratioDroit = Math.min(1, translateX / SEUIL_PIXELS);
  const ratioActivationDroit = translateX > SEUIL_PIXELS / 2 ? 1 : ratioDroit;

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {/* Fond gauche (destructif) */}
      {!desactiverGauche && onSwipeLeft && (
        <div
          className="absolute inset-y-0 right-0 flex items-center justify-end bg-destructive px-5 text-destructive-foreground"
          style={{ opacity: ratioActivation }}
          aria-hidden="true"
        >
          <span className="flex flex-col items-center gap-1 text-xs font-medium">
            {iconeGauche}
            {labelGauche}
          </span>
        </div>
      )}

      {/* Fond droit (validation) */}
      {!desactiverDroit && onSwipeRight && (
        <div
          className="absolute inset-y-0 left-0 flex items-center justify-start bg-green-500 px-5 text-white"
          style={{ opacity: ratioActivationDroit }}
          aria-hidden="true"
        >
          <span className="flex flex-col items-center gap-1 text-xs font-medium">
            {iconeDroit}
            {labelDroit}
          </span>
        </div>
      )}

      {/* Contenu principal */}
      <div
        style={itemStyle}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
        className={`relative bg-card ${actionDeclenche ? "pointer-events-none" : ""}`}
      >
        {children}
      </div>
    </div>
  );
}
