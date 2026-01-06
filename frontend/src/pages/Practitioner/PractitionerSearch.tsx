import { Alert, Button, Pagination } from "@cmsgov/design-system"
import classNames from "classnames"
import React, { type ChangeEvent, type FormEvent, useState } from "react"
import { useTranslation } from "react-i18next"
import { NpdMarkdown } from "../../components/markdown/NpdMarkdown"
import { PaginationCaption } from "../../components/PaginationCaption"
import { TitlePanel } from "../../components/TitlePanel"
import { apiUrl } from "../../state/api"
import { PractitionerSearchProvider } from "../../state/Search/PractitionerSearchProvider"
import { useSearchDispatch, usePractitionerSearchState } from "../../state/Search/useSearch"
import layout from "../Layout.module.css"
import search from "../Search.module.css"
import { ListedPractitioner } from "./ListedPractitioner"

const PractitionerSearchForm: React.FC = () => {
  const { t } = useTranslation()
  const { setQuery, navigateToPage, clearSearch } = useSearchDispatch()
  const {
    isLoading,
    isPaging,
    initialQuery,
    query: searchQuery,
    error: searchError,
    data,
    pagination,
  } = usePractitionerSearchState()

  const [query, setQueryValue] = useState<string>(initialQuery || "")

  const contentClass = classNames(layout.content, "ds-l-container")
  const inputClass = classNames(search.input)

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setQuery(query)
  }

  const handleClear = () => {
    setQueryValue("")
    clearSearch()
  }

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const value = e.target.value
    setQueryValue(value)
  }

  return (
    <>
      <TitlePanel
        title={t("practitioners.search.title")}
        className={layout.compactLeader}
      >
        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-padding-bottom--4">
            <form onSubmit={handleSubmit}>
              <input type="hidden" name="page" value={pagination?.page} />
              <div className="ds-u-clearfix">
                <label className="ds-c-label" htmlFor="query">
                  {t("practitioners.search.inputLabel")}
                </label>
                <div className={inputClass}>
                  <input
                    className="ds-c-field"
                    type="text"
                    name="query"
                    id="query"
                    value={query}
                    onChange={handleInputChange}
                  />
                  <Button
                    type="submit"
                    variation="solid"
                    disabled={query.length < 1 || isLoading && !isPaging}
                  >
                    {isLoading && !isPaging ? "Searching..." : "Search"}
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
          {searchError && (
            <div className="error-message">
              <strong>Error:</strong> {searchError}
            </div>
          )}

          <div className="ds-l-col--12 ds-u-margin-bottom--7">
            {data && data.length > 0 && (
              <>
                {pagination && (
                  <>
                    <PaginationCaption pagination={pagination} />
                    <Pagination
                      currentPage={pagination.page}
                      onPageChange={(evt, page) => {
                        evt.preventDefault()
                        evt.stopPropagation()
                        navigateToPage(page)
                      }}
                      renderHref={(pageNumber) => {
                        const nextParams = new URLSearchParams()
                        nextParams.set("page", pageNumber.toString())
                        if (searchQuery) nextParams.set("query", searchQuery)
                        return apiUrl(`/practitioners?${nextParams.toString()}`)
                      }}
                      totalPages={pagination.totalPages}
                    />
                  </>
                )}
                <div data-testid="searchresults" role="list">
                  {data.map((org) => (
                    <ListedPractitioner data={org} key={org.id} />
                  ))}
                </div>
              </>
            )}

            {data && data.length === 0 && (
              <p>No Practitioners found for query: {query}</p>
            )}

            {!data && (
              <Alert heading={t("patients.alert.heading")}>
                <NpdMarkdown content={t("patients.alert.body")} />
              </Alert>
            )}
          </div>
        </div>
      </main>
    </>
  )
}

export const PractitionerSearch = () => {
  return (
    <PractitionerSearchProvider>
      <PractitionerSearchForm />
    </PractitionerSearchProvider>
  )
}
