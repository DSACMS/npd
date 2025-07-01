-- Create an address table using the Smarty Streets API schema as the basis.

-- Main address table
CREATE TABLE address (
    id SERIAL PRIMARY KEY,
    barcode_delivery_code VARCHAR(12),
    smarty_key VARCHAR(10),
    address_us_id INT NULL,
    address_international_id INT NULL,
    address_nonstandard_id INT NULL
);

-- US address table
CREATE TABLE address_us (
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
    precision VARCHAR(18),
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

-- International address table
CREATE TABLE address_international (
    id SERIAL PRIMARY KEY,
    address_id INT NOT NULL,
    input_id VARCHAR(36),
    country VARCHAR(64),
    geocode VARCHAR(4),
    language VARCHAR(6),
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

-- Non-standard address table
CREATE TABLE address_nonstandard (
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


CREATE TABLE "AddressTypeLUT" (
    "id" SERIAL PRIMARY KEY,
    "address_type_description" TEXT   NOT NULL,
    CONSTRAINT "uc_AddressTypeLUT_address_type_description" UNIQUE (
        "address_type_description"
    )
);

-- We keep this seperate because there are several state-data-not-address data elements we need it for.
CREATE TABLE "StateCodeLUT" (
    "id" SERIAL PRIMARY KEY,
    "state_code" VARCHAR(100)   NOT NULL,
    "state_name" VARCHAR(100)   NOT NULL,
    CONSTRAINT "uc_StateCodeLUT_state_code" UNIQUE (
        "state_code"
    )
);

CREATE TABLE "NPIAddress" (
    "id" SERIAL PRIMARY KEY,
    "NPI_id" BIGINT   NOT NULL,
    "AddressType_id" INTEGER   NOT NULL,
    "Address_id" INT   NOT NULL
);
