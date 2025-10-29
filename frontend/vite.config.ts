/// <reference types="vitest" />

import react from "@vitejs/plugin-react"
import process from "node:process"
import { defineConfig, type Plugin } from "vite"

const outDir =
  process.env.BUILD_OUTPUT_DIR || "../backend/provider_directory/static/"

// replace Django {{ ... }} template strings with nothing
const stripTemplateStrings = (data: Record<string, string>): Plugin => ({
  name: "strip-template-strings",
  transformIndexHtml: {
    order: "pre",
    handler(html: string) {
      return html.replace(
        /\{\{(.*)\}\}/gi,
        (_match, key: string) => data[key.trim()] || "",
      )
    },
  },
})

export default defineConfig(({ mode, command }) => {
  const plugins: (Plugin | Plugin[])[] = [react()]

  if (command === "serve") {
    plugins.push(stripTemplateStrings({ title: "NPD Dev Service" }))
  }

  return {
    plugins,
    base: mode === "development" ? "" : "/static/",
    build: {
      outDir,
      emptyOutDir: false,
    },
    server: {
      port: 3000,
      host: true,
      proxy: {
        "/frontend_settings": {
          target: process.env.IN_DOCKER
            ? "http://django-web:8000"
            : "http://localhost:8000",
          changeOrigin: true,
        },
        "^/fhir/.*": {
          target: process.env.IN_DOCKER
            ? "http://django-web:8000"
            : "http://localhost:8000",
          changeOrigin: true,
        },
      },
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
