import { Badge, SkipNav, UsaBanner } from "@cmsgov/design-system"
import classnames from "classnames"
import { useTranslation } from "react-i18next"

import close from "@uswds/uswds/img/usa-icons/close.svg"
import cmsLogo from "../assets/cms-gov-logo.svg"
import styles from "./Header.module.css"
import { slugId } from "./markdown/slug"

export const Header = () => {
  const { t } = useTranslation()
  const classes = classnames("usa-header", "usa-header--basic", styles.header)

  return (
    <>
      <SkipNav href="#after-header">{t("header.skip")}</SkipNav>
      <UsaBanner />
      <header className={classes} role="banner">
        <div className="usa-nav-container">
          <div className="usa-navbar">
            <div className={`usa-logo ${styles.title}`}>
              <a
                href="/"
                className="ds-u-display--flex ds-l-col--6 ds-u-align-items--center ds-u-padding-left--0"
                title="Return to the homepage"
              >
                <img src={cmsLogo} className={styles.logo} alt="CMS.gov" />
                <em className={`${styles.logoText} usa-logo__text `}>
                  {t("header.title")}
                </em>
                <Badge variation="info" className={styles.betaBadge}>
                  {t("header.badge")}
                </Badge>
              </a>
            </div>
            <button type="button" className="usa-menu-btn">
              Menu
            </button>
          </div>

          <nav aria-label="Primary navigation" className="usa-nav">
            <button type="button" className="usa-nav__close">
              <img src={close} role="img" alt="Close" />
            </button>

            <ul className="usa-nav__primary usa-accordion" role="navigation">
              {/* <li className="usa-nav__primary-item">
                <a href="#" className="usa-nav-link">
                  {t("header.link.search")}
                </a>
              </li> */}
              <li className="usa-nav__primary-item">
                <button
                  type="button"
                  className="usa-accordion__button usa-nav__link"
                  aria-expanded="false"
                  aria-controls="basic-nav-section"
                >
                  <span>{t("header.link.developers")}</span>
                </button>
                <ul
                  id="basic-nav-section"
                  className={`usa-nav__submenu ${styles.submenuList}`}
                  role="menu"
                  hidden
                >
                  <li className="usa-nav__submenu-item">
                    <a
                      href={`/developers${slugId(t("developers.nav.overview"))}`}
                    >
                      <span>{t("developers.nav.overview")}</span>
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a href={`/developers${slugId(t("developers.nav.about"))}`}>
                      <span>{t("developers.nav.about")}</span>
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a
                      href={`/developers${slugId(t("developers.nav.accessing"))}`}
                    >
                      <span>{t("developers.nav.accessing")}</span>
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a
                      href={`/developers${slugId(t("developers.nav.opensource"))}`}
                    >
                      <span>{t("developers.nav.opensource")}</span>
                    </a>
                  </li>
                </ul>
              </li>
              {/* <li className="usa-nav__primary-item">
                <a href="#" className="ds-u-link">
                  {t("header.link.providers")}
                </a>
              </li> */}
            </ul>
          </nav>
        </div>
      </header>
      <a id="after-header" />
    </>
  )
}
