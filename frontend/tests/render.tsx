import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import {
  render as originalRender,
  type RenderOptions,
} from "@testing-library/react"
import { FrontendSettingsProvider } from "../src/state/FrontendSettingsProvider"

const testQueryClient = new QueryClient()

export const customRender = (ui: React.ReactNode, options?: RenderOptions) =>
  originalRender(
    <QueryClientProvider client={testQueryClient}>
      <FrontendSettingsProvider>{ui}</FrontendSettingsProvider>
    </QueryClientProvider>,
    options,
  )

// eslint-disable-next-line react-refresh/only-export-components
export * from "@testing-library/react" // Re-export all original exports
export { customRender as render } // Export the custom render as 'render'
