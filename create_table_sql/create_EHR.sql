--Sourced from CHPL data and Lantern data


CREATE TABLE "EHRToNPI" (
    "id" SERIAL PRIMARY KEY,
    "NPI_id" BIGINT   NOT NULL,
    "EHR_id" int   NOT NULL
);

CREATE TABLE "EHR" (
    "id" SERIAL PRIMARY KEY,
    -- Sourced from CHPL data here https://chpl.healthit.gov/
    "CHPL_ID" VARCHAR(200)   NOT NULL
);
