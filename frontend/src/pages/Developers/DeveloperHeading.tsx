import { useTranslation } from "react-i18next"

import layoutstyles from "../Layout.module.css"

export const DeveloperHeading = () => {
  const { t } = useTranslation()

  return (
    <section className="ds-l-container">
      <div className="ds-l-row">
        <div className="ds-l-col--12">
          <div className={layoutstyles.leader}>
            <span className={layoutstyles.subtitle}>
              {t("developers.subtitle")}
            </span>
            <div role="heading" aria-level={1} className={layoutstyles.title}>
              {t("developers.title")}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
