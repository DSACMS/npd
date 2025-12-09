import { Alert } from "@cmsgov/design-system"
import classNames from "classnames"
import { useParams } from "react-router"
import { FeatureFlag } from "../../components/FeatureFlag"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import { organizationNpiSelector } from "../../state/requests/organizations"
import {
  practitionerAddressSelector,
  practitionerNameSelector,
  practitionerGenderSelector,
  usePractitionerAPI,
  practitionerDeceasedSelector,
  practitionerActiveSelector,
  practitionerPhoneSelector,
  practitionerFaxSelector,
  practitionerIdentifiersSelector,
} from "../../state/requests/practitioners"
import { useTranslation } from "react-i18next"
import { InfoItem } from "../../components/InfoItem"
import layout from "../Layout.module.css"
import {
  Table,
  TableRow,
  TableHead,
  TableCell,
  TableBody
} from "@cmsgov/design-system"
import { getIdentifierTypeDisplay } from "../../helpers/org_helpers"

export const Practitioner = () => {
  const { t } = useTranslation()
  const { practitionerId } = useParams()
  const { data, error, isLoading } = usePractitionerAPI(practitionerId)

  if (isLoading) {
    return <LoadingIndicator />
  }

  if (typeof data === "undefined" || error) {
    return <p>API Error: {JSON.stringify(error)}</p>
  }

  const contentClass = classNames(layout.content, "ds-l-container")
  const bannerClass = classNames(layout.banner)

  const name = practitionerNameSelector(data)
  const npi = organizationNpiSelector(data)
  const address = practitionerAddressSelector(data)
  const gender = practitionerGenderSelector(data)
  const deceased = practitionerDeceasedSelector(data)
  const active = practitionerActiveSelector(data)
  const phone = practitionerPhoneSelector(data)
  const fax = practitionerFaxSelector(data)
  const identifiers = practitionerIdentifiersSelector(data)

  return (
    <>
      <section className={bannerClass}>
        <div className="ds-l-container">
          <div className="ds-l-row">
            <div className="ds-l-col--12">
              <div className={layout.leader}>
                <h1 role="heading" aria-level={1} className={layout.title}>
                  {name}
                </h1>
                <span
                  data-testid="practitioner-npi"
                  className={layout.subtitle}
                >
                  NPI: {npi}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>
      <main className={contentClass}>
        <FeatureFlag  name="PRACTITIONER_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            This content is not currently available.
          </Alert>
        </FeatureFlag>

        <FeatureFlag inverse name="PRACTITIONER_LOOKUP_DETAILS">
          <Alert heading={t("practitioners.update.title")}>
          {t("practitioners.update.subtitle")}{' '}
          <a href="#">{t("practitioners.update.link")}</a>
          </Alert>

          <section className={layout.section}>
            <h2>{t("practitioners.about")}</h2>
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label="Name(s)" value={name} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label="Gender" value={gender} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label="Deceased" value={deceased} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label="Active status" value={active} />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("practitioners.contact")}</h2>
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label="Mailing address" value={address} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label="Phone" value={phone} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label="Fax" value={fax} />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.identifiers")}</h2>
            {/* TODO: look into modularizing table creation to reduce code duplication */}
            {identifiers.length > 0 ? (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Type</TableCell>
                    <TableCell>Number</TableCell>
                    <TableCell>Details</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {identifiers.map((identifier, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        {getIdentifierTypeDisplay(identifier.system ?? "Unknown")}
                      </TableCell>
                      <TableCell>{identifier.number}</TableCell>
                      <TableCell>{identifier.details}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="ds-u-color--gray">No identifiers available</p>
            )}
          </section>

          <section className={layout.section}>
            <h2>Taxonomy</h2>
            <p>[taxonomy information]</p>
          </section>

          <section className={layout.section}>
            <h2>Organization(s)</h2>
            <p>[endpoint information]</p>
          </section>
        </FeatureFlag>

        <div className="ds-u-margin-top--7"></div>
      </main>
    </>
  )
}
