"use client";

import { type HTMLMotionProps, type Variants, motion, useReducedMotion } from "framer-motion";
import { forwardRef, type ReactNode } from "react";

// ═══════════════════════════════════════════════════════════
// Variantes réutilisables
// ═══════════════════════════════════════════════════════════

export const variantesListeItem: Variants = {
  hidden: { opacity: 0, scale: 0.9, y: 8 },
  visible: { opacity: 1, scale: 1, y: 0 },
  exit: { opacity: 0, scale: 0.85, y: -4, transition: { duration: 0.18 } },
};

export const variantesShake: Variants = {
  idle: { x: 0 },
  shake: {
    x: [0, -6, 6, -4, 4, 0],
    transition: { duration: 0.4, ease: "easeInOut" },
  },
};

export const variantesFadeIn: Variants = {
  hidden: { opacity: 0, y: 6 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.25, ease: "easeOut" } },
};

export const variantesPop: Variants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1, transition: { type: "spring", stiffness: 400, damping: 20 } },
  exit: { opacity: 0, scale: 0.8, transition: { duration: 0.15 } },
};

// ═══════════════════════════════════════════════════════════
// Composant ItemAnime — wrapper pour items de liste animés
// ═══════════════════════════════════════════════════════════

interface ItemAnimeProps extends HTMLMotionProps<"div"> {
  children: ReactNode;
  index?: number;
}

export const ItemAnime = forwardRef<HTMLDivElement, ItemAnimeProps>(
  function ItemAnime({ children, index = 0, ...props }, ref) {
    return (
      <motion.div
        ref={ref}
        variants={variantesListeItem}
        initial="hidden"
        animate="visible"
        exit="exit"
        transition={{
          duration: 0.22,
          delay: Math.min(index * 0.03, 0.15),
          ease: [0.22, 1, 0.36, 1],
        }}
        layout
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

// ═══════════════════════════════════════════════════════════
// Composant PopAnime — animation pop pour apparition/suppression
// ═══════════════════════════════════════════════════════════

interface PopAnimeProps extends HTMLMotionProps<"div"> {
  children: ReactNode;
}

export const PopAnime = forwardRef<HTMLDivElement, PopAnimeProps>(
  function PopAnime({ children, ...props }, ref) {
    return (
      <motion.div
        ref={ref}
        variants={variantesPop}
        initial="hidden"
        animate="visible"
        exit="exit"
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

interface SectionRevealProps extends HTMLMotionProps<"section"> {
  children: ReactNode;
  delay?: number;
  staggerChildren?: number;
}

export function SectionReveal({
  children,
  delay = 0,
  staggerChildren = 0.04,
  ...props
}: SectionRevealProps) {
  const reduireAnimations = useReducedMotion();

  const variantesSection: Variants = {
    hidden: {
      opacity: 0,
      y: reduireAnimations ? 0 : 10,
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: reduireAnimations ? 0 : 0.24,
        delay: reduireAnimations ? 0 : delay,
        staggerChildren: reduireAnimations ? 0 : staggerChildren,
        ease: [0.22, 1, 0.36, 1],
      },
    },
  };

  return (
    <motion.section initial="hidden" animate="visible" variants={variantesSection} {...props}>
      {children}
    </motion.section>
  );
}
