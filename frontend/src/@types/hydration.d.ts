interface FrontendSettings {
  require_authentication?: boolean
  user?: AuthenticatedUser
}

interface AuthenticatedUser {
  username: string
  is_anonymous: boolean
  ready?: boolean
}
