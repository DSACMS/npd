const baseUrl = (): URL | undefined => {
  try {
    return new URL(
      import.meta.env.VITE_API_BASE_URL ||
        `${window.location.protocol}//${window.location.host}`,
    )
  } catch (e) {
    console.error(e)
  }
}

export const apiUrl = (path: string): string => {
  const base = baseUrl()
  if (base) {
    try {
      return new URL(path, baseUrl()).toString()
    } catch (e) {
      console.error(e)
    }
  }
  return path
}
