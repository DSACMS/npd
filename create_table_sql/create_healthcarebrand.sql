CREATE TABLE "HealthcareBrand" (
    "id" SERIAL PRIMARY KEY,
    "HealthcareBrand_name" VARCHAR(200)   NOT NULL,
    "TrademarkSerialNumber" VARCHAR(20)   NOT NULL
);

CREATE TABLE "OrganizationToHealthcareBrand" (
    "id" SERIAL PRIMARY KEY,
    "HealthcareBrand_id" INT   NOT NULL,
    "Organization_id" INT   NOT NULL
);
