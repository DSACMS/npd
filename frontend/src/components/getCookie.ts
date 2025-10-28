/*
 * NOTE: (@abachman-dsac) in order for the React application to create forms
 * which submit to the Django backend, we have to have access to the CSRF token
 * stored in the csrftoken cookie.
 */
export function getCookie(name: string): string | null {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}
