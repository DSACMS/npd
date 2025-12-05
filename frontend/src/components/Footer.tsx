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

  const logoColumnClasses = classNames(
    "ds-l-md-col--5",
    "ds-l-sm-col--12",
    "ds-u-padding-bottom--4",
    "ds-u-md-padding-bottom--0",
  )

  const columnClasses = classNames(
    "ds-l-md-col--2",
    "ds-l-sm-col--12",
    "ds-u-padding-y--3",
    "ds-u-md-padding-y--0",
  )

  const linkHeaderClasses = classNames(
    "usa-footer__primary-link",
    "ds-u-padding-top--none",
    "ds-u-sm-padding-top--1",
    "ds-u-md-padding-top--0",
    "ds-u-padding-left--0",
    "ds-u-margin-top--0",
    "ds-u-margin-top--0",
  )

  return (
    <footer className={styles.footer}>
      <section className="ds-l-container">
        <div className="ds-l-row">
          <div className={logoColumnClasses}>
            <FooterLogo />
          </div>
          <div className={columnClasses}>
            <h4 className={linkHeaderClasses}>
              {t("footer.section.support.title")}
            </h4>
            <ul className="usa-list usa-list--unstyled">
              {(
                t("footer.section.support.links", {
                  returnObjects: true,
                }) as Array<{ text: string; url: string }>
              ).map((link, i) => (
                <li key={i}>
                  <a href={link.url}>{link.text}</a>
                </li>
              ))}
            </ul>
          </div>
          <div className={columnClasses}>
            <h4 className={linkHeaderClasses}>
              {t("footer.section.cms.title")}
            </h4>
            <ul className="usa-list usa-list--unstyled">
              {(
                t("footer.section.cms.links", {
                  returnObjects: true,
                }) as Array<{ text: string; url: string }>
              ).map((link, i) => (
                <li key={i}>
                  <a href={link.url}>{link.text}</a>
                </li>
              ))}
            </ul>
          </div>
          <div className={columnClasses}>
            <h4 className={linkHeaderClasses}>
              {t("footer.section.info.title")}
            </h4>
            <ul className="usa-list usa-list--unstyled">
              {(
                t("footer.section.info.links", {
                  returnObjects: true,
                }) as Array<{ text: string; url: string }>
              ).map((link, i) => (
                <li key={i}>
                  <a href={link.url}>{link.text}</a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>
    </footer>
  )
}
