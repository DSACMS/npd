import { Button } from "@cmsgov/design-system"
import classNames from "classnames"
import React, { type ChangeEvent, type FormEvent, useState } from "react"
import { useTranslation } from "react-i18next"
import { TitlePanel } from "../../components/TitlePanel"
import { SearchProvider } from "../../state/Search/SearchProvider"
import { useSearch } from "../../state/Search/useSearch"
import layout from "../Layout.module.css"
import search from "../Search.module.css"
import { ListedOrganization } from "./ListedOrganization"

const OrganizationSearchForm: React.FC = () => {
  const { t } = useTranslation()
  const [query, setQuery] = useState<string>("")
  const { searchResult, searchByNameOrIdentifier, clearSearch } = useSearch()

  const contentClass = classNames(layout.content, "ds-l-container")
  const inputClass = classNames(search.input)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault()
    await searchByNameOrIdentifier(query)
  }

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const value = e.target.value
    // require some amount of input
    if (/.+/.test(value)) {
      setQuery(value)
    }
  }

  const handleClear = (): void => {
    setQuery("")
    clearSearch()
  }

  return (
    <>
      <TitlePanel
        title={t("organizations.search.title")}
        className={layout.compactLeader}
      >
        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-padding-bottom--4">
            <form onSubmit={handleSubmit}>
              <div className="ds-u-clearfix">
                <label className="ds-c-label" htmlFor="query-input">
                  {t("organizations.search.inputLabel")}
                </label>
                <div className={inputClass}>
                  <input
                    className="ds-c-field"
                    type="text"
                    name="query-input"
                    id="query-input"
                    onChange={handleInputChange}
                  />
                  <Button
                    type="submit"
                    variation="solid"
                    disabled={query.length < 1 || searchResult.loading}
                  >
                    {searchResult.loading ? "Searching..." : "Search"}
                  </Button>
                  <Button onClick={handleClear}>Clear</Button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </TitlePanel>

      <main className={contentClass}>
        <div className="ds-l-row">
          {searchResult.error && (
            <div className="error-message">
              <strong>Error:</strong> {searchResult.error}
            </div>
          )}

          {searchResult.data && searchResult.data.length > 0 && (
            <div
              data-testid="searchresults"
              role="list"
              className="ds-l-col--12 ds-u-margin-bottom--2"
            >
              {searchResult.data.map((org) => (
                <ListedOrganization data={org} key={org.id} />
              ))}
            </div>
          )}

          {searchResult.data && searchResult.data.length === 0 && (
            <div className="ds-l-col--12 ds-u-margin-bottom--2">
              No Organizations found for query: {query}
            </div>
          )}

          {!searchResult.data && (
            <div className="ds-l-col--12 ds-u-margin-bottom--2">
              <p>No results available</p>
            </div>
          )}
        </div>
      </main>
    </>
  )
}

export const OrganizationSearch = () => {
  return (
    <SearchProvider>
      <OrganizationSearchForm />
    </SearchProvider>
  )
}
