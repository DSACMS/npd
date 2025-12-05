-- ensure that `python manage.py showmigrations` returns:
--
--   flags
--    [X] 0012_replace_migrations_for_wagtail_independence (11 squashed migrations)
--    [X] 0013_add_required_field
--
INSERT INTO
    ${apiSchema}.django_migrations (app, name, applied)
VALUES
    ('flags', '0001_initial', now()),
    ('flags', '0002_auto_20151030_1401', now()),
    ('flags', '0003_flag_hidden', now()),
    ('flags', '0004_remove_flag_hidden', now()),
    ('flags', '0005_flag_enabled_by_default', now()),
    ('flags', '0006_auto_20151217_2003', now()),
    ('flags', '0007_unique_flag_site', now()),
    ('flags', '0008_add_state_conditions', now()),
    ('flags', '0009_migrate_to_conditional_state', now()),
    ('flags', '0010_delete_flag_site_fk', now()),
    ('flags', '0011_migrate_path_data_startswith_to_matches', now()),
    ('flags', '0012_replace_migrations_for_wagtail_independence', now()),
    ('flags', '0013_add_required_field', now());
