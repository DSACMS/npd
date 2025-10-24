import type { Components } from "react-markdown"
import { SluggedHeading } from "./SluggedHeading"

export const MdComponents: Components = {
  h1: SluggedHeading("h1"),
  h2: SluggedHeading("h2"),
  h3: SluggedHeading("h3"),
  h4: SluggedHeading("h4"),
}
