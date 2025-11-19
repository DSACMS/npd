-- seed default feature flags
INSERT INTO
    flags_flagstate (name, condition, value, required)
values
    ('SEARCH_APP', 'in_group', 'Developers', false),
    (
        'PROVIDER_LOOKUP',
        'in_group',
        'Developers',
        false
    ),
    (
        'PROVIDER_LOOKUP_DETAILS',
        'in_group',
        'Developers',
        false
    ),
    (
        'ORGANIZATION_LOOKUP',
        'in_group',
        'Developers',
        false
    ),
    (
        'ORGANIZATION_LOOKUP_DETAILS',
        'in_group',
        'Developers',
        false
    ) ON CONFLICT
DO NOTHING;