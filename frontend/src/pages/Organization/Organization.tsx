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

export const Organization = () => {
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
                <span className={layout.subtitle}>Provider group</span>
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
        <Alert heading="Are you the practitioner listed?">
          Learn how to <a href="#">update your information</a>.
        </Alert>

        <FeatureFlag inverse name="ORGANIZATION_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            This content is not currently available.
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="ORGANIZATION_LOOKUP_DETAILS">
          <section className={layout.section}>
            <h2>About</h2>
            <p>[demographic information]</p>
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
            <h2>Endpoints</h2>
            <p>[endpoint information]</p>
          </section>

          <section className={layout.section}>
            <h2>Locations</h2>
            <p>[location information]</p>
          </section>

          <section className={layout.section}>
            <h2>Practitioners</h2>
            <p>[practitioner information]</p>
          </section>
        </FeatureFlag>

        <div className="ds-u-margin-top--7"></div>
      </main>
    </>
  )
}
