"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "./ThemeProvider";

export function NightShiftToggle({ compact = false }: { compact?: boolean }) {
  const { nightShift, toggleNightShift } = useTheme();

  return (
    <button
      type="button"
      onClick={toggleNightShift}
      aria-pressed={nightShift}
      title="Night shift"
      className={
        compact
          ? "flex h-10 w-10 items-center justify-center border border-line bg-canopy text-ink hover:bg-slab"
          : "flex w-full items-center gap-3 border border-line bg-canopy px-3 py-2 text-sm text-ink hover:bg-slab"
      }
    >
      {nightShift ? (
        <Moon className="h-4 w-4 shrink-0" aria-hidden="true" strokeWidth={2} />
      ) : (
        <Sun className="h-4 w-4 shrink-0" aria-hidden="true" strokeWidth={2} />
      )}
      {!compact ? <span>Night shift</span> : <span className="sr-only">Night shift</span>}
    </button>
  );
}
