import classNames from "classnames"

import layout from "../pages/Layout.module.css"

type Props = React.PropsWithChildren<{ title?: string; className?: string }>

export const TitlePanel = ({ title, children, className }: Props) => {
  const bannerClass = classNames(layout.banner, className)

  return (
    <section className={bannerClass}>
      <div className="ds-l-container">
        <div className="ds-l-row">
          <div className="ds-l-col--12">
            <div className={layout.leader}>
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
