import useGetFhirPoc from "../hooks/getFhirPoc.ts"
import {
  Table,
  TableBody,
  TableCaption,
  TableHead,
  TableCell,
  TableRow,
} from "@cmsgov/design-system"

function UrlList() {
  const urlList = useGetFhirPoc()

  const headers = Object.keys(urlList)

  return (
    <>
      <Table>
        <TableCaption>
          POC of pulling in FHIR data from the Django API
        </TableCaption>
        <TableHead>
          <TableRow>
            <TableCell>Resource</TableCell>
            <TableCell>URL</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {headers.map((header) => (
            <TableRow key={header}>
              <TableCell key={`${header}-resoure`}>{header}</TableCell>
              <TableCell key={`${header}-url`}>{urlList[header]}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  )
}

export default UrlList
