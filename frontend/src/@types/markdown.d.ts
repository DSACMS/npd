import type { ComponentType } from "react"
import { ExtraProps } from "react-markdown"

export type MarkdownComponent = ComponentType<
  JSX.IntrinsicElements[Key] & ExtraProps
>

export type WrappedMarkdownComponent = (
  tag: React.HTMLElementType,
) => MarkdownComponent
