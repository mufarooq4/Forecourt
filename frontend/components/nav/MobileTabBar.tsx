"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { isNavActive, NAV_ITEMS } from "./nav-items";

export function MobileTabBar() {
  const pathname = usePathname();

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-30 flex border-t border-line bg-canopy md:hidden"
      style={{ height: "var(--tab-bar-height)" }}
      aria-label="Main"
    >
      {NAV_ITEMS.map((item) => {
        const active = isNavActive(pathname, item);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={[
              "flex flex-1 flex-col items-center justify-center gap-0.5 px-1 text-[11px]",
              active ? "font-semibold text-ink" : "text-ink-muted",
            ].join(" ")}
          >
            <Icon className="h-4 w-4" aria-hidden="true" strokeWidth={2} />
            <span className="leading-tight">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
