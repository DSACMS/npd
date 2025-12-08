import { Alert } from "@cmsgov/design-system"
import classNames from "classnames"
import { useParams } from "react-router"
import { FeatureFlag } from "../../components/FeatureFlag"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import { organizationNpiSelector } from "../../state/requests/organizations"
import {
  practitionerAddressOneline,
  practitionerNameSelector,
  usePractitionerAPI,
} from "../../state/requests/practitioners"
import { useTranslation } from "react-i18next"
import { InfoItem } from "../../components/InfoItem"
import layout from "../Layout.module.css"

export const Practitioner = () => {
  const { t } = useTranslation()
  const { practitionerId } = useParams()
  const { data, error, isLoading } = usePractitionerAPI(practitionerId)

  if (isLoading) {
    return <LoadingIndicator />
  }

  if (typeof data === "undefined" || error) {
    return <p>API Error: {JSON.stringify(error)}</p>
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
                <h1 role="heading" aria-level={1} className={layout.title}>
                  {practitionerNameSelector(data)}
                </h1>
                <span
                  data-testid="practitioner-npi"
                  className={layout.subtitle}
                >
                  NPI: {organizationNpiSelector(data)}
                </span>
                {data.address && (
                  <span
                    data-testid="practitioner-npi"
                    className={layout.subtitle}
                  >
                    {practitionerAddressOneline(data)}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>
      <main className={contentClass}>
        <FeatureFlag inverse name="PRACTITIONER_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            This content is not currently available.
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="PRACTITIONER_LOOKUP_DETAILS">
          <Alert heading={t("practitioners.update.title")}>
          {t("practitioners.update.subtitle")}{' '}
          <a href="#">{t("practitioners.update.link")}</a>
          </Alert>

          <section className={layout.section}>
            <h2>{t("organizations.about")}</h2>
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label="Name(s)" value={null} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label="Gender" value={null} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label="Deceased" value={null} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label="Active status" value={null} />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>Contact information</h2>
            <p>[contact information]</p>
          </section>

          <section className={layout.section}>
            <h2>Identifiers</h2>
            <p>[identifier information]</p>
          </section>

          <section className={layout.section}>
            <h2>Taxonomy</h2>
            <p>[taxonomy information]</p>
          </section>

          <section className={layout.section}>
            <h2>Organization(s)</h2>
            <p>[endpoint information]</p>
          </section>
        </FeatureFlag>

        <div className="ds-u-margin-top--7"></div>
      </main>
    </>
  )
}
