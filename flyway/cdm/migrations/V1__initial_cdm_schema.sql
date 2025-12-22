CREATE TABLE cdm.address (
    id uuid NOT NULL,
    barcode_delivery_code character varying(12),
    smarty_key character varying(10),
    address_us_id uuid,
    address_international_id uuid,
    address_nonstandard_id uuid
);