--- a materialized view covering the base query used by /fhir/Organization/
CREATE MATERIALIZED VIEW IF NOT EXISTS
    "${apiSchema}"."organization_by_name" AS
SELECT
    "organization"."id",
    "organization_to_name"."name"
FROM
    "${apiSchema}".organization
    LEFT OUTER JOIN "${apiSchema}".organization_to_name ON (
        "organization"."id" = "organization_to_name"."organization_id"
    )
ORDER BY
    "organization_to_name"."name" ASC;

-- an index on the column we always sort by
CREATE INDEX IF NOT EXISTS idx_organizationbyname_on_name ON "${apiSchema}"."organization_by_name" (name ASC);
-- a unique index to allow for use of REFRESH MATERIALIZED VIEW CONCURRENTLY
CREATE UNIQUE INDEX idx_organizationbyname_on_id_name ON "${apiSchema}"."organization_by_name" (id, name);

REFRESH MATERIALIZED VIEW CONCURRENTLY "${apiSchema}"."organization_by_name";