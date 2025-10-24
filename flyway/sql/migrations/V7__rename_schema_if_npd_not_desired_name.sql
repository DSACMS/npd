--all migration files after this should have the placeholder schema name
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = '${apiSchema}') THEN
        RAISE NOTICE 'Schema ${apiSchema} already exists';
    ELSE
        ALTER SCHEMA npd RENAME TO ${apiSchema};
    END IF;
END $$;