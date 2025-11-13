-- Upsert a bootstrap / default superuser account if and only if a variable has
-- been passed into the `flyway migrate` script
--
-- WARNING: any time this script is run with a new value for
-- `superuserDefaultPassword`, the INSERT will be attempted.
INSERT INTO
    auth_user (
        password,
        is_superuser,
        username,
        email,
        first_name,
        last_name,
        is_staff,
        is_active,
        date_joined
    )
SELECT
    '${superuserDefaultPassword}',
    true,
    'npd+deploy@cms.hhs.gov',
    'npd+deploy@cms.hhs.gov',
    'NPD',
    'Deployment',
    true,
    true,
    now()
WHERE
    '${superuserDefaultPassword}' LIKE 'pbkdf2_sha256$%' ON CONFLICT (username)
DO
UPDATE
SET
    password = '${superuserDefaultPassword}';