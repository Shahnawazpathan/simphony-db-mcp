from server import validate

validate('SELECT pg_catalog.count(*) FROM mcp_reporting.daily_sales')
for query in [
    'DELETE FROM mcp_reporting.daily_sales',
    'SELECT 1; SELECT 2',
    'SELECT * FROM public.auth_user',
    'SELECT pg_catalog.pg_sleep(9)',
    'SELECT x FROM mcp_reporting.daily_sales FOR UPDATE',
    'SELECT 1 INTO test_table',
    'WITH x AS (DELETE FROM mcp_reporting.daily_sales RETURNING *) SELECT 1',
]:
    try:
        validate(query)
    except ValueError:
        continue
    raise AssertionError(f'Accepted prohibited query: {query}')
print('SQL validation passed')
