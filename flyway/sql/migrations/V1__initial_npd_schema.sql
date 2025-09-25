--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Homebrew)
-- Dumped by pg_dump version 17.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: npd; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA npd;


--
-- Name: address; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.address (
    id uuid NOT NULL,
    barcode_delivery_code character varying(12),
    smarty_key character varying(10),
    address_us_id uuid,
    address_international_id uuid,
    address_nonstandard_id uuid
);


--
-- Name: address_international; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.address_international (
    id uuid NOT NULL,
    input_id character varying(36),
    country_code character varying(2) NOT NULL,
    geocode character varying(4),
    local_language character varying(6),
    freeform character varying(512),
    address1 character varying(64) NOT NULL,
    address2 character varying(64),
    address3 character varying(64),
    address4 character varying(64),
    organization character varying(64),
    locality character varying(64),
    administrative_area character varying(32),
    postal_code character varying(16),
    administrative_area_iso2 character varying(8),
    sub_administrative_area character varying(64),
    country_iso_3 character varying(3),
    premise character varying(64),
    premise_number character varying(64),
    thoroughfare character varying(64),
    latitude numeric(9,6),
    longitude numeric(9,6),
    geocode_precision character varying(32),
    max_geocode_precision character varying(32),
    address_format character varying(128),
    verification_status character varying(32),
    address_precision character varying(32),
    max_address_precision character varying(32)
);


--
-- Name: address_nonstandard; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.address_nonstandard (
    id uuid NOT NULL,
    input_id character varying(36),
    input_index integer,
    candidate_index integer,
    addressee character varying(64),
    delivery_line_1 character varying(64) NOT NULL,
    delivery_line_2 character varying(64),
    last_line character varying(64),
    address_type character varying(32),
    address_format character varying(128),
    raw_address text,
    latitude numeric(9,6),
    longitude numeric(9,6),
    notes text
);


--
-- Name: address_us; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.address_us (
    id uuid NOT NULL,
    input_id character varying(36),
    input_index integer,
    candidate_index integer,
    addressee character varying(64),
    delivery_line_1 character varying(64),
    delivery_line_2 character varying(64),
    last_line character varying(64),
    delivery_point_barcode character varying(12),
    urbanization character varying(64),
    primary_number character varying(30) NOT NULL,
    street_name character varying(64) NOT NULL,
    street_predirection character varying(16),
    street_postdirection character varying(16),
    street_suffix character varying(16),
    secondary_number character varying(32),
    secondary_designator character varying(16),
    extra_secondary_number character varying(32),
    extra_secondary_designator character varying(16),
    pmb_designator character varying(16),
    pmb_number character varying(16),
    city_name character varying(64) NOT NULL,
    default_city_name character varying(64),
    state_code character(2) NOT NULL,
    zipcode character(5) NOT NULL,
    plus4_code character varying(4),
    delivery_point character(2),
    delivery_point_check_digit character(1),
    record_type character(1),
    zip_type character varying(32),
    county_code character(5) NOT NULL,
    ews_match character(5),
    carrier_route character(4),
    congressional_district character(2),
    building_default_indicator character(1),
    rdi character varying(12),
    elot_sequence character varying(4),
    elot_sort character varying(4),
    latitude numeric(9,6),
    longitude numeric(9,6),
    coordinate_license integer,
    geo_precision character varying(18),
    time_zone character varying(48),
    utc_offset numeric(4,2),
    dst character(5),
    dpv_match_code character varying(1),
    dpv_footnotes character varying(32),
    dpv_cmra character varying(1),
    dpv_vacant character varying(1),
    dpv_no_stat character varying(1),
    active character varying(1),
    footnotes character varying(24),
    lacslink_code character varying(2),
    lacslink_indicator character varying(1),
    suitelink_match character varying(5),
    enhanced_match character varying(64)
);


--
-- Name: clinical_organization; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.clinical_organization (
    organization_id uuid,
    npi bigint NOT NULL,
    endpoint_instance_id uuid
);


--
-- Name: credential_type; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.credential_type (
    id integer NOT NULL,
    value character varying(20)
);


--
-- Name: credential_type_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.credential_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: credential_type_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.credential_type_id_seq OWNED BY npd.credential_type.id;


--
-- Name: degree_type; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.degree_type (
    id integer NOT NULL,
    value character varying(50)
);


--
-- Name: degree_type_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.degree_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: degree_type_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.degree_type_id_seq OWNED BY npd.degree_type.id;


--
-- Name: ehr_vendor; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.ehr_vendor (
    id uuid NOT NULL,
    name character varying(200) NOT NULL,
    is_cms_aligned_network boolean DEFAULT false
);


--
-- Name: endpoint; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.endpoint (
    id uuid NOT NULL,
    address character varying(200) NOT NULL,
    endpoint_type_id integer NOT NULL,
    endpoint_instance_id uuid NOT NULL
);


--
-- Name: endpoint_instance; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.endpoint_instance (
    id uuid NOT NULL,
    ehr_vendor_id uuid NOT NULL,
    endpoint_instance_type_id integer NOT NULL,
    address character varying(200) NOT NULL
);


--
-- Name: endpoint_instance_type; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.endpoint_instance_type (
    id integer NOT NULL,
    value character varying(50)
);


--
-- Name: endpoint_instance_type_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.endpoint_instance_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: endpoint_instance_type_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.endpoint_instance_type_id_seq OWNED BY npd.endpoint_instance_type.id;


--
-- Name: endpoint_type; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.endpoint_type (
    id integer NOT NULL,
    value character varying(50)
);


--
-- Name: endpoint_type_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.endpoint_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: endpoint_type_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.endpoint_type_id_seq OWNED BY npd.endpoint_type.id;


--
-- Name: fhir_address_use; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.fhir_address_use (
    id integer NOT NULL,
    value character varying(20)
);


--
-- Name: fhir_address_use_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.fhir_address_use_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fhir_address_use_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.fhir_address_use_id_seq OWNED BY npd.fhir_address_use.id;


--
-- Name: fhir_email_use; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.fhir_email_use (
    id integer NOT NULL,
    value character varying(20)
);


--
-- Name: fhir_email_use_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.fhir_email_use_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fhir_email_use_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.fhir_email_use_id_seq OWNED BY npd.fhir_email_use.id;


--
-- Name: fhir_name_use; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.fhir_name_use (
    id integer NOT NULL,
    value character varying(20)
);


--
-- Name: fhir_name_use_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.fhir_name_use_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fhir_name_use_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.fhir_name_use_id_seq OWNED BY npd.fhir_name_use.id;


--
-- Name: fhir_phone_system; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.fhir_phone_system (
    id integer NOT NULL,
    value character varying(20)
);


--
-- Name: fhir_phone_system_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.fhir_phone_system_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fhir_phone_system_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.fhir_phone_system_id_seq OWNED BY npd.fhir_phone_system.id;


--
-- Name: fhir_phone_use; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.fhir_phone_use (
    id integer NOT NULL,
    value character varying(20)
);


--
-- Name: fhir_phone_use_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.fhir_phone_use_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fhir_phone_use_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.fhir_phone_use_id_seq OWNED BY npd.fhir_phone_use.id;


--
-- Name: fips_county; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.fips_county (
    id character varying(5) NOT NULL,
    name character varying(200) NOT NULL,
    fips_state_id character varying(2) NOT NULL
);


--
-- Name: fips_state; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.fips_state (
    id character(2) NOT NULL,
    name character varying(100) NOT NULL,
    abbreviation character(2) NOT NULL
);


--
-- Name: individual; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.individual (
    id uuid NOT NULL,
    ssn_id uuid,
    gender character(1),
    sex character(1),
    birth_date date
);


--
-- Name: individual_to_address; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.individual_to_address (
    individual_id uuid NOT NULL,
    address_id uuid NOT NULL,
    address_use_id integer NOT NULL
);


--
-- Name: individual_to_email; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.individual_to_email (
    individual_id uuid NOT NULL,
    email_address character varying(1000) NOT NULL,
    email_use_id integer NOT NULL
);


--
-- Name: individual_to_language_spoken; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.individual_to_language_spoken (
    language_spoken_id character(2) NOT NULL,
    individual_id uuid NOT NULL
);


--
-- Name: individual_to_name; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.individual_to_name (
    individual_id uuid NOT NULL,
    prefix character varying(10),
    first_name character varying(50) NOT NULL,
    middle_name character varying(50),
    last_name character varying(200) NOT NULL,
    start_date date,
    end_date date,
    name_use_id integer NOT NULL,
    suffix character varying(10)
);


--
-- Name: individual_to_phone; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.individual_to_phone (
    individual_id uuid NOT NULL,
    phone_number character varying(20) NOT NULL,
    extension character varying(10),
    phone_use_id integer NOT NULL
);


--
-- Name: iso_country; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.iso_country (
    code character varying(2) NOT NULL,
    name character varying(50)
);


--
-- Name: language_spoken; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.language_spoken (
    id character varying(2) NOT NULL,
    value character varying(100)
);


--
-- Name: legal_entity; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.legal_entity (
    ein_id uuid NOT NULL,
    dba_name character varying(100) NOT NULL
);


--
-- Name: location; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.location (
    id uuid NOT NULL,
    name character varying(200),
    organization_id uuid NOT NULL,
    address_id uuid NOT NULL
);


--
-- Name: medicare_provider_type; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.medicare_provider_type (
    id integer NOT NULL,
    value character varying(20)
);


--
-- Name: medicare_provider_type_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.medicare_provider_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: medicare_provider_type_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.medicare_provider_type_id_seq OWNED BY npd.medicare_provider_type.id;


--
-- Name: npi; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.npi (
    npi bigint NOT NULL,
    entity_type_code smallint NOT NULL,
    replacement_npi character varying(11),
    enumeration_date date NOT NULL,
    last_update_date date NOT NULL,
    deactivation_reason_code character varying(3),
    deactivation_date date,
    reactivation_date date,
    certification_date date
);


--
-- Name: nucc; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.nucc (
    code character varying(10) NOT NULL,
    display_name text NOT NULL,
    definition text,
    notes text,
    certifying_board_name text,
    certifying_board_url text
);



--
-- Name: nucc_classification; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.nucc_classification (
    id integer NOT NULL,
    nucc_code character varying(10),
    display_name character varying(100),
    nucc_grouping_id integer
);


--
-- Name: nucc_classification_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.nucc_classification_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: nucc_classification_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.nucc_classification_id_seq OWNED BY npd.nucc_classification.id;


--
-- Name: nucc_grouping; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.nucc_grouping (
    id integer NOT NULL,
    display_name character varying(100)
);


--
-- Name: nucc_grouping_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.nucc_grouping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: nucc_grouping_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.nucc_grouping_id_seq OWNED BY npd.nucc_grouping.id;


--
-- Name: nucc_specialization; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.nucc_specialization (
    id integer NOT NULL,
    nucc_code character varying(10),
    display_name character varying(100),
    nucc_classification_id integer
);


--
-- Name: nucc_specialization_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.nucc_specialization_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: nucc_specialization_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.nucc_specialization_id_seq OWNED BY npd.nucc_specialization.id;


--
-- Name: nucc_to_medicare_provider_type; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.nucc_to_medicare_provider_type (
    medicare_provider_type_id integer NOT NULL,
    nucc_code character varying(10) NOT NULL
);


--
-- Name: organization; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.organization (
    id uuid NOT NULL,
    authorized_official_id uuid NOT NULL,
    ein_id uuid,
    parent_id uuid
);


--
-- Name: organization_to_address; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.organization_to_address (
    organization_id uuid NOT NULL,
    address_id uuid NOT NULL,
    address_use_id integer NOT NULL
);


--
-- Name: organization_to_name; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.organization_to_name (
    organization_id uuid NOT NULL,
    name character varying(1000) NOT NULL,
    is_primary boolean DEFAULT false
);


--
-- Name: organization_to_other_id; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.organization_to_other_id (
    npi bigint NOT NULL,
    other_id character varying(100) NOT NULL,
    other_id_type_id integer NOT NULL,
    state_code character varying(2) NOT NULL,
    issuer character varying(200) NOT NULL
);


--
-- Name: organization_to_phone; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.organization_to_phone (
    organization_id uuid NOT NULL,
    phone_number character varying(20) NOT NULL,
    extension character varying(10),
    phone_use_id integer NOT NULL
);


--
-- Name: organization_to_taxonomy; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.organization_to_taxonomy (
    npi bigint NOT NULL,
    nucc_code character varying(10) NOT NULL,
    is_primary boolean DEFAULT false
);


--
-- Name: other_id_type; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.other_id_type (
    id integer NOT NULL,
    value character varying(50)
);


--
-- Name: other_id_type_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.other_id_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: other_id_type_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.other_id_type_id_seq OWNED BY npd.other_id_type.id;


--
-- Name: provider; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.provider (
    npi bigint NOT NULL,
    individual_id uuid
);


--
-- Name: provider_education; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.provider_education (
    npi bigint NOT NULL,
    school_id integer NOT NULL,
    degree_type_id integer NOT NULL,
    start_date date,
    end_date date
);


--
-- Name: provider_to_credential; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.provider_to_credential (
    npi bigint NOT NULL,
    credential_type_id integer NOT NULL,
    license_number character varying(20) NOT NULL,
    state_code character(2) NOT NULL,
    nucc_code character varying(10) NOT NULL
);


--
-- Name: provider_to_location; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.provider_to_location (
    individual_id uuid NOT NULL,
    organization_id uuid NOT NULL,
    location_id uuid NOT NULL,
    other_address_id uuid,
    nucc_code integer,
    specialty_id integer
);


--
-- Name: provider_to_organization; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.provider_to_organization (
    individual_id uuid NOT NULL,
    organization_id uuid NOT NULL,
    relationship_type_id integer NOT NULL,
    endpoint_id uuid
);


--
-- Name: provider_to_other_id; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.provider_to_other_id (
    npi bigint NOT NULL,
    other_id character varying(100) NOT NULL,
    other_id_type_id integer NOT NULL,
    state_code character varying(2) NOT NULL,
    issuer character varying(100) NOT NULL
);


--
-- Name: provider_to_taxonomy; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.provider_to_taxonomy (
    npi bigint NOT NULL,
    nucc_code character varying(10) NOT NULL,
    is_primary boolean DEFAULT false
);


--
-- Name: relationship_type; Type: TABLE; Schema: npd; Owner: -
--

CREATE TABLE npd.relationship_type (
    id integer NOT NULL,
    value character varying(20)
);


--
-- Name: relationship_type_id_seq; Type: SEQUENCE; Schema: npd; Owner: -
--

CREATE SEQUENCE npd.relationship_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: relationship_type_id_seq; Type: SEQUENCE OWNED BY; Schema: npd; Owner: -
--

ALTER SEQUENCE npd.relationship_type_id_seq OWNED BY npd.relationship_type.id;


--
-- Name: credential_type id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.credential_type ALTER COLUMN id SET DEFAULT nextval('npd.credential_type_id_seq'::regclass);


--
-- Name: degree_type id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.degree_type ALTER COLUMN id SET DEFAULT nextval('npd.degree_type_id_seq'::regclass);


--
-- Name: endpoint_instance_type id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint_instance_type ALTER COLUMN id SET DEFAULT nextval('npd.endpoint_instance_type_id_seq'::regclass);


--
-- Name: endpoint_type id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint_type ALTER COLUMN id SET DEFAULT nextval('npd.endpoint_type_id_seq'::regclass);


--
-- Name: fhir_address_use id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_address_use ALTER COLUMN id SET DEFAULT nextval('npd.fhir_address_use_id_seq'::regclass);


--
-- Name: fhir_email_use id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_email_use ALTER COLUMN id SET DEFAULT nextval('npd.fhir_email_use_id_seq'::regclass);


--
-- Name: fhir_name_use id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_name_use ALTER COLUMN id SET DEFAULT nextval('npd.fhir_name_use_id_seq'::regclass);


--
-- Name: fhir_phone_system id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_phone_system ALTER COLUMN id SET DEFAULT nextval('npd.fhir_phone_system_id_seq'::regclass);


--
-- Name: fhir_phone_use id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_phone_use ALTER COLUMN id SET DEFAULT nextval('npd.fhir_phone_use_id_seq'::regclass);


--
-- Name: medicare_provider_type id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.medicare_provider_type ALTER COLUMN id SET DEFAULT nextval('npd.medicare_provider_type_id_seq'::regclass);


--
-- Name: nucc_classification id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_classification ALTER COLUMN id SET DEFAULT nextval('npd.nucc_classification_id_seq'::regclass);


--
-- Name: nucc_grouping id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_grouping ALTER COLUMN id SET DEFAULT nextval('npd.nucc_grouping_id_seq'::regclass);


--
-- Name: nucc_specialization id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_specialization ALTER COLUMN id SET DEFAULT nextval('npd.nucc_specialization_id_seq'::regclass);


--
-- Name: other_id_type id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.other_id_type ALTER COLUMN id SET DEFAULT nextval('npd.other_id_type_id_seq'::regclass);


--
-- Name: relationship_type id; Type: DEFAULT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.relationship_type ALTER COLUMN id SET DEFAULT nextval('npd.relationship_type_id_seq'::regclass);


--
-- Name: address pk_address; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.address
    ADD CONSTRAINT pk_address PRIMARY KEY (id);


--
-- Name: address_international pk_address_international; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.address_international
    ADD CONSTRAINT pk_address_international PRIMARY KEY (id);


--
-- Name: address_nonstandard pk_address_nonstandard; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.address_nonstandard
    ADD CONSTRAINT pk_address_nonstandard PRIMARY KEY (id);


--
-- Name: address_us pk_address_us; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.address_us
    ADD CONSTRAINT pk_address_us PRIMARY KEY (id);


--
-- Name: clinical_organization pk_clinical_organization; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.clinical_organization
    ADD CONSTRAINT pk_clinical_organization PRIMARY KEY (npi);


--
-- Name: credential_type pk_credential_type; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.credential_type
    ADD CONSTRAINT pk_credential_type PRIMARY KEY (id);


--
-- Name: degree_type pk_degree_type; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.degree_type
    ADD CONSTRAINT pk_degree_type PRIMARY KEY (id);


--
-- Name: ehr_vendor pk_ehr_vendor; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.ehr_vendor
    ADD CONSTRAINT pk_ehr_vendor PRIMARY KEY (id);


--
-- Name: endpoint pk_endpoint; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint
    ADD CONSTRAINT pk_endpoint PRIMARY KEY (id);


--
-- Name: endpoint_instance pk_endpoint_instance; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint_instance
    ADD CONSTRAINT pk_endpoint_instance PRIMARY KEY (id);


--
-- Name: endpoint_instance_type pk_endpoint_instance_type; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint_instance_type
    ADD CONSTRAINT pk_endpoint_instance_type PRIMARY KEY (id);


--
-- Name: endpoint_type pk_endpoint_type; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint_type
    ADD CONSTRAINT pk_endpoint_type PRIMARY KEY (id);


--
-- Name: fhir_address_use pk_fhir_address_use; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_address_use
    ADD CONSTRAINT pk_fhir_address_use PRIMARY KEY (id);


--
-- Name: fhir_email_use pk_fhir_email_use; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_email_use
    ADD CONSTRAINT pk_fhir_email_use PRIMARY KEY (id);


--
-- Name: fhir_name_use pk_fhir_name_use; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_name_use
    ADD CONSTRAINT pk_fhir_name_use PRIMARY KEY (id);


--
-- Name: fhir_phone_system pk_fhir_phone_system; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_phone_system
    ADD CONSTRAINT pk_fhir_phone_system PRIMARY KEY (id);


--
-- Name: fhir_phone_use pk_fhir_phone_use; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_phone_use
    ADD CONSTRAINT pk_fhir_phone_use PRIMARY KEY (id);


--
-- Name: fips_county pk_fips_county; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fips_county
    ADD CONSTRAINT pk_fips_county PRIMARY KEY (id);


--
-- Name: fips_state pk_fips_state; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fips_state
    ADD CONSTRAINT pk_fips_state PRIMARY KEY (id);


--
-- Name: individual pk_individual; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual
    ADD CONSTRAINT pk_individual PRIMARY KEY (id);


--
-- Name: individual_to_address pk_individual_to_address; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_address
    ADD CONSTRAINT pk_individual_to_address PRIMARY KEY (individual_id, address_id, address_use_id);


--
-- Name: individual_to_email pk_individual_to_email; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_email
    ADD CONSTRAINT pk_individual_to_email PRIMARY KEY (individual_id, email_address, email_use_id);


--
-- Name: individual_to_language_spoken pk_individual_to_language_spoken; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_language_spoken
    ADD CONSTRAINT pk_individual_to_language_spoken PRIMARY KEY (individual_id, language_spoken_id);


--
-- Name: individual_to_name pk_individual_to_name; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_name
    ADD CONSTRAINT pk_individual_to_name PRIMARY KEY (individual_id, first_name, last_name, name_use_id);


--
-- Name: individual_to_phone pk_individual_to_phone; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_phone
    ADD CONSTRAINT pk_individual_to_phone PRIMARY KEY (individual_id, phone_number, phone_use_id);


--
-- Name: iso_country pk_iso_country; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.iso_country
    ADD CONSTRAINT pk_iso_country PRIMARY KEY (code);


--
-- Name: language_spoken pk_language_spoken; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.language_spoken
    ADD CONSTRAINT pk_language_spoken PRIMARY KEY (id);


--
-- Name: legal_entity pk_legal_entity; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.legal_entity
    ADD CONSTRAINT pk_legal_entity PRIMARY KEY (ein_id);


--
-- Name: location pk_location; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.location
    ADD CONSTRAINT pk_location PRIMARY KEY (id);


--
-- Name: medicare_provider_type pk_medicare_provider_type; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.medicare_provider_type
    ADD CONSTRAINT pk_medicare_provider_type PRIMARY KEY (id);


--
-- Name: npi pk_npi; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.npi
    ADD CONSTRAINT pk_npi PRIMARY KEY (npi);


--
-- Name: nucc pk_nucc; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc
    ADD CONSTRAINT pk_nucc PRIMARY KEY (code);


--
-- Name: nucc_classification pk_nucc_classification; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_classification
    ADD CONSTRAINT pk_nucc_classification PRIMARY KEY (id);


--
-- Name: nucc_grouping pk_nucc_grouping; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_grouping
    ADD CONSTRAINT pk_nucc_grouping PRIMARY KEY (id);


--
-- Name: nucc_specialization pk_nucc_specialization; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_specialization
    ADD CONSTRAINT pk_nucc_specialization PRIMARY KEY (id);


--
-- Name: nucc_to_medicare_provider_type pk_nucc_to_medicare_provider_type; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_to_medicare_provider_type
    ADD CONSTRAINT pk_nucc_to_medicare_provider_type PRIMARY KEY (medicare_provider_type_id, nucc_code);


--
-- Name: organization pk_organization; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization
    ADD CONSTRAINT pk_organization PRIMARY KEY (id);


--
-- Name: organization_to_name pk_organization_name; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_name
    ADD CONSTRAINT pk_organization_name PRIMARY KEY (organization_id, name);


--
-- Name: organization_to_address pk_organization_to_address; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_address
    ADD CONSTRAINT pk_organization_to_address PRIMARY KEY (organization_id, address_id, address_use_id);


--
-- Name: organization_to_other_id pk_organization_to_other_id; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_other_id
    ADD CONSTRAINT pk_organization_to_other_id PRIMARY KEY (npi, other_id, other_id_type_id, issuer, state_code);


--
-- Name: organization_to_phone pk_organization_to_phone; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_phone
    ADD CONSTRAINT pk_organization_to_phone PRIMARY KEY (organization_id, phone_number, phone_use_id);


--
-- Name: organization_to_taxonomy pk_organization_to_taxonomy; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_taxonomy
    ADD CONSTRAINT pk_organization_to_taxonomy PRIMARY KEY (npi, nucc_code);


--
-- Name: other_id_type pk_other_id_type; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.other_id_type
    ADD CONSTRAINT pk_other_id_type PRIMARY KEY (id);


--
-- Name: provider pk_provider; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider
    ADD CONSTRAINT pk_provider PRIMARY KEY (npi);


--
-- Name: provider_education pk_provider_education; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_education
    ADD CONSTRAINT pk_provider_education PRIMARY KEY (npi, school_id);


--
-- Name: provider pk_provider_individual_id; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider
    ADD CONSTRAINT pk_provider_individual_id UNIQUE (individual_id);


--
-- Name: provider_to_credential pk_provider_to_credential; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_credential
    ADD CONSTRAINT pk_provider_to_credential PRIMARY KEY (npi, license_number, state_code, nucc_code);


--
-- Name: provider_to_location pk_provider_to_location; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_location
    ADD CONSTRAINT pk_provider_to_location PRIMARY KEY (individual_id, location_id);


--
-- Name: provider_to_organization pk_provider_to_organization; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_organization
    ADD CONSTRAINT pk_provider_to_organization PRIMARY KEY (individual_id, organization_id);


--
-- Name: provider_to_other_id pk_provider_to_other_id; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_other_id
    ADD CONSTRAINT pk_provider_to_other_id PRIMARY KEY (npi, other_id, other_id_type_id, issuer, state_code);


--
-- Name: provider_to_taxonomy pk_provider_to_taxonomy; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_taxonomy
    ADD CONSTRAINT pk_provider_to_taxonomy PRIMARY KEY (npi, nucc_code);


--
-- Name: relationship_type pk_relationship_type; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.relationship_type
    ADD CONSTRAINT pk_relationship_type PRIMARY KEY (id);


--
-- Name: clinical_organization uc_clinical_organization_organization_id; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.clinical_organization
    ADD CONSTRAINT uc_clinical_organization_organization_id UNIQUE (organization_id);


--
-- Name: degree_type uc_degree_type_value; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.degree_type
    ADD CONSTRAINT uc_degree_type_value UNIQUE (value);


--
-- Name: endpoint_instance_type uc_endpoint_instance_type_value; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint_instance_type
    ADD CONSTRAINT uc_endpoint_instance_type_value UNIQUE (value);


--
-- Name: endpoint_type uc_endpoint_type_value; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint_type
    ADD CONSTRAINT uc_endpoint_type_value UNIQUE (value);


--
-- Name: fhir_address_use uc_fhir_address_use_value; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_address_use
    ADD CONSTRAINT uc_fhir_address_use_value UNIQUE (value);


--
-- Name: fhir_email_use uc_fhir_email_use_value; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_email_use
    ADD CONSTRAINT uc_fhir_email_use_value UNIQUE (value);


--
-- Name: fhir_name_use uc_fhir_name_use_value; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_name_use
    ADD CONSTRAINT uc_fhir_name_use_value UNIQUE (value);


--
-- Name: fhir_phone_system uc_fhir_phone_system_value; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_phone_system
    ADD CONSTRAINT uc_fhir_phone_system_value UNIQUE (value);


--
-- Name: fhir_phone_use uc_fhir_phone_use_value; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fhir_phone_use
    ADD CONSTRAINT uc_fhir_phone_use_value UNIQUE (value);


--
-- Name: fips_county uc_fips_county_name_fips_state_id; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fips_county
    ADD CONSTRAINT uc_fips_county_name_fips_state_id UNIQUE (name, fips_state_id);


--
-- Name: fips_state uc_fips_state_abbreviation; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fips_state
    ADD CONSTRAINT uc_fips_state_abbreviation UNIQUE (abbreviation);


--
-- Name: fips_state uc_fips_state_name; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fips_state
    ADD CONSTRAINT uc_fips_state_name UNIQUE (name);


--
-- Name: iso_country uc_iso_country_name; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.iso_country
    ADD CONSTRAINT uc_iso_country_name UNIQUE (name);


--
-- Name: medicare_provider_type uc_medicare_provider_type_value; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.medicare_provider_type
    ADD CONSTRAINT uc_medicare_provider_type_value UNIQUE (value);


--
-- Name: nucc_classification uc_nucc_classification_nucc_code_nucc_grouping; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_classification
    ADD CONSTRAINT uc_nucc_classification_nucc_code_nucc_grouping UNIQUE (nucc_code, nucc_grouping_id);


--
-- Name: nucc_grouping uc_nucc_grouping_display_name; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_grouping
    ADD CONSTRAINT uc_nucc_grouping_display_name UNIQUE (display_name);


--
-- Name: nucc_specialization uc_nucc_specialization_nucc_code_nucc_classification; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_specialization
    ADD CONSTRAINT uc_nucc_specialization_nucc_code_nucc_classification UNIQUE (nucc_code, nucc_classification_id);


--
-- Name: relationship_type uc_relationship_type_value; Type: CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.relationship_type
    ADD CONSTRAINT uc_relationship_type_value UNIQUE (value);


--
-- Name: address fk_address_address_international_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.address
    ADD CONSTRAINT fk_address_address_international_id FOREIGN KEY (address_international_id) REFERENCES npd.address_international(id);


--
-- Name: address fk_address_address_nonstandard_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.address
    ADD CONSTRAINT fk_address_address_nonstandard_id FOREIGN KEY (address_nonstandard_id) REFERENCES npd.address_nonstandard(id);


--
-- Name: address fk_address_address_us_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.address
    ADD CONSTRAINT fk_address_address_us_id FOREIGN KEY (address_us_id) REFERENCES npd.address_us(id);


--
-- Name: address_international fk_address_international_country_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.address_international
    ADD CONSTRAINT fk_address_international_country_code FOREIGN KEY (country_code) REFERENCES npd.iso_country(code);


--
-- Name: address_us fk_address_us_county_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.address_us
    ADD CONSTRAINT fk_address_us_county_code FOREIGN KEY (county_code) REFERENCES npd.fips_county(id);


--
-- Name: address_us fk_address_us_state_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.address_us
    ADD CONSTRAINT fk_address_us_state_code FOREIGN KEY (state_code) REFERENCES npd.fips_state(id);


--
-- Name: clinical_organization fk_clinical_organization_endpoint_instance_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.clinical_organization
    ADD CONSTRAINT fk_clinical_organization_endpoint_instance_id FOREIGN KEY (endpoint_instance_id) REFERENCES npd.endpoint_instance(id);


--
-- Name: clinical_organization fk_clinical_organization_npi; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.clinical_organization
    ADD CONSTRAINT fk_clinical_organization_npi FOREIGN KEY (npi) REFERENCES npd.npi(npi) ON DELETE CASCADE;


--
-- Name: clinical_organization fk_clinical_organization_organization_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.clinical_organization
    ADD CONSTRAINT fk_clinical_organization_organization_id FOREIGN KEY (organization_id) REFERENCES npd.organization(id) ON DELETE CASCADE;


--
-- Name: endpoint fk_endpoint_endpoint_instance_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint
    ADD CONSTRAINT fk_endpoint_endpoint_instance_id FOREIGN KEY (endpoint_instance_id) REFERENCES npd.endpoint_instance(id);


--
-- Name: endpoint fk_endpoint_endpoint_type_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint
    ADD CONSTRAINT fk_endpoint_endpoint_type_id FOREIGN KEY (endpoint_type_id) REFERENCES npd.endpoint_type(id);


--
-- Name: endpoint_instance fk_endpoint_instance_ehr_vendor_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint_instance
    ADD CONSTRAINT fk_endpoint_instance_ehr_vendor_id FOREIGN KEY (ehr_vendor_id) REFERENCES npd.ehr_vendor(id);


--
-- Name: endpoint_instance fk_endpoint_instance_endpoint_instance_type_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.endpoint_instance
    ADD CONSTRAINT fk_endpoint_instance_endpoint_instance_type_id FOREIGN KEY (endpoint_instance_type_id) REFERENCES npd.endpoint_instance_type(id);


--
-- Name: fips_county fk_fips_county_fips_state_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.fips_county
    ADD CONSTRAINT fk_fips_county_fips_state_id FOREIGN KEY (fips_state_id) REFERENCES npd.fips_state(id);


--
-- Name: individual_to_address fk_individual_to_address_address_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_address
    ADD CONSTRAINT fk_individual_to_address_address_id FOREIGN KEY (address_id) REFERENCES npd.address(id);


--
-- Name: individual_to_address fk_individual_to_address_address_use_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_address
    ADD CONSTRAINT fk_individual_to_address_address_use_id FOREIGN KEY (address_use_id) REFERENCES npd.fhir_address_use(id) ON DELETE CASCADE;


--
-- Name: individual_to_address fk_individual_to_address_individual_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_address
    ADD CONSTRAINT fk_individual_to_address_individual_id FOREIGN KEY (individual_id) REFERENCES npd.individual(id) ON DELETE CASCADE;


--
-- Name: individual_to_email fk_individual_to_email_email_use_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_email
    ADD CONSTRAINT fk_individual_to_email_email_use_id FOREIGN KEY (email_use_id) REFERENCES npd.fhir_email_use(id);


--
-- Name: individual_to_email fk_individual_to_email_individual_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_email
    ADD CONSTRAINT fk_individual_to_email_individual_id FOREIGN KEY (individual_id) REFERENCES npd.individual(id) ON DELETE CASCADE;


--
-- Name: individual_to_language_spoken fk_individual_to_language_spoken_language_spoken_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_language_spoken
    ADD CONSTRAINT fk_individual_to_language_spoken_language_spoken_id FOREIGN KEY (language_spoken_id) REFERENCES npd.language_spoken(id);


--
-- Name: individual_to_name fk_individual_to_name_individual_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_name
    ADD CONSTRAINT fk_individual_to_name_individual_id FOREIGN KEY (individual_id) REFERENCES npd.individual(id) ON DELETE CASCADE;


--
-- Name: individual_to_name fk_individual_to_name_name_use_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_name
    ADD CONSTRAINT fk_individual_to_name_name_use_id FOREIGN KEY (name_use_id) REFERENCES npd.fhir_name_use(id);


--
-- Name: individual_to_phone fk_individual_to_phone_individual_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_phone
    ADD CONSTRAINT fk_individual_to_phone_individual_id FOREIGN KEY (individual_id) REFERENCES npd.individual(id) ON DELETE CASCADE;


--
-- Name: individual_to_phone fk_individual_to_phone_phone_use_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.individual_to_phone
    ADD CONSTRAINT fk_individual_to_phone_phone_use_id FOREIGN KEY (phone_use_id) REFERENCES npd.fhir_phone_use(id);


--
-- Name: location fk_location_address_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.location
    ADD CONSTRAINT fk_location_address_id FOREIGN KEY (address_id) REFERENCES npd.address(id);


--
-- Name: location fk_location_organization_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.location
    ADD CONSTRAINT fk_location_organization_id FOREIGN KEY (organization_id) REFERENCES npd.organization(id) ON DELETE CASCADE;


--
-- Name: nucc_classification fk_nucc_classification_nucc_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_classification
    ADD CONSTRAINT fk_nucc_classification_nucc_code FOREIGN KEY (nucc_code) REFERENCES npd.nucc(code);


--
-- Name: nucc_classification fk_nucc_classification_nucc_grouping_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_classification
    ADD CONSTRAINT fk_nucc_classification_nucc_grouping_id FOREIGN KEY (nucc_grouping_id) REFERENCES npd.nucc_grouping(id);


--
-- Name: nucc_specialization fk_nucc_specialization_nucc_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_specialization
    ADD CONSTRAINT fk_nucc_specialization_nucc_code FOREIGN KEY (nucc_code) REFERENCES npd.nucc(code);


--
-- Name: nucc_to_medicare_provider_type fk_nucc_to_medicare_provider_type_medicare_provider_type_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_to_medicare_provider_type
    ADD CONSTRAINT fk_nucc_to_medicare_provider_type_medicare_provider_type_id FOREIGN KEY (medicare_provider_type_id) REFERENCES npd.medicare_provider_type(id);


--
-- Name: nucc_to_medicare_provider_type fk_nucc_to_medicare_provider_type_nucc_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.nucc_to_medicare_provider_type
    ADD CONSTRAINT fk_nucc_to_medicare_provider_type_nucc_code FOREIGN KEY (nucc_code) REFERENCES npd.nucc(code);


--
-- Name: organization fk_organization_authorized_official_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization
    ADD CONSTRAINT fk_organization_authorized_official_id FOREIGN KEY (authorized_official_id) REFERENCES npd.individual(id) ON DELETE CASCADE;


--
-- Name: organization fk_organization_ein_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization
    ADD CONSTRAINT fk_organization_ein_id FOREIGN KEY (ein_id) REFERENCES npd.legal_entity(ein_id);


--
-- Name: organization_to_name fk_organization_name_organization_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_name
    ADD CONSTRAINT fk_organization_name_organization_id FOREIGN KEY (organization_id) REFERENCES npd.organization(id) ON DELETE CASCADE;


--
-- Name: organization fk_organization_parent_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization
    ADD CONSTRAINT fk_organization_parent_id FOREIGN KEY (parent_id) REFERENCES npd.organization(id) ON DELETE CASCADE;


--
-- Name: organization_to_address fk_organization_to_address_address_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_address
    ADD CONSTRAINT fk_organization_to_address_address_id FOREIGN KEY (address_id) REFERENCES npd.address(id);


--
-- Name: organization_to_address fk_organization_to_address_address_use_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_address
    ADD CONSTRAINT fk_organization_to_address_address_use_id FOREIGN KEY (address_use_id) REFERENCES npd.fhir_address_use(id) ON DELETE CASCADE;


--
-- Name: organization_to_address fk_organization_to_address_organization_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_address
    ADD CONSTRAINT fk_organization_to_address_organization_id FOREIGN KEY (organization_id) REFERENCES npd.organization(id) ON DELETE CASCADE;


--
-- Name: organization_to_other_id fk_organization_to_other_id_npi; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_other_id
    ADD CONSTRAINT fk_organization_to_other_id_npi FOREIGN KEY (npi) REFERENCES npd.clinical_organization(npi) ON DELETE CASCADE;


--
-- Name: organization_to_other_id fk_organization_to_other_id_other_id_type_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_other_id
    ADD CONSTRAINT fk_organization_to_other_id_other_id_type_id FOREIGN KEY (other_id_type_id) REFERENCES npd.other_id_type(id);


--
-- Name: provider_to_other_id fk_organization_to_other_id_state_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_other_id
    ADD CONSTRAINT fk_organization_to_other_id_state_code FOREIGN KEY (state_code) REFERENCES npd.fips_state(id);


--
-- Name: organization_to_phone fk_organization_to_phone_organization_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_phone
    ADD CONSTRAINT fk_organization_to_phone_organization_id FOREIGN KEY (organization_id) REFERENCES npd.organization(id) ON DELETE CASCADE;


--
-- Name: organization_to_phone fk_organization_to_phone_phone_use_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_phone
    ADD CONSTRAINT fk_organization_to_phone_phone_use_id FOREIGN KEY (phone_use_id) REFERENCES npd.fhir_phone_use(id);


--
-- Name: organization_to_taxonomy fk_organization_to_taxonomy_npi; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_taxonomy
    ADD CONSTRAINT fk_organization_to_taxonomy_npi FOREIGN KEY (npi) REFERENCES npd.clinical_organization(npi) ON DELETE CASCADE;


--
-- Name: organization_to_taxonomy fk_organization_to_taxonomy_nucc_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.organization_to_taxonomy
    ADD CONSTRAINT fk_organization_to_taxonomy_nucc_code FOREIGN KEY (nucc_code) REFERENCES npd.nucc(code);


--
-- Name: provider_education fk_provider_education_degree_type_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_education
    ADD CONSTRAINT fk_provider_education_degree_type_id FOREIGN KEY (degree_type_id) REFERENCES npd.degree_type(id);


--
-- Name: provider_education fk_provider_education_npi; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_education
    ADD CONSTRAINT fk_provider_education_npi FOREIGN KEY (npi) REFERENCES npd.provider(npi) ON DELETE CASCADE;


--
-- Name: provider fk_provider_individual_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider
    ADD CONSTRAINT fk_provider_individual_id FOREIGN KEY (individual_id) REFERENCES npd.individual(id) ON DELETE CASCADE;


--
-- Name: provider fk_provider_npi; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider
    ADD CONSTRAINT fk_provider_npi FOREIGN KEY (npi) REFERENCES npd.npi(npi) ON DELETE CASCADE;


--
-- Name: provider_to_credential fk_provider_to_credential_credential_type_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_credential
    ADD CONSTRAINT fk_provider_to_credential_credential_type_id FOREIGN KEY (credential_type_id) REFERENCES npd.credential_type(id);


--
-- Name: provider_to_credential fk_provider_to_credential_npi_nucc_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_credential
    ADD CONSTRAINT fk_provider_to_credential_npi_nucc_code FOREIGN KEY (npi, nucc_code) REFERENCES npd.provider_to_taxonomy(npi, nucc_code);


--
-- Name: provider_to_credential fk_provider_to_credential_state_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_credential
    ADD CONSTRAINT fk_provider_to_credential_state_code FOREIGN KEY (state_code) REFERENCES npd.fips_state(id);


--
-- Name: provider_to_location fk_provider_to_location_individual_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_location
    ADD CONSTRAINT fk_provider_to_location_individual_id FOREIGN KEY (individual_id) REFERENCES npd.individual(id) ON DELETE CASCADE;


--
-- Name: provider_to_location fk_provider_to_location_individual_id_organization_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_location
    ADD CONSTRAINT fk_provider_to_location_individual_id_organization_id FOREIGN KEY (individual_id, organization_id) REFERENCES npd.provider_to_organization(individual_id, organization_id);


--
-- Name: provider_to_location fk_provider_to_location_location_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_location
    ADD CONSTRAINT fk_provider_to_location_location_id FOREIGN KEY (location_id) REFERENCES npd.location(id);


--
-- Name: provider_to_location fk_provider_to_location_other_address_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_location
    ADD CONSTRAINT fk_provider_to_location_other_address_id FOREIGN KEY (other_address_id) REFERENCES npd.address(id);


--
-- Name: provider_to_organization fk_provider_to_organization_endpoint_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_organization
    ADD CONSTRAINT fk_provider_to_organization_endpoint_id FOREIGN KEY (endpoint_id) REFERENCES npd.endpoint(id);


--
-- Name: provider_to_organization fk_provider_to_organization_individual_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_organization
    ADD CONSTRAINT fk_provider_to_organization_individual_id FOREIGN KEY (individual_id) REFERENCES npd.provider(individual_id);


--
-- Name: provider_to_organization fk_provider_to_organization_organization_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_organization
    ADD CONSTRAINT fk_provider_to_organization_organization_id FOREIGN KEY (organization_id) REFERENCES npd.organization(id) ON DELETE CASCADE;


--
-- Name: provider_to_organization fk_provider_to_organization_relationship_type_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_organization
    ADD CONSTRAINT fk_provider_to_organization_relationship_type_id FOREIGN KEY (relationship_type_id) REFERENCES npd.relationship_type(id);


--
-- Name: provider_to_other_id fk_provider_to_other_id_npi; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_other_id
    ADD CONSTRAINT fk_provider_to_other_id_npi FOREIGN KEY (npi) REFERENCES npd.provider(npi) ON DELETE CASCADE;


--
-- Name: provider_to_other_id fk_provider_to_other_id_other_id_type_id; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_other_id
    ADD CONSTRAINT fk_provider_to_other_id_other_id_type_id FOREIGN KEY (other_id_type_id) REFERENCES npd.other_id_type(id);


--
-- Name: provider_to_other_id fk_provider_to_other_id_state_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_other_id
    ADD CONSTRAINT fk_provider_to_other_id_state_code FOREIGN KEY (state_code) REFERENCES npd.fips_state(id);


--
-- Name: provider_to_taxonomy fk_provider_to_taxonomy_npi; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_taxonomy
    ADD CONSTRAINT fk_provider_to_taxonomy_npi FOREIGN KEY (npi) REFERENCES npd.provider(npi) ON DELETE CASCADE;


--
-- Name: provider_to_taxonomy fk_provider_to_taxonomy_nucc_code; Type: FK CONSTRAINT; Schema: npd; Owner: -
--

ALTER TABLE ONLY npd.provider_to_taxonomy
    ADD CONSTRAINT fk_provider_to_taxonomy_nucc_code FOREIGN KEY (nucc_code) REFERENCES npd.nucc(code);


--
-- PostgreSQL database dump complete
--

