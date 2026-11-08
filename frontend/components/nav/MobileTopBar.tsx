import { NightShiftToggle } from "@/components/theme/NightShiftToggle";

export function MobileTopBar() {
  return (
    <header
      className="sticky top-0 z-20 flex h-mobile-top items-center justify-between border-b border-line bg-canopy px-4 md:hidden"
      style={{ height: "var(--mobile-top-bar)" }}
    >
      <p className="font-extrabold tracking-tight text-ink">Forecourt</p>
      <NightShiftToggle compact />
    </header>
  );
}
