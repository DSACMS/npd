import type { Components } from "react-markdown"
import { SluggedHeading } from "./SluggedHeading"
import { StyledComponent } from "./StyledComponent"
import { StyledTable, StyledTd, StyledTh } from "./StyledTableComponents"

export const MdComponents: Components = {
  h1: SluggedHeading("h1"),
  h2: SluggedHeading("h2"),
  h3: SluggedHeading("h3"),
  h4: SluggedHeading("h4"),
  table: StyledTable,
  th: StyledTh,
  td: StyledTd,
  pre: StyledComponent("pre"),
  code: StyledComponent("code"),
}
