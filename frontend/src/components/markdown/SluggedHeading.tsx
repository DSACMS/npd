import React from "react"
import type { WrappedMarkdownComponent } from "../../@types/markdown"
import { slug } from "./slug"

import styles from "./Markdown.module.css"

export const SluggedHeading: WrappedMarkdownComponent =
  (tag: React.HTMLElementType) => (props) => {
    const level = /h\d/.test(tag) ? tag[1] : "1"
    return React.createElement(tag, {
      id: slug(props.children),
      role: "heading",
      "aria-level": parseInt(level) + 1,
      className: styles[tag],
      children: <>{props.children}</>,
    })
  }
