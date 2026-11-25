-- Run as a DBA in simphony-db. Provision a separate LOGIN per person.
BEGIN;
CREATE ROLE simphony_mcp_read NOLOGIN;
CREATE SCHEMA mcp_reporting;
REVOKE ALL ON SCHEMA mcp_reporting FROM PUBLIC;
CREATE VIEW mcp_reporting.daily_sales AS
SELECT business_date, location_id, location_name, status,
       journal_checks, sales_net, sales_gross, financial_verified_at
FROM public.grn_salesfastday;
CREATE VIEW mcp_reporting.portal_run_status AS
SELECT from_date, to_date, status, row_count, started_at, finished_at
FROM public.self_service_portal_invoice_portalinvoicerun;
GRANT CONNECT ON DATABASE "simphony-db" TO simphony_mcp_read;
GRANT USAGE ON SCHEMA mcp_reporting TO simphony_mcp_read;
GRANT SELECT ON ALL TABLES IN SCHEMA mcp_reporting TO simphony_mcp_read;
COMMIT;
