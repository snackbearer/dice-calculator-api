-- Grants for API runtime user (used with IAM auth)
-- Run this as a DB owner/admin in the target database.

-- Ensure role exists (on RDS this is your DB login role, e.g. diceapp).
-- CREATE ROLE diceapp LOGIN;

-- Required to access objects in public schema.
GRANT USAGE ON SCHEMA public TO diceapp;

-- Read/write privileges on current tables used by the API.
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO diceapp;

-- Required for identity/serial-backed inserts.
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO diceapp;

-- Keep privileges for future objects created by the schema owner.
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO diceapp;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO diceapp;

-- IAM DB auth requires role membership on the DB role.
-- Run this once as admin (safe if already granted):
GRANT rds_iam TO diceapp;
