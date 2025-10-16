import react from "@vitejs/plugin-react"
import process from "node:process"
import { defineConfig } from "vite"

const outDir =
  process.env.BUILD_OUTPUT_DIR || "../backend/provider_directory/static/"

export default defineConfig({
  plugins: [react()],
  base: "/static/",
  build: {
    outDir,
    emptyOutDir: false,
  },
  server: {
    port: 3000,
    host: true,
    watch: {
      usePolling: true,
    },
  },
})
