import { useEffect, useState } from "react"

const url = "/fhir/?format=json"

interface UrlList {
  [key: string]: string
}

const defaultUrlList: UrlList = {
  Resource: "URL",
}

export const useGetFhirPoc = () => {
  const [urlList, setUrlList] = useState(defaultUrlList)

  useEffect(() => {
    fetch(url)
      .then((res) => res.json())
      .then((urlList: UrlList) => setUrlList(urlList))
  }, [])

  return urlList
}
