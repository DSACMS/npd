import { useState, useEffect } from "react";

const url = 'http://localhost:8000/fhir/?format=json';


interface UrlList {
    [key: string]: string;
}

const defaultUrlList: UrlList = {
    'Resource': 'URL'
}

const useGetFhirPoc = () => {
const [urlList, setUrlList] = useState(defaultUrlList);

  useEffect(() => {
    fetch(url)
      .then((res) => res.json())
      .then((urlList: UrlList) => setUrlList(urlList));
  }, [url]);
  console.log(urlList);
  {return urlList}
};

export default useGetFhirPoc;