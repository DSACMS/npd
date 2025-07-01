LOAD DATA LOCAL INFILE 'REPLACE_ME_CSV_FULL_PATH'
INTO TABLE REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @full_name, @age, @email_address, @phone_number, @date_of_birth, @salary
)
SET
    `full_name` = NULLIF(@full_name, ''),
    `age` = NULLIF(@age, ''),
    `email_address` = NULLIF(@email_address, ''),
    `phone_number` = NULLIF(@phone_number, ''),
    `date_of_birth` = NULLIF(@date_of_birth, ''),
    `salary` = NULLIF(@salary, '')
;