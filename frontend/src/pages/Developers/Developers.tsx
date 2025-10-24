import { SkipNav } from "@cmsgov/design-system"

import classNames from "classnames"
import Markdown from "react-markdown"

import { MdComponents } from "../../components/markdown/MdComponents"
import { DeveloperHeading } from "./DeveloperHeading"
import { SidebarMenu } from "./SidebarMenu"

import layoutstyles from "../Layout.module.css"

/*
 * This is a first attempt at a static content page for the NPD frontend.
 *
 * Content is derived from a vite.js ?raw asset import.
 *
 *
 */
import content from "./Developers.content.md?raw"

export const Developers = () => {
  const contentClass = classNames(layoutstyles.content, "ds-l-container")

  return (
    <>
      <DeveloperHeading />
      <main className={contentClass}>
        <SkipNav href="#content" />
        <div className="ds-l-row">
          <SidebarMenu />
          <article
            id="content"
            className="ds-content ds-l-md-col--8 ds-l-lg-col--9"
          >
            <Markdown components={MdComponents}>{content}</Markdown>
            <p className="ds-u-margin-top--7 ds-u-margin-bottom--2">
              <a className="ds-c-link" href="#content">
                Back to Top
              </a>
            </p>
          </article>
        </div>
      </main>
    </>
  )
}
