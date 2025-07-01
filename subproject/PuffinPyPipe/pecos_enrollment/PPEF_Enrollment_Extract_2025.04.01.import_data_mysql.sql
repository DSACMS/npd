LOAD DATA LOCAL INFILE 'REPLACE_ME_CSV_FULL_PATH'
INTO TABLE REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @npi, @pecos_asct_cntl_id, @enrlmt_id, @provider_type_cd, @provider_type_desc, @state_cd, @first_name, @mdl_name, @last_name, @org_name
)
SET
    `npi` = NULLIF(@npi, ''),
    `pecos_asct_cntl_id` = NULLIF(@pecos_asct_cntl_id, ''),
    `enrlmt_id` = NULLIF(@enrlmt_id, ''),
    `provider_type_cd` = NULLIF(@provider_type_cd, ''),
    `provider_type_desc` = NULLIF(@provider_type_desc, ''),
    `state_cd` = NULLIF(@state_cd, ''),
    `first_name` = NULLIF(@first_name, ''),
    `mdl_name` = NULLIF(@mdl_name, ''),
    `last_name` = NULLIF(@last_name, ''),
    `org_name` = NULLIF(@org_name, '')
;