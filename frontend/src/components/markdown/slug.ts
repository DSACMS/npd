export function slug(text: string): string {
  return text.toLowerCase().replace(/\W/g, "-")
}

export function slugId(text: string): string {
  return `#${slug(text)}`
}
