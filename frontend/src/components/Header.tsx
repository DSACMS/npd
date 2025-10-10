import { Badge, UsaBanner } from "@cmsgov/design-system"

import close from "@uswds/uswds/img/usa-icons/close.svg"

import cmsLogo from "../assets/cms-gov-logo.png"
import styles from "./Header.module.css"

function Header() {
  return (
    <>
      <UsaBanner />
      <div className="usa-overlay"></div>
      <header className="usa-header usa-header--basic" role="banner">
        <div className="usa-nav-container">
          <div className="usa-navbar">
            <div className={`usa-logo grid-row flex-no-wrap ${styles.title}`}>
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

            <ul
              className="usa-nav__primary usa-accordion"
              role="navigation"
              hidden
            >
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
                  <span>For Developers</span>
                </button>
                <ul
                  id="basic-nav-section"
                  className="usa-nav__submenu"
                  role="menu"
                >
                  <li className="usa-nav__submenu-item">
                    <a href="javascript:void(0);">
                      <span>Navigation Link</span>
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a href="javascript:void(0);">
                      <span>Navigation Link</span>
                    </a>
                  </li>
                </ul>
              </li>
              <li className="usa-nav__primary-item">
                <a href="#" className="ds-u-link">
                  For Providers
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
