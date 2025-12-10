import { Alert } from "@cmsgov/design-system"
import classNames from "classnames"
import { useParams } from "react-router"
import { FeatureFlag } from "../../components/FeatureFlag"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import { PractitionerPresenter } from "../../presenters/PractitionerPresenter"
import { formatIdentifierType } from "../../helpers/formatters"
import { usePractitionerAPI } from "../../state/requests/practitioners"
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

  const practitioner = new PractitionerPresenter(data)

  return (
    <>
      <section className={bannerClass}>
        <div className="ds-l-container">
          <div className="ds-l-row">
            <div className="ds-l-col--12">
              <div className={layout.leader}>
                <h1 role="heading" aria-level={1} className={layout.title}>
                  {practitioner.name}
                </h1>
                <span
                  data-testid="practitioner-npi"
                  className={layout.subtitle}
                >
                  NPI: {practitioner.npi}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>
      <main className={contentClass}>
        <FeatureFlag inverse name="PRACTITIONER_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            This content is not currently available.
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="PRACTITIONER_LOOKUP_DETAILS">
          <Alert heading={t("practitioners.update.title")}>
          {t("practitioners.update.subtitle")}{' '}
          <a href="#">{t("practitioners.update.link")}</a>
          </Alert>

          <section className={layout.section}>
            <h2>{t("practitioners.about.title")}</h2>
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label={t("practitioners.about.name")} value={practitioner.name} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label={t("practitioners.about.gender")} value={practitioner.gender} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label={t("practitioners.about.deceased")} value={practitioner.isDeceased} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label={t("practitioners.about.status")} value={practitioner.isActive} />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("practitioners.contact.title")}</h2>
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label={t("practitioners.contact.address")} value={practitioner.address} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label={t("practitioners.contact.phone")} value={practitioner.phone} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem label={t("practitioners.contact.fax")} value={practitioner.fax} />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("practitioners.identifiers.title")}</h2>
            {/* TODO: look into modularizing table creation to reduce code duplication */}
            {practitioner.identifiers.length > 0 ? (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>{t("practitioners.identifiers.type")}</TableCell>
                    <TableCell>{t("practitioners.identifiers.number")}</TableCell>
                    <TableCell>{t("practitioners.identifiers.details")}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {practitioner.identifiers.map((identifier, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        {formatIdentifierType(identifier.system ?? "Unknown")}
                      </TableCell>
                      <TableCell>{identifier.number}</TableCell>
                      <TableCell>{identifier.details}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="ds-u-color--gray">{t("practitioners.identifiers.fallback")}</p>
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
