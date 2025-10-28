import { useCallback } from "react"

const useCsrfInputElement = () => {
  const csrfinput: HTMLTemplateElement | null = document.getElementById(
    "csrf-token-input",
  ) as HTMLTemplateElement

  if (csrfinput && csrfinput.content) {
    return csrfinput.content.querySelector("input")
  }

  return null
}

// returns a callback function that can be passed as a `ref` prop to attach a
// valid Django CSRF form input tag.
export const useCsrfInput = () => {
  const csrfInputElement = useCsrfInputElement()

  const attachCsrf = useCallback(
    (node: HTMLFormElement) => {
      if (csrfInputElement && node) {
        node.appendChild(csrfInputElement)
      }
    },
    [csrfInputElement],
  )

  return attachCsrf
}
