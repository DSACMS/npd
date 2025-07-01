
CREATE TABLE "User" (
    "id" SERIAL PRIMARY KEY,
    "Email" varchar   NOT NULL,
    "FirstName" varchar   NOT NULL,
    "LastName" varchar   NOT NULL,
    "IdentityVerified" boolean   NOT NULL
);

CREATE TABLE "UserAccessRole" (
    "id" SERIAL PRIMARY KEY,
    "User_id" INT   NOT NULL,
    "Role_id" INT   NOT NULL,
    "NPI_id" BIGINT   NOT NULL
);

CREATE TABLE "Role" (
    "id" SERIAL PRIMARY KEY,
    "Role" varchar(100)   NOT NULL
);
