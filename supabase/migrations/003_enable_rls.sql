-- Enable Row Level Security on all public tables.
--
-- Supabase grants its `anon` and `authenticated` roles full
-- SELECT/INSERT/UPDATE/DELETE privileges on public-schema tables by default.
-- RLS is the only thing standing between those roles and full read/write
-- access via the auto-generated REST API. None of these tables have any
-- policies defined, so enabling RLS makes them default-deny for `anon` and
-- `authenticated` — while the backend (which authenticates with the
-- `service_role` key) is unaffected, since `service_role` always bypasses RLS.

ALTER TABLE fred_series                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE bls_series                     ENABLE ROW LEVEL SECURITY;
ALTER TABLE census_m3                      ENABLE ROW LEVEL SECURITY;
ALTER TABLE bea_data                       ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_reports                     ENABLE ROW LEVEL SECURITY;
ALTER TABLE etl_runs                       ENABLE ROW LEVEL SECURITY;
ALTER TABLE state_manufacturing_employment ENABLE ROW LEVEL SECURITY;
