import React from "react"

const tableStyles = {
  borderCollapse: "collapse" as const,
  width: "100%",
  border: "1px solid #ddd",
}

const cellStyles = {
  border: "1px solid #ddd",
  padding: "12px",
}

const headerStyles = {
  ...cellStyles,
  backgroundColor: "#f2f2f2",
  textAlign: "left" as const,
}

export const StyledTable = (props: React.ComponentPropsWithoutRef<"table">) =>
  React.createElement("table", { style: tableStyles, ...props })

export const StyledTh = (props: React.ComponentPropsWithoutRef<"th">) =>
  React.createElement("th", { style: headerStyles, ...props })

export const StyledTd = (props: React.ComponentPropsWithoutRef<"td">) =>
  React.createElement("td", { style: cellStyles, ...props })