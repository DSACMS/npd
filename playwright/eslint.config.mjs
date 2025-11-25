import js from "@eslint/js"
import globals from "globals"
import tseslint from "typescript-eslint"
import eslintConfigPrettier from "eslint-config-prettier/flat"
import { defineConfig } from "eslint/config"

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs,ts,mts,cts}"],
    plugins: { js },
    extends: ["js/recommended", eslintConfigPrettier],
    languageOptions: { globals: globals.browser },
  },
  tseslint.configs.recommended,
])
