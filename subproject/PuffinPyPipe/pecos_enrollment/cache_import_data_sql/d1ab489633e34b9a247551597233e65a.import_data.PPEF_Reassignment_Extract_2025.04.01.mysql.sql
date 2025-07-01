LOAD DATA LOCAL INFILE 'REPLACE_ME_CSV_FULL_PATH'
INTO TABLE REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @reasgn_bnft_enrlmt_id, @rcv_bnft_enrlmt_id
)
SET
    `reasgn_bnft_enrlmt_id` = NULLIF(@reasgn_bnft_enrlmt_id, ''),
    `rcv_bnft_enrlmt_id` = NULLIF(@rcv_bnft_enrlmt_id, '')
;