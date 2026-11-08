"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NightShiftToggle } from "@/components/theme/NightShiftToggle";
import { isNavActive, NAV_ITEMS } from "./nav-items";

export function SideRail() {
  const pathname = usePathname();

  return (
    <aside
      className="fixed inset-y-0 left-0 z-30 hidden border-r border-line bg-canopy md:flex md:w-rail-collapsed md:flex-col lg:w-rail"
      aria-label="Main"
    >
      <div className="border-b border-line px-3 py-4 lg:px-4">
        <Link
          href="/"
          className="block font-extrabold tracking-tight text-ink"
        >
          <span className="hidden lg:inline text-lg">Forecourt</span>
          <span className="flex justify-center lg:hidden" aria-label="Forecourt">
            <span className="text-sm font-extrabold">F</span>
          </span>
        </Link>
        <p className="mt-0.5 hidden text-xs text-ink-muted lg:block">
          Regional operations
        </p>
      </div>

      <nav className="flex flex-1 flex-col gap-0.5 p-2" aria-label="Pages">
        {NAV_ITEMS.map((item) => {
          const active = isNavActive(pathname, item);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              title={item.label}
              aria-current={active ? "page" : undefined}
              className={[
                "flex items-center gap-3 rounded-control border px-2.5 py-2 text-sm",
                "lg:px-3",
                active
                  ? "border-line bg-slab font-semibold text-ink"
                  : "border-transparent text-ink-muted hover:border-line hover:bg-slab hover:text-ink",
              ].join(" ")}
            >
              <Icon
                className="h-4 w-4 shrink-0"
                aria-hidden="true"
                strokeWidth={2}
              />
              <span className="hidden lg:inline">{item.label}</span>
              <span className="sr-only lg:hidden">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-line p-2">
        <div className="hidden lg:block">
          <NightShiftToggle />
        </div>
        <div className="flex justify-center lg:hidden">
          <NightShiftToggle compact />
        </div>
      </div>
    </aside>
  );
}
