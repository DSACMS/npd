import { Button } from "@cmsgov/design-system"
import classNames from "classnames"
import { TitlePanel } from "../../components/TitlePanel"
import layout from "../Layout.module.css"
import { useTranslation } from "react-i18next"

export const Search = () => {
  const { t } = useTranslation()
  const contentClass = classNames(layout.content, "ds-l-container")

  return (
    <>
      <TitlePanel
        title={t("search.title")}
        className={layout.compactLeader}
      >
        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-margin-bottom--4">
            <p>
            {t("search.subtitle")}
            </p>
          </div>
        </div>
      </TitlePanel>

      <main className={contentClass}>
        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-display--flex ds-u-justify-content--center ds-u-margin-bottom--6">
            <Button variation="solid" size="big" href="/practitioners/search" className="ds-u-margin-right--2">
            {t("search.practitioner")}
            </Button>
            <Button variation="solid" size="big" href="/organizations/search">
            {t("search.organization")}
            </Button>
          </div>
        </div>
      </main>
    </>
  )
}
