import { Pagination } from "@cmsgov/design-system"
import classNames from "classnames"
import { useTranslation } from "react-i18next"
import { Link } from "react-router"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import { PaginationCaption } from "../../components/PaginationCaption"
import { TitlePanel } from "../../components/TitlePanel"
import { usePagination, usePaginationParams } from "../../hooks/usePagination"
import { apiUrl } from "../../state/api"
import { useOrganizationsAPI } from "../../state/requests/organizations"
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
    setParams({ page: page.toString() }, { preventScrollReset: true })
  }

  const paginationComponent = (
    <Pagination
      currentPage={pagination.page}
      onPageChange={onPageChange}
      renderHref={(pageNumber) => apiUrl(`/organizations?page=${pageNumber}`)}
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
              {data && <PaginationCaption pagination={pagination} />}
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
