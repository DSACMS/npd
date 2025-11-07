// Example in a React component
import { useEffect, useState } from "react"

function MyApp() {
  const [featureFlags, setFeatureFlags] = useState<Record<string, boolean>>({})

  useEffect(() => {
    fetch("/api/flags/") // Replace with your actual API endpoint
      .then((response) => response.json())
      .then((data) => setFeatureFlags(data))
      .catch((error) => console.error("Error fetching flags:", error))
  }, [])

  return (
    <div>
      {featureFlags.my_new_feature && <p>This is the new feature!</p>}
      {featureFlags.beta_testing ? (
        <p>Welcome to beta testing!</p>
      ) : (
        <p>Beta testing is not available for you.</p>
      )}
    </div>
  )
}

export default MyApp
