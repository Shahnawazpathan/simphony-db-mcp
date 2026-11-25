-- Run as a DBA while connected to the intended database.
-- This changes privileges only. It creates no tables, views, or schemas.
BEGIN;
DO $permissions$
DECLARE
    tbl record;
    columns_to_read text;
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'simphony_mcp_read') THEN
        CREATE ROLE simphony_mcp_read NOLOGIN;
    END IF;
    IF EXISTS (SELECT FROM pg_namespace WHERE nspname = 'mcp_reporting') THEN
        REVOKE ALL ON SCHEMA mcp_reporting FROM simphony_mcp_read;
        REVOKE ALL ON ALL TABLES IN SCHEMA mcp_reporting FROM simphony_mcp_read;
    END IF;
    EXECUTE format('GRANT CONNECT ON DATABASE %I TO simphony_mcp_read', current_database());
    FOR tbl IN
        SELECT c.oid, n.nspname, c.relname
        FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('r', 'p')
          AND left(n.nspname, 3) <> 'pg_'
          AND n.nspname NOT IN ('information_schema', 'mcp_reporting')
    LOOP
        SELECT string_agg(format('%I', attname), ', ' ORDER BY attnum)
        INTO columns_to_read
        FROM pg_attribute
        WHERE attrelid = tbl.oid AND attnum > 0 AND NOT attisdropped
          AND attname !~* 'password|secret|token|api_?key|credential|session_key|session_data|cookie';
        IF columns_to_read IS NOT NULL THEN
            EXECUTE format('GRANT USAGE ON SCHEMA %I TO simphony_mcp_read', tbl.nspname);
            EXECUTE format('GRANT SELECT (%s) ON TABLE %I.%I TO simphony_mcp_read',
                           columns_to_read, tbl.nspname, tbl.relname);
        END IF;
    END LOOP;
END
$permissions$;
COMMIT;
