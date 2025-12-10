import {
  organizationMailingAddressSelector,
  organizationNpiSelector,
  useOrganizationsAPI,
} from "../../state/requests/organizations"

import classNames from "classnames"
import { useTranslation } from "react-i18next"
import type { FHIRCollection, FHIROrganization } from "../../@types/fhir"
import { LoadingIndicator } from "../../components/LoadingIndicator"

import { Link } from "react-router"
import layout from "../Layout.module.css"
import search from "../Search.module.css"

const ListedOrganization = ({ data }: { data: FHIROrganization }) => {
  const { t } = useTranslation()

  return (
    <div className="ds-u-border-top--1 ds-u-padding-y--2">
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

const PaginationCaption = ({
  searchParams,
  response,
}: {
  searchParams: URLSearchParams
  response: FHIRCollection<FHIROrganization>
}) => {
  const searchPage = searchParams.get("page")
  let page = 1
  if (searchPage !== null && !isNaN(parseInt(searchPage))) {
    page = parseInt(searchPage)
  }

  return (
    <span>
      Showing {page} - {page + (response.results.total - 1)} of {response.count}
    </span>
  )
}

export const OrganizationList = () => {
  const { t } = useTranslation()
  const { data, isLoading } = useOrganizationsAPI()

  if (isLoading) {
    return <LoadingIndicator />
  }

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
      <main className={contentClass}>
        {data && (
          <PaginationCaption
            searchParams={new URLSearchParams("page=1&page_size=25")}
            response={data}
          />
        )}

        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-margin-bottom--2">
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
        </div>
      </main>
    </>
  )
}
