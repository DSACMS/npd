export const formatAddress = (address?: Address): string => {
    if (!address) return ""
  
    const cityStateZip = [address.city, address.state, address.postalCode]
      .filter(Boolean)
      .join(", ")
  
    return [address.line, cityStateZip].filter(Boolean).join("\n")
  }