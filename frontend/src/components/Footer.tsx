import classNames from "classnames"
import { useTranslation } from "react-i18next"
import logoImgSrc from "../assets/hss-logo.png"
import styles from "./Footer.module.css"

const FooterLogo = () => {
  const { t } = useTranslation()

  const classes = classNames(
    "ds-u-display--flex",
    "ds-u-flex-direction--row",
    "ds-u-align-items--center",
    styles.logoContainer,
  )
  return (
    <div className={classes}>
      <img src={logoImgSrc} className={styles.logoImg} alt="HHS Logo" />
      <div className={styles.logoText}>
        <p>{t("footer.logo.disclaimer")}</p>
        <p>{t("footer.logo.address")}</p>
      </div>
    </div>
  )
}

export const Footer = () => {
  const { t } = useTranslation()

  const linkHeaderClasses = classNames(
    "usa-footer__primary-link",
    "ds-u-padding-top--0",
    "ds-u-margin-top--0",
  )
  return (
    <footer className={styles.footer}>
      <section className="ds-l-container">
        <div className="ds-l-row">
          <div className="ds-l-col--5">
            <FooterLogo />
          </div>
          <div className="ds-l-col--2">
            <h4 className={linkHeaderClasses}>
              {t("footer.section.support.title")}
            </h4>
            <ul className="usa-list usa-list--unstyled">
              {(t("footer.section.support.links", { returnObjects: true }) as Array<{text: string, url: string}>).map((link, i) => (
                <li key={i}><a href={link.url}>{link.text}</a></li>
              ))}
            </ul>
          </div>
          <div className="ds-l-col--2">
            <h4 className={linkHeaderClasses}>
              {t("footer.section.cms.title")}
            </h4>
            <ul className="usa-list usa-list--unstyled">
              {(t("footer.section.cms.links", { returnObjects: true }) as Array<{text: string, url: string}>).map((link, i) => (
                <li key={i}><a href={link.url}>{link.text}</a></li>
              ))}
            </ul>
          </div>
          <div className="ds-l-col--2">
            <h4 className={linkHeaderClasses}>
              {t("footer.section.info.title")}
            </h4>
            <ul className="usa-list usa-list--unstyled">
              {(t("footer.section.info.links", { returnObjects: true }) as Array<{text: string, url: string}>).map((link, i) => (
                <li key={i}><a href={link.url}>{link.text}</a></li>
              ))}
            </ul>
          </div>
        </div>
      </section>
    </footer>
  )
}
