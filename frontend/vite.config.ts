/// <reference types="vitest" />

import react from "@vitejs/plugin-react"
import process from "node:process"
import { defineConfig } from "vite"

const outDir =
  process.env.BUILD_OUTPUT_DIR || "../backend/provider_directory/static/"

export default defineConfig(({ mode }) => {
  return {
    plugins: [react()],
    base: mode === "development" ? "" : "/static/",
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
    // https://vitest.dev/guide/
    test: {
      environment: "jsdom",
      globals: true,
      setupFiles: "./tests/setup.ts",
      coverage: {
        provider: "v8",
        reporter: ["text", "cobertura"],
      },
    },
  }
})
