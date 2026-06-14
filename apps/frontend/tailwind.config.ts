import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // Brand palette built around #7f508a (a muted dusty plum).
        // Use `bg-brand` / `text-brand` for the headline shade; lighter and
        // darker steps cover subtle backgrounds, borders, and hover states.
        brand: {
          DEFAULT: "#7f508a",
          50: "#f5edf7",
          100: "#ead9ee",
          200: "#d3b5dc",
          300: "#bb8fc8",
          400: "#a06fae",
          500: "#7f508a", // base
          600: "#6c4275",
          700: "#583460",
          800: "#43274a",
          900: "#2f1b34",
        },
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "monospace",
        ],
      },
    },
  },
  plugins: [],
};

export default config;
