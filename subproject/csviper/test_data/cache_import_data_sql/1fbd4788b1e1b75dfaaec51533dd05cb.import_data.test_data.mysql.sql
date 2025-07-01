LOAD DATA LOCAL INFILE 'REPLACE_ME_CSV_FULL_PATH'
INTO TABLE REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @employee_full_name, @employee_age, @contact_email, @contact_phone, @birth_date, @annual_salary
)
SET
    `employee_full_name` = NULLIF(@employee_full_name, ''),
    `employee_age` = NULLIF(@employee_age, ''),
    `contact_email` = NULLIF(@contact_email, ''),
    `contact_phone` = NULLIF(@contact_phone, ''),
    `birth_date` = NULLIF(@birth_date, ''),
    `annual_salary` = NULLIF(@annual_salary, '')
;