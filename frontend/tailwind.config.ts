import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Brand palette
        brand: {
          indigo: "#6366f1",
          emerald: "#10b981",
          rose: "#f43f5e",
          amber: "#f59e0b",
        },
        // Neutral surface scale (dark-first)
        surface: {
          900: "#0f172a",
          800: "#1e293b",
          700: "#334155",
          600: "#475569",
          400: "#94a3b8",
          200: "#e2e8f0",
          100: "#f1f5f9",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        shimmer: "shimmer 1.5s infinite linear",
      },
    },
  },
  plugins: [],
} satisfies Config;
