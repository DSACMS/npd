import { Spinner } from "@cmsgov/design-system"
import classNames from "classnames"

import layout from "../pages/Layout.module.css"

export const LoadingIndicator = () => {
  const contentClass = classNames(layout.content, "ds-l-container")

  return (
    <main className={contentClass}>
      <div className="ds-l-row">
        <div className="ds-l-col--12">
          <div className={layout.leader}>
            <Spinner size="big" />
          </div>
        </div>
      </div>
    </main>
  )
}
