import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        canopy: "var(--canopy)",
        slab: "var(--slab)",
        line: "var(--line)",
        ink: {
          DEFAULT: "var(--ink)",
          muted: "var(--ink-muted)",
        },
        super: {
          DEFAULT: "var(--super)",
          text: "var(--super-text)",
        },
        "hi-octane": {
          DEFAULT: "var(--hi-octane)",
          text: "var(--hi-octane-text)",
        },
        diesel: {
          DEFAULT: "var(--diesel)",
          text: "var(--diesel-text)",
        },
      },
      fontFamily: {
        sans: ["var(--font-overpass)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      fontWeight: {
        normal: "400",
        semibold: "600",
        extrabold: "800",
      },
      maxWidth: {
        content: "1200px",
      },
      width: {
        rail: "200px",
        "rail-collapsed": "56px",
      },
      borderRadius: {
        control: "2px",
        none: "0",
      },
      spacing: {
        rail: "200px",
        "rail-collapsed": "56px",
        "tab-bar": "64px",
        "mobile-top": "52px",
      },
      boxShadow: {
        none: "none",
      },
    },
  },
  plugins: [],
};

export default config;
