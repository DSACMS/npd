// Example in a React component

import { useFrontendSettings } from "../hooks/useFrontendSettings"

// render the
export const FeatureFlag = ({
  name,
  children,
  inverse,
}: React.PropsWithChildren<{ name: string; inverse?: boolean }>) => {
  const {
    settings: { feature_flags },
    loading,
  } = useFrontendSettings()

  if (loading) return null
  // flags haven't loaded
  if (!feature_flags) return null

  // inverse flag
  if (inverse && !feature_flags[name]) return children

  // flag unset
  if (!feature_flags[name]) return null

  // flag set
  return children
}
