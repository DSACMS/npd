// When Django renders the frontend index.html, it will inject the current

import { getCookie } from "../getCookie"

// csrf_token as an <input> tag, inside <template id="csrf-token-input">
export const CsrfInput = () => {
  const csrfinput: HTMLTemplateElement | null = document.getElementById(
    "csrf-token-input",
  ) as HTMLTemplateElement

  if (csrfinput && csrfinput.content) {
    const __html = csrfinput.content.querySelector("input")?.outerHTML
    if (__html) {
      return (
        <span
          aria-hidden
          style={{ display: "none" }}
          dangerouslySetInnerHTML={{
            __html,
          }}
        />
      )
    }

    const token = getCookie("csrftoken")
    if (csrfinput.content.textContent.startsWith("{%") && token) {
      // we are likely running in a vite dev server context, try getting the
      // CSRF token from the appropriate cookie
      if (token) {
        return <input name="csrfmiddlewaretoken" value={token} type="hidden" />
      }
    }

    console.warn(
      "expected to find input element in csrf-token-input template or token value in csrftoken cookie",
      csrfinput,
      token,
    )
  }

  return null
}
