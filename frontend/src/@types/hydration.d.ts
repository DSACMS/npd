interface FrontendSettings {
  require_authentication?: boolean
  user?: AuthenticatedUser
  feature_flags?: Record<string, boolean>
}

interface AuthenticatedUser {
  username: string
  is_anonymous: boolean
  ready?: boolean
}
