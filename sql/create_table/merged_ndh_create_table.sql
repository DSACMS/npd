-- Merged SQL statements for schema: ndh
-- Generated on: 2025-07-11 18:00:40
-- Total statements for this schema: 48
--
-- Source files:
--   ./sql/create_table_sql/create_address.sql
--   ./sql/create_table_sql/create_clinical_organization.sql
--   ./sql/create_table_sql/create_ehr.sql
--   ./sql/create_table_sql/create_healthcarebrand.sql
--   ./sql/create_table_sql/create_identifier.sql
--   ./sql/create_table_sql/create_individual.sql
--   ./sql/create_table_sql/create_interop_endpoint.sql
--   ./sql/create_table_sql/create_npi.sql
--   ./sql/create_table_sql/create_payer_data.sql
--   ./sql/create_table_sql/create_phone.sql
--   ./sql/create_table_sql/create_provider_taxonomy.sql
--   ./sql/create_table_sql/create_user_tables.sql


-- Source: ./sql/create_table_sql/create_address.sql
CREATE TABLE ndh.address (
    id SERIAL PRIMARY KEY,
    barcode_delivery_code VARCHAR(12),
    smarty_key VARCHAR(10),
    address_us_id INT NULL,
    address_international_id INT NULL,
    address_nonstandard_id INT NULL
);

-- Source: ./sql/create_table_sql/create_address.sql
CREATE TABLE ndh.address_us (
    id SERIAL PRIMARY KEY,
    address_id INT NOT NULL,
    input_id VARCHAR(36),
    input_index INT,
    candidate_index INT,
    addressee VARCHAR(64),
    delivery_line_1 VARCHAR(64),
    delivery_line_2 VARCHAR(64),
    last_line VARCHAR(64),
    delivery_point_barcode VARCHAR(12),
    
    -- Components
    urbanization VARCHAR(64),
    primary_number VARCHAR(30),
    street_name VARCHAR(64),
    street_predirection VARCHAR(16),
    street_postdirection VARCHAR(16),
    street_suffix VARCHAR(16),
    secondary_number VARCHAR(32),
    secondary_designator VARCHAR(16),
    extra_secondary_number VARCHAR(32),
    extra_secondary_designator VARCHAR(16),
    pmb_designator VARCHAR(16),
    pmb_number VARCHAR(16),
    city_name VARCHAR(64),
    default_city_name VARCHAR(64),
    state_abbreviation CHAR(2),
    zipcode CHAR(5),
    plus4_code VARCHAR(4),
    delivery_point CHAR(2),
    delivery_point_check_digit CHAR(1),
    
    -- Metadata
    record_type CHAR(1),
    zip_type VARCHAR(32),
    county_fips CHAR(5),
    county_name VARCHAR(64),
    ews_match CHAR(5),
    carrier_route CHAR(4),
    congressional_district CHAR(2),
    building_default_indicator CHAR(1),
    rdi VARCHAR(12),
    elot_sequence VARCHAR(4),
    elot_sort VARCHAR(4),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    coordinate_license INT,
    geo_precision VARCHAR(18),
    time_zone VARCHAR(48),
    utc_offset DECIMAL(4,2),
    dst CHAR(5),
    
    -- Analysis
    dpv_match_code VARCHAR(1),
    dpv_footnotes VARCHAR(32),
    dpv_cmra VARCHAR(1),
    dpv_vacant VARCHAR(1),
    dpv_no_stat VARCHAR(1),
    active VARCHAR(1),
    footnotes VARCHAR(24),
    lacslink_code VARCHAR(2),
    lacslink_indicator VARCHAR(1),
    suitelink_match VARCHAR(5),
    enhanced_match VARCHAR(64)
);

-- Source: ./sql/create_table_sql/create_address.sql
CREATE TABLE ndh.address_international (
    id SERIAL PRIMARY KEY,
    address_id INT NOT NULL,
    input_id VARCHAR(36),
    country VARCHAR(64),
    geocode VARCHAR(4),
    local_language VARCHAR(6),
    freeform VARCHAR(512),
    address1 VARCHAR(64),
    address2 VARCHAR(64),
    address3 VARCHAR(64),
    address4 VARCHAR(64),
    organization VARCHAR(64),
    locality VARCHAR(64),
    administrative_area VARCHAR(32),
    postal_code VARCHAR(16),
    
    -- Components
    administrative_area_iso2 VARCHAR(8),
    sub_administrative_area VARCHAR(64),
    country_iso_3 VARCHAR(3),
    premise VARCHAR(64),
    premise_number VARCHAR(64),
    thoroughfare VARCHAR(64),
    
    -- Metadata
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    geocode_precision VARCHAR(32),
    max_geocode_precision VARCHAR(32),
    address_format VARCHAR(128),
    
    -- Analysis
    verification_status VARCHAR(32),
    address_precision VARCHAR(32),
    max_address_precision VARCHAR(32)
);

-- Source: ./sql/create_table_sql/create_address.sql
CREATE TABLE ndh.address_nonstandard (
    id SERIAL PRIMARY KEY,
    address_id INT NOT NULL,
    input_id VARCHAR(36),
    input_index INT,
    candidate_index INT,
    addressee VARCHAR(64),
    delivery_line_1 VARCHAR(64),
    delivery_line_2 VARCHAR(64),
    last_line VARCHAR(64),
    
    -- Any additional fields specific to non-standard addresses
    address_type VARCHAR(32),
    address_format VARCHAR(128),
    raw_address TEXT,
    notes TEXT
);

-- Source: ./sql/create_table_sql/create_address.sql
CREATE TABLE ndh.address_type (
    id SERIAL PRIMARY KEY,
    address_type_description TEXT   NOT NULL,
    CONSTRAINT uc_address_type_address_type_description UNIQUE (
        address_type_description
    )
);

-- Source: ./sql/create_table_sql/create_address.sql
CREATE TABLE ndh.state_code (
    id SERIAL PRIMARY KEY,
    state_code VARCHAR(100)   NOT NULL,
    state_name VARCHAR(100)   NOT NULL,
    CONSTRAINT uc_StateCodeLUT_state_code UNIQUE (
        state_code
    )
);

-- Source: ./sql/create_table_sql/create_address.sql
CREATE TABLE ndh.npi_address (
    id SERIAL PRIMARY KEY,
    npi_id BIGINT   NOT NULL,
    address_type_id INTEGER   NOT NULL,
    address_id INT   NOT NULL
);

-- Source: ./sql/create_table_sql/create_clinical_organization.sql
CREATE TABLE ndh.clinical_organization (
    id SERIAL PRIMARY KEY,
    clinical_organization_legal_name VARCHAR(200)   NOT NULL,
    authorized_official_individual_id INT   NOT NULL,
    organization_tin VARCHAR(10)   DEFAULT NULL,
    organization_vtin VARCHAR(50) DEFAULT NULL,
    organization_glief VARCHAR(300)  DEFAULT NULL,
    CONSTRAINT uc_organization_organization_vtin UNIQUE (
        organization_vtin
    )
);

-- Source: ./sql/create_table_sql/create_clinical_organization.sql
CREATE TABLE ndh.clinical_orgname_type (
    id SERIAL PRIMARY KEY,
    orgname_type_description TEXT   NOT NULL,
    source_file TEXT   NOT NULL,
    source_field TEXT   NOT NULL,
    CONSTRAINT uc_orgname_type_orgname_description UNIQUE (
        orgname_type_description
    )
);

-- Source: ./sql/create_table_sql/create_clinical_organization.sql
CREATE TABLE ndh.orgname (
    id SERIAL PRIMARY KEY,
    clinical_organization_id INT   NOT NULL,
    clinical_organization_name VARCHAR(70)   NOT NULL,
    clinical_orgname_type_id INTEGER   NOT NULL
);

-- Source: ./sql/create_table_sql/create_clinical_organization.sql
CREATE TABLE ndh.assigning_npi (
    clinical_organization_id INT   NOT NULL,
    npi_id INT NOT NULL
);

-- Source: ./sql/create_table_sql/create_ehr.sql
CREATE TABLE ndh.ehr_instance_to_npi (
    id SERIAL PRIMARY KEY,
    npi_id BIGINT   NOT NULL,
    ehr_id INT   NOT NULL
);

-- Source: ./sql/create_table_sql/create_ehr.sql
CREATE TABLE ndh.ehr_instance (
    id SERIAL PRIMARY KEY,
    -- Sourced from CHPL data here https://chpl.healthit.gov/
    chpl_if VARCHAR(200)   NOT NULL,
    bulk_endpoint_json_url VARCHAR(500) NULL
);

-- Source: ./sql/create_table_sql/create_healthcarebrand.sql
CREATE TABLE ndh.healthcare_brand (
    id SERIAL PRIMARY KEY,
    healthcare_brand_name VARCHAR(200)   NOT NULL,
    trademark_serial_number VARCHAR(20)   NOT NULL
);

-- Source: ./sql/create_table_sql/create_healthcarebrand.sql
CREATE TABLE ndh.organization_healthcare_brand (
    id SERIAL PRIMARY KEY,
    healthcare_brand_id INT   NOT NULL,
    organization_id INT   NOT NULL
);

-- Source: ./sql/create_table_sql/create_identifier.sql
CREATE TABLE ndh.identifier_type (
    id SERIAL PRIMARY KEY,
    identifier_type_description TEXT   NOT NULL,
    CONSTRAINT uc_IdentifierTypeLUT_identifier_type_description UNIQUE (
        identifier_type_description
    )
);

-- Source: ./sql/create_table_sql/create_identifier.sql
CREATE TABLE ndh.npi_identifier (
    id SERIAL PRIMARY KEY,
    npi_id BIGINT   NOT NULL,
    identifier VARCHAR(21)   NOT NULL,
    identifier_type_id INTEGER   NOT NULL,
    state_id INT   NOT NULL,
    identifier_issuer_name VARCHAR(81)   NOT NULL
);

-- Source: ./sql/create_table_sql/create_individual.sql
CREATE TABLE ndh.clinical_credential (
    id SERIAL PRIMARY KEY,
    -- i.e. M.D.
    credential_acronym VARCHAR(20)   NOT NULL,
    -- i.e. Medical Doctor
    credential_name VARCHAR(100)   NOT NULL,
    -- for when there is only one source for the credential (unlike medical schools etc)
    credential_source_url VARCHAR(250)   NOT NULL,
    graduation_date DATE,
    clinical_school_id INT 
);

-- Source: ./sql/create_table_sql/create_individual.sql
CREATE TABLE ndh.clinical_school (
    id SERIAL PRIMARY KEY,
    -- i.e. M.D.
    clinical_school_name VARCHAR(20)   NOT NULL,
    clinical_school_url VARCHAR(500)
);

-- Source: ./sql/create_table_sql/create_individual.sql
CREATE TABLE ndh.individual_to_credential (
    id SERIAL PRIMARY KEY,
    individual_id int   NOT NULL,
    clinical_credential_id int   NOT NULL
);

-- Source: ./sql/create_table_sql/create_individual.sql
CREATE TABLE ndh.individual (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(100)   NOT NULL,
    first_name VARCHAR(100)   NOT NULL,
    middle_name VARCHAR(21)   NOT NULL,
    name_prefix VARCHAR(6)   NOT NULL,
    name_suffix VARCHAR(6)   NOT NULL,
    email_address VARCHAR(200)   DEFAULT NULL,
    ssn VARCHAR(10)   DEFAULT NULL.
    sex_code CHAR(1)  DEFAULT NULL,
    birth_date DATE
);

-- Source: ./sql/create_table_sql/create_interop_endpoint.sql
CREATE TABLE ndh.interop_endpoint_type (
    id SERIAL PRIMARY KEY,
    identifier_type_description TEXT   NOT NULL,
    CONSTRAINT uc_endpoint_type_identifier_type_description UNIQUE (
        identifier_type_description
    )
);

-- Source: ./sql/create_table_sql/create_interop_endpoint.sql
CREATE TABLE ndh.interop_endpoint (
    id SERIAL PRIMARY KEY,
    -- for now only FHIR and Direct
    fhir_endpoint_url VARCHAR(500)   NOT NULL,
    -- endpoint NPPES file as endpoint_description
    endpoint_name VARCHAR(100)   NOT NULL,
    -- endpoint NPPES file as endpoint_comments
    endpoint_desc VARCHAR(100)   NOT NULL,
    endpoint_address_id INT   DEFAULT NULL, -- this I am unsure about. It is specified in the FHIR standard, but perhaps it is ephemerial? What does it mean for a mutli-ONPI EHR endpoint to have 'an' address?
    interop_endpoint_type_id INT DEFAULT 1  NOT NULL,
    -- Prevent duplicate FHIR endpoint URLs
    CONSTRAINT uq_interop_endpoint_url UNIQUE (fhir_endpoint_url)    
);

-- Source: ./sql/create_table_sql/create_interop_endpoint.sql
CREATE TABLE ndh.clinicalorg_to_interopendpoint (
    id SERIAL PRIMARY KEY,
    clinical_organization_id INT   NOT NULL,
    interop_endpoint_id INT   NOT NULL
);

-- Source: ./sql/create_table_sql/create_npi.sql
CREATE TABLE ndh.npi (
    id BIGINT PRIMARY KEY,
    npi BIGINT   NOT NULL,
    entity_type_code SMALLINT   NOT NULL,
    replacement_npi BIGINT  DEFAULT NULL,
    enumeration_date DATE  NOT NULL,
    last_update_date DATE   NOT NULL,
    deactivation_reason_code VARCHAR(3)   NOT NULL,
    deactivation_date DATE ,
    reactivation_date DATE ,
    certification_date DATE 
);

-- Source: ./sql/create_table_sql/create_npi.sql
CREATE TABLE ndh.individual_npi (
    id BIGINT  PRIMARY KEY,
    npi_id BIGINT   NOT NULL UNIQUE,
    individual_id INT   NOT NULL,
    is_sole_proprietor BOOLEAN   NOT NULL

);

-- Source: ./sql/create_table_sql/create_npi.sql
CREATE TABLE ndh.organizational_npi (
    id BIGINT  PRIMARY KEY,
    npi_id BIGINT   NOT NULL UNIQUE,
    clinical_organization_id INT  DEFAULT NULL,
    primary_authorized_official_individual_id INT NOT NULL,
    parent_npi_id BIGINT DEFAULT NULL-- TODO shold this be its own intermediate table? With an is_primary boolean in it?
);

-- Source: ./sql/create_table_sql/create_phone.sql
CREATE TABLE ndh.phone_type (
    id SERIAL PRIMARY KEY,
    phone_type_description TEXT   NOT NULL,
    CONSTRAINT uc_phone_type_phone_type_description UNIQUE (
        phone_type_description
    )
);

-- Source: ./sql/create_table_sql/create_phone.sql
CREATE TABLE ndh.npi_phone (
    id SERIAL PRIMARY KEY,
    npi_id BIGINT   NOT NULL,
    phonetype_id INTEGER   NOT NULL,
    phone_number_id INTEGER   NOT NULL,
    phone_extension VARCHAR(10)   NOT NULL,
    is_fax BOOLEAN   NOT NULL   -- TODO there is an edge case where one provider lists a phone as a fax and another lists it as a phone. Rare, but it could cause complexity
);

-- Source: ./sql/create_table_sql/create_phone.sql
Create TABLE ndh.phone_number (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20)   NOT NULL,
    CONSTRAINT uc_phonenumber_phone_number UNIQUE (phone_number)
);


-- Source: ./sql/create_table_sql/create_provider_taxonomy.sql
CREATE TABLE ndh.nucc_taxonomy_code (
    id SERIAL PRIMARY KEY,
    parent_nucc_taxonomy_code_id INT   NOT NULL,
    taxonomy_code VARCHAR(10)   NOT NULL,
    tax_grouping TEXT   NOT NULL,
    tax_classification TEXT   NOT NULL,
    tax_specialization TEXT   NOT NULL,
    tax_definition TEXT   NOT NULL,
    tax_notes TEXT   NOT NULL,
    tax_display_name TEXT   NOT NULL,
    tax_certifying_board_name TEXT   NOT NULL,
    tax_certifying_board_url TEXT   NOT NULL,
    CONSTRAINT uc_nucctaxonomycode_taxonomy_code UNIQUE (
        taxonomy_code
    )
);

-- Source: ./sql/create_table_sql/create_provider_taxonomy.sql
CREATE TABLE ndh.nucc_taxonomy_code_ancestor_path (
    id SERIAL PRIMARY KEY,
    decendant_nucc_taxonomy_code_id INT   NOT NULL,
    ancestor_nucc_taxonomy_code_id INT   NOT NULL
);

-- Source: ./sql/create_table_sql/create_provider_taxonomy.sql
CREATE TABLE ndh.npi_nucc_taxonomy_code (
    id SERIAL PRIMARY KEY,
    npi_id BIGINT   NOT NULL,
    nucc_taxonomy_code_id INT   NOT NULL,
    license_number VARCHAR(20)   NOT NULL,
    state_code_id INTEGER   NOT NULL,
    is_primary BOOLEAN   NOT NULL,
    taxonomy_group VARCHAR(10)   NOT NULL
);

-- Source: ./sql/create_table_sql/create_provider_taxonomy.sql
CREATE TABLE ndh.medicare_provider_type_code (
    id SERIAL PRIMARY KEY,
    medicare_provider_type_name VARCHAR   NOT NULL
);

-- Source: ./sql/create_table_sql/create_provider_taxonomy.sql
CREATE TABLE ndh.nucc_medicare_provider_type_code (
    id SERIAL PRIMARY KEY,
    medicare_provider_type_code_id INT   NOT NULL,
    nucc_taxonomy_code_id INT   NOT NULL
);

-- Source: ./sql/create_table_sql/create_user_tables.sql
CREATE TABLE ndh.user (
    id SERIAL PRIMARY KEY,
    email varchar   NOT NULL,
    first_name varchar   NOT NULL,
    last_name varchar   NOT NULL,
    is_identity_verified boolean   NOT NULL
);

-- Source: ./sql/create_table_sql/create_user_tables.sql
CREATE TABLE ndh.user_access_role (
    id SERIAL PRIMARY KEY,
    user_id INT   NOT NULL,
    user_role_id INT   NOT NULL,
    npi_id BIGINT   NOT NULL
);

-- Source: ./sql/create_table_sql/create_user_tables.sql
CREATE TABLE ndh.user_role (
    id SERIAL PRIMARY KEY,
    role_name varchar(100)   NOT NULL
);
