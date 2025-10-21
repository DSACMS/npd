import { Badge, SkipNav, UsaBanner } from "@cmsgov/design-system"
import classnames from "classnames"

import close from "@uswds/uswds/img/usa-icons/close.svg"

import cmsLogo from "../assets/cms-gov-logo.svg"
import styles from "./Header.module.css"

function Header() {
  const classes = classnames("usa-header", "usa-header--basic", styles.header)

  return (
    <>
      <SkipNav href="#">Skip navigation</SkipNav>
      <UsaBanner />
      <header className={classes} role="banner">
        <div className="usa-nav-container">
          <div className="usa-navbar">
            <div className={`usa-logo ${styles.title}`}>
              <img src={cmsLogo} className={styles.logo} alt="CMS.gov" />
              <em className={`${styles.logoText} usa-logo__text `}>
                National Provider Directory
              </em>
              <Badge variation="info" className={styles.betaBadge}>
                BETA
              </Badge>
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
              <li className="usa-nav__primary-item">
                <a href="#" className="usa-nav-link">
                  Search the data
                </a>
              </li>
              <li className="usa-nav__primary-item">
                <button
                  type="button"
                  className="usa-accordion__button usa-nav__link"
                  aria-expanded="false"
                  aria-controls="basic-nav-section"
                >
                  <span>For developers</span>
                </button>
                <ul
                  id="basic-nav-section"
                  className={`usa-nav__submenu ${styles.submenuList}`}
                  role="menu"
                  hidden
                >
                  <li className="usa-nav__submenu-item">
                    <a href="javascript:void(0);">
                      <span>Overview</span>
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a href="javascript:void(0);">
                      <span>About the data</span>
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a href="javascript:void(0);">
                      <span>API documentation</span>
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a href="javascript:void(0);">
                      <span>Bulk data files</span>
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a href="javascript:void(0);">
                      <span>Developer support</span>
                    </a>
                  </li>
                </ul>
              </li>
              <li className="usa-nav__primary-item">
                <a href="#" className="ds-u-link">
                  For providers
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </header>
    </>
  )
}

export default Header
