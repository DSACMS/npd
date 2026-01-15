import classNames from "classnames"
import type { ReactNode } from "react"

import layout from "../pages/Layout.module.css"

type Props = React.PropsWithChildren<{
  title?: string
  icon?: ReactNode
  className?: string
}>

export const TitlePanel = ({ title, icon, children, className }: Props) => {
  const bannerClass = classNames(layout.banner, className)

  return (
    <section className={bannerClass}>
      <div className="ds-l-container">
        <div className="ds-l-row">
          <div className="ds-l-col--12">
            <div className={layout.leader}>
              {icon && <div className="ds-u-margin-bottom--1">{icon}</div>}
              {title && (
                <div role="heading" aria-level={1} className={layout.title}>
                  {title}
                </div>
              )}
            </div>
          </div>
        </div>

        {children}
      </div>
    </section>
  )
}
