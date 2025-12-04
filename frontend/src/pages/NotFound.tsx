import classNames from "classnames"

import { Link } from "react-router"
import layout from "./Layout.module.css"

export const NotFound = () => {
  // const { t } = useTranslation()

  const mainClasses = classNames(layout.main)

  return (
    <main className={mainClasses}>
      <div className="ds-base ds-l-container">
        <div className="ds-l-row">
          <div className="ds-l-lg-col--6 ds-l-md-col--8">
            <div className={layout.spacer}></div>
            <section className={layout.section}>
              <h2>Page not found</h2>

              <p>The page you are looking for isn't in our records.</p>

              <p>
                You can <Link to="/">return home</Link> or{" "}
                <a href="/fhir/docs/">visit the API documentation</a>.
              </p>
            </section>

            <div className={layout.spacer}></div>
          </div>
        </div>
      </div>
    </main>
  )
}
