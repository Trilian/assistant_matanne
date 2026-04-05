"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { MouseEvent, ReactNode } from "react";

type DocumentAvecTransition = Document & {
  startViewTransition?: (callback: () => void) => void;
};

export function LienTransition({
  href,
  children,
  className,
}: {
  href: string;
  children: ReactNode;
  className?: string;
}) {
  const router = useRouter();

  const gererClick = (event: MouseEvent<HTMLAnchorElement>) => {
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return;
    }

    const documentAvecTransition = document as DocumentAvecTransition;

    if (typeof documentAvecTransition.startViewTransition !== "function") {
      return;
    }

    event.preventDefault();
    documentAvecTransition.startViewTransition(() => router.push(href));
  };

  return (
    <Link href={href} className={className} onClick={gererClick}>
      {children}
    </Link>
  );
}
