import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableRow,
} from "@cmsgov/design-system"
import { useGetFhirPoc } from "../hooks/getFhirPoc"

function UrlList() {
  const urlList = useGetFhirPoc()

  const headers = Object.keys(urlList)

  return (
    <>
      <section className="ds-l-container">
        <div className="ds-l-row">
          <div className="ds-l-col--12">
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
                    <TableCell key={`${header}-url`}>
                      {urlList[header]}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </section>
    </>
  )
}

export default UrlList
