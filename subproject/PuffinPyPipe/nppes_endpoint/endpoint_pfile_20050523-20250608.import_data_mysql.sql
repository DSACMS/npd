LOAD DATA LOCAL INFILE 'REPLACE_ME_CSV_FULL_PATH'
INTO TABLE REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @npi, @endpoint_type, @endpoint_type_description, @endpoint, @affiliation, @endpoint_description, @affiliation_legal_business_name, @use_code, @use_description, @other_use_description, @content_type, @content_description, @other_content_description, @affiliation_address_line_1, @affiliation_address_line_1, @affiliation_address_city, @affiliation_address_state, @affiliation_address_country, @affiliation_address_postal_code
)
SET
    `npi` = NULLIF(@npi, ''),
    `endpoint_type` = NULLIF(@endpoint_type, ''),
    `endpoint_type_description` = NULLIF(@endpoint_type_description, ''),
    `endpoint` = NULLIF(@endpoint, ''),
    `affiliation` = NULLIF(@affiliation, ''),
    `endpoint_description` = NULLIF(@endpoint_description, ''),
    `affiliation_legal_business_name` = NULLIF(@affiliation_legal_business_name, ''),
    `use_code` = NULLIF(@use_code, ''),
    `use_description` = NULLIF(@use_description, ''),
    `other_use_description` = NULLIF(@other_use_description, ''),
    `content_type` = NULLIF(@content_type, ''),
    `content_description` = NULLIF(@content_description, ''),
    `other_content_description` = NULLIF(@other_content_description, ''),
    `affiliation_address_line_1` = NULLIF(@affiliation_address_line_1, ''),
    `affiliation_address_line_1` = NULLIF(@affiliation_address_line_1, ''),
    `affiliation_address_city` = NULLIF(@affiliation_address_city, ''),
    `affiliation_address_state` = NULLIF(@affiliation_address_state, ''),
    `affiliation_address_country` = NULLIF(@affiliation_address_country, ''),
    `affiliation_address_postal_code` = NULLIF(@affiliation_address_postal_code, '')
;