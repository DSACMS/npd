import { Button } from "@cmsgov/design-system"
import classNames from "classnames"
import { TitlePanel } from "../../components/TitlePanel"
import layout from "../Layout.module.css"

export const Search = () => {
  const contentClass = classNames(layout.content, "ds-l-container")

  return (
    <>
      <TitlePanel
        title="Search the Data"
        className={layout.compactLeader}
      >
        <p>
          Search the National Provider Directory to find practitioners and organizations.
        </p>
      </TitlePanel>

      <main className={contentClass}>
        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-display--flex ds-u-justify-content--center ds-u-margin-top--4">
            <Button
              variation="solid"
              size="big"
              href="/practitioners/search"
              className="ds-u-margin-right--2"
            >
              Practitioner
            </Button>
            <Button variation="solid" size="big" href="/organizations/search">
              Organization
            </Button>
          </div>
        </div>
      </main>
    </>
  )
}