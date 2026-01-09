import { Pagination, Dropdown, type DropdownChangeObject } from "@cmsgov/design-system"
import classNames from "classnames"
import { useTranslation } from "react-i18next"
import { Link } from "react-router"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import { PaginationCaption } from "../../components/PaginationCaption"
import { TitlePanel } from "../../components/TitlePanel"
import { usePagination, usePaginationParams } from "../../hooks/usePagination"
import { apiUrl } from "../../state/api"
import { useOrganizationsAPI, ORGANIZATION_SORT_OPTIONS } from "../../state/requests/organizations"
import layout from "../Layout.module.css"
import { ListedOrganization } from "./ListedOrganization"

export const OrganizationList = () => {
  const { t } = useTranslation()
  const [params, setParams] = usePaginationParams()
  const { data, isLoading, isSuccess } = useOrganizationsAPI(params)
  const pagination = usePagination(params, data)

  const contentClass = classNames(layout.content, "ds-l-container")

  const onPageChange: React.ComponentProps<
    typeof Pagination
  >["onPageChange"] = (evt, page) => {
    evt.preventDefault()
    evt.stopPropagation()
    setParams({ 
      page: page.toString(),
      ...(params.sort && { sort: params.sort })
    }, { preventScrollReset: true })
  }

  const handleSort = (change: DropdownChangeObject): void => {
    const value = change.target.value
    setParams({ 
      page: "1", 
      sort: value 
    }, { preventScrollReset: true })
  }

  const sortOptions = Object.entries(ORGANIZATION_SORT_OPTIONS).map(([value, { label }]) => ({
    label,
    value
  }))

  const defaultSort = sortOptions[0]?.value || ""

  const paginationComponent = (
    <Pagination
      currentPage={pagination.page}
      onPageChange={onPageChange}
      renderHref={(pageNumber) => {
        const hrefParams = new URLSearchParams()
        hrefParams.set("page", pageNumber.toString())
        if (params.sort) hrefParams.set("sort", params.sort)
        return apiUrl(`/organizations?${hrefParams.toString()}`)
      }}
      totalPages={pagination.totalPages}
    />
  )

  return (
    <>
      <TitlePanel
        title={t("organizations.listing.title")}
        className={layout.compactLeader}
      >
        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-margin-bottom--4">
            <Link to="/organizations/search">Search organizations</Link>
          </div>
        </div>
      </TitlePanel>

      {isLoading && <LoadingIndicator />}

      {isSuccess && data && (
        <main className={contentClass}>
          <div className="ds-l-row">
            <div className="ds-l-col--12 ds-u-margin-bottom--2">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  {data && <PaginationCaption pagination={pagination} />}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  Sort by
                  <Dropdown
                    label=""
                    name="sort-dropdown-field"
                    labelClassName="ds-u-display--none"
                    options={sortOptions}
                    value={params.sort || defaultSort}
                    onChange={handleSort}
                  />
                </div>
              </div>
              {paginationComponent}
            </div>
          </div>

          <div className="ds-l-row">
            <div
              data-testid="searchresults"
              role="list"
              className="ds-l-col--12 ds-u-margin-bottom--2"
            >
              {data?.results?.entry?.map((entry, idx) => {
                if (!entry) return null
                return (
                  <ListedOrganization
                    data={entry.resource}
                    key={entry.resource.id || idx}
                  />
                )
              })}
            </div>

            <div className="ds-l-col--12 ds-u-margin-bottom--2">
              {paginationComponent}
            </div>
          </div>
        </main>
      )}
    </>
  )
}
