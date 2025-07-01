LOAD DATA LOCAL INFILE 'REPLACE_ME_CSV_FULL_PATH'
INTO TABLE REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @npi, @provider_other_organization_name, @provider_other_organization_name_type_code
)
SET
    `npi` = NULLIF(@npi, ''),
    `provider_other_organization_name` = NULLIF(@provider_other_organization_name, ''),
    `provider_other_organization_name_type_code` = NULLIF(@provider_other_organization_name_type_code, '')
;