import {
  organizationMailingAddressSelector,
  organizationNpiSelector,
  useOrganizationsAPI,
} from "../../state/requests/organizations"

import classNames from "classnames"
import { useTranslation } from "react-i18next"
import type { FHIROrganization } from "../../@types/fhir"
import { LoadingIndicator } from "../../components/LoadingIndicator"

import { Pagination } from "@cmsgov/design-system"
import { Link } from "react-router"
import { PaginationCaption } from "../../components/PaginationCaption"
import { usePagination, usePaginationParams } from "../../hooks/usePagination"
import { apiUrl } from "../../state/api"
import layout from "../Layout.module.css"
import search from "../Search.module.css"

const ListedOrganization = ({ data }: { data: FHIROrganization }) => {
  const { t } = useTranslation()

  return (
    <div role="listitem" className="ds-u-border-top--1 ds-u-padding-y--2">
      <div className={search.entry}>
        <div className={search.head}>
          <Link className={search.name} to={`/organizations/${data.id}`}>
            {data.name}
          </Link>
          <span>
            <strong>NPI:</strong> {organizationNpiSelector(data)}
          </span>
        </div>
        <div className="ds-l-row">
          <div className="ds-l-col--4 ds-m-col--6">
            <strong>{t("organizations.listing.taxonomy")}</strong>
            <br />
            TBD
          </div>
          <div className="ds-l-col--4 ds-m-col--6">
            <strong>{t("organizations.listing.location")}</strong>
            <br />
            {organizationMailingAddressSelector(data)}
          </div>
        </div>
      </div>
    </div>
  )
}

export const OrganizationList = () => {
  const { t } = useTranslation()
  const params = usePaginationParams()
  const { data, isLoading, isSuccess } = useOrganizationsAPI(params)
  const pagination = usePagination(params, data)

  const contentClass = classNames(layout.content, "ds-l-container")
  const bannerClass = classNames(layout.banner)

  return (
    <>
      <section className={bannerClass}>
        <div className="ds-l-container">
          <div className="ds-l-row">
            <div className="ds-l-col--12">
              <div className={layout.leader}>
                <div role="heading" aria-level={1} className={layout.title}>
                  {t("organizations.listing.title")}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

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
