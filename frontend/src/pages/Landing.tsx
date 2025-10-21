import Header from "../components/Header"

import { Badge, Button, SkipNav } from "@cmsgov/design-system"
import { Footer } from "../components/Footer"
import styles from "./Landing.module.css"

export const Landing = () => {
  return (
    <>
      <SkipNav href="#main-content" />
      <Header />
      <section id="main-content" className={styles.hero}>
        <div className="ds-l-container">
          <div className={styles.heroSpacing}></div>
          <div className={styles.heroBody}>
            <div className="ds-l-row">
              <div className="ds-l-col--12">
                <Badge variation="info" className={styles.heroBadge}>
                  LIMITED-RELEASE BETA
                </Badge>

                <h1>National Provider Directory</h1>
                <p className={styles.tagline}>
                  Building the new infrastructure for health data
                  interoperability
                </p>

                <div className={styles.primaryActions}>
                  <Button variation="solid" href="/developers">
                    Developer resources
                  </Button>
                  <Button variation="solid" href="/providers">
                    Provider information
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
              <h2>About the directory</h2>

              <p className={styles.secondaryDescription}>
                The National Provider Directory uses data from multiple
                publicly-available data sources and combines them to create a
                trusted source of truth for information about healthcare
                providers.
              </p>

              <Button href="#">Learn how it works</Button>
            </div>
          </div>
        </div>
      </section>
      <Footer />
    </>
  )
}
