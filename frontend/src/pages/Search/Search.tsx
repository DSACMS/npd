import { Button } from "@cmsgov/design-system"
import { FaUserMd, FaHospital } from "react-icons/fa"
import { TitlePanel } from "../../components/TitlePanel"
import layout from "../Layout.module.css"

export const Search = () => {
  return (
    <>
      <TitlePanel
        title="Search the data"
        className={layout.compactLeader}
      >
        <p>
          Search by name or NPI number to see the details of any practitioner or organization in the database.
        </p>

        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-display--flex ds-u-justify-content--start ds-u-margin-top--4 ds-u-margin-bottom--4">
            <Button
              variation="solid"
              size="big"
              href="/practitioners/search"
              className="ds-u-margin-right--2"
            >
              <FaUserMd className="ds-u-margin-right--1" aria-hidden="true" />
              Practitioner search
            </Button>
            <Button
              variation="solid"
              size="big"
              href="/organizations/search"
            >
              <FaHospital className="ds-u-margin-right--1" aria-hidden="true" />
              Organization search
            </Button>
          </div>
        </div>
      </TitlePanel>
    </>
  )
}