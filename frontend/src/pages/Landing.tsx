import { Badge, Button } from "@cmsgov/design-system"

import { useTranslation } from "react-i18next"
import styles from "./Landing.module.css"

export const Landing = () => {
  const { t } = useTranslation()

  return (
    <>
      <section className={styles.hero}>
        <div className="ds-l-container">
          <div className={styles.heroSpacing}></div>
          <div className={styles.heroBody}>
            <div className="ds-l-row">
              <div className="ds-l-col--12">
                <Badge variation="info" className={styles.heroBadge}>
                  {t("landing.badge")}
                </Badge>

                <h1>{t("landing.title")}</h1>
                <p className={styles.tagline}>{t("landing.tagline")}</p>

                <div className={styles.primaryActions}>
                  <Button variation="solid" href="/developers">
                    {t("landing.links.developers")}
                  </Button>
                </div>
              </div>
            </div>
          </div>
          <div className={styles.heroSpacing}></div>
        </div>
      </section>

      <section className="ds-l-container">
        <div className="ds-l-row">
          <div className="ds-l-col--12">
            <div className={styles.secondary}>
              <h2>{t("landing.about.title")}</h2>

              <p className={styles.secondaryDescription}>
                {t("landing.about.description")}
              </p>

              <Button href="#">{t("landing.links.learn")}</Button>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
