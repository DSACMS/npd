


CREATE TABLE "NPIToEndpoint" (
    "id" SERIAL PRIMARY KEY,
    "NPI_id" BIGINT   NOT NULL,
    "Endpoint_id" INT   NOT NULL
);

CREATE TABLE "EndpointTypeLUT" (
    "id" SERIAL PRIMARY KEY,
    "identifier_type_description" TEXT   NOT NULL,
    CONSTRAINT "uc_EndpointTypeLUT_identifier_type_description" UNIQUE (
        "identifier_type_description"
    )
);

CREATE TABLE "Endpoint" (
    "id" SERIAL PRIMARY KEY,
    -- for now only FHIR and Direct
    "endpoint_url" VARCHAR(500)   NOT NULL,
    -- endpoint NPPES file as endpoint_description
    "endpoint_name" VARCHAR(100)   NOT NULL,
    -- endpoint NPPES file as endpoint_comments
    "endpoint_desc" VARCHAR(100)   NOT NULL,
    "EndpointAddress_id" int   NOT NULL,
    "EndpointType_id" int   NOT NULL
);

CREATE TABLE "OrgToEndpoint" (
    "id" SERIAL PRIMARY KEY,
    "Organization_id" int   NOT NULL,
    "Endpoint_id" int   NOT NULL
);
