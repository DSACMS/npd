
CREATE TABLE ndh.address (
    id SERIAL PRIMARY KEY,
    barcode_delivery_code VARCHAR(12),
    smarty_key VARCHAR(10),
    address_us_id INT NULL, --references address_us.id
    address_international_id INT NULL, --references address_international.id
    address_nonstandard_id INT NULL --references address_nonstandard.id
);

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
    state_code CHAR(2), --references fips_state.state_code
    zipcode CHAR(5),
    plus4_code VARCHAR(4),
    delivery_point CHAR(2),
    delivery_point_check_digit CHAR(1),
    -- Metadata
    record_type CHAR(1),
    zip_type VARCHAR(32),
    county_code CHAR(5), --references fips_county.county_code
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

CREATE TABLE ndh.address_type (
    id SERIAL PRIMARY KEY,
    address_type_description TEXT   NOT NULL,
    CONSTRAINT uc_address_type_address_type_description UNIQUE (
        address_type_description
    )
);


CREATE TABLE ndh.fips_state (
    state_code CHAR(2)   primary key,
    state_name VARCHAR(100)   NOT NULL,
    CONSTRAINT uc_fips_state_state_name UNIQUE (
        state_name
    )
);

CREATE TABLE ndh.fips_county (
    county_code VARCHAR(5) primary key,
    county_name VARCHAR(200),
    state_code VARCHAR(2), --references fips_state.state_code,
    CONSTRAINT uc_fips_county UNIQUE (
        county_name
    )
);


CREATE TABLE ndh.organization_to_address (
    organization_id BIGINT   NOT NULL, --references clinical_organization.id
    address_type_id INTEGER   NOT NULL, --references address_type.id
    address_id INT   NOT NULL, --references address.id
    primary key (organization_id, address_id)
);

CREATE TABLE ndh.individual_to_address (
    individual_id BIGINT   NOT NULL, --references individual.id
    address_type_id INTEGER   NOT NULL, --references address_type.id
    address_id INT   NOT NULL, --references address.id
    primary key (individual_id, address_id)
);


CREATE TABLE ndh.organization (
    id SERIAL PRIMARY KEY,
    npi bigint, --references npi.npi
    organization_description VARCHAR(2000) NOT NULL,
    organization_legal_name VARCHAR(200)   NOT NULL,
    authorized_official_individual_id INT   NOT NULL, --references individual.id
    primary_authorized_official_individual_id INT NOT NULL --references individual.id
);

CREATE TABLE ndh.organization_to_tax_identifier (
    organization_id int, --references clinical_organization.id
    organization_tin VARCHAR(10),
    organization_vtin VARCHAR(50) DEFAULT NULL,
    organization_glief VARCHAR(300)  DEFAULT NULL,
    CONSTRAINT uc_organization_tax_identifier_organization_tin UNIQUE (
        organization_tin
    ),
    CONSTRAINT uc_organization_tax_identifier_organization_vtin UNIQUE (
        organization_vtin
    ),
    CONSTRAINT uc_organization_tax_identifier_organization_glief UNIQUE (
        organization_glief
    ),
    primary key (organization_id, organization_tin)
);


CREATE TABLE ndh.organization_hierarchy (
    organization_id int, --references clinical_organization.id
    parent_organization_id int, --references clinical_organization.id
    PRIMARY KEY (organization_id, parent_organization_id)
);


CREATE TABLE ndh.organization_name_type (
    id SERIAL PRIMARY KEY,
    name_type TEXT   NOT NULL,
    CONSTRAINT uc_orgname_type_orgname_description UNIQUE (
        name_type
    )
);

CREATE TABLE ndh.organization_name (
    id SERIAL PRIMARY KEY,
    organization_id INT   NOT NULL, --references organization.id
    organization_name VARCHAR(70)   NOT NULL,
    organization_name_type_id INTEGER   NOT NULL --references organization_name_type.id
);


CREATE TABLE ndh.individual_to_organization (
    organization_id INT, --references clinical_organization.id
    individual_id INT, --references individual.id
    relationship_type_id int, --references relationship_type.id
    primary key (organization_id, individual_id, relationship_type_id)
);

CREATE TABLE ndh.relationship_type (
    relationship_type_id SERIAL PRIMARY KEY,
    relationship_type_value varchar(200) --assigning, sole proprietor, etc.
);


CREATE TABLE ndh.organization_to_ehr_instance (
    id SERIAL PRIMARY KEY,
    organization_id INT NOT NULL, --references organization.id
    ehr_id INT NOT NULL --references ehr_instance.id
);


CREATE TABLE ndh.ehr_instance (
    id SERIAL PRIMARY KEY,
    -- Sourced from CHPL data here https://chpl.healthit.gov/
    chpl_id VARCHAR(200)   NOT NULL, --FRED: Can we use this as pk?
    bulk_endpoint_json_url VARCHAR(500) NULL
);


CREATE TABLE ndh.healthcare_brand (
    id SERIAL PRIMARY KEY,
    healthcare_brand_name VARCHAR(200)   NOT NULL,
    trademark_serial_number VARCHAR(20)   NOT NULL
);


CREATE TABLE ndh.organization_to_healthcare_brand (
    healthcare_brand_id INT NOT NULL, --references healthcare_brand.id
    organization_id INT NOT NULL, --references clinical_organization.id
    PRIMARY KEY (healthcare_brand_id, organization_id)
);


CREATE TABLE ndh.other_identifier_type (
    id SERIAL PRIMARY KEY,
    identifier_type_description TEXT NOT NULL,
    CONSTRAINT uc_identifier_type_identifier_type_description UNIQUE (
        identifier_type_description
    )
);


CREATE TABLE ndh.individual_to_other_identifier (
    individual_id  int NOT NULL, --references individual.id
    identifier VARCHAR(21)   NOT NULL,
    identifier_type_id INTEGER   NOT NULL, --references identifier_type.id
    state_code char(2), --references fips_state.state_code
    identifier_issuer_name VARCHAR(81)   NOT NULL,
    identifier_issue_date date,
    identifier_expiry_date date,
    primary key (individual_id, identifier, state_code)
);


CREATE TABLE ndh.certification_credential (
    id SERIAL PRIMARY KEY,
    -- i.e. M.D.
    credential_acronym VARCHAR(20)   NOT NULL,
    -- i.e. Medical Doctor
    credential_name VARCHAR(100)   NOT NULL,
    -- for when there is only one source for the credential (unlike medical schools etc)
    credential_source_url VARCHAR(250)   NOT NULL,
    graduation_date DATE,
    clinical_school_id INT --references clinical_school.id
);

CREATE TABLE ndh.language_spoken (
    language_abbreviation char(2) primary key,
    language_description varchar(200)
);

CREATE TABLE ndh.individual_to_language_spoken (
    individual_id int, --references individual.id
    language_abbreviation char(2),
    primary key (individual_id, language_abbreviation)
);

CREATE TABLE ndh.individual_to_schedule (
    individual_id int, --references individual_to_address
    address_id int not null, --references individual_to_address
    day_of_week int,
    start_time int, --24 hour clock
    end_time int, --24 hour clock
    primary key (individual_id, day_of_week, start_time, end_time)
);

CREATE TABLE ndh.clinical_school (
    id SERIAL PRIMARY KEY,
    -- i.e. M.D.
    clinical_school_name VARCHAR(20)   NOT NULL,
    clinical_school_url VARCHAR(500)
);


CREATE TABLE ndh.individual_to_certification_credential (
    individual_id int   NOT NULL,
    certification_credential_id int   NOT NULL, --references certification_credential.id
    primary key (individual_id, certification_credential_id)
);


CREATE TABLE ndh.individual (
    id SERIAL PRIMARY KEY,
    ssn VARCHAR(10)   DEFAULT NULL,
    sex_code CHAR(1)  DEFAULT NULL,
    birth_date DATE,
    npi bigint
);

CREATE TABLE ndh.individual_to_name (
    individual_id int, --references individual.id
    last_name VARCHAR(100)   NOT NULL,
    first_name VARCHAR(100)   NOT NULL,
    middle_name VARCHAR(21)   NOT NULL,
    name_prefix VARCHAR(6)   NOT NULL,
    name_suffix VARCHAR(6)   NOT NULL,
    name_type_id int, --references name_type.id
    effective_date date NOT null,
    end_date date,
    primary key (individual_id, last_name, first_name, middle_name, name_prefix, name_suffix, name_type_id, effective_date)
);

CREATE TABLE ndh.name_type (
    id serial primary key,
    name_type varchar(50)
);

CREATE TABLE ndh.individual_to_email_address (
    individual_id int, --references individual.id
    email_address varchar(300),
    primary key (individual_id, email_address)
);


CREATE TABLE ndh.interop_endpoint_type (
    id SERIAL PRIMARY KEY,
    interop_endpoint_type_description TEXT   NOT NULL,
    CONSTRAINT uc_interop_endpoint_type_interop_endpoint_type_description UNIQUE (
        interop_endpoint_type_description
    )
);


CREATE TABLE ndh.interop_endpoint (
    id SERIAL PRIMARY KEY,
    -- for now only FHIR and Direct
    interop_endpoint_url VARCHAR(500)   NOT NULL,
    -- endpoint NPPES file as endpoint_description
    interop_endpoint_name VARCHAR(100)   NOT NULL,
    -- endpoint NPPES file as endpoint_comments
    interop_endpoint_description VARCHAR(100)   NOT NULL,
    interop_endpoint_type_id INT DEFAULT 1  NOT NULL, --references interop_endpoint_type.id
    -- Prevent duplicate FHIR endpoint URLs
    CONSTRAINT uq_interop_endpoint_interop_endpoint_url UNIQUE (interop_endpoint_url)    
);


CREATE TABLE ndh.organization_to_interop_endpoint (
    id SERIAL PRIMARY KEY,
    organization_id INT   NOT NULL, --references organization.id
    interop_endpoint_id INT   NOT NULL --references interop_endpoint.id
);


CREATE TABLE ndh.npi (
    npi BIGINT   primary key check (npi>999999999 and npi<10000000000), --currently npis are 10 digits
    entity_type_code SMALLINT   NOT NULL,
    replacement_npi BIGINT  DEFAULT NULL, --references ndh.npi
    enumeration_date DATE  NOT NULL,
    last_update_date DATE   NOT NULL,
    deactivation_reason_code VARCHAR(3)   NOT NULL,
    deactivation_date DATE ,
    reactivation_date DATE ,
    certification_date DATE 
);


CREATE TABLE ndh.phone_type (
    id SERIAL PRIMARY KEY,
    phone_type_description TEXT   NOT NULL,
    CONSTRAINT uc_phone_type_phone_type_description UNIQUE (
        phone_type_description
    )
);


CREATE TABLE ndh.individual_to_phone_number (
    individual_id BIGINT   NOT NULL, --references individual.id
    phone_type_id INTEGER   NOT NULL, --references phone_type.id
    phone_number_id INTEGER   NOT NULL, --references phone_number.id
    phone_extension VARCHAR(10)   NOT NULL,
    --to the prior comment about the fax issue, phone type would include fax
    PRIMARY KEY (individual_id, phone_number_id)
);


Create TABLE ndh.phone_number (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20)   NOT NULL,
    CONSTRAINT uc_phone_number_phone_number UNIQUE (phone_number)
);



CREATE TABLE ndh.nucc_taxonomy_code (
    taxonomy_code VARCHAR(10) primary key,
    taxonomy_display_name TEXT   NOT NULL,
    parent_taxonomy_code VARCHAR(10), --references nucc_taxonomy_code.taxonomy_code (Note: this is how we get the classification/ specialization/ etc.)
    taxonomy_definition TEXT   NOT NULL,
    taxonomy_notes TEXT   NOT NULL,
    tax_certifying_board_name TEXT   NOT NULL,
    tax_certifying_board_url TEXT   NOT NULL,
    CONSTRAINT uc_nucc_taxonomy_code_taxonomy_code UNIQUE (
        taxonomy_code
    )
);


CREATE TABLE ndh.individual_to_nucc_taxonomy_code (
    individual_id int, --references individual.id
    nucc_taxonomy_code INT, --references nucc_taxonomy_code.taxonomy_code
    license_number VARCHAR(20),
    state_code char(2), --references fips_state.state_code
    is_primary BOOLEAN,
    primary key (individual_id, nucc_taxonomy_code, state_code)
);


CREATE TABLE ndh.medicare_provider_type (
    id SERIAL PRIMARY KEY,
    medicare_provider_type_name VARCHAR   NOT NULL
);

--FRED: Is this part of the hydration or something we'll be storing like this long term?
CREATE TABLE ndh.taxonomy_code_to_medicare_provider_type_code (
    id SERIAL PRIMARY KEY,
    medicare_provider_type_code_id INT   NOT NULL,
    nucc_taxonomy_code_id INT   NOT NULL
);

