LOAD DATA LOCAL INFILE 'REPLACE_ME_CSV_FULL_PATH'
INTO TABLE REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
    @Name, @Age, @Email_Address, @Phone_Number, @Date_of_Birth, @Salary
)
SET
    `Name` = NULLIF(@Name, ''),
    `Age` = NULLIF(@Age, ''),
    `Email_Address` = NULLIF(@Email_Address, ''),
    `Phone_Number` = NULLIF(@Phone_Number, ''),
    `Date_of_Birth` = NULLIF(@Date_of_Birth, ''),
    `Salary` = NULLIF(@Salary, '')
;