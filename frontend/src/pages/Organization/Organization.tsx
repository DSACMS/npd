import { Alert } from "@cmsgov/design-system"
import classNames from "classnames"
import { useParams } from "react-router"
import { FeatureFlag } from "../../components/FeatureFlag"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import { InfoItem } from "../../components/InfoItem"
import {
  organizationNpiSelector,
  useOrganizationAPI,
  organizationMailingAddressSelector,
  organizationAuthorizedOfficialSelector,
  organizationAuthorizedPhoneSelector,
} from "../../state/requests/organizations"
import layout from "../Layout.module.css"
import styles from "./Organization.module.css"
import { useTranslation } from "react-i18next"

export const Organization = () => {
  const { t } = useTranslation()
  const { organizationId } = useParams()
  const { data, isLoading } = useOrganizationAPI(organizationId)

  if (isLoading) {
    return <LoadingIndicator />
  }

  const contentClass = classNames(layout.content, "ds-l-container")
  const bannerClass = classNames(layout.banner)

  const npi = organizationNpiSelector(data)
  const mailingAddress = organizationMailingAddressSelector(data)
  const authorizedOfficial = organizationAuthorizedOfficialSelector(data)
  const authorizedPhone = organizationAuthorizedPhoneSelector(data)

  return (
    <>
      <section className={bannerClass}>
        <div className="ds-l-container">
          <div className="ds-l-row">
            <div className="ds-l-col--12">
              <div className={layout.leader}>
                <span className={layout.subtitle}>{t("organizations.title")}</span>
                <div role="heading" aria-level={1} className={layout.title}>
                  {data?.name}
                </div>
                <span className={layout.subtitle}>
                  NPI: {npi}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>
      <main className={contentClass}>
        <FeatureFlag inverse name="ORGANIZATION_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            {t("organizations.unavailable")}
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="ORGANIZATION_LOOKUP_DETAILS">
          <Alert heading={t("organizations.update.title")}>
          {t("organizations.update.subtitle")}
          <a href="#">{t("organizations.update.link")}</a>
          </Alert>

          <section className={layout.section}>
            <h2>{t("organizations.about")}</h2>
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem label="Other name(s)" value={data?.name} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem label="Type" value="Provider Group" />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem label="Parent organization" value={null} />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.contact")}</h2>
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem label="Mailing address" value={mailingAddress} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem label="Authorized official" value={authorizedOfficial} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem label="Authorized official phone" value={authorizedPhone} />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.identifiers")}</h2>
            <p className={styles.emptyState}>No identifiers available</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.taxonomy")}</h2>
            <p className={styles.emptyState}>No taxonomy available</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.endpoints")}</h2>
            <p className={styles.emptyState}>No endpoints available</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.locations")}</h2>
            <p className={styles.emptyState}>No locations available</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.practitioners")}</h2>
            <p className={styles.emptyState}>No practitioners available</p>
          </section>
        </FeatureFlag>

        <div className="ds-u-margin-top--7"></div>
      </main>
    </>
  )
}
