LOAD DATA LOCAL INFILE 'REPLACE_ME_CSV_FULL_PATH'
INTO TABLE REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @npi, @provider_secondary_practice_location_address_address_line_1, @provider_secondary_practice_location_address_address_line_2, @provider_secondary_practice_location_address_city_name, @provider_secondary_practice_location_address_state_name, @provider_secondary_practice_location_address_postal_code, @provider_secondary_practice_location_address_country_code_if, @provider_secondary_practice_location_address_telephone_numbe, @provider_secondary_practice_location_address_telephone_exten, @provider_practice_location_address_fax_number
)
SET
    `npi` = NULLIF(@npi, ''),
    `provider_secondary_practice_location_address_address_line_1` = NULLIF(@provider_secondary_practice_location_address_address_line_1, ''),
    `provider_secondary_practice_location_address_address_line_2` = NULLIF(@provider_secondary_practice_location_address_address_line_2, ''),
    `provider_secondary_practice_location_address_city_name` = NULLIF(@provider_secondary_practice_location_address_city_name, ''),
    `provider_secondary_practice_location_address_state_name` = NULLIF(@provider_secondary_practice_location_address_state_name, ''),
    `provider_secondary_practice_location_address_postal_code` = NULLIF(@provider_secondary_practice_location_address_postal_code, ''),
    `provider_secondary_practice_location_address_country_code_if` = NULLIF(@provider_secondary_practice_location_address_country_code_if, ''),
    `provider_secondary_practice_location_address_telephone_numbe` = NULLIF(@provider_secondary_practice_location_address_telephone_numbe, ''),
    `provider_secondary_practice_location_address_telephone_exten` = NULLIF(@provider_secondary_practice_location_address_telephone_exten, ''),
    `provider_practice_location_address_fax_number` = NULLIF(@provider_practice_location_address_fax_number, '')
;