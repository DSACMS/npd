import { useEffect, useState } from "react"
import { apiUrl } from "../state/api"

interface UrlList {
  [key: string]: string
}

const defaultUrlList: UrlList = {
  Resource: "URL",
}

export const useGetFhirPoc = () => {
  const [urlList, setUrlList] = useState(defaultUrlList)
  const url = apiUrl("/fhir/?format=json")

  useEffect(() => {
    fetch(url)
      .then((res) => res.json())
      .then((urlList: UrlList) => setUrlList(urlList))
  }, [url])

  return urlList
}
