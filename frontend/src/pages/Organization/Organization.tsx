import { Alert } from "@cmsgov/design-system"
import classNames from "classnames"
import { useParams } from "react-router"
import { FeatureFlag } from "../../components/FeatureFlag"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import {
  organizationNpiSelector,
  useOrganizationAPI,
} from "../../state/requests/organizations"
import layout from "../Layout.module.css"
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
                  NPI: {organizationNpiSelector(data)}
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
          {t("organizations.update.subtitle")}<a href="#">{t("organizations.update.link")}</a>
          </Alert>

          <section className={layout.section}>
            <h2>{t("organizations.about.text")}</h2>
            <p>{t("organizations.about.placeholder")}</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.contact.text")}</h2>
            <p>{t("organizations.contact.placeholder")}</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.identifiers.text")}</h2>
            <p>{t("organizations.identifiers.placeholder")}</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.taxonomy.text")}</h2>
            <p>{t("organizations.taxonomy.placeholder")}</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.endpoints.text")}</h2>
            <p>{t("organizations.endpoints.placeholder")}</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.locations.text")}</h2>
            <p>{t("organizations.locations.placeholder")}</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.practitioners.text")}</h2>
            <p>{t("organizations.practitioners.placeholder")}</p>
          </section>
        </FeatureFlag>

        <div className="ds-u-margin-top--7"></div>
      </main>
    </>
  )
}
