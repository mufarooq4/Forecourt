"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

type Theme = "light" | "dark";

interface ThemeContextValue {
  theme: Theme;
  nightShift: boolean;
  setNightShift: (on: boolean) => void;
  toggleNightShift: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function getSystemPrefersDark(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  if (theme === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem("forecourt-theme") as Theme | null;
    const initial: Theme =
      stored === "light" || stored === "dark"
        ? stored
        : getSystemPrefersDark()
          ? "dark"
          : "light";
    setTheme(initial);
    applyTheme(initial);
    setReady(true);

    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = (e: MediaQueryListEvent) => {
      const manual = window.localStorage.getItem("forecourt-theme");
      if (manual === "light" || manual === "dark") return;
      const next: Theme = e.matches ? "dark" : "light";
      setTheme(next);
      applyTheme(next);
    };
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  const setNightShift = useCallback((on: boolean) => {
    const next: Theme = on ? "dark" : "light";
    setTheme(next);
    applyTheme(next);
    window.localStorage.setItem("forecourt-theme", next);
  }, []);

  const toggleNightShift = useCallback(() => {
    setNightShift(theme !== "dark");
  }, [setNightShift, theme]);

  const value: ThemeContextValue = {
    theme: ready ? theme : "light",
    nightShift: theme === "dark",
    setNightShift,
    toggleNightShift,
  };

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return ctx;
}
