LOAD DATA LOCAL INFILE 'REPLACE_ME_CSV_FULL_PATH'
INTO TABLE REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @full_name, @years_old, @email, @phone, @birth_date, @annual_salary
)
SET
    `full_name` = NULLIF(@full_name, ''),
    `years_old` = NULLIF(@years_old, ''),
    `email` = NULLIF(@email, ''),
    `phone` = NULLIF(@phone, ''),
    `birth_date` = NULLIF(@birth_date, ''),
    `annual_salary` = NULLIF(@annual_salary, '')
;