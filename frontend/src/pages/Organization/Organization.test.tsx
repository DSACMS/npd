import { screen, within } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router"
import { beforeEach, describe, expect, it } from "vitest"
import { DEFAULT_ORGANIZATION } from "../../../tests/fixtures"
import {
  mockGlobalFetch,
  settingsResponseWithFeature,
  type MockResponse,
} from "../../../tests/mockGlobalFetch"
import { render } from "../../../tests/render"
import { Organization } from "./Organization"

const orgApiResponse: MockResponse = [
  "^/fhir/Organization/.*",
  DEFAULT_ORGANIZATION,
]

const RoutedOrganization = ({ path }: { path: string }) => {
  return (
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route
          path="/organizations/:organizationId"
          element={<Organization />}
        />
      </Routes>
    </MemoryRouter>
  )
}

describe("Organization", () => {
  describe("without ORGANIZATION_LOOKUP_DETAILS feature flag", () => {
    beforeEach(() => {
      mockGlobalFetch([
        settingsResponseWithFeature({ ORGANIZATION_LOOKUP_DETAILS: false }),
        orgApiResponse,
      ])
    })

    it("does not render content when feature flag is unset", async () => {
      render(<RoutedOrganization path="/organizations/12345" />)

      // ensure FeatureFlag components have finished loading
      await screen.findByText("Content not available")

      expect(screen.queryByText("About", { selector: "section h2" })).toBeNull()
    })
  })

  describe("with ORGANIZATION_LOOKUP_DETAILS feature flag", () => {
    beforeEach(() => {
      // update /api/frontend_settings mocked response
      mockGlobalFetch([
        settingsResponseWithFeature({ ORGANIZATION_LOOKUP_DETAILS: true }),
        orgApiResponse,
      ])
    })

    it("shows detailed content", async () => {
      render(<RoutedOrganization path="/organizations/12345" />)

      // ensure FeatureFlag components have finished loading
      await screen.findByText("Are you the practitioner listed?")

      expect(
        screen.queryByText("About", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
        screen.queryByText("Contact Information", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
        screen.queryByText("Identifiers", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
        screen.queryByText("Taxonomy", { selector: "section h2" }),
      ).toBeInTheDocument()
    })
  })

    it("displays all section headers", async () => {
      render(<RoutedOrganization path="/organizations/12345" />)

      await screen.findByText("Are you the practitioner listed?")

      expect(screen.getByText("About", { selector: "h2" })).toBeInTheDocument()
      expect(
        screen.getByText("Contact Information", { selector: "h2" }),
      ).toBeInTheDocument()
      expect(
        screen.getByText("Identifiers", { selector: "h2" }),
      ).toBeInTheDocument()
      expect(screen.getByText("Taxonomy", { selector: "h2" })).toBeInTheDocument()
      expect(screen.getByText("Endpoints", { selector: "h2" })).toBeInTheDocument()
      expect(screen.getByText("Locations", { selector: "h2" })).toBeInTheDocument()
      expect(
        screen.getByText("Practitioners", { selector: "h2" }),
      ).toBeInTheDocument()
    })

    it("displays empty states for sections without data", async () => {
      render(<RoutedOrganization path="/organizations/12345" />)

      await screen.findByText("Are you the practitioner listed?")

      expect(screen.getByText("No taxonomy available")).toBeInTheDocument()
      expect(screen.getByText("No endpoints available")).toBeInTheDocument()
      expect(screen.getByText("No locations available")).toBeInTheDocument()
      expect(screen.getByText("No practitioners available")).toBeInTheDocument()
    })
  })

  describe("identifiers section", () => {
    beforeEach(() => {
      mockGlobalFetch([
        settingsResponseWithFeature({ ORGANIZATION_LOOKUP_DETAILS: true }),
        orgApiResponse,
      ])
    })

    it("displays identifiers table when identifiers exist", async () => {
      render(<RoutedOrganization path="/organizations/12345" />)

      await screen.findByText("Are you the practitioner listed?")

      const table = screen.getByRole("table")
      expect(table).toBeInTheDocument()

      expect(
        within(table).getByText("Type", { selector: "th" }),
      ).toBeInTheDocument()
      expect(
        within(table).getByText("Number", { selector: "th" }),
      ).toBeInTheDocument()
      expect(
        within(table).getByText("Details", { selector: "th" }),
      ).toBeInTheDocument()
    })

    it("displays empty message when no identifiers exist", async () => {
      const orgWithoutIdentifiers = {
        ...DEFAULT_ORGANIZATION,
        identifier: [],
      }

      mockGlobalFetch([
        settingsResponseWithFeature({ ORGANIZATION_LOOKUP_DETAILS: true }),
        ["^/fhir/Organization/.*", orgWithoutIdentifiers],
      ])

      render(<RoutedOrganization path="/organizations/12345" />)

      await screen.findByText("Are you the practitioner listed?")

      expect(screen.getByText("No identifiers available")).toBeInTheDocument()
      expect(screen.queryByRole("table")).not.toBeInTheDocument()
    })
  })
