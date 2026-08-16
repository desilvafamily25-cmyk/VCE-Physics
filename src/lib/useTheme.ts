import { useCallback, useEffect, useState } from "react";

export type ThemePreference = "light" | "dark" | "system";

const STORAGE_KEY = "vce-physics.theme";

function applyTheme(pref: ThemePreference) {
  const root = document.documentElement;
  if (pref === "system") {
    root.removeAttribute("data-theme");
  } else {
    root.setAttribute("data-theme", pref);
  }
}

function readStoredTheme(): ThemePreference {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === "light" || stored === "dark" ? stored : "system";
}

/**
 * Tri-state light/dark/system preference, persisted to localStorage and
 * reflected as a data-theme attribute on <html> -- see src/styles.css's
 * :root[data-theme="..."] blocks. Defaults to "system" (prefers-color-scheme),
 * matching the artifact/theme convention of never hardcoding one look.
 */
export function useTheme(): { theme: ThemePreference; toggle: () => void } {
  const [theme, setTheme] = useState<ThemePreference>(() => readStoredTheme());

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  const toggle = useCallback(() => {
    setTheme((current) => {
      // Cycle system -> light -> dark -> system, resolving "system" against
      // the current OS preference so the first tap always visibly flips.
      const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
      let next: ThemePreference;
      if (current === "system") next = prefersDark ? "light" : "dark";
      else if (current === "light") next = "dark";
      else next = "system";
      localStorage.setItem(STORAGE_KEY, next);
      return next;
    });
  }, []);

  return { theme, toggle };
}
