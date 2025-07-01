



CREATE TABLE "NUCCTaxonomyCode" (
    "id" SERIAL PRIMARY KEY,
    "ParentNUCCTaxonomyCode_id" INT   NOT NULL,
    "taxonomy_code" VARCHAR(10)   NOT NULL,
    "tax_grouping" TEXT   NOT NULL,
    "tax_classification" TEXT   NOT NULL,
    "tax_specialization" TEXT   NOT NULL,
    "tax_definition" TEXT   NOT NULL,
    "tax_notes" TEXT   NOT NULL,
    "tax_display_name" TEXT   NOT NULL,
    "tax_certifying_board_name" TEXT   NOT NULL,
    "tax_certifying_board_url" TEXT   NOT NULL,
    CONSTRAINT "uc_NUCCTaxonomyCode_taxonomy_code" UNIQUE (
        "taxonomy_code"
    )
);

CREATE TABLE "NUCCTaxonomyCodePath" (
    "id" SERIAL PRIMARY KEY,
    "NUCCTaxonomyCodeDecendant_id" INT   NOT NULL,
    "NUCCTaxonomyCodeAncestor_id" INT   NOT NULL
);



CREATE TABLE "NPITaxonomy" (
    "id" SERIAL PRIMARY KEY,
    "NPI_id" BIGINT   NOT NULL,
    "NUCCTaxonomyCode_id" INT   NOT NULL,
    "license_number" VARCHAR(20)   NOT NULL,
    "StateCode_id" INTEGER   NOT NULL,
    "is_primary" BOOLEAN   NOT NULL,
    "taxonomy_group" VARCHAR(10)   NOT NULL
);

CREATE TABLE "MedicareProviderType" (
    "id" SERIAL PRIMARY KEY,
    "MedicareProviderType_name" VARCHAR   NOT NULL
);

CREATE TABLE "NUCCMedicareProviderType" (
    "id" SERIAL PRIMARY KEY,
    "MedicareProviderType_id" INT   NOT NULL,
    "NUCCTaxonomyCode_id" INT   NOT NULL
);
