import type { Metadata } from "next";
import { Overpass } from "next/font/google";
import { AppShell } from "@/components/layout/AppShell";
import { ThemeProvider } from "@/components/theme/ThemeProvider";
import "@/styles/globals.css";

const overpass = Overpass({
  subsets: ["latin"],
  weight: ["400", "600", "800"],
  variable: "--font-overpass",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Forecourt",
  description: "Regional petrol station operations for Pakistan",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('forecourt-theme');var d=window.matchMedia('(prefers-color-scheme: dark)').matches;if(t==='dark'||(t!=='light'&&d))document.documentElement.classList.add('dark');}catch(e){}})();`,
          }}
        />
      </head>
      <body className={`${overpass.variable} font-sans`}>
        <ThemeProvider>
          <AppShell>{children}</AppShell>
        </ThemeProvider>
      </body>
    </html>
  );
}
