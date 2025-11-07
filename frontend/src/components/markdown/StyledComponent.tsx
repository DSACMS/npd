import React from "react"
import type { WrappedMarkdownComponent } from "../../@types/markdown"

import styles from "./Markdown.module.css"

export const StyledComponent: WrappedMarkdownComponent =
  (tag: React.HTMLElementType) => (props) => {
    return React.createElement(tag, {
      className: styles[tag],
      children: <>{props.children}</>,
    })
  }
