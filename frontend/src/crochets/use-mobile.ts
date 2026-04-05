import * as React from "react"

const MOBILE_BREAKPOINT = 768

/**
 * Hook de détection du mode mobile via media query (breakpoint 768px).
 * @returns `true` si la largeur de la fenêtre est inférieure à 768px
 */
export function useIsMobile() {
  const [isMobile, setIsMobile] = React.useState<boolean | undefined>(undefined)

  React.useEffect(() => {
    if (typeof window === "undefined") {
      return
    }

    const onChange = () => {
      setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
    }

    onChange()

    if (typeof window.matchMedia !== "function") {
      window.addEventListener("resize", onChange)
      return () => window.removeEventListener("resize", onChange)
    }

    const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`)
    mql.addEventListener("change", onChange)
    return () => mql.removeEventListener("change", onChange)
  }, [])

  return !!isMobile
}
