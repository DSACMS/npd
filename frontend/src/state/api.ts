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

const pathWithOptions = (
  pathOrTemplate: string,
  templateOptions?: Record<string, string>,
) => {
  if (!templateOptions) {
    return pathOrTemplate
  }

  let result = pathOrTemplate

  // Find all placeholders in the template
  const placeholders = pathOrTemplate.match(/:(\w+)/g) || []
  placeholders.forEach((keyWithLeader: string) => {
    const key = keyWithLeader.slice(1)
    if (templateOptions[key]) {
      result = result.replace(keyWithLeader, templateOptions[key])
    }
  })

  // Check for any remaining unreplaced placeholders
  const remainingPlaceholders = result.match(/:(\w+)/g)
  if (remainingPlaceholders) {
    console.warn(
      `Warning: Unreplaced placeholders found: ${remainingPlaceholders.join(", ")}`,
    )
  }

  return result
}

/**
 * Converts a path string into a full API URL.
 *
 * @param pathOrTemplate - a simple path like "/api/something" or a path
 *                         template with :placeholders like "/api/somthing/:id"
 * @param templateOptions - [optional] placholder values for template paths
 */
export const apiUrl = (
  pathOrTemplate: string,
  templateOptions?: Record<string, string>,
): string => {
  const base = baseUrl()
  const path = pathWithOptions(pathOrTemplate, templateOptions)

  if (base) {
    try {
      return new URL(path, baseUrl()).toString()
    } catch (e) {
      console.error(e)
    }
  }
  return path
}
