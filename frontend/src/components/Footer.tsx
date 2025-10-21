import classNames from "classnames"
import logoImgSrc from "../assets/hss-logo.png"
import styles from "./Footer.module.css"

const FooterLogo = () => {
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
        <p>
          A federal government website managed and paid for by the U.S. Centers
          for Medicare & Medicaid Services.
        </p>
        <p>7500 Security Boulevard, Baltimore, MD 21244</p>
      </div>
    </div>
  )
}

export const Footer = () => {
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
            <h4 className={linkHeaderClasses}>National Provider Directory</h4>
            <ul className="usa-list usa-list--unstyled">
              <a href="#">Footer link</a>
            </ul>
          </div>
          <div className="ds-l-col--2">
            <h4 className={linkHeaderClasses}>CMS & HHS Websites</h4>
            <ul className="usa-list usa-list--unstyled">
              <a href="#">Footer link</a>
            </ul>
          </div>
          <div className="ds-l-col--2">
            <h4 className={linkHeaderClasses}>Additional Information</h4>
            <ul className="usa-list usa-list--unstyled">
              <a href="#">Footer link</a>
            </ul>
          </div>
        </div>
      </section>
    </footer>
  )
}
