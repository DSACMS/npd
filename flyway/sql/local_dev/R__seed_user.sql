-- Seed the local development DB with a superuser in the "Developers" group
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
VALUES
    -- PBKDF2 encoded string for "password123", generated with:
    --   echo '{"password_input":"password123"}' | python infrastructure/modules/fhir-api/generate_hash.py
    (
        'pbkdf2_sha256$1000000$abb7cc0b98bc51048fd48d8d47f86744$9+dkxu3JWeQ74YAzLusq4Rwq1jYnS+fjepjGfo3Cppo=',
        true,
        'developer@cms.hhs.gov',
        'developer@cms.hhs.gov',
        'NPD',
        'Developer',
        true,
        true,
        now()
    ) ON CONFLICT
DO NOTHING;

-- add the Developers group
INSERT INTO
    auth_group (name)
VALUES
    ('Developers') ON CONFLICT
DO NOTHING;

-- ensure the superuser is in the group
INSERT INTO
    auth_user_groups (user_id, group_id)
VALUES
    (
        (
            select
                id
            from
                auth_user
            where
                username = 'developer@cms.hhs.gov'
        ),
        (
            select
                id
            from
                auth_group
            where
                name = 'Developers'
        )
    ) ON CONFLICT
DO NOTHING;