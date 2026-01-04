import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ["axios"], // force Vite to pre-bundle axios
  },
  base: "/",
});
