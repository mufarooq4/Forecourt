import { MobileTabBar } from "@/components/nav/MobileTabBar";
import { MobileTopBar } from "@/components/nav/MobileTopBar";
import { SideRail } from "@/components/nav/SideRail";
import type { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-full">
      <SideRail />
      <div className="md:pl-rail-collapsed lg:pl-rail">
        <MobileTopBar />
        <main className="mx-auto w-full max-w-content px-4 pb-[calc(var(--tab-bar-height)+1.5rem)] pt-5 sm:px-6 md:pb-10 md:pt-8 lg:px-8">
          {children}
        </main>
      </div>
      <MobileTabBar />
    </div>
  );
}
