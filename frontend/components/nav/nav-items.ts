import {
  CircleHelp,
  LayoutGrid,
  Scale,
  Wallet,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Overview", icon: LayoutGrid },
  { href: "/reconciliation", label: "Reconciliation", icon: Scale },
  { href: "/cashflow", label: "Cash flow", icon: Wallet },
  { href: "/ask", label: "Ask", icon: CircleHelp },
];

export function isNavActive(pathname: string, item: NavItem): boolean {
  if (item.href === "/") {
    return pathname === "/" || pathname.startsWith("/stations/");
  }
  return pathname === item.href || pathname.startsWith(`${item.href}/`);
}
