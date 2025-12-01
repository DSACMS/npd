import classNames from "classnames"
import layout from "../Layout.module.css"

export const Search = () => {
  const contentClass = classNames(layout.content, "ds-l-container")

  return (
    <main className={contentClass}>
      <div className="ds-l-row">
        <div className="ds-l-col--12">
          <div className={layout.leader}>
            <h1>Search goes here</h1>
          </div>
        </div>
      </div>
    </main>
  )
}
