import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  base: "/static/",
  build: {
    manifest: "manifest.json",
    outDir: "./static",
    rollupOptions: {
      input: {
        init: "src/init.ts",
        main: "src/main.tsx",
        uswds: "src/uswds.ts",
      },
    },
  },
  server: {
    port: 3000,
    host: true,
    watch: {
      usePolling: true,
    },
  },
})
