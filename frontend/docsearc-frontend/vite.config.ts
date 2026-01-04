import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  resolve: {
    dedupe: ["react", "react-dom"], // avoids duplicate React in monorepo
  },
  optimizeDeps: {
    include: ["axios"], // <-- forces Vite to pre-bundle axios
  },
  base: "/", // ensures proper path on Vercel
});
