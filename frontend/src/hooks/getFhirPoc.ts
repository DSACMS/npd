import { useEffect, useState } from "react"

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
const url = baseUrl + "/fhir/?format=json"

interface UrlList {
  [key: string]: string
}

const defaultUrlList: UrlList = {
  Resource: "URL",
}

const useGetFhirPoc = () => {
  const [urlList, setUrlList] = useState(defaultUrlList)

  useEffect(() => {
    fetch(url)
      .then((res) => res.json())
      .then((urlList: UrlList) => setUrlList(urlList))
  }, [])
  console.log(urlList)
  {
    return urlList
  }
}

export default useGetFhirPoc
