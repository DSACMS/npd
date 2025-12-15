import { Pagination } from "@cmsgov/design-system"
import classNames from "classnames"
import { useTranslation } from "react-i18next"
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
  const params = usePaginationParams()
  const { data, isLoading, isSuccess } = useOrganizationsAPI(params)
  const pagination = usePagination(params, data)

  const contentClass = classNames(layout.content, "ds-l-container")

  return (
    <>
      <TitlePanel title={t("organizations.listing.title")} />

      {isLoading && <LoadingIndicator />}

      {isSuccess && data && (
        <main className={contentClass}>
          <div className="ds-l-row">
            <div className="ds-l-col--12 ds-u-margin-bottom--2">
              {data && <PaginationCaption pagination={pagination} />}
              <Pagination
                currentPage={pagination.page}
                onPageChange={() => {}}
                renderHref={(pageNumber) =>
                  apiUrl(`/organizations?page=${pageNumber}`)
                }
                totalPages={pagination.totalPages}
              />
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
              <Pagination
                currentPage={pagination.page}
                onPageChange={() => {}}
                renderHref={(pageNumber) =>
                  apiUrl(`/organizations?page=${pageNumber}`)
                }
                totalPages={pagination.totalPages}
              />
            </div>
          </div>
        </main>
      )}
    </>
  )
}
