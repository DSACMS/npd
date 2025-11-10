import { Alert } from "@cmsgov/design-system"
import classNames from "classnames"
import { FeatureFlag } from "../../components/FeatureFlag"
import layout from "../Layout.module.css"

export const Organization = () => {
  const contentClass = classNames(layout.content, "ds-l-container")

  return (
    <>
      <section className="ds-l-container">
        <div className="ds-l-row">
          <div className="ds-l-col--12">
            <div className={layout.leader}>
              <span className={layout.subtitle}>Provider group</span>
              <div role="heading" aria-level={1} className={layout.title}>
                Lorem Mental Health Group LLC
              </div>
              <span className={layout.subtitle}>NPI: 1234567891</span>
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
      </main>
    </>
  )
}
