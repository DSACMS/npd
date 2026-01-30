DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'npd_readonly') THEN
        CREATE USER npd_readonly WITH PASSWORD '${npdReadonlyPassword}';
    ELSE
        ALTER USER npd_readonly WITH PASSWORD '${npdReadonlyPassword}';
    END IF;
END
$$;

GRANT pg_read_all_data TO npd_readonly;