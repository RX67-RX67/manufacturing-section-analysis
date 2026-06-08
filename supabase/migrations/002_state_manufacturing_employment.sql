-- state_manufacturing_employment stores annual state-level manufacturing
-- employment from the Census Bureau's County Business Patterns dataset
-- (NAICS sector 31-33). One snapshot row per state per year — this is
-- cross-sectional data, not a monthly time series like the other tables.
-- fips: 2-digit state FIPS code (e.g. "06" = California)
CREATE TABLE state_manufacturing_employment (
  id          SERIAL PRIMARY KEY,
  fips        TEXT NOT NULL,
  year        INT NOT NULL,
  value       NUMERIC,
  fetched_at  TIMESTAMPTZ DEFAULT now(),
  UNIQUE(fips, year)
);
