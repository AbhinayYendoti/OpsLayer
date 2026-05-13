import type { Config } from "tailwindcss";
import typography from "@tailwindcss/typography";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./hooks/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#111111",
        surface: "#161616",
        "surface-hover": "#1e1e1e",
        border: "#2a2a2a",
        "text-primary": "#e5e5e5",
        "text-secondary": "#888888",
        accent: "#3b82f6",
        "agent-researcher": "#3b82f6",
        "agent-analyst": "#8b5cf6",
        "agent-executor": "#f97316",
        "agent-manager": "#22c55e",
        "agent-safety": "#ef4444",
      },
    },
  },
  plugins: [typography],
};

export default config;
