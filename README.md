# Simphony database MCP

Run read-only sales and portal run audits from a local MCP client. The server
provides two tools, list_reports and query_reports. It has no SSH or shell tool.
Raw invoices, receipts, customer data, and unrestricted tables are outside the
initial reporting scope. To audit inventory, a DBA can add a reviewed inventory
view and grant SELECT on it.

## Install

1. Your DBA runs setup.sql once in simphony-db, creates an individual login with
   no privileges beyond membership in simphony_mcp_read, and provides access via
   an approved private connection or an existing narrow IP firewall rule. Review
   effective grants inherited from PUBLIC before issuing logins. Revoke the
   individual login when access ends.
2. Run python -m venv .venv and install requirements.txt with the venv's pip.
3. Configure your client to start the venv Python with the absolute path to
   server.py. Put SIMPHONY_READ_DSN in its private environment configuration.
   Use verified PostgreSQL TLS (sslmode=verify-full with a matching hostname and
   trusted CA). Never use a database administrator or check credentials into Git.

Example client configuration (local desktop MCP or CLI client supporting stdio):

    {
      "mcpServers": {
        "simphony": {
          "command": "/absolute/path/to/.venv/bin/python",
          "args": ["/absolute/path/to/server.py"]
        }
      }
    }

On Windows use .venv/Scripts/python.exe. Browser-only/cloud clients that cannot
launch a local process need a separate hosted MCP endpoint with per-user
authentication and private database connectivity. This repository supplies the
local server only. Private GitHub access does not grant database access.
A report can establish what the database recorded. Causes outside its records
require corroboration.

Example SQL:

    SELECT business_date, pg_catalog.count(*) AS stores
    FROM mcp_reporting.daily_sales
    WHERE status = 'failed'
    GROUP BY business_date
    ORDER BY business_date DESC;
