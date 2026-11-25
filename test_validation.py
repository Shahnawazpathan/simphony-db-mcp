from server import validate

validate('SELECT pg_catalog.count(*) FROM public.grn_salesfastday')
for query in [
    'DELETE FROM public.grn_salesfastday',
    'SELECT 1; SELECT 2',
    'SELECT * FROM pg_catalog.pg_authid',
    'SELECT * FROM mcp_reporting.daily_sales',
    'SELECT 1 OPERATOR(public.+) 2',
    'SELECT 1::public.custom_type',
    'SELECT pg_catalog.pg_sleep(9)',
    'SELECT x FROM public.grn_salesfastday FOR UPDATE',
    'SELECT 1 INTO test_table',
    'WITH x AS (DELETE FROM public.grn_salesfastday RETURNING *) SELECT 1',
]:
    try:
        validate(query)
    except ValueError:
        continue
    raise AssertionError(f'Accepted prohibited query: {query}')
print('SQL validation passed')
