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

  return (
    <>
      <section className="ds-l-container">
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
      </section>
      <main className={contentClass}>
        <FeatureFlag inverse name="ORGANIZATION_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            This content is not currently available.
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="ORGANIZATION_LOOKUP_DETAILS">
          <p className="ds-u-margin-top--7 ds-u-margin-bottom--2">
            Details go here.
          </p>
        </FeatureFlag>

        <div className="ds-u-margin-top--7"></div>
      </main>
    </>
  )
}
