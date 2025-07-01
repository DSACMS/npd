
CREATE TABLE "IdentifierTypeLUT" (
    "id" SERIAL PRIMARY KEY,
    "identifier_type_description" TEXT   NOT NULL,
    CONSTRAINT "uc_IdentifierTypeLUT_identifier_type_description" UNIQUE (
        "identifier_type_description"
    )
);

CREATE TABLE "NPIIdentifier" (
    "id" SERIAL PRIMARY KEY,
    "NPI_id" BIGINT   NOT NULL,
    "identifier" VARCHAR(21)   NOT NULL,
    "IdentifierType_id" INTEGER   NOT NULL,
    "state" VARCHAR(3)   NOT NULL,
    "issuer" VARCHAR(81)   NOT NULL
);


